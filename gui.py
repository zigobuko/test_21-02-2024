import tkinter as tk
from tkinter import ttk
import data
import api_calls
import threading
import helper

# Modify ttk.Button to handle Return key presses
class TButton(ttk.Button):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.bind('<Return>', self.on_return_press)

    def on_return_press(self, event) -> None:
        self.invoke()

def set_focus_to_widget(widget) -> None:
    widget.focus_set()

def decorator(func):
    def wrapper(*args, **kwargs):
        print(f"Function [{func.__name__}] started")
        func(*args,**kwargs)

    return wrapper


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('SMST')
        self.geometry('650x550')
        self.resizable(width=True, height=False)

        # recall app settings on opening
        data.AppSettings.from_file()

        # Add app title
        title_label = ttk.Label(master=self, text='Sequential Metadata Sending Tool', font='Calibri 24 bold')
        title_label.pack()

        # create notebook
        self.notebook = ttk.Notebook(self.master)
        self.notebook.pack()

        # create tabs in notebook
        self.main_tab = MainTab(self)
        self.add_tab(self.main_tab)

        self.settings_tab = SettingsTab(self)
        self.add_tab(self.settings_tab)

        # Insert saved credentials to main tab if still valid
        if data.AppSettings.credentials:
            self.insert_saved_creds_to_main_tab()
            set_focus_to_widget(self.main_tab.start_button)
        else:
            set_focus_to_widget(self.main_tab.json_entry)

        # Check if there are ARNs saved
        if data.AppSettings.arns:
            self.main_tab.update_arn_dropbox()
            self.settings_tab.insert_data_to_treeview(data.AppSettings.arns)
        else:
            self.notebook.select(1) # switch to Settings tab
            set_focus_to_widget(self.settings_tab.ch_arn_entry)
            self.notebook.tab(0, state='disabled')  # lock Main tab

        # Set focus on widget depending on selected
        self.notebook.bind("<<NotebookTabChanged>>", self.set_focus_on_tab_changed)

        # on app closing
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # run
        self.mainloop()

    def set_focus_on_tab_changed(self, event):
        selected_tab = event.widget.select()
        tab_text = event.widget.tab(selected_tab, "text")
        match tab_text:
            case "Main":
                displayed_creds = self.main_tab.credentials_info.get("1.0", "end-1c")
                if displayed_creds:
                    set_focus_to_widget(self.main_tab.start_button)
            case "Settings":
                # Can be used in future if needed
                pass

    def insert_saved_creds_to_main_tab(self) -> None:
        saved_credentials = data.AppSettings.credentials

        expire_str = saved_credentials['expiration']
        expire_datetime_obj = helper.convert_datetime_str_to_object(expire_str)

        if helper.credentials_expired(expire_datetime_obj):
            self.main_tab.clear_credentials()
            return

        self.main_tab.update_credentials_in_main_tab(saved_credentials)
        set_focus_to_widget(self.main_tab.start_button)

    def add_tab(self, tab):
        self.notebook.add(tab, text=tab.name)

    def on_closing(self):
        data.AppSettings.to_file()
        # self.settings.to_file()
        print("App is closed :)")
        self.destroy()


