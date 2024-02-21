#!/bin/bash

# Define GitHub repository owner and name
owner="zigobuko"
repo="test_21-02-2024"

# Get the latest release tag
latest_tag=$(curl -s "https://api.github.com/repos/$owner/$repo/releases/latest" | grep '"tag_name":' | sed -E 's/.*"([^"]+)".*/\1/')

# Extract download URL for the zip file containing "SMST" in its name
download_url=$(echo "$release_info" | grep -o '"browser_download_url": ".*SMST.*\.zip"' | cut -d '"' -f 4)

# Extract file name from the download URL
filename=$(basename "$download_url")

# Download the zip file to the Downloads folder with the original name
curl -sSL "$download_url" -o ~/Downloads/"$filename"
