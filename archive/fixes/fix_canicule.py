with open('dashboard/app.py', 'r') as f:
    content = f.read()

old = "                    cols[i%6].markdown(f\"<div style='background:#2d0a0a;border-radius:8px;padding:10px;text-align:center;color:#ff4444;font-weight:bold;'>{annee}</div>\",unsafe_allow_html=True)\n        else:\n            st.warning"

new = "                    cols[i%6].markdown(f\"<div style='background:#2d0a0a;border-radius:8px;padding:10px;text-align:center;color:#ff4444;font-weight:bold;'>{annee}</div>\",unsafe_allow_html=True)\n            else:\n                st.success('Pour ce scenario, les temperatures restent gerables.')\n            if 'year_month' in df_m.columns:\n                mois_chauds = df_m[df_m['temp_max']>=38][['year_month','temp_max']].head(10)\n                if not mois_chauds.empty:\n                    st.markdown('### Mois les plus caniculaires')\n                    for _,row in mois_chauds.iterrows():\n                        st.error('Mois ' + str(row['year_month']) + ' : ' + str(int(row['temp_max'])) + ' C — Ne travaillez pas aux champs en journee')\n        else:\n            st.warning"

with open('dashboard/app.py', 'w') as f:
    f.write(content.replace(old, new, 1))
print('Done')
