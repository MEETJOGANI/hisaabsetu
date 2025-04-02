# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['hisaabsetu_launcher.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('app.py', '.'),
        ('calculations.py', '.'),
        ('database.py', '.'),
        ('utils.py', '.'),
        ('check_db.py', '.'),
        ('data', 'data'),
        ('.streamlit', '.streamlit'),
        ('generated-icon.png', '.'),
    ],
    hiddenimports=[
        'streamlit',
        'pandas',
        'openpyxl',
        'sqlite3',
        'trafilatura',
        'twilio',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    module_collection_mode={
        'streamlit': 'pyz+py',
        'pandas': 'pyz+py',
    }
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='HISAABSETU',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='generated-icon.png',
)