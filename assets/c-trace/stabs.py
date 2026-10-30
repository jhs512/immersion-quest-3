"""STABS records that TinyCC 0.9.27 writes for `-g`: functions and statement lines only (no variables)."""
import struct


def stab_table(exe):
    b = open(exe, 'rb').read(); pe = struct.unpack_from('<I', b, 0x3c)[0]; n = struct.unpack_from('<H', b, pe + 6)[0]
    o = pe + 24 + struct.unpack_from('<H', b, pe + 20)[0]; sec = {}
    for i in range(n):
        name = b[o + 40 * i:o + 40 * i + 8].rstrip(b'\0').decode(); vs, va, rs, rp = struct.unpack_from('<IIII', b, o + 40 * i + 8)
        sec[name] = b[rp:rp + vs]
    stab, strs = sec['.stab'], sec['.stabstr']
    funcs, lines, cur = [], {}, None
    for i in range(12, len(stab) // 12 * 12, 12):
        strx, t, _, d, v = struct.unpack_from('<IBBHI', stab, i)
        name = strs[strx:strs.index(b'\0', strx)].decode() if strx else ''
        if t == 0x24 and name:
            cur = {'name': name.split(':')[0], 'start': v, 'line': d}; funcs.append(cur)
        elif t == 0x24:
            cur['end'] = cur['start'] + v
        elif t == 0x44 and cur:
            lines[cur['start'] + v] = d   # last record wins: the `{` line and the first statement can share an address
    return funcs, lines
