# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

datas = [('user_input_cli.py', '.'), ('validate_input.py', '.'), ('main.py', '.'), ('visualize_input_data.py', '.'), ('visualize_schedule.py', '.'), ('data_loader.py', '.'), ('models.py', '.'), ('scheduler.py', '.')]
binaries = []
hiddenimports = ['user_input_cli', 'validate_input', 'main', 'visualize_input_data', 'visualize_schedule', 'data_loader', 'models', 'scheduler', 'json', 'shutil', 'random', 'dataclasses', 'enum', 'collections', 'matplotlib', 'matplotlib.pyplot', 'matplotlib.backends.backend_agg', 'matplotlib.patches', 'numpy']
tmp_ret = collect_all('matplotlib')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('numpy')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


a = Analysis(
    ['app_cli.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='PlannerAllInOne',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
