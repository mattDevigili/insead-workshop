# %% Imports
import re
import numpy as np
import pandas as pd
from pymongo import MongoClient
import statsmodels.api as sm
from sklearn.preprocessing import LabelEncoder

# %% Database Connection
client = MongoClient()
db = client.insead_workshop
collection = db.python

# %% Data Retrieval
query_projection = {
    '_id': 0,
    'object': '$metadata.object',
    'author_date': '$metadata.author_date',
    'author_email': '$metadata.author_email',
    'tm_10': 1
}

df = pd.DataFrame(collection.find({}, query_projection))

# %% Data Preprocessing

#--+ Clean and prepare 'object'
df['object'] = df['object'].str.lower()
df['obj_c'] = df['object'].str.replace('^re: ', '', regex=True)

#--+ Compute discussion size and merge back
discussion_size = df.groupby('obj_c', as_index=False).size()
df = df.merge(discussion_size, on='obj_c')
df['size_log']  = np.log(df['size'])
df['size_log'].hist()

#--+ Filter out replies (i.e., subjects starting with 're:')
df = df[~df['object'].str.contains('^re:')]

#--+ Time Features
df['year'] = df['author_date'].dt.year
df['month'] = df['author_date'].dt.month
df['day_of_week'] = df['author_date'].dt.day_of_week

month_dummies = pd.get_dummies(df['month'], prefix='m', dtype=float)
dow_dummies = pd.get_dummies(df['day_of_week'], prefix='d_w', dtype=float)

df = pd.concat([df, month_dummies, dow_dummies], axis=1)

#--+ Author Encoding
le = LabelEncoder()
df['authors'] = le.fit_transform(df['author_email'])

author_dummies = pd.get_dummies(df['authors'], prefix='a', dtype=float)
df = pd.concat([df, author_dummies], axis=1)

#--+ Topic Features
k = 10
topic_cols = [f'topic_{i}' for i in range(k)]
df[topic_cols] = pd.DataFrame(df['tm_10'].tolist(), index=df.index)

# %% Regression Analysis

## Define features and target
feature_cols = (
    topic_cols[1:] +
    month_dummies.columns.tolist()[1:] +
    dow_dummies.columns.tolist()[1:] +
    author_dummies.columns.tolist()[1:]
)

X = df[feature_cols]
y = df['size_log']

## Add constant for intercept
X = sm.add_constant(X)

## Fit OLS model
model = sm.OLS(y, X).fit()

## Output results
print(model.summary())
#%%