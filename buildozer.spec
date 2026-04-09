[app]
title = Neural Face HD
package.name = neuralfacehd
package.domain = com.anderson
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,ttf,onnx
source.include_patterns = assets/*,images/*

# REQUISITOS (Versão 2.3.0 é a melhor para Android moderno)
requirements = python3, kivy==2.3.0, kivymd==1.2.0, requests, urllib3, chardet, idna, certifi, pyrebase4, pycryptodome, setuptools, requests-toolbelt, cryptography, hostpython3

version = 1.3
orientation = portrait

android.permissions = INTERNET, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, CAMERA

# --- AJUSTE DE ESTABILIDADE (Fugindo do erro ALooper) ---
# Voltamos para a API 33 e NDK 25b que não têm o bug de compilação
android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 25b
android.skip_update = False
android.accept_sdk_license = True
# -------------------------------------------------------

android.uses_cleartext_traffic = True

# FOCO NO SEU REDMI (64 bits)
android.archs = arm64-v8a

p4a.bootstrap = sdl2
android.entrypoint = main.py
android.copy_libs = 1

[buildozer]
log_level = 2
warn_on_root = 1
