[app]
# (section) Nome e Identificação
title = Neural Face HD
package.name = neuralfacehd
package.domain = com.anderson

# (section) Origem dos arquivos e Extensões
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,ttf,onnx
source.include_patterns = assets/*,images/*

# (section) REQUISITOS (Versões atualizadas para evitar erro 404)
requirements = python3,kivy==2.3.0,kivymd==1.2.0,requests,urllib3,chardet,idna,certifi,pyrebase4,gcloud-free,oauth2client,pycryptodome,setuptools,requests-toolbelt,cryptography,hostpython3

# (section) Versão e Orientação
version = 1.3
orientation = portrait

# (section) PERMISSÕES
android.permissions = INTERNET, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, CAMERA

# (section) CONFIGURAÇÕES ANDROID
android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 25b
android.skip_update = False
android.accept_sdk_license = True
android.enable_v2_signing = True

# (section) LIBERA CONEXÃO HTTP (Para o IP do servidor)
android.uses_cleartext_traffic = True

# (section) ARQUITETURA (Gera para o seu Redmi Note 14)
android.archs = armeabi-v7a, arm64-v8a

# (section) BOOTSTRAP E ENTRYPOINT
p4a.bootstrap = sdl2
# Mudamos para 'main' sem o .py para o Android reconhecer a classe corretamente
android.entrypoint = main
android.copy_libs = 1

[buildozer]
log_level = 2
warn_on_root = 1