class MainTab(ttk.Frame):
    def __init__(self, master: App):
        super().__init__(master)
        self.__master = master
        self.name = 'Main'
        self.running_thread = None
        self.stop_flag = False
        self.thread_lock = threading.Lock()

        # arn dropdown
        arn_frame = ttk.Frame(master=self)
        arn_frame.pack(fill="x", padx='10', pady='10')

        arn_label = ttk.Label(master=arn_frame, text='Channel:')
        arn_label.pack(side='left')

        self.selected_arn = tk.StringVar()

        self.arn_dropdown = tk.OptionMenu(arn_frame, self.selected_arn, None)
        # self.arn_dropdown = tk.OptionMenu(arn_frame, self.selected_arn, *self.arn_names)
        self.arn_dropdown.config(width='45')
        self.arn_dropdown.pack(side='left')

        # json string input field
        input_frame = ttk.Frame(master=self)
        input_frame.pack(fill="x", padx='10', pady='10')

        json_entry_label = ttk.Label(master=input_frame, text='Paste JSON string here:')
        json_entry_label.pack(side='left')

        self.json_entry = ttk.Entry(master=input_frame, width=33)
        # self.json_entry.focus_set()
        self.json_entry.pack(side='left')

        self.submit_button = TButton(master=input_frame, text='Submit', command=self.submit_action)
        self.submit_button.pack(side='right', padx='3')

        self.json_entry.bind("<Return>", self.json_entry_return_key_event) # Handling Return key press

        # main buttons
        buttons_frame = ttk.Frame(master=self)
        buttons_frame.pack(fill="x", padx='10', pady='5')

        self.stop_button = TButton(master=buttons_frame, text='Stop', command=self.stop_action)
        self.stop_button.pack(side='left', padx='120')

        self.start_button = TButton(master=buttons_frame, text='Start', command=self.start_action)
        self.start_button.pack(side='left')

        # credential window
        credentials_frame = ttk.Labelframe(master=self, text="Credentials:")
        credentials_frame.pack(fill="x", padx='10', pady='10')

        self.credentials_info = tk.Text(master=credentials_frame, height=8, state='disabled')
        self.credentials_info.pack()

        self.clear_credentials_button = TButton(master=credentials_frame, text='Clear', command=self.clear_credentials)
        self.clear_credentials_button.pack()

        # Log window
        log_frame = ttk.Labelframe(master=self, text="Logs:")
        log_frame.pack(fill="x", padx='10', pady='10')

        self.__log = tk.Text(master=log_frame, height=10, state='disabled')
        self.__log.pack()

    def submit_action(self):
        self.__process_json_input(self.json_entry.get())

    def clear_credentials(self):
        self.update_credentials_in_main_tab() # updating credentials in the main tab with empty string
        data.AppSettings.credentials = None

    def start_action(self) -> None:
        settings = data.AppSettings
        with self.thread_lock:
            if self.running_thread is None or not self.running_thread.is_alive():
                self.stop_flag = False
                self.disable_user_input_in_widgets(True)
                self.running_thread = threading.Thread(target=api_calls.main, args=(self, settings))  # CHECK
                self.running_thread.start()
                self.stop_button.focus_set()

    def stop_action(self, widget_to_focus=None) -> None:
        with self.thread_lock:
            if self.running_thread and self.running_thread.is_alive():
                self.stop_flag = True
                self.running_thread = None
            self.disable_user_input_in_widgets(False)
            if widget_to_focus is None:
                widget_to_focus = self.start_button
            set_focus_to_widget(widget_to_focus)

    def update_arn_dropbox(self):
        # Clear the existing menu
        menu = self.arn_dropdown["menu"]
        menu.delete(0, "end")

        # Add the updated options to the menu
        variable = self.selected_arn
        for arn_name in data.AppSettings.arns:
            menu.add_command(label=arn_name, command=lambda opt=arn_name: variable.set(opt))
        self.__master.main_tab.arn_names = list(data.AppSettings.arns.keys())
        self.selected_arn.set(self.arn_names[0])

    def update_credentials_in_main_tab(self, creds: dict = None):
        self.credentials_info['state'] = 'normal'
        self.credentials_info.delete(1.0, 'end')

        if not creds:
            string_to_display = ''
        else:
            string_to_display = helper.credentials_to_str_for_display(creds)

        self.credentials_info.insert('end', string_to_display)
        self.credentials_info.yview_scroll(10, "pages")  # check if 'pages' can be changed to 'lines' or smth?
        self.credentials_info.see(0.0)
        self.credentials_info['state'] = 'disabled'

    def write_to_log(self, msg):
        self.__log['state'] = 'normal'
        tag = ''
        self.__log.tag_config('warning', foreground="red")  # Create fromatting tag for warnings
        if msg.startswith(data.warning_prefix):  # Check if message has a warning prefix
            msg = msg[len(data.warning_prefix):]
            tag = 'warning'
        self.__log.insert('end', f'{helper.now_datetime()} {msg}\n', tag)
        self.__log.yview_scroll(10, "pages")  # check if 'pages' can be changed to 'lines' or smth?
        self.__log['state'] = 'disabled'

    def json_entry_return_key_event(self, event):
        self.submit_action()

    def __process_json_input(self, json_input):
        if not json_input:
            return
        creds = helper.get_credentials_form_json_string(str(json_input), self)
        self.update_credentials_in_settings(creds)
        self.update_credentials_in_main_tab(creds)
        self.json_entry.delete(0, 'end')
        set_focus_to_widget(self.start_button)

    def update_credentials_in_settings(self, creds):
        data.AppSettings.credentials = creds

    def disable_user_input_in_widgets(self, b):
        if b:
            state = 'disabled'
            self.__master.settings_tab.delay_entry['state'] = state
        else:
            state = 'normal'
            self.__master.settings_tab.delay_entry['state'] = 'readonly'
        self.arn_dropdown['state'] = state
        self.json_entry['state'] = state
        self.clear_credentials_button['state'] = state
        self.submit_button['state'] = state
        self.start_button['state'] = state
        self.__master.settings_tab.message_entry['state'] = state
        self.__master.settings_tab.index_entry['state'] = state
        self.__master.settings_tab.ch_name_entry['state'] = state
        self.__master.settings_tab.ch_arn_entry['state'] = state
        self.__master.settings_tab.add_item_button['state'] = state
        self.__master.settings_tab.remove_item_button['state'] = state
        self.__master.settings_tab.up_button['state'] = state
        self.__master.settings_tab.down_button['state'] = state


