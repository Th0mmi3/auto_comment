#!/bin/bash
sudo apt-get update
sudo apt-get install -y git python3-pip
if [ ! -d "{REPO_DIR}" ]; then
    git clone {GITHUB_REPO} {REPO_DIR}
fi
cd {REPO_DIR}
pip3 install -r requirements.txt
python3 {SCRIPT_TO_RUN} &
