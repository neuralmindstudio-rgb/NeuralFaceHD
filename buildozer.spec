[app]
# (section) Nome e Identificação
title = Neural Face HD
package.name = neuralfacehd
package.domain = com.anderson.neuralface

# (section) Origem dos arquivos e Extensões
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,ttf
source.include_patterns = assets/*,images/*

# (section) REQUISITOS - Removido vídeo para estabilidade e adicionado o essencial para o Firebase
requirements = python3,kivy==2.2.1,kivymd==1.1.1,requests,urllib3,chardet,idna,certifi,pyrebase4,gcloud,oauth2client,pycryptodome,setuptools,requests-toolbelt,cryptography,hostpython3

# (section) Versão e Orientação
version = 1.0.0
orientation = portrait

# (section) PERMISSÕES - Cruciais para o app e para a Play Store
android.permissions = INTERNET, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, CAMERA, BILLING

# (section) CONFIGURAÇÕES ANDROID
android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 25b
android.skip_update = False
android.accept_sdk_license = True

# (section) LIBERA CONEXÃO HTTP (Importante para o IP do seu servidor 8080)
android.uses_cleartext_traffic = True

# (section) ARQUITETURA - Crucial para o seu Redmi Note 14
android.archs = armeabi-v7a, arm64-v8a

# (section) BOOTSTRAP E ENTRYPOINT (Ajuste para evitar ClassNotFoundException)
p4a.bootstrap = sdl2
android.entrypoint = main.py
android.copy_libs = 1

[buildozer]
log_level = 2
warn_on_root = 1
