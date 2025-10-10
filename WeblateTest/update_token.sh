#!/bin/bash
# Update GitHub token for Component0201

# Replace with your new token
NEW_TOKEN="PASTE_YOUR_NEW_TOKEN_HERE"
USERNAME="Giggly19890103"
REPO="demo"

# Update Git remote
cd /home/wefwe2ffw2/Documents/weblate/data/vcs/project02/component0201
git config --unset remote.origin.pushurl 2>/dev/null
git remote set-url origin "https://${USERNAME}:${NEW_TOKEN}@github.com/${USERNAME}/${REPO}.git"

echo "✅ Token updated!"
git remote -v

