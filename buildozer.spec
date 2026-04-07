[app]
# (section) Nome e Domínio
title = Neural Face HD
package.name = neuralfacehd
package.domain = com.anderson.neuralface

# (section) Origem dos arquivos
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,mp4,wav,ttf
source.include_patterns = assets/*,images/*

# (section) REQUISITOS (Versão Blindada para Redmi Note 14)
# Adicionados: setuptools (Firebase), ffmpeg, sdl2_image, sdl2_ttf (Vídeo)
requirements = python3,kivy==2.2.1,kivymd==1.1.1,requests,urllib3,chardet,idna,certifi,pyrebase4,gcloud,oauth2client,pycryptodome,setuptools,ffpyplayer,ffmpeg,sdl2_image,sdl2_ttf,hostpython3

# (section) Versão e Ícones
version = 1.0.0

# (section) ORIENTAÇÃO
orientation = portrait

# (section) PERMISSÕES
android.permissions = INTERNET, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, CAMERA, BILLING

# (section) CONFIGURAÇÕES ANDROID
android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 25b
android.skip_update = False
android.accept_sdk_license = True

# (section) LIBERA CONEXÃO COM O SERVIDOR (Importante para porta 8080)
android.uses_cleartext_traffic = True

# (section) ARQUITETURA (Gera para o seu Redmi 64 bits e outros 32 bits)
android.archs = armeabi-v7a, arm64-v8a

# (section) BIBLIOTECAS DE VÍDEO
android.copy_libs = 1
android.entrypoint = main.py

[buildozer]
log_level = 2
warn_on_root = 1
