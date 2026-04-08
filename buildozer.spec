[app]
# (section) Nome e Identificação
title = Neural Face HD
package.name = neuralfacehd
# Simplifiquei o domínio para evitar caminhos de pasta muito longos no Android
package.domain = com.anderson

# (section) Origem dos arquivos e Extensões
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,ttf
source.include_patterns = assets/*,images/*

# (section) REQUISITOS (Versão Turbo e Estável)
requirements = python3,kivy==2.2.1,kivymd==1.1.1,requests,urllib3,chardet,idna,certifi,pyrebase4,gcloud,oauth2client,pycryptodome,setuptools,requests-toolbelt,cryptography,hostpython3

# (section) Versão e Orientação
# Mudei a versão para 1.1 para forçar o Android a ignorar caches antigos
version = 1.1
orientation = portrait

# (section) PERMISSÕES
android.permissions = INTERNET, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, CAMERA, BILLING

# (section) CONFIGURAÇÕES ANDROID (Otimizadas para Android 13/14)
android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 25b
android.skip_update = False
android.accept_sdk_license = True
# Ativa a assinatura moderna exigida pelos novos Redmis
android.enable_v2_signing = True

# (section) LIBERA CONEXÃO HTTP (Essencial para o IP do seu servidor 8080)
android.uses_cleartext_traffic = True

# (section) ARQUITETURA
android.archs = armeabi-v7a, arm64-v8a

# (section) BOOTSTRAP E ENTRYPOINT (Ajuste Crítico)
p4a.bootstrap = sdl2
# Mudança estratégica: apenas 'main' sem o '.py'
android.entrypoint = main
android.copy_libs = 1

[buildozer]
log_level = 2
warn_on_root = 1
