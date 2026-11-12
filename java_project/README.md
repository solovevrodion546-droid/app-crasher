# AppCrasher - Android приложение для вылета приложений
Чистый Java Android проект. Не требует Python, Kivy, Buildozer.

## Структура проекта
```
java_project/
├── app/
│   ├── src/main/
│   │   ├── java/org/appcrasher/crasher/
│   │   │   ├── MainActivity.java  # Главный экран + force-stop
│   │   │   └── AppAdapter.java    # Адаптер списка
│   │   ├── AndroidManifest.xml    # Манифест
│   │   └── res/                   # Ресурсы
│   └── build.gradle               # Зависимости
├── build.gradle                   # Top-level
├── settings.gradle
└── gradle.properties
```

## Как собрать
1. Открыть в Android Studio
2. Build → Build APK
3. APK появится в `app/build/outputs/apk/debug/`

## Или через CI
GitHub Actions собирает APK автоматически.
