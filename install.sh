#!/bin/bash

# به‌روزرسانی بسته‌ها
sudo apt update

# نصب Python در صورت نیاز
if ! command -v python3 &> /dev/null
then
    echo "Python3 not found. Installing..."
    sudo apt install -y python3 python3-pip
fi

# کلون کردن مخزن
REPO_URL="https://github.com/YOUR_USERNAME/ipv6-tunnel-script.git"
INSTALL_DIR="/opt/ipv6-tunnel-script"

if [ -d "$INSTALL_DIR" ]; then
    echo "Script already installed in $INSTALL_DIR."
    echo "Updating the script..."
    cd $INSTALL_DIR && git pull
else
    echo "Cloning repository..."
    sudo git clone $REPO_URL $INSTALL_DIR
fi

# تنظیم مجوزها
sudo chmod +x $INSTALL_DIR/script_name.py

# پیام موفقیت
echo "Installation completed. Run the script using:"
echo "python3 $INSTALL_DIR/script_name.py"
