from pathlib import Path
from platform import system
import sys

from SCons.Script import DefaultEnvironment

env = DefaultEnvironment()

PROJECT_SRC_DIR = Path(env['PROJECT_SRC_DIR'])

# Find the bundled pioasm executable
pioasm_dir = env.PioPlatform().get_package_dir("tool-pioasm-rp2040-earlephilhower")
pioasm_exe = Path(pioasm_dir) / ("pioasm.exe" if system() == "Windows" else "pioasm")

def pio_to_pioh_cmd(pio_file: Path) -> str:
    header_file = pio_file.with_suffix(".pio.h")
    return f'"{pioasm_exe}" -o c-sdk "{pio_file}" "{header_file}"'

# Process all .pio files in PROJECT_SRC_DIR
for pio_file in PROJECT_SRC_DIR.rglob("*.pio"):
    header_file = pio_file.with_suffix(".pio.h")

    # Only rebuild if missing or outdated
    if not header_file.exists() or pio_file.stat().st_mtime > header_file.stat().st_mtime:
        action = env.VerboseAction(pio_to_pioh_cmd(pio_file), f"Building {header_file}")
        ret = env.Execute(action)
        if ret != 0:
            print(f"[ERROR] Failed to build {pio_file}, stopping.", file=sys.stderr)
            sys.exit(1)
