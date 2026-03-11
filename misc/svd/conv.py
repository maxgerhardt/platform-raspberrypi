#!/usr/bin/env python3
"""
Adds a <description> tag to each <peripheral> in an SVD file,
duplicating the peripheral's <n> value.
Preserves all original formatting.
"""

import re
import sys
import os

def add_peripheral_descriptions(input_path: str, output_path: str) -> None:
    with open(input_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Match the opening of a peripheral block up to and including <name>NAME</name>
    # Capture group 1 = the peripheral name
    pattern = r'\s+<peripheral>\s+<name>([\s\S]+?)<\/name>'

    # Replace with the full match ($&) plus a new <description> line
    replacement = r'\g<0>\n        <description>\1</description>'

    patched_content, count = re.subn(pattern, replacement, content)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(patched_content)

    print(f"Descriptions added: {count}")
    print(f"Output written to : {output_path}")


if __name__ == "__main__":
    if len(sys.argv) == 3:
        input_file  = sys.argv[1]
        output_file = sys.argv[2]
    else:
        input_file  = "/mnt/user-data/uploads/backup_svd.bak"
        output_file = "/mnt/user-data/outputs/rp2350_patched.svd"

    if not os.path.exists(input_file):
        print(f"Error: input file not found: {input_file}", file=sys.stderr)
        sys.exit(1)

    add_peripheral_descriptions(input_file, output_file)