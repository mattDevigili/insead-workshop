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

# on ubuntu: you need to install python3.12-venv
# apt install python3.12-venv

# --+ initialize python environment
python3 -m venv .venv
source .venv/bin/activate
# --+ upgrate pip
pip3 install --upgrade pip
# --+ install requirements
pip3 install -r requirements.txt
# --+ get en_core_web_sm
python -m spacy download en_core_web_lg