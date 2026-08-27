import re

with open('/sessions/determined-great-cori/mnt/Desktop/global-travel-dashboard/index.html', 'r') as f:
    html = f.read()

# 1. Add streak badge
target = "esc(e.tag)+'</div>'"
streak_code = "'+(e.consecutive_days>1?'<div class=\"ev-streak\">📆 '+e.consecutive_days+'天</div>':'')"

new_html = html.replace(target, target + streak_code, 1)
if new_html != html:
    print("Streak badge added")
else:
    print("Streak badge pattern NOT found - trying alt...")
    # Try alternate pattern
    alt = "esc(e.tag)+'</div>'" 
    # The actual text in the minified JS
    idx = html.find('ev-tag')
    if idx > 0:
        print(f"Found ev-tag at {idx}: {html[idx:idx+80]}")
html = new_html

# 2. Cache-busting
if 'no-cache' not in html[:500]:
    html = html.replace(
        '<meta charset="UTF-8">',
        '<meta charset="UTF-8">\n<meta http-equiv="Cache-Control" content="no-cache,no-store,must-revalidate">\n<meta http-equiv="Pragma" content="no-cache">',
        1
    )
    print("Cache-busting added")

# 3. Version badge
if 'v20260827' not in html:
    html = html.replace(
        '<div class="w">',
        '<div style="position:fixed;top:0;left:0;background:#ff0;color:#000;padding:4px 12px;font-size:14px;font-weight:bold;z-index:99999;border-radius:0 0 8px 0">v20260827</div>\n<div class="w">',
        1
    )
    print("Version badge added")

with open('/sessions/determined-great-cori/mnt/Desktop/global-travel-dashboard/index.html', 'w') as f:
    f.write(html)
with open('/sessions/determined-great-cori/mnt/Desktop/global-travel-dashboard/docs/index.html', 'w') as f:
    f.write(html)

print("Done!")
