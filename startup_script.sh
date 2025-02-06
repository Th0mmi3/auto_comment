#!/bin/bash

#!/bin/bash

# Configuratie
REPO_DIR="/opt/repo"
GITHUB_REPO="https://github.com/tr4m0ryp/auto_comment.git"
SCRIPT_TO_RUN="wallet_generator.py"
LOG_FILE="${REPO_DIR}/wallet_generator.log"

if [ "$(id -u)" -ne 0 ]; then
    echo "Dit script moet als root (sudo) worden uitgevoerd."
    exit 1
fi

echo "Updating package lists..."
sudo apt-get update && sudo apt-get upgrade -y || { echo "Fout: Kon pakketten niet updaten."; exit 1; }

echo "Installing dependencies..."
if ! command -v git &> /dev/null; then
    sudo apt-get install -y git || { echo "Fout: Kon git niet installeren."; exit 1; }
fi

if ! command -v python3.9 &> /dev/null; then
    sudo apt-get install -y software-properties-common || { echo "Fout: Kon software-properties-common niet installeren."; exit 1; }
    sudo add-apt-repository ppa:deadsnakes/ppa -y
    sudo apt-get update
    sudo apt-get install -y python3.9 python3.9-distutils python3.9-venv || { echo "Fout: Kon Python 3.9 niet installeren."; exit 1; }
fi

python3.9 -m ensurepip --upgrade
python3.9 -m pip install --upgrade pip setuptools || { echo "Fout: Kon pip en setuptools niet upgraden."; exit 1; }

if [ ! -d "${REPO_DIR}" ]; then
    echo "Cloning repository..."
    sudo git clone "${GITHUB_REPO}" "${REPO_DIR}" || { echo "Fout: Kon repository niet klonen."; exit 1; }
else
    echo "Repository already exists. Pulling latest changes..."
    cd "${REPO_DIR}" || exit 1
    sudo git pull || { echo "Fout: Kon repository niet updaten."; exit 1; }
fi

cd "${REPO_DIR}" || exit 1
python3.9 -m pip install --upgrade -r requirements.txt || { echo "Fout: Kon vereiste Python-pakketten niet installeren."; exit 1; }

sudo chown -R azureuser:azureuser "${REPO_DIR}"
sudo chmod -R 755 "${REPO_DIR}"

echo "Starting script..."
nohup python3.9 "${SCRIPT_TO_RUN}" > "${LOG_FILE}" 2>&1 &

echo "Script started successfully! Logs available at: ${LOG_FILE}"
