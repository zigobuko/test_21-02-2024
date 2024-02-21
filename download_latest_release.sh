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

# Unzip the downloaded file to a temporary directory
temp_dir=$(mktemp -d)
unzip -q ~/Downloads/"$filename" -d "$temp_dir"

# Find the .app file
app_file=$(find "$temp_dir" -name "*.app" -type f)

# Check if .app file is found
if [ -z "$app_file" ]; then
    echo "No .app file found in the zip archive."
    rm -rf "$temp_dir"  # Remove the temporary directory
    rm ~/Downloads/"$filename"  # Remove the zip file
    exit 1
fi

# Move the .app file to the Downloads folder
mv "$app_file" ~/Downloads/

# Remove the temporary directory and the zip file
rm -rf "$temp_dir"
rm ~/Downloads/"$filename"

echo "Downloaded and extracted successfully."
