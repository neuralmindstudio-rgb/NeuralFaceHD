[app]
title = Neural Face HD
package.name = neuralfacehd
package.domain = org.neuralmind
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,ttf
version = 1.0.0
version.code = 1

# REQUISITOS: Adicionei ffpyplayer e pyjnius que seu main.py exige
requirements = python3,kivy==2.2.1,kivymd==1.1.1,requests,urllib3,charset-normalizer,idna,certifi,plyer,ffpyplayer,pyjnius,openssl,pyopenssl

orientation = portrait
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, CAMERA

# ESTABILIDADE: API 33 e NDK 23b para evitar o erro dos 17 minutos
android.api = 33
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a
android.accept_sdk_license = True
android.skip_update = True

[buildozer]
log_level = 2
warn_on_root = 1
