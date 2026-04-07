[app]
title = Neural Face HD
package.name = neuralfacehd
package.domain = com.anderson.neuralface
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,ttf
source.include_patterns = assets/*,images/*

# REQUISITOS LIMPOS (Sem ffpyplayer/ffmpeg)
requirements = python3,kivy==2.2.1,kivymd==1.1.1,requests,urllib3,chardet,idna,certifi,pyrebase4,gcloud,oauth2client,pycryptodome,setuptools,requests-toolbelt,cryptography,hostpython3

version = 1.0.0
orientation = portrait

# Permissões necessárias para fotos e servidor
android.permissions = INTERNET, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, CAMERA, BILLING

android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 25b
android.skip_update = False
android.accept_sdk_license = True
android.uses_cleartext_traffic = True

# Focado no seu Redmi (64 bits) e compatível com 32 bits
android.archs = armeabi-v7a, arm64-v8a

android.copy_libs = 1
android.entrypoint = main.py

[buildozer]
log_level = 2
warn_on_root = 1
