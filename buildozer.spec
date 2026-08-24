```ini
[app]

# Nome e identidade
title = Neural Face HD
package.name = neuralfacepro
package.domain = com.neuralmindstudio

# Código-fonte
source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,json,onnx,keystore,ttf
source.include_patterns = assets/*,gfpgan/*,*.onnx,images/*

# Versão
version = 1.0.1
android.numeric_version = 169

# Interface
orientation = portrait
fullscreen = 0

# --------------------------------------------------
# ANDROID
# --------------------------------------------------

# API Android
android.api = 35
android.minapi = 21
android.sdk = 35

# NDK
android.ndk = 25b

# Somente 64 bits
android.archs = arm64-v8a

# Aceitar licenças automaticamente
android.accept_sdk_license = True

# Permitir que o python-for-android atualize componentes
android.skip_update = False

# Rede
android.uses_cleartext_traffic = True

# Copiar bibliotecas nativas necessárias
android.copy_libs = 1

# --------------------------------------------------
# PERMISSÕES
# --------------------------------------------------

android.permissions = INTERNET,CAMERA,ACCESS_NETWORK_STATE,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,READ_MEDIA_IMAGES

# --------------------------------------------------
# PYTHON / KIVY
# --------------------------------------------------

android.python_version = 3.11

requirements = python3,kivy==2.3.0,kivymd==1.1.1,requests,urllib3,certifi,pyrebase4,pycryptodome,cryptography,pillow>=9.5,<11,pyjnius

# Bootstrap
p4a.bootstrap = sdl2

# --------------------------------------------------
# VISUAL
# --------------------------------------------------

icon.filename = logo.png
presplash.filename = splash.png

# --------------------------------------------------
# BUILD
# --------------------------------------------------

log_level = 2
warn_on_root = 0
```

