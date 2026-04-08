[app]
# (section) Nome e Identificação
title = Neural Face HD
package.name = neuralfacehd
package.domain = com.anderson

# (section) Origem dos arquivos e Extensões
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,ttf,onnx
source.include_patterns = assets/*,images/*

# (section) REQUISITOS (Ajustado para não quebrar no build)
# Travar a cryptography em 38.0.4 é o segredo para o APK gerar sem erro de Rust/C++
requirements = python3,kivy==2.2.1,kivymd==1.1.1,requests,urllib3,chardet,idna,certifi,pyrebase4,gcloud-free,oauth2client,pycryptodome,setuptools,requests-toolbelt,cryptography==38.0.4,hostpython3

# (section) Versão e Orientação
# Versão 1.2 para garantir que o Android limpe o app velho
version = 1.2
orientation = portrait

# (section) PERMISSÕES
android.permissions = INTERNET, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, CAMERA, BILLING

# (section) CONFIGURAÇÕES ANDROID (Otimizadas para seu Redmi - Android 14)
android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 25b
android.skip_update = False
android.accept_sdk_license = True
android.enable_v2_signing = True

# (section) LIBERA CONEXÃO HTTP (Para seu servidor 191.253.31.209)
android.uses_cleartext_traffic = True

# (section) ARQUITETURA
android.archs = armeabi-v7a, arm64-v8a

# (section) BOOTSTRAP E ENTRYPOINT (O ajuste que remove o erro de Main)
p4a.bootstrap = sdl2
android.entrypoint = main
android.copy_libs = 1

[buildozer]
log_level = 2
warn_on_root = 1
