import docx

doc = docx.Document(r'reading_sessions\20261031_生成式AI與企業數據分析專題\20261110_期中報告_楊亞恩\楊亞恩.docx')
print('Number of tables in doc:', len(doc.tables))
print('Table 0 rows:', len(doc.tables[0].rows))
for r in doc.tables[0].rows:
    print(' ', [c.text.strip().replace('\n', ' ') for c in r.cells])

print('\nFirst 10 paragraphs:')
for i, p in enumerate(doc.paragraphs[:10]):
    print(f'P{i}: "{p.text}"')
