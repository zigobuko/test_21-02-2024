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

# Find and extract the .app file from the zip
app_file=$(unzip -l ~/Downloads/"$filename" | awk '$NF ~ /\.app$/ && $NF !~ /__MACOSX/ {print $NF; exit}')

# Check if .app file is found
if [ -z "$app_file" ]; then
    echo "No .app file found in the zip archive."
    rm ~/Downloads/"$filename"  # Remove the zip file
    exit 1
fi

# Extract the .app file to the Downloads folder
unzip -q ~/Downloads/"$filename" "$app_file" -d ~/Downloads/

# Remove the zip file
rm ~/Downloads/"$filename"

echo "Downloaded and extracted successfully."
