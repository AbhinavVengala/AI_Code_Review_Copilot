import re

pattern = re.compile(r"^(\d+):(\d+):\s*(.*)$")

lines = [
    "3:1: 'unused_module_test' imported but unused",
    "42:38: trailing whitespace",
    "96:9: undefined name 'sys'",
    "  12:1: blank line contains whitespace" 
]

for line in lines:
    line = line.strip()
    match = pattern.match(line)
    if match:
        print(f"MATCH: {match.groups()}")
    else:
        print(f"NO MATCH: '{line}'")
