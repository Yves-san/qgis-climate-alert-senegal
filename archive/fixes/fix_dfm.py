with open('dashboard/app.py', 'r') as f:
    content = f.read()

old = "            if 'year_month' in df_m.columns:"
new = "            df_m = agreger_mensuel(df_proj)\n            if 'year_month' in df_m.columns:"

with open('dashboard/app.py', 'w') as f:
    f.write(content.replace(old, new, 1))
print('Done')
