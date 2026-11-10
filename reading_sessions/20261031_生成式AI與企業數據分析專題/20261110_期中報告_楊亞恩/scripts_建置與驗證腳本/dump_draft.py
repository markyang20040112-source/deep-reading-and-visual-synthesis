import docx

doc = docx.Document(r'C:\Users\User\OneDrive\桌面\期中報告\楊亞恩—初稿.docx')
with open('draft_dump.txt', 'w', encoding='utf-8') as f:
    for i, p in enumerate(doc.paragraphs):
        runs_info = []
        for r in p.runs:
            bold = '[B]' if r.bold else ''
            runs_info.append(f"{r.text}{bold}")
        line_content = "".join(runs_info)
        f.write(f"P{i:03d} [{p.style.name}]: {line_content}\n")
print("Wrote draft_dump.txt with", len(doc.paragraphs), "paragraphs")
