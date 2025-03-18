#%% Library
import re
import pandas as pd
from pymongo import MongoClient
import statsmodels.api as sm
from sklearn.preprocessing import LabelEncoder
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
#--+ connection
client = MongoClient()
db = client.insead_workshop
collection = db.python
#--+ get data
df = pd.DataFrame(
    collection.find({},{
        '_id':0,
        'object': '$metadata.object',
        'author_date': '$metadata.author_date',
        'author_email': '$metadata.author_email',
        'tm_10':1
    })
)
# %% manipulate
#--+ get DV
df['obj_c'] = df['object'].apply(lambda x: re.sub('^Re: ', '',x).lower())
df['object'] = df['object'].str.lower()
_ = df.groupby(['obj_c'], as_index=False).size()
df = df.merge(_, on='obj_c')
#--+ drop RE
df = df.loc[~df['object'].str.contains('^re:')]
#--+ time
df['year'] = df['author_date'].dt.year
df['month'] = df['author_date'].dt.month
df['day_of_week'] = df['author_date'].dt.day_of_week
m = pd.get_dummies(df['month'], dtype=float)
m.columns = ['m_{}'.format(i) for i in m.columns]
df = pd.concat([df,m], axis=1)
d_w = pd.get_dummies(df['day_of_week'], dtype=float)
d_w.columns = ['d_w_{}'.format(i) for i in d_w.columns]
df = pd.concat([df,d_w], axis=1)
#--+ authors
le = LabelEncoder()
df['authors'] = le.fit_transform(df['author_email'].to_list())
a = pd.get_dummies(df['authors'], dtype=float)
a.columns = ['a_{}'.format(i) for i in a.columns]
df = pd.concat([df,a], axis=1)
#--+ topics
topic_cols = [f'topic_{i}' for i in range(0, 10)]
df[topic_cols] = pd.DataFrame(df['tm_10'].tolist(), index=df.index)
#%% Stats
# %% Linear Regression to predict size
#--+ Define features and target
features = topic_cols[1:] + list(m.columns)[1:] + list(d_w.columns)[1:] + list(a.columns)[1:] 
X = df[features]
y = df['size']
# Add constant for intercept
X_sm = sm.add_constant(X)
# Fit OLS regression model on the full data
model = sm.OLS(y, X_sm).fit()
# Display regression summary
print(model.summary())
# %%
#--+ Split into train/test
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

#--+ Initialize and fit the model
lr = LinearRegression()
lr.fit(X_train, y_train)

#--+ Predictions
y_pred = lr.predict(X_test)

#--+ Evaluation
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print(f'Mean Squared Error: {mse:.2f}')
print(f'R^2 Score: {r2:.2f}')

# Optional: See coefficients
coef_df = pd.DataFrame({
    'Feature': features,
    'Coefficient': lr.coef_
})
print(coef_df)
#%%