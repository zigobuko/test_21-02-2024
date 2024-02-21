#!/bin/bash

# Define GitHub repository owner and name
owner="zigobuko"
repo="test_21-02-2024"

# Get the latest release tag
latest_tag=$(curl -s "https://api.github.com/repos/$owner/$repo/releases/latest" | grep '"tag_name":' | sed -E 's/.*"([^"]+)".*/\1/')

# Construct download URL
download_url="https://github.com/$owner/$repo/archive/$latest_tag.zip"

# Extract file name from the download URL
filename=$(basename "$download_url")

# Download the zip file to the Downloads folder with the original name
curl -sSL "$download_url" -o ~/Downloads/"$filename"
