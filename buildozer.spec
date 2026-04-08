[app]
title = Neural Face HD
package.name = neuralfacehd
package.domain = com.anderson
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,ttf,onnx
source.include_patterns = assets/*,images/*

# REQUISITOS OTIMIZADOS
requirements = python3,kivy==2.2.1,kivymd==1.1.1,requests,urllib3,chardet,idna,certifi,pyrebase4,pycryptodome,setuptools,requests-toolbelt,cryptography,hostpython3

version = 1.3
orientation = portrait

android.permissions = INTERNET, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, CAMERA

# AJUSTE PARA O GITHUB ACTIONS 2026
# Usando API 34 e apontando para o NDK 27 que o log mostrou estar presente
android.api = 34
android.minapi = 21
android.sdk = 34
android.ndk = 27c
android.ndk_path = /usr/local/lib/android/sdk/ndk/27.3.13750724
android.skip_update = False
android.accept_sdk_license = True

android.uses_cleartext_traffic = True

# FOCO NO SEU REDMI (64 bits)
android.archs = arm64-v8a

p4a.bootstrap = sdl2
android.entrypoint = main
android.copy_libs = 1

[buildozer]
log_level = 2
warn_on_root = 1
