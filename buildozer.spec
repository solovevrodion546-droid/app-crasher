[app]

# Название приложения
title = AppCrasher

# Версия
version = 1.0.0

# Имя пакета
package.name = appcrasher

# Домен пакета
package.domain = org.appcrasher

# Исходный код
source.dir = .

# Включаемые расширения
source.include_exts = py

# Требования
requirements = python3,kivy

# Android API
android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 25b
android.ndk_api = 21

# Разрешения
android.permissions = INTERNET

# Ориентация
orientation = portrait

# Полноэкранный режим
fullscreen = 0

# Debug
android.debug = true

[buildozer]
log_level = 2
warn_on_root = 0
