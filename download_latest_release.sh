#!/bin/bash

# Define GitHub repository owner and name
owner="owner_name"
repo="repository_name"

# Get the latest release tag
latest_tag=$(curl -s "https://api.github.com/repos/$owner/$repo/releases/latest" | grep '"tag_name":' | sed -E 's/.*"([^"]+)".*/\1/')

# Construct download URL
download_url="https://github.com/$owner/$repo/archive/$latest_tag.zip"

# Download the zip file to the Downloads folder
wget -P ~/Downloads "$download_url"
