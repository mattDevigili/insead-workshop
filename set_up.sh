#--------------------------------------------------------------------------------------
# Setup python
#
# Notes ―  before running the script:
#
# 1. Change working directory to the desired folder
# 
# Then, run sp.sh with:
#    `bash sp.sh`    
#
#-------------------------------------------------------------------------------------

#MONGO
#--+ install
sudo apt-get install gnupg curl
curl -fsSL https://www.mongodb.org/static/pgp/server-8.0.asc | \
   sudo gpg -o /usr/share/keyrings/mongodb-server-8.0.gpg \
   --dearmor
echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-8.0.gpg ] https://repo.mongodb.org/apt/ubuntu noble/mongodb-org/8.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-8.0.list
sudo apt-get update
sudo apt-get install -y mongodb-org
#--+ start service
sudo systemctl start mongod

#PYTHON
#--+ set up python
sudo apt install python3.12-venv
# --+ initialize python environment
python3 -m venv .venv
source .venv/bin/activate
# --+ upgrate pip
pip3 install --upgrade pip
# --+ install requirements
pip3 install -r requirements.txt
# --+ get en_core_web_sm
python -m spacy download en_core_web_lg