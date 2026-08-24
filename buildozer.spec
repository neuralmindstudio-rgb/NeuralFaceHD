[app]

title = Neural Face HD
package.name = neuralfacehd
package.domain = com.neuralmindstudio

source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,json,onnx,keystore,ttf
source.include_patterns = assets/*,gfpgan/*,*.onnx,images/*

version = 1.0.1
android.numeric_version = 169

orientation = portrait
fullscreen = 0

android.permissions = INTERNET,CAMERA,ACCESS_NETWORK_STATE,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,READ_MEDIA_IMAGES

android.api = 35
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a

android.accept_sdk_license = True
android.skip_update = False
android.uses_cleartext_traffic = True
android.copy_libs = 1

android.python_version = 3.11

p4a.branch = v2024.01.21
p4a.bootstrap = sdl2

requirements = python3==3.11.9,kivy==2.3.0,kivymd==1.1.1,requests,urllib3,certifi,pyrebase4,pycryptodome,cryptography,pillow==10.4.0,pyjnius

icon.filename = logo.png
presplash.filename = splash.png

log_level = 2
warn_on_root = 0

