[app]
# (str) Title of your application
title = Neural Face HD

# (str) Package name
package.name = neuralfacehd

# (str) Package domain (needed for android packaging)
package.domain = org.neuralmind

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,json

# (str) Application versioning (method 1)
version.official = 1.0.0
# (int) Android version code (PARA ATUALIZAR NA PLAY STORE, SEMPRE AUMENTE ESSE NUMERO)
version.code = 1

# (list) Application requirements
# MUITO IMPORTANTE: Incluir plyer e as bibliotecas de rede
requirements = python3,kivy==2.3.0,kivymd,requests,urllib3,charset-normalizer,idna,certifi,plyer

# (str) Presplash of the application
# presplash.filename = %(source.dir)s/data/presplash.png

# (str) Icon of the application
# icon.filename = %(source.dir)s/data/icon.png

# (list) Supported orientations
orientation = portrait

# (list) Permissions
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, CAMERA

# (int) Target Android API, should be as high as possible.
# EXIGÊNCIA DA PLAY STORE EM 2026: API 34
android.api = 34

# (int) Minimum API your APK will support.
android.minapi = 21

# (str) Android NDK version to use
android.ndk = 25b

# (bool) Use --private data storage (True) or --dir public storage (False)
android.private_storage = True

# (str) Android entry point, default is to use start.py
android.entrypoint = main.py

# (list) List of Java .jar files to add to the libs so that pyjnius can access
# their classes. Don't add jar files that you do not need, since each jar
# adds a few hundreds of KB to your APK size.
# android.add_jars = foo.jar,bar.jar,path/to/baz.jar

# (list) Android build states
android.release_artifact = aab

# (str) Path to a custom keystore to sign the APK (WE WILL USE GITHUB SECRETS FOR THIS)
# android.keystore = 
# android.keystore_password = 
# android.keyalias = 
# android.keyalias_password = 

[buildozer]
# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = no, 1 = yes)
warn_on_root = 1
