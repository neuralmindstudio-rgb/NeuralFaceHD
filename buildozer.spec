[app]
# (section) Nome e Domínio
title = Neural Face HD
package.name = neuralfacehd
package.domain = com.anderson.neuralface

# (section) Origem dos arquivos
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,mp4,wav,ttf
source.include_patterns = assets/*,images/*

# (section) REQUISITOS (Ajustados para o seu projeto + FFmpeg)
# Adicionamos ffpyplayer e as dependências do Firebase/Requests
requirements = python3,kivy==2.2.1,kivymd==1.1.1,requests,urllib3,chardet,idna,certifi,pyrebase4,gcloud,oauth2client,pycryptodome,ffpyplayer,hostpython3

# (section) Versão e Ícones
version = 1.0.0
# Se tiver ícone, coloque o caminho aqui:
# icon.filename = %(source.dir)s/data/icon.png

# (section) ORIENTAÇÃO
orientation = portrait

# (section) PERMISSÕES (Essenciais para a IA e Loja)
android.permissions = INTERNET, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, CAMERA, BILLING

# (section) CONFIGURAÇÕES ANDROID
android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 25b
android.skip_update = False
android.accept_sdk_license = True

# (section) ARQUITETURA (Importante para Play Store)
# Gera para celulares 32 e 64 bits
android.archs = armeabi-v7a, arm64-v8a

# (section) BIBLIOTECAS DE VÍDEO (Para o ffpyplayer funcionar)
android.copy_libs = 1
# Dependência do FFmpeg para o Kivy reconhecer o vídeo
p4a.branch = master
android.entrypoint = main.py

[buildozer]
log_level = 2
warn_on_root = 1
