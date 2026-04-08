[app]
# (section) Nome e Identificação
title = Neural Face HD
package.name = neuralfacehd
package.domain = com.anderson

# (section) Origem dos arquivos e Extensões
source.dir = .
# Adicionado onnx caso você precise carregar algum modelo local no futuro
source.include_exts = py,png,jpg,kv,atlas,json,ttf,onnx
source.include_patterns = assets/*,images/*

# (section) REQUISITOS (Blindado contra erros de compilação)
requirements = python3,kivy==2.2.1,kivymd==1.1.1,requests,urllib3,chardet,idna,certifi,pyrebase4,gcloud-free,oauth2client,pycryptodome,setuptools,requests-toolbelt,cryptography==38.0.4,hostpython3

# (section) Versão e Orientação
# Pulamos para 1.3 para ignorar qualquer cache de erro da 1.2
version = 1.3
orientation = portrait

# (section) PERMISSÕES
# Removido BILLING para evitar o erro de compilação JNI/C que vimos no log
android.permissions = INTERNET, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, CAMERA

# (section) CONFIGURAÇÕES ANDROID (Otimizadas para Android 14)
android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 25b
android.skip_update = False
android.accept_sdk_license = True
android.enable_v2_signing = True

# (section) LIBERA CONEXÃO HTTP (Para o IP 191.253.31.209)
android.uses_cleartext_traffic = True

# (section) ARQUITETURA
android.archs = armeabi-v7a, arm64-v8a

# (section) BOOTSTRAP E ENTRYPOINT
p4a.bootstrap = sdl2
android.entrypoint = main
android.copy_libs = 1

[buildozer]
log_level = 2
warn_on_root = 1
