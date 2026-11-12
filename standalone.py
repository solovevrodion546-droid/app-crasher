"""
AppCrasher - Android APK приложение
Работает БЕЗ ADB - использует Android API напрямую
"""
# Этот код будет запущен внутри Android через python-for-android

import subprocess
import os

def get_installed_packages():
    """Получить список установленных приложений через Android"""
    try:
        # Используем am list packages
        result = subprocess.run(
            ['am', 'list', 'packages', '-3'],
            capture_output=True, text=True, timeout=10
        )
        packages = []
        for line in result.stdout.strip().split('\n'):
            if line.startswith('package:'):
                pkg = line.split(':', 1)[1].strip()
                if pkg:
                    packages.append(pkg)
        return packages
    except:
        return []

def get_app_name(package):
    """Получить имя приложения"""
    try:
        result = subprocess.run(
            ['pm', 'label', package],
            capture_output=True, text=True, timeout=5
        )
        if result.stdout.startswith("Name: "):
            return result.stdout[6:].strip()
    except:
        pass
    return package

def crash_app(package):
    """Выплотеть приложение через Android API"""
    try:
        # Используем am force-stop (работает без root на Android 12)
        result = subprocess.run(
            ['am', 'force-stop', package],
            capture_output=True, text=True, timeout=5
        )
        return result.returncode == 0
    except:
        return False

if __name__ == '__main__':
    print("AppCrasher запущен!")
    print(f"Найдено приложений: {len(get_installed_packages())}")
