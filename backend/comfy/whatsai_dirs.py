import os
from pathlib import Path

if os.name == 'nt':
    base_dir = Path("D:/") / 'whatsai' / 'comfy_outer'
else:
    base_dir = Path.home() / 'whatsai' / 'comfy_outer'
