from cx_Freeze import setup, Executable

setup(
    name="SMST",
    version="1.0",
    description="test creating app file",
    executables=[Executable("gui.py", base=None)]
)
