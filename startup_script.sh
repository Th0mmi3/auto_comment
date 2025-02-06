#!/bin/bash

# Configuratie
REPO_DIR="/opt/repo"
GITHUB_REPO="https://github.com/tr4m0ryp/auto_comment.git"
SCRIPT_TO_RUN="wallet_generator.py"

echo "Updating package lists..."
sudo apt-get update && sudo apt-get upgrade -y

echo "Installing dependencies..."
if ! command -v git &> /dev/null; then
    sudo apt-get install -y git
fi

if ! command -v python3.9 &> /dev/null; then
    sudo apt-get install -y software-properties-common
    sudo add-apt-repository ppa:deadsnakes/ppa -y
    sudo apt-get update
    sudo apt-get install -y python3.9 python3.9-distutils python3.9-venv
fi

python3.9 -m ensurepip --upgrade
python3.9 -m pip install --upgrade pip setuptools

if [ ! -d "${REPO_DIR}" ]; then
    echo "Cloning repository..."
    sudo git clone "${GITHUB_REPO}" "${REPO_DIR}"
else
    echo "Repository already exists. Pulling latest changes..."
    cd "${REPO_DIR}" && sudo git pull
fi

cd "${REPO_DIR}" || exit
python3.9 -m pip install --upgrade -r requirements.txt

echo "Starting script..."
nohup python3.9 "${SCRIPT_TO_RUN}" > /var/log/wallet_generator.log 2>&1 &

echo "Script started successfully!"
