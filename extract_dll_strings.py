#!/usr/bin/env python3
"""Extract string literals from a .NET DLL's #US (UserStrings) heap."""
import sys
import dnfile

dll = sys.argv[1]
pe = dnfile.dnPE(dll)
us = pe.net.user_strings

results = []
# us provides .get_us(token) but iteration is not direct. Walk the raw stream.
stream = us
data = stream.__data__ if hasattr(stream, "__data__") else stream._data_
# dnfile exposes user_strings via .get_us(rid). Use the raw heap.
heap = pe.net.metadata.streams.get(b"#US")
if heap is None:
    print("No #US stream found", file=sys.stderr)
    sys.exit(0)
raw = heap.struct.contents if hasattr(heap.struct, "contents") else heap.__data__
# heap data is at heap.__data__
raw = heap.__data__

i = 1  # skip null entry
while i < len(raw):
    # decode compressed length
    b = raw[i]
    if b == 0:
        i += 1
        continue
    if (b & 0x80) == 0:
        length = b & 0x7F
        i += 1
    elif (b & 0xC0) == 0x80:
        if i + 1 >= len(raw): break
        length = ((b & 0x3F) << 8) | raw[i+1]
        i += 2
    elif (b & 0xE0) == 0xC0:
        if i + 3 >= len(raw): break
        length = ((b & 0x1F) << 24) | (raw[i+1] << 16) | (raw[i+2] << 8) | raw[i+3]
        i += 4
    else:
        i += 1
        continue
    if length == 0:
        continue
    if i + length > len(raw):
        break
    # last byte is "final" flag, length-1 is utf-16le
    str_bytes = raw[i:i+length-1]
    try:
        s = str_bytes.decode("utf-16-le", errors="replace")
        if s:
            results.append(s)
    except Exception:
        pass
    i += length

print(f"# {dll}: {len(results)} strings")
for s in results:
    if not s.strip():
        continue
    # one-line repr
    print(repr(s))
