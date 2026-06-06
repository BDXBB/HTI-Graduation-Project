#!/bin/bash
# Installation Script for HTI Automation System

echo "=================================================="
echo "HTI Automation & Security System"
echo "Installation Script"
echo "=================================================="

echo ""
echo "Step 1: Update system..."
sudo apt update && sudo apt upgrade -y

echo ""
echo "Step 2: Install required packages..."
sudo apt install -y python3-dev python3-pip
sudo apt install -y libatlas-base-dev libjasper-dev libtiff5 libcamera-dev
sudo apt install -y portaudio19-dev mariadb-server mariadb-client
sudo apt install -y apache2 php libapache2-mod-php php-mysql

echo ""
echo "Step 3: Install Python packages..."
pip install -r requirements.txt

echo ""
echo "Step 4: Setup Web Server..."
sudo rm -f /var/www/html/index.html
sudo cp -r www/* /var/www/html/
sudo chown -R www-data:www-data /var/www/html/
sudo chmod -R 755 /var/www/html/

echo ""
echo "Step 5: Set permissions..."
chmod +x main.py
chmod +x setup.py

echo ""
echo "=================================================="
echo " Installation completed!"
echo "=================================================="
echo ""
echo " Next steps:"
echo "   1. Setup Database: python3 setup.py"
echo "   2. Run daemon: python3 main.py"
echo ""
