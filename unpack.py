#!/bin/env python3
import argparse
import struct
import zlib
import os
import io
import magic

# This file format hasn't been totally reverse engineered. This script only
# works as well as it needs to in order to successfully extract data from the
# game. Some fields are still unknown.

def extract_file(filename, output):
    with open(filename, 'rb') as f:
        reader = io.BytesIO(f.read())
    file_title = os.path.basename(filename).split('.')[0]

    magic_header, = struct.unpack('8s', reader.read(8))
    _, = struct.unpack("<H", reader.read(2))
    _, = struct.unpack("<H", reader.read(2))
    _, = struct.unpack("<I", reader.read(4))
    _, = struct.unpack("<I", reader.read(4))
    file_count, = struct.unpack("<I", reader.read(4))

    print(f'Found {file_count} files in {filename}')

    _, = struct.unpack("<I", reader.read(4))

    file_data = []

    for _ in range(file_count):
        file_data.append(struct.unpack("<IIII", reader.read(16)))
        # start_addr, unknown, flags, length

    os.makedirs(output, exist_ok=True)

    for i, file in enumerate(file_data):
        start_addr, _, flags, length = file
        reader.seek(start_addr)
        data = reader.read(length)
        data = zlib.decompress(data)

        file_name = f'{file_title}-{i}'
        file_path = os.path.join(output, file_name)

        with open(file_path, 'wb') as f:
            f.write(data)

        file_type = magic.from_file(file_path)

        extension = 'dat'

        if 'WAVE audio' in file_type:
            extension = 'wav'
        elif 'PC bitmap' in file_type:
            extension = 'bmp'
        else:
            print(f'{file_name} - Unknown file type: {file_type}')
        
        os.rename(file_path, f'{file_path}.{extension}')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('files', type=str, nargs='*')
    parser.add_argument('--output', type=str, default='qbert_data')
    args = parser.parse_args()

    for filename in args.files:
        try:
            extract_file(filename, args.output)
        except FileNotFoundError:
            print(f'{filename} not found.')
        except IsADirectoryError:
            print(f'{filename} is not a file.')


if __name__ == '__main__':
    main()