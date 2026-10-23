"""Add English PC voices (BlackDes1 DQXI 3DS voice patch, v18) on top of OUR text build.

Usage: voice_build.py VP_SRC ORIG_ROMFS BUILD_ROMFS VOICE_DIR
  VP_SRC      = clone of the voice-patch repo's src/ folder (recipes + verified-inputs)
  ORIG_ROMFS  = untouched Japanese romfs
  BUILD_ROMFS = our built romfs (modified in place: syscmn.pack, sound/...)
  VOICE_DIR   = converted voices (folder that contains sound/str/dqxi_voice/V_*.bcstm),
                made locally from the user's own PC copy by pc_components.py

The native voice code (from their code.ips) hashes the dialogue string that is shown
and looks the hash up in a table stored in syscmn.pack/sound_se.bxon. Their table hashes
THEIR English text; here we rebuild it from the text in OUR built packs, so the clips play
with our translation. Nothing game-derived is written into this repository.
"""
import sys, json, struct, shutil, collections
from pathlib import Path

vp_src, orig, build, voice_dir = map(Path, sys.argv[1:5])
sys.path.insert(0, str(vp_src / 'python'))
import dq11_pack, threeds_textblock
from voice_map_builder import fingerprint, page_rate

inp = vp_src / 'verified-inputs'
rows = json.load(open(inp / 'dialogue.json', encoding='utf-8'))
links = json.load(open(inp / 'runtime_links.json', encoding='utf-8'))
jobs = json.load(open(inp / 'jobs.json', encoding='utf-8'))
template = (inp / 'voice-template.bxon').read_bytes()

where = {(r['scene'], r['text_id']): (r['entry'], r['index']) for r in rows}
packs = collections.defaultdict(list)
for p in orig.rglob('*.pack'):
    packs[p.stem.lower()].append(p.relative_to(orig))

cache = {}
def our_text(scene, text_id):
    # several packs can share a scene name (e.g. two a_130_cs_020.pack); use the one
    # whose text block has this text_id at the expected index
    entry, index = where[(scene, text_id)]
    if scene not in cache:
        cands = []
        for rel in packs[scene.lower()]:
            src = build / rel if (build / rel).exists() else orig / rel
            mem = {e.name: e.data for e in dq11_pack.read_archive(src).entries}
            cands.append({n: threeds_textblock.read(d) for n, d in mem.items() if n.endswith('text.bxon')})
        cache[scene] = cands
    hits = [c[entry][index] for c in cache[scene]
            if entry in c and index < len(c[entry]) and c[entry][index]['key'] == text_id]
    if not hits:
        raise KeyError('text_id')
    if len({h['text'] for h in hits}) > 1:
        raise KeyError('ambiguous_pack')
    return hits[0]['text']

jobs_by_id = {j['sound_id']: j for j in jobs}
count = struct.unpack_from('<I', template, 32)[0]
end = 44 + count * 12
old = struct.unpack_from('<8I', template, end)
assert count == 12384 and old[:2] == (0x34565144, 32) and old[7] == 6, 'template'
existing = collections.defaultdict(set)
for i in range(old[2]):
    h1, h2, ln, match, sound, rate = struct.unpack_from('<6I', template, end + 32 + i * 24)
    existing[(h1, h2, ln, sound)].add(match)

native, held = {}, collections.Counter()
for link in links:
    try:
        text = our_text(link['scene'], link['text_id'])
    except (KeyError, IndexError) as e:
        held['no_target_' + str(e)] += 1; continue
    job = jobs_by_id[link['sound_id']]
    if not (voice_dir / 'sound' / job['path']).exists():
        held['voice_file_missing'] += 1; continue
    try:
        h1, h2, ln = fingerprint(text)
    except ValueError:
        held['empty_text'] += 1; continue
    dur = job['samples'] / job['sample_rate']
    if job.get('segment_end_sample_22050') is not None:
        dur = (job['segment_end_sample_22050'] - job.get('segment_start_sample_22050', 0)) / 22050
    matches = existing[tuple(link['fingerprint']) + (link['sound_id'],)]
    if len(matches) == 1:
        match = next(iter(matches))
    elif link.get('match_text_id', link['text_id']) in matches:
        match = link.get('match_text_id', link['text_id'])
    else:
        match = link['text_id']
    key = (h1, h2, ln, match)
    val = (link['sound_id'], page_rate(dur, ln))
    if key in native and native[key] != val:
        held['conflict'] += 1; continue
    native[key] = val

body = b''.join(struct.pack('<6I', *k, *v) for k, v in sorted(native.items()))
paths = b''
for job in jobs:
    p = f"str/dqxi_voice/V_{job['sound_id'] - 7452:05d}.bcstm"
    assert job['path'] == p
    e = (p + '\0').encode('ascii'); paths += e + bytes(32 - len(e))
header = struct.pack('<8I', 0x34565144, 32, len(native), 24, 7452, len(jobs), 32 + len(body) + len(paths), 6)
payload = template[:end] + header + body + paths

src = build / 'syscmn.pack' if (build / 'syscmn.pack').exists() else orig / 'syscmn.pack'
arc = dq11_pack.read_archive(src)
old_se = next(e.data for e in arc.entries if e.name == 'sound_se.bxon')
assert old_se[44:44 + 7452 * 12] == template[44:44 + 7452 * 12], 'sound_se rows changed'
from verified_overlay import write_archive
write_archive(arc, {'sound_se.bxon': payload}, build / 'syscmn.pack')

# sound archive + pool slots, then the voice clips
shutil.copytree(inp / 'pool', build, dirs_exist_ok=True)
n = 0
for job in jobs:
    s = voice_dir / 'sound' / job['path']
    if s.exists():
        dst = build / 'sound' / job['path']; dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(s, dst); n += 1
print(json.dumps(dict(links=len(links), mapped_rows=len(native), held=dict(held), voices_copied=n)))
