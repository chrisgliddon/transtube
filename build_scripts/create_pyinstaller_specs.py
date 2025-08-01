#!/usr/bin/env python3
"""
Create PyInstaller spec files for different platforms
"""
import os
import sys
from pathlib import Path

def create_macos_spec():
    """Create PyInstaller spec file for macOS"""
    
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-
import sys
import os
from pathlib import Path

# Get the absolute path to the project root
project_root = Path(os.path.abspath(SPECPATH)).parent

block_cipher = None

# Collect all Python dependencies
hiddenimports = [
    'pytubefix',
    'faster_whisper',
    'pandas',
    'numpy',
    'numba',
    'spacy',
    'openai',
    'pydub',
    'tqdm',
    'asyncio',
    'concurrent.futures',
    'psutil',
    'whisper',
    'torch',
    'torchaudio',
    'transformers',
    'regex',
    'requests',
    'urllib3',
    'certifi',
    'charset_normalizer',
    'idna',
    'ffmpeg',
    'scipy',
    'librosa',
    'soundfile',
    'audioread',
    'sklearn',
]

# Data files to include
datas = [
    # Include the main transcription script
    (str(project_root / 'bulk_transcribe_youtube_videos_from_playlist.py'), '.'),
    # Include spaCy model if it exists
    # Note: You may need to adjust this path based on your spaCy installation
]

# Binary files to include
binaries = []

# Try to include ffmpeg binary if available
ffmpeg_paths = [
    '/opt/homebrew/bin/ffmpeg',
    '/usr/local/bin/ffmpeg',
    '/usr/bin/ffmpeg',
]
for ffmpeg_path in ffmpeg_paths:
    if os.path.exists(ffmpeg_path):
        binaries.append((ffmpeg_path, '.'))
        break

a = Analysis(
    [str(project_root / 'build_scripts' / 'transtube_backend.py')],
    pathex=[str(project_root), str(project_root / 'build_scripts')],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib', 'PIL'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='transtube_backend',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch='arm64',  # For Apple Silicon
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='transtube_backend',
)
'''
    
    spec_path = 'config/pyinstaller_macos.spec'
    os.makedirs(os.path.dirname(spec_path), exist_ok=True)
    
    with open(spec_path, 'w') as f:
        f.write(spec_content)
    
    print(f"Created macOS spec file at: {spec_path}")
    return spec_path

def create_windows_spec():
    """Create PyInstaller spec file for Windows"""
    
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-
import sys
import os
from pathlib import Path

# Get the absolute path to the project root
project_root = Path(os.path.abspath(SPECPATH)).parent

block_cipher = None

# Collect all Python dependencies
hiddenimports = [
    'pytubefix',
    'faster_whisper',
    'pandas',
    'numpy',
    'numba',
    'spacy',
    'openai',
    'pydub',
    'tqdm',
    'asyncio',
    'concurrent.futures',
    'psutil',
    'whisper',
    'torch',
    'torchaudio',
    'transformers',
    'regex',
    'requests',
    'urllib3',
    'certifi',
    'charset_normalizer',
    'idna',
    'ffmpeg',
    'scipy',
    'librosa',
    'soundfile',
    'audioread',
    'sklearn',
]

# Data files to include
datas = [
    # Include the main transcription script
    (str(project_root / 'bulk_transcribe_youtube_videos_from_playlist.py'), '.'),
    # Include spaCy model if it exists
    # Note: You may need to adjust this path based on your spaCy installation
]

# Binary files to include
binaries = []

# Try to include ffmpeg.exe if available
ffmpeg_paths = [
    'C:\\\\ffmpeg\\\\bin\\\\ffmpeg.exe',
    'ffmpeg.exe',  # If in PATH
]
for ffmpeg_path in ffmpeg_paths:
    if os.path.exists(ffmpeg_path):
        binaries.append((ffmpeg_path, '.'))
        break

a = Analysis(
    [str(project_root / 'build_scripts' / 'transtube_backend.py')],
    pathex=[str(project_root), str(project_root / 'build_scripts')],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib', 'PIL'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='transtube_backend',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='transtube_gui\\\\windows\\\\runner\\\\resources\\\\app_icon.ico',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='transtube_backend',
)
'''
    
    spec_path = 'config/pyinstaller_windows.spec'
    os.makedirs(os.path.dirname(spec_path), exist_ok=True)
    
    with open(spec_path, 'w') as f:
        f.write(spec_content)
    
    print(f"Created Windows spec file at: {spec_path}")
    return spec_path

if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == 'macos':
            create_macos_spec()
        elif sys.argv[1] == 'windows':
            create_windows_spec()
    else:
        # Create both by default
        create_macos_spec()
        create_windows_spec()