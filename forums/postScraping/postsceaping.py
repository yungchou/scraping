import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

#from numpy import *
import scipy as sp


from rpy2.robjects.packages import importr
base = importr('base')
stats = importr('stats')
graphics = importr('graphics')

plot = graphics.plot
rnorm = stats.rnorm
plot(rnorm(100), ylab="random")


df = pd.DataFrame.from_dict(json.load(open('N:/dnd-webscraping/forums/postScraping/z.json')), orient='columns')

print('shape = ',df.shape, ', ',df.index)
print(df.dtypes)

print(df.describe())
df.head(2)

# check the dataset
df[df['lastReplyTime'].str.contains("minutes ago")]
df['lastReplyTime'].value_counts()

df1=df.drop(['categoryLink','createdByLink', 'lastReplyLink',
             'subCategoryLink', 'threadTitleLink','threadSummary'], axis='columns')
print('df.shape\t',df.shape);print('df1.shape\t',df1.shape)

# All subcategories are too many to plot, need to sort and take the top20
df2 = df1.groupby(['category','subCategory']).threadState.value_counts()
df2.plot.barh(x='index', y='threadState')

# Top Answered subcategory
#.df1[['category','subCategory','replyCount','viewCount','votes']]\
state = ['Answered','Unanaswered','Proposed','Discusstion']

df1[df1.threadState=='Answered']\
.sort_values('replyCount').head(10)\
.groupby(['category','subCategory']).threadState.value_counts()\
.plot.barh(x='index', y='threadState')

df1[df1.threadState=='Unanswered']\
.sort_values('replyCount').head(10)\
.groupby(['category','subCategory']).threadState.value_counts()\
.plot.barh(x='index', y='threadState')

df1[df1.threadState=='Proposed']\
.sort_values('replyCount').head(10)\
.groupby(['category','subCategory']).threadState.value_counts()\
.plot.barh(x='index', y='threadState')

df1[df1.threadState=='Discussion']\
.sort_values('replyCount').head(10)\
.groupby(['category','subCategory']).threadState.value_counts()\
.plot.barh(x='index', y='threadState')

df1\
.groupby(['category','subCategory']).threadState.value_counts(normalize=True)\
.plot.barh(x='index', y='threadState')