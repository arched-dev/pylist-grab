a = Analysis(
    ['./pylist/gui.py'],
    pathex=[],
    datas=[
        ('./pylist/assets/dark_teal.xml', 'pylist-grab/assets/'),
        ('./venv/Lib/site-packages/qt_material/fonts/', 'qt_material/fonts/'),
        ('./venv/Lib/site-packages/qt_material', 'qt_material'),
        ('./venv/Lib/site-packages/qt_material/resources/', 'qt_material/resources/'),
        ('./pylist/assets/', 'pylist/assets/'),
    ],
    hiddenimports=['qt_material', 'PySide6', 'PIL', 'PIL.Image', 'PIL.ImageFilter', 'imageio', 'imageio_ffmpeg', 'decorator', 'tqdm', 'numpy', 'scipy'],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    noarchive=True,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='pylist-grab',
    debug=True,
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
    distpath='windows_dist',
    icon='./pylist/assets/icon_256.ico',
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='windows_dist',
)
