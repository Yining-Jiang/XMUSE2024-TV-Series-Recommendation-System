# coding=utf-8

import pandas as pd

df = pd.read_csv('all_links.csv', header=None)
links = df.iloc[:, 0].tolist()
print(len(links))
print(links)
# uuids = [l.split('/')[-2] for l in links]
# print(uuids)
df2 = pd.read_csv('all_links_details.csv')
df2['douban_link'] = links
print(df2.columns.values)
df2.drop(df2.columns[13], axis=1, inplace=True)
df2.to_csv('all_links_details.csv', index=False)
