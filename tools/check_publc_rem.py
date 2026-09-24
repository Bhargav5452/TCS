import re

content = open('public-limited-company.html', encoding='utf-8').read()
matches = re.findall(r'[^\n\r]*indiafilings\.com[^\n\r]*', content, re.I)
print(f"Total lines with indiafilings.com: {len(matches)}")
for m in matches[:10]:
    print("  ", m.strip()[:140])
