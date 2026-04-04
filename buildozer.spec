[app]
# (str) Title of your application
title = Neural Face HD

# (str) Package name
package.name = neuralfacehd

# (str) Package domain (needed for android packaging)
package.domain = org.neuralmind

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include
source.include_exts = py,png,jpg,kv,atlas,json

# --- AQUI ESTAVA O ERRO: Mudei para 'version' ---
version = 1.0.0

# (int) Android version code
version.code = 1

# (list) Application requirements
requirements = python3,kivy==2.3.0,kivymd,requests,urllib3,charset-normalizer,idna,certifi,plyer

# (list) Supported orientations
orientation = portrait

# (list) Permissions
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, CAMERA, MANAGE_EXTERNAL_STORAGE

# (int) Target Android API
android.api = 34

# (int) Minimum API
android.minapi = 21

# (str) Android NDK version
android.ndk = 25b

# (bool) Use --private data storage
android.private_storage = True

# (str) Android entry point
android.entrypoint = main.py

# (list) Android build states
android.release_artifact = aab

# (str) Skip update (Saves time in GitHub Actions)
android.skip_update = False

# (bool) copy library to project (set to True for complex libraries)
android.copy_libs = True

[buildozer]
# (int) Log level (2 = debug para vermos tudo no GitHub)
log_level = 2

# (int) Display warning if buildozer is run as root
warn_on_root = 1
