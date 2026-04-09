[app]
title = Neural Face HD
package.name = neuralfacehd
package.domain = com.anderson
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,ttf,onnx
source.include_patterns = assets/*,images/*

# REQUISITOS ATUALIZADOS (Essencial para corrigir o erro ALooper do NDK 27)
requirements = python3, kivy==2.3.0, kivymd==1.2.0, requests, urllib3, chardet, idna, certifi, pyrebase4, pycryptodome, setuptools, requests-toolbelt, cryptography, hostpython3

version = 1.3
orientation = portrait

android.permissions = INTERNET, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, CAMERA

# --- AJUSTE CIRÚRGICO PARA GITHUB ACTIONS 2026 ---
android.api = 34
# Subimos para 24 para garantir compatibilidade com o NDK novo
android.minapi = 24
android.sdk = 34
android.ndk = 27c
# Caminho confirmado pelo seu log
android.ndk_path = /usr/local/lib/android/sdk/ndk/27.3.13750724
android.skip_update = False
android.accept_sdk_license = True
# ------------------------------------------------

android.uses_cleartext_traffic = True

# FOCO TOTAL NO SEU REDMI (64 bits)
android.archs = arm64-v8a

p4a.bootstrap = sdl2
android.entrypoint = main
android.copy_libs = 1

[buildozer]
log_level = 2
warn_on_root = 1
