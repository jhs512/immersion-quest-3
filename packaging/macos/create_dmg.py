"""Create a compressed image with room for the uncompressed app and filesystem."""
import argparse
import json
import os
from pathlib import Path
import stat
import subprocess


def source_bytes(source):
    total = 0
    for directory, directories, files in os.walk(source, followlinks=False):
        for name in directories + files:
            entry = Path(directory) / name
            metadata = entry.lstat()
            if stat.S_ISREG(metadata.st_mode) or stat.S_ISLNK(metadata.st_mode):
                total += metadata.st_size
    return total


def create_image(source, destination, volume, execute=subprocess.run):
    source = Path(source).resolve(strict=True)
    destination = Path(destination).resolve()
    if not source.is_dir():
        raise ValueError('Image source must be a directory')
    if destination == source or source in destination.parents:
        raise ValueError('Image destination must be outside its source')
    payload = source_bytes(source)
    mib = 1024 * 1024
    # hdiutil's automatic estimate can underallocate the writable staging image.
    # Count logical bytes, including sparse files, and reserve filesystem room.
    capacity = max(128 * mib, payload + max(64 * mib, (payload + 3) // 4))
    size_mib = (capacity + mib - 1) // mib
    execute([
        'hdiutil', 'create', '-volname', volume,
        '-size', f'{size_mib}m', '-srcfolder', str(source),
        '-ov', '-format', 'UDZO', str(destination),
    ], check=True)
    return {'source_bytes': payload, 'size_mib': size_mib}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', required=True)
    parser.add_argument('--destination', required=True)
    parser.add_argument('--volume', required=True)
    args = parser.parse_args()
    print(json.dumps(create_image(args.source, args.destination, args.volume)))
