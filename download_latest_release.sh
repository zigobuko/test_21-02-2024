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

# Unzip the downloaded file to the Downloads folder
unzip -q -d ~/Downloads/ ~/Downloads/"$filename"

# Remove macOS-specific metadata directory (__MACOSX)
rm -rf ~/Downloads/__MACOSX

# Check if an .app file with the same name already exists in Downloads
app_file=$(find ~/Downloads/ -name "*.app" -type f | head -n 1)
if [ -n "$app_file" ]; then
    app_filename=$(basename "$app_file")
    if [ -e ~/Downloads/"$app_filename" ]; then
        echo "An .app file with the same name already exists in the Downloads folder."
        rm -rf ~/Downloads/"$filename"
        exit 1
    fi
fi

# Move the .app file to the Downloads folder
mv "$app_file" ~/Downloads/

# Remove the zip file
rm ~/Downloads/"$filename"

echo "Downloaded and extracted successfully."
