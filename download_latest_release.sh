#!/bin/bash

# Define GitHub repository owner and name
owner="zigobuko"
repo="test_21-02-2024"

# Create a temporary directory within the Downloads folder
temp_dir=$(mktemp -d ~/Downloads/temp.XXXXXX)

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

# Download the zip file to the temporary folder
curl -sSL "$download_url" -o "$temp_dir/$filename"

# Unzip the downloaded file to the temporary folder
unzip -q -d "$temp_dir" "$temp_dir/$filename"

# Check if .app file exists in the Downloads folder with the same name
if [ -e "~/Downloads/${filename%.zip}.app" ]; then
    echo "File ${filename%.zip}.app already exists in Downloads."
    # Remove the temporary directory
    rm -rf "$temp_dir"
else
    # Move .app file from the temp folder to Downloads folder
    mv "$temp_dir/${filename%.zip}.app" ~/Downloads/
    # Remove the temporary directory
    rm -rf "$temp_dir"
fi

echo "Downloaded and extracted successfully."
