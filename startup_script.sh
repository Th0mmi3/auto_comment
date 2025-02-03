#!/bin/bash

REPO_DIR="/opt/repo"
GITHUB_REPO="https://github.com/Th0mmi3/auto_comment.git"
SCRIPT_TO_RUN="wallet_generator.py"
sudo apt-get update
sudo apt-get install -y git python3.9 python3.9-distutils python3.9-venv
python3.9 -m ensurepip --upgrade
python3.9 -m pip install --upgrade pip
if [ ! -d "${REPO_DIR}" ]; then
    git clone "${GITHUB_REPO}" "${REPO_DIR}"
fi
cd "${REPO_DIR}"

python3.9 -m pip install -r requirements.txt
python3.9 "${SCRIPT_TO_RUN}" &
