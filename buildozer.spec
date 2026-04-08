[app]
title = Neural Face HD
package.name = neuralfacehd
package.domain = com.anderson
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,ttf,onnx
source.include_patterns = assets/*,images/*

# REQUISITOS OTIMIZADOS (Removido o que é pesado e desnecessário para o build passar)
requirements = python3,kivy==2.2.1,kivymd==1.1.1,requests,urllib3,chardet,idna,certifi,pyrebase4,pycryptodome,setuptools,requests-toolbelt,cryptography,hostpython3

version = 1.3
orientation = portrait

android.permissions = INTERNET, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, CAMERA
android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 25b
android.skip_update = False
android.accept_sdk_license = True

android.uses_cleartext_traffic = True

# FOCO TOTAL NO REDMI NOTE 14 (64 bits)
# Removendo armeabi-v7a para o build ser mais rápido e não dar erro de tempo/espaço
android.archs = arm64-v8a

p4a.bootstrap = sdl2
# Mantendo 'main' sem o .py para evitar erro de classe não encontrada
android.entrypoint = main
android.copy_libs = 1

[buildozer]
log_level = 2
warn_on_root = 1