class SettingsTab(ttk.Frame):
    def __init__(self, master: App):
        super().__init__(master)
        self.__master = master
        self.name = 'Settings'

        # Message
        message_frame = ttk.Labelframe(master=self, text="Message:")
        message_frame.pack(fill="x", padx='10', pady='10')

        self.message = tk.StringVar()
        self.message_entry = ttk.Entry(master=message_frame, textvariable=self.message)
        self.message_entry.config(width=24)
        self.message.set(data.AppSettings.metadata_message)
        # self.message.set(self.__master.settings.metadata_message)
        self.message_entry.pack(fill='x')
        self.message_entry.bind("<KeyRelease>", self.update_message_in_settings)

        # Start index
        index_and_delay_frame = ttk.Frame(master=self)
        index_and_delay_frame.pack(fill="x", padx='10', pady='10')

        index_entry_label = ttk.Label(master=index_and_delay_frame,
                                      text='Start index:\n(will be appended\nto the message)')
        index_entry_label.pack(side='left', padx=10)

        self.entered_index = tk.StringVar()
        self.index_entry = ttk.Entry(master=index_and_delay_frame, textvariable=self.entered_index)
        self.index_entry.config(width=4)
        self.entered_index.set(str(data.AppSettings.metadata_start_index))
        # self.entered_index.set(self.__master.settings.metadata_start_index)
        self.index_entry.pack(side='left')
        self.index_entry.bind("<KeyRelease>", self.update_index_in_settings)
        self.index_entry.bind("<FocusOut>",
                              lambda x: self.entered_index.set('0')
                              if data.AppSettings.metadata_start_index == 0 else None)
                              # if self.__master.settings.metadata_start_index == 0 else None)

        # Delay (wait)
        self.entered_delay = tk.IntVar()
        self.entered_delay.set(data.AppSettings.wait)
        # self.entered_delay.set(self.__master.settings.wait)
        self.delay_entry = tk.Spinbox(master=index_and_delay_frame, from_=2, to=10,
                                        textvariable=self.entered_delay,
                                        width=2, state='readonly',
                                      command=self.update_delay_in_settings)
        self.delay_entry.pack(side='right', padx=10)
        delay_entry_label = ttk.Label(master=index_and_delay_frame,
                                      text='Delay(sec):\n(between\nmessages)')
        delay_entry_label.pack(side='right')

        # ARN table
        arn_table_frame = ttk.Frame(master=self)
        arn_table_frame.pack(fill="x", padx='10', pady='10')

        self.arn_table = ttk.Treeview(master=arn_table_frame, columns=('name', 'arn'), show='headings', height=5)
        self.arn_table.heading('name', text='Channel Name')
        self.arn_table.heading('arn', text='ARN')
        self.arn_table.column('name', width=160, stretch=False)
        # self.insert_data_to_treeview(data.AppSettings.arns)
        self.arn_table.pack(fill='x')

        # Input Name/ARN fields
        name_input_frame = ttk.Frame(master=self)
        name_input_frame.pack(fill="x", padx='10')
        ch_name_entry_label = ttk.Label(master=name_input_frame, text="Channel Name:")
        ch_name_entry_label.pack(side='left')
        self.ch_name_entry = ttk.Entry(master=name_input_frame)
        self.ch_name_entry.pack(fill='x')

        arn_input_frame = ttk.Frame(master=self)
        arn_input_frame.pack(fill="x", padx='10')
        ch_arn_entry_label = ttk.Label(master=arn_input_frame, text="Channel ARN:")
        ch_arn_entry_label.pack(side='left')
        self.ch_arn_entry = ttk.Entry(master=arn_input_frame)
        self.ch_arn_entry.pack(fill='x')

        # ARN Buttons
        arn_buttons_frame = ttk.Frame(master=self)
        arn_buttons_frame.pack(fill="x", padx='10', pady='10')

        self.add_item_button = TButton(master=arn_buttons_frame, text="Add Item", command=self.add_item)
        self.add_item_button.pack(side='left', padx=15)

        self.remove_item_button = TButton(master=arn_buttons_frame, text="Remove Selected", command=self.remove_item)
        self.remove_item_button.pack(side='left', padx=15)

        self.up_button = TButton(arn_buttons_frame, text="Move Up", command=self.move_item_up)
        self.up_button.pack(side=tk.LEFT, padx=15)

        self.down_button = TButton(arn_buttons_frame, text="Move Down", command=self.move_item_down)
        self.down_button.pack(side=tk.LEFT, padx=15)

        # Info label
        info_label_frame = ttk.Frame(master=self)
        info_label_frame.pack(fill="x", padx='10', pady='10')

        self.info_label = ttk.Label(master=info_label_frame, foreground='red')
        self.info_label.pack()

        if not data.AppSettings.arns:
            print("Table has no arns. line 384")
            self.update_info_label_in_settings_tab("You have no saved Channel ARNs.\nPlease, add at least 1 ARN.")

    @decorator
    def update_info_label_in_settings_tab(self, msg =''):
            self.info_label.config(text=msg)

    def update_message_in_settings(self, event):
        new_message = self.message.get()
        data.AppSettings.metadata_message = new_message

    def update_delay_in_settings(self):
        new_delay_value = int(self.entered_delay.get())
        data.AppSettings.wait = new_delay_value

    def update_index_in_settings(self, event):
        entry_content = self.entered_index.get()

        if not entry_content:
            entry_content = 0
        try:
            entry_content = int(entry_content)
        except ValueError:
            entry_content = 0
        data.AppSettings.metadata_start_index = entry_content

    def insert_data_to_treeview(self, arns):
        if arns.items(): # Check ?????
            for name, arn in arns.items():
                self.arn_table.insert('', 'end', values=(name, arn))

    def arn_table_has_items(self) -> bool:
        return True if self.arn_table.get_children() else False

    def add_item(self):
        name = self.ch_name_entry.get()
        number = self.ch_arn_entry.get()

        if name and number:
            # Insert new item into the Treeview
            self.arn_table.insert(parent='', index='end', values=(name, number))

            # Clear the entry widgets
            self.ch_name_entry.delete(0, 'end')
            self.ch_arn_entry.delete(0, 'end')

            # Clear the info label
            self.update_info_label_in_settings_tab('')
        else:
            # Display warning
            self.update_info_label_in_settings_tab("Both 'Channel Name' and 'Channel ARN' are required!")

        if self.arn_table_has_items():
            print("arn table has items. line 460")
            self.update_arns_in_settings()
            self.__master.main_tab.update_arn_dropbox()

            if self.__master.notebook.tab(0)["state"] == 'disabled':  # CHECK here????
                self.__master.notebook.tab(0, state='normal')

    def remove_item(self):
        selected_items = self.arn_table.selection()

        if selected_items:
            # Remove selected items from the Treeview
            for item in selected_items:
                self.arn_table.delete(item)
            # Update app settings
            self.update_arns_in_settings()

        if self.arn_table_has_items():
            self.update_info_label_in_settings_tab('')
            self.__master.main_tab.update_arn_dropbox()
        else:
            self.__master.notebook.tab(0, state='disabled')
            self.update_info_label_in_settings_tab("You have no saved Channel ARNs.\nPlease, add at least 1 ARN.")
            set_focus_to_widget(self.ch_arn_entry)

    def move_item_up(self):
        # Move the selected item up in the table
        selected_item = self.arn_table.selection()

        if selected_item:
            current_index = self.arn_table.index(selected_item)
            if current_index > 0:
                self.arn_table.move(selected_item, '', current_index - 1)

        if self.arn_table_has_items():
            self.update_arns_in_settings()
            self.__master.main_tab.update_arn_dropbox()

    def move_item_down(self):
        # Move the selected item down in the table
        selected_item = self.arn_table.selection()

        if selected_item:
            current_index = self.arn_table.index(selected_item)
            if current_index < len(self.arn_table.get_children()) - 1:
                self.arn_table.move(selected_item, '', current_index + 1)

        if self.arn_table_has_items():
            self.update_arns_in_settings()
            self.__master.main_tab.update_arn_dropbox()

    def update_arns_in_settings(self):
        all_arns = {}
        for item_id in self.arn_table.get_children():
            values = self.arn_table.item(item_id, 'values')
            name, arn = values
            all_arns[name] = arn
        data.AppSettings.arns = all_arns


if __name__ == "__main__":
    app = App()

