import pandas as pd

df = pd.read_csv('lcom_results.csv')
df['LCOM1'] = pd.to_numeric(df['LCOM1'], errors='coerce')
df = df.dropna(subset=['LCOM1'])
top20 = df.sort_values(by='LCOM1', ascending=False).head(20)
table = top20[['Package Name', 'Type Name', 'LCOM1', 'LCOM2', 'LCOM3', 'LCOM4', 'LCOM5', 'YALCOM']]
table.insert(0, 'Java Code', table['Package Name'] + '.' + table['Type Name'])
table = table.drop(columns=['Package Name', 'Type Name'])
table.to_csv('top20_lcom_table.csv', index=False)

print(" Top 20 LCOM classes table saved as 'top20_lcom_table.csv'")
