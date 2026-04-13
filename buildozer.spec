[app]
title = Neural Face HD
package.name = neuralfacehd
package.domain = com.anderson

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,ttf,onnx
source.include_patterns = assets/*,images/*

version = 1.3
orientation = portrait
fullscreen = 0

# 🔥 REQUISITOS LIMPOS E ESTÁVEIS
requirements = python3,kivy==2.3.0,kivymd==1.2.0,requests,urllib3,certifi,pyrebase4,pycryptodome,cryptography

# 🔐 Permissões
android.permissions = INTERNET, CAMERA, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, READ_MEDIA_IMAGES, ACCESS_NETWORK_STATE

# ⚙️ CONFIG ANDROID ESTÁVEL
android.api = 33
android.minapi = 21
android.ndk = 25b

android.accept_sdk_license = True
android.skip_update = False
android.uses_cleartext_traffic = True

# 📱 64 bits
android.archs = arm64-v8a

# 🔧 Bootstrap correto
p4a.bootstrap = sdl2

# ❌ NÃO usar entrypoint (quebrava o build)
# android.entrypoint = main.py

android.copy_libs = 1

[buildozer]
log_level = 2
warn_on_root = 1
