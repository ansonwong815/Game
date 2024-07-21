# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('/Users/ansonwong/PycharmProjects/Task2/wands.csv', '.'),
        ('/Users/ansonwong/PycharmProjects/Task2/swords.csv', '.'),
        ('/Users/ansonwong/PycharmProjects/Task2/bows.csv', '.'),
        ('/Users/ansonwong/PycharmProjects/Task2/weaponsArt', 'weaponsArt'),
        ('/Users/ansonwong/PycharmProjects/Task2/Characters', 'Characters'),
        ('/Users/ansonwong/PycharmProjects/Task2/heart.png', '.'),
        ('/Users/ansonwong/PycharmProjects/Task2/coin.png', '.'),
        ('/Users/ansonwong/PycharmProjects/Task2/attack.png', '.'),
        ('/Users/ansonwong/PycharmProjects/Task2/delete.png', '.'),
        ('/Users/ansonwong/PycharmProjects/Task2/settings.json', '.'),
    ],
    hiddenimports=[],
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
    name='main',
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
