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

# Create a temporary directory for extraction
temp_dir=$(mktemp -d)

# Download the zip file to the temporary directory
curl -sSL "$download_url" -o "$temp_dir/$filename"

# Unzip the downloaded file to the temporary directory, excluding macOS-specific metadata
unzip -q -X -d "$temp_dir" "$temp_dir/$filename"

# Check if an .app file with the same name already exists in Downloads
app_file=$(find "$temp_dir" -name "*.app" -type f | head -n 1)
if [ -n "$app_file" ]; then
    app_filename=$(basename "$app_file")
    if [ -e ~/Downloads/"$app_filename" ]; then
        echo "An .app file with the same name already exists in the Downloads folder."
        rm -rf "$temp_dir"
        exit 1
    fi
fi

# Debug: Print the app file path
echo "App file path: $app_file"

# Move the .app file to the Downloads folder
mv "$app_file" ~/Downloads/

# Remove the temporary directory
rm -rf "$temp_dir"

echo "Downloaded and extracted successfully."
