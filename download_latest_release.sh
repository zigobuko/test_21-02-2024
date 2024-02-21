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

# Download the zip file to the Downloads folder
curl -sSL "$download_url" -o ~/Downloads/"$filename"

# Create a temporary directory to extract the files
temp_dir=$(mktemp -d)

# Unzip the downloaded file to the temporary directory
unzip -q -d "$temp_dir" ~/Downloads/"$filename"

# Remove unwanted files and folders
rm -rf "$temp_dir"/__MACOSX

# Check if an .app file with the same name already exists in Downloads
app_file=$(find "$temp_dir" -name "*.app" -type f | head -n 1)
if [ -e ~/Downloads/"$(basename "$app_file")" ]; then
    echo "An .app file with the same name already exists in the Downloads folder."
    rm -rf "$temp_dir"
    rm ~/Downloads/"$filename"
    exit 1
fi

# Move the .app file to the Downloads folder
mv "$app_file" ~/Downloads/ && zip_deleted=true

# Remove the temporary directory if the move was successful
if [ $? -eq 0 ]; then
    rm -rf "$temp_dir"
fi

# Remove the zip file if it was successfully extracted and moved
if [ "$zip_deleted" = true ]; then
    rm ~/Downloads/"$filename"
    echo "Downloaded and extracted successfully."
else
    echo "Failed to extract the zip file."
fi
