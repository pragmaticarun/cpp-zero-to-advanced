# authoring helper: move a stray `std="..."` line into the lesson's dict(title=..., std=...) header
import re, sys
p = sys.argv[1]; s = open(p).read()
while True:
    m = re.search(r'\nstd="(C\+\+\d\d)",\n', s)
    if not m: break
    head = [h for h in re.finditer(r'dict\(title="[^"]*", std="C\+\+\d\d"', s[:m.start()])][-1]
    newhead = re.sub(r'std="C\+\+\d\d"', f'std="{m.group(1)}"', head.group(0))
    s = s[:head.start()] + newhead + s[head.end():m.start()] + "\n" + s[m.end():]
open(p, 'w').write(s)
