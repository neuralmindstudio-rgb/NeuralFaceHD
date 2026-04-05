[app]
# (str) Title of your application
title = Neural Face HD

# (str) Package name
package.name = neuralfacehd

# (str) Package domain
package.domain = org.neuralmind

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include
source.include_exts = py,png,jpg,kv,atlas,json,ttf

# Versão do App
version = 1.0.0
version.code = 1

# --- REQUISITOS CORRIGIDOS ---
# Adicionei ffpyplayer e pyjnius porque seu código usa vídeo e autoclass
requirements = python3,kivy==2.3.0,kivymd==1.2.0,pillow,requests,urllib3,charset-normalizer,idna,certifi,plyer,ffpyplayer,pyjnius

# (list) Supported orientations
orientation = portrait

# (list) Permissions
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, CAMERA

# --- ESTABILIDADE GITHUB ACTIONS ---
# API 33 e NDK 23b são a combinação que NÃO TRAVA nos 17 minutos
android.api = 33
android.minapi = 21
android.ndk = 23b

# (bool) Use --private data storage
android.private_storage = True

# (list) Android archs (Garante que rode em celulares novos e antigos)
android.archs = arm64-v8a, armeabi-v7a

# (bool) Aceitar licenças automaticamente
android.accept_sdk_license = True

# (list) Android build states
android.release_artifact = aab

[buildozer]
log_level = 2
warn_on_root = 1
