#!/bin/bash

# Update packages
sudo apt update

# Install Python3 and pip if not installed
if ! command -v python3 &> /dev/null; then
    echo "Python3 not found. Installing..."
    sudo apt install -y python3 python3-pip
fi

# Install required Python libraries
pip3 install -r requirements.txt

echo "Setup completed. Run the script using:"
echo "python3 ipv6_tunnel_manager.py"
