# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['App.py'],
    pathex=[],
    binaries=[],
    datas=[('env\\Lib\\site-packages\\face_recognition_models\\models\\dlib_face_recognition_resnet_model_v1.dat', 'face_recognition_models/models'),
                ('env\\Lib\\site-packages\\face_recognition_models\\models\\mmod_human_face_detector.dat', 'face_recognition_models/models'),
                ('env\\Lib\\site-packages\\face_recognition_models\\models\\shape_predictor_5_face_landmarks.dat', 'face_recognition_models/models'),
                ('env\\Lib\\site-packages\\face_recognition_models\\models\\shape_predictor_68_face_landmarks.dat', 'face_recognition_models/models'),
                ('env\\Lib\\site-packages\\cv2\\data\\haarcascade_frontalface_default.xml', 'cv2/data'),
                ('assets\\citydata.db', 'assets'),
                ('assets\\locker.ico', 'assets'),
                ('assets\\theme.json', 'assets'),
                
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
    name='App',
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
    icon=['assets\\locker.ico'],
)
