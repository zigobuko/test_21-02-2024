#!/bin/bash

# Define GitHub repository owner and name
owner="zigobuko"
repo="test_21-02-2024"

# Get the latest release information
release_info=$(curl -s "https://api.github.com/repos/$owner/$repo/releases/latest")

# Extract download URL for the zip file containing "SMST" in its name
download_url=$(echo "$release_info" | grep -o '"browser_download_url": ".*SMST.*\.zip"' | cut -d '"' -f 4)

# Check if download URL is empty (i.e., if no matching zip file was found)
if [ -z "$download_url" ]; then
    echo "No zip file containing 'SMST' in its name found in the latest release."
    exit 1
fi

# Extract file name from the download URL
filename=$(basename "$download_url")
echo "Filename: $filename"

# Download the zip file to the temp folder within the Downloads folder
temp_folder=~/Downloads/temp
mkdir -p "$temp_folder"
echo "Downloading zip file to: $temp_folder/$filename"
curl -sSL "$download_url" -o "$temp_folder/$filename"

# Unzip the downloaded file to the temp folder
echo "Unzipping the downloaded file to: $temp_folder"
unzip -q -d "$temp_folder" "$temp_folder/$filename"

# Delete the .zip file
echo "Deleting the zip file: $temp_folder/$filename"
rm "$temp_folder/$filename"

# Check if the Downloads folder already contains the .app file with the same name
if [ -e ~/Downloads/"$filename" ]; then
    if [ -e "$temp_folder/$filename" ]; then
        echo "File $filename already exists in Downloads."
    else
        echo "Moving $filename to Downloads folder."
        mv "$temp_folder/$filename" ~/Downloads/ || { echo "Failed to move $filename to Downloads folder."; exit 1; }
    fi
else
    if [ -e "$temp_folder/$filename" ]; then
        echo "Moving $filename to Downloads folder."
        mv "$temp_folder/$filename" ~/Downloads/ || { echo "Failed to move $filename to Downloads folder."; exit 1; }
    else
        echo "Error: $filename not found in temp folder."
        exit 1
    fi
fi

# Delete the temp folder
echo "Deleting temp folder: $temp_folder"
rm -rf "$temp_folder"

echo "Downloaded and extracted successfully."

