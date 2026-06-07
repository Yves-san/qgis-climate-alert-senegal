with open('dashboard/app.py', 'r') as f:
    content = f.read()

start = '    st.markdown("---")\n    st.markdown("### Carte superposee — Reseau hydraulique et forages")'
end = 'import json as _json'

idx_start = content.find(start)
idx_end = content.find(end)

if idx_start != -1 and idx_end != -1:
    content = content[:idx_start] + '\n\n' + end + content[idx_end+len(end):]
    with open('dashboard/app.py', 'w') as f:
        f.write(content)
    print('Done')
else:
    print(f'start={idx_start}, end={idx_end}')
