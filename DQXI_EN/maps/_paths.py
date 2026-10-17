# Shared paths for the map scripts. Override with environment variables when running outside the
# original workspace:  DQXI_TOOLS (tools dir), DQXI_FONTS (patched romfs/font of a build),
# DQXI_DB (progress.sqlite), DQXI_OFFICIAL_ROWS (rows.jsonl made by tools/en_script_parse.py from
# your own copy of the official English script; not included in this project).
import os
_here = os.path.dirname(os.path.abspath(__file__))
_root = os.path.dirname(_here)
def _first(*c):
    for p in c:
        if p and os.path.exists(p): return p
    return c[-1]
TOOLS = os.environ.get('DQXI_TOOLS') or _first(os.path.join(_root, 'tools'), '/home/claude/tools')
FONTS = os.environ.get('DQXI_FONTS') or _first(os.path.join(_root, 'work', 'build', 'romfs', 'font'), '/home/claude/work/build/romfs/font')
DB = os.environ.get('DQXI_DB') or _first(os.path.join(_root, 'db', 'progress.sqlite'), '/home/claude/work/proj/db/progress.sqlite')
ROWS = os.environ.get('DQXI_OFFICIAL_ROWS') or _first(os.path.join(_root, 'official', 'rows.jsonl'), '/home/claude/enscript/rows.jsonl')
