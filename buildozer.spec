[app]
# Nome e Identidade
title = Neural Face HD
package.name = neuralfacepro
package.domain = com.neuralmindstudio
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,onnx,keystore,ttf
source.include_patterns = assets/*, gfpgan/*, *.onnx, images/*

# VERSÃO OFICIAL DE LANÇAMENTO
version = 1.0.0
android.numeric_version = 1
orientation = portrait
fullscreen = 0

# Requisitos do Android para a Play Store
android.permissions = INTERNET, CAMERA, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, READ_MEDIA_IMAGES, ACCESS_NETWORK_STATE
android.api = 34
android.minapi = 21
android.sdk = 34
android.ndk = 25b
# 🔥 Ajustado para 64 bits apenas, para garantir que o build termine com sucesso
android.archs = arm64-v8a
android.accept_sdk_license = True
android.skip_update = False
android.uses_cleartext_traffic = True
android.copy_libs = 1
android.release_artifact = aab
p4a.bootstrap = sdl2

# --- ASSINATURA DA PLAY STORE (DADOS ATUALIZADOS) ---
android.keystore = neuralface_oficial.keystore
android.keystore_password = neural2026
android.keyalias = neural_oficial
android.keyalias_password = neural2026

# Assets Visuais
icon.filename = logo.png
presplash.filename = splash.png

# Requisitos do Python (Mantendo suas correções)
requirements = python3,kivy==2.3.0,kivymd==1.1.1,requests,urllib3,certifi,pyrebase4,pycryptodome,cryptography,pillow

# Configurações de Build
log_level = 2
warn_on_root = 0
