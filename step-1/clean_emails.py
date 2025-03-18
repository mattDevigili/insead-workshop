#%% Libraries
import os, re
import pandas as pd
from email.parser import Parser
from email.policy import default
#--+ read marc
path = '/'.join(i for i in os.getcwd().split('/')[:-1])
folder = 'step-0/data-collected'
file = 'marc_rawBody.jsonl'
df = pd.read_json(
    os.path.join(path,folder,file), 
    lines=True)
#--+ prep
for c in df.columns:
    df[c] = df[c].apply(lambda x: x[0])
#%% cleaning functions
#--+ extract name and email
def extract_contact(x):
    if '()' in x:
        x = x.replace('()', '@')
        if '<' in x:
            #--+ get email
            try:
                email = re.findall('<(.*)>',x)[0]
            except:
                email = None
            if ' <' in x:
                name = x.split(' <')[0]
            else:
                name = None
        elif '(' in x:
            x = x.split('(')
            email = x[0]
            name = x[1].replace(')', '')
        elif '!' in x:
            email = x
            name = None
        else:
            email = None
            name = None
    else:
        if '"' in x:
            email = None
            try:
                name = re.findall('"(.*)"',x)[0]
            except:
                name = None
        else:
            email = None
            name = None
    if isinstance(email,str):
        #--+ replace !
        if '!' in email:
            email = email.replace('!', '.')
        #--+ remove extra spaces
        email = email.replace(' ', '')
        #--+ lower
        email = email.lower()
    if isinstance(name,str):
        name = name.replace('"','')
        name = name.lower()
    # return
    return email,name

def extract_datetime(x):
    try:
        x = pd.to_datetime(x)
        _tz = x.tzname()
    except:
        x = None
        _tz = None
    return x,_tz
# %% extract basic info
rawemails = df['rawBody'].to_list()
#--+ author info
sender = [re.findall('From: (.*)', i)[0] for i in rawemails]
data = [extract_contact(i) for i in sender]
get_author = [{'author_email': i[0], 'author_name': i[1]} for i in data]
dt = pd.DataFrame(get_author)
df = pd.concat([df,dt], axis=1)
#--+ mailing list info
get_mailingList = [re.findall('To: (.*)', i)[0] for i in rawemails]
df['committer_name'] = get_mailingList
#--+ object
get_subject = [re.findall('Subject: (.*)', i)[0] for i in rawemails]
get_subject = [i.replace('[Python-Dev] ', '') for i in get_subject]
df['object'] = get_subject
#--+ date
get_date = [re.findall('Date: (.*)', i)[0] for i in rawemails]
get_date = [extract_datetime(i) for i in get_date]
get_d_tz = [{'author_date': i[0], 'author_timezone': i[1]} for i in get_date]
dt = pd.DataFrame(get_d_tz)
df = pd.concat([df,dt], axis=1)
#--+ clean
content = []
for e in rawemails:
    try:
        _ = Parser(policy=default).parsestr(e)
        content.append(_.get_content())
    except:
        content.append(e)
df['body'] = content
# %% store
from pymongo import MongoClient
#--+ connection
client = MongoClient()
db = client.insead_workshop
collection = db.python
#--+ insert many
manual = []
for d in df.to_dict(orient='records'):
    try:
        collection.insert_one(d)
    except:
        print('err')
# %%
collection.aggregate([
    {
        '$project': {
            'metadata': {
                'object': '$object', 
                'author_email': '$author_email', 
                'author_date': '$author_date', 
                'author_timezone': '$author_timezone', 
                'committer_name': '$committer_name', 
                'url': '$url'
            }, 
            'body': '$body'
        }
    }, {
        '$out': {
            'db': 'insead_workshop',
            'coll': 'python'
        }
    }
])
# %%
