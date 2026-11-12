"""
AppCrasher - Приложение для вылета других приложений на Android
Работает БЕЗ ADB - использует Android API напрямую
"""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.core.window import Window
from kivy.utils import platform
import subprocess
import threading


class AppCrasherApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.packages = []
        self.selected_package = ""
        self.app_names = {}

    def build(self):
        # Темная тема
        Window.clearcolor = (0.06, 0.06, 0.1, 1)

        # Основной layout
        main = BoxLayout(orientation='vertical', padding=12, spacing=8)

        # Заголовок
        title = Label(
            text="💥 AppCrasher 💥",
            font_size='30sp',
            bold=True,
            color=(1, 0.15, 0.2, 1),
            size_hint=(1, 0.12)
        )

        subtitle = Label(
            text="Выбери приложение и выплотите!\n(Без ADB - работает на телефоне)",
            font_size='12sp',
            color=(0.6, 0.6, 0.7, 1),
            size_hint=(1, 0.05)
        )

        # Поиск
        self.search_input = TextInput(
            hint_text="🔍 Поиск...",
            multiline=False,
            font_size='16sp',
            size_hint=(1, 0.07),
            background_color=(0.12, 0.12, 0.22, 1),
            foreground_color=(1, 1, 1, 1),
            cursor_color=(1, 1, 1, 1)
        )
        self.search_input.bind(text=self.on_search)

        # Список
        self.scroll_view = ScrollView()
        self.list_layout = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=4
        )
        self.list_layout.bind(minimum_height=self.list_layout.setter('height'))

        # Статус
        self.status_label = Label(
            text="⏳ Загрузка приложений...",
            font_size='11sp',
            color=(0.4, 0.7, 1, 1),
            size_hint=(1, 0.04)
        )

        # Кнопка вылета
        self.crash_button = Button(
            text="💥 ВЫПЛЕТЕТЬ!",
            font_size='22sp',
            bold=True,
            background_color=(0.9, 0.12, 0.12, 1),
            color=(1, 1, 1, 1),
            size_hint=(1, 0.1)
        )
        self.crash_button.bind(on_press=self.crash_selected)

        # Закрыть
        close_button = Button(
            text="Закрыть",
            font_size='14sp',
            background_color=(0.15, 0.15, 0.25, 1),
            color=(0.7, 0.7, 0.8, 1),
            size_hint=(1, 0.07)
        )
        close_button.bind(on_press=lambda x: self.stop())

        # Собираем всё
        main.add_widget(title)
        main.add_widget(subtitle)
        main.add_widget(self.search_input)
        main.add_widget(self.scroll_view)
        main.add_widget(self.status_label)
        main.add_widget(self.crash_button)
        main.add_widget(close_button)

        self.scroll_view.add_widget(self.list_layout)

        # Загружаем приложения
        self.load_apps_in_thread()

        return main

    def load_apps_in_thread(self):
        """Загружаем список приложений в фоновом потоке"""
        def load():
            packages = self.get_packages()
            names = {}
            for pkg in packages[:50]:  # Первые 50 для скорости
                names[pkg] = self.get_app_name(pkg)

            def update():
                self.packages = packages
                self.app_names = names
                self.populate_list(packages, names)
                self.status_label.text = f"✅ Загружено: {len(packages)} приложений"
                self.status_label.color = (0.2, 1, 0.3, 1)

            # На Android вызываем в UI-потоке
            if platform == 'android':
                from kivy.base import EventLoop
                EventLoop.add_callback(update)
            else:
                update()

        threading.Thread(target=load, daemon=True).start()

    def get_packages(self):
        """Получить список установленных приложений"""
        try:
            result = subprocess.run(
                ['am', 'list', 'packages', '-3'],
                capture_output=True,
                text=True,
                timeout=10
            )
            packages = []
            for line in result.stdout.strip().split('\n'):
                if line.startswith('package:'):
                    pkg = line.split(':', 1)[1].strip()
                    if pkg and len(pkg) > 3:
                        packages.append(pkg)
            return packages
        except Exception as e:
            print(f"Ошибка загрузки пакетов: {e}")
            return []

    def get_app_name(self, package):
        """Получить имя приложения"""
        try:
            result = subprocess.run(
                ['pm', 'label', package],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.stdout.startswith("Name: "):
                return result.stdout[6:].strip()
        except:
            pass
        # Дефолтное имя
        parts = package.split('.')
        if len(parts) > 1:
            return parts[-1].replace('_', ' ').title()
        return package

    def populate_list(self, packages, names):
        """Заполняем список кнопок"""
        self.list_layout.clear_widgets()

        for pkg in packages:
            name = names.get(pkg, pkg)
            btn = Button(
                text=f"{name}\n{pkg}",
                font_size='11sp',
                size_hint_y=None,
                height=50,
                background_color=(0.1, 0.1, 0.2, 1),
                color=(0.9, 0.95, 1, 1),
                halign='left',
                valign='middle',
                padding=(10, 5),
                text_size=(None, None)
            )
            btn.bind(on_press=lambda *args, p=pkg: self.select_app(p, *args))
            self.list_layout.add_widget(btn)

    def on_search(self, instance, value):
        """Фильтрация по поиску"""
        query = value.lower()
        for child in self.list_layout.children:
            if isinstance(child, Button):
                if query in child.text.lower():
                    child.opacity = 1
                    child.disabled = False
                else:
                    child.opacity = 0.2
                    child.disabled = True

    def select_app(self, package, button):
        """Выбираем приложение"""
        self.selected_package = package

        # Сбрасываем цвет всех
        for child in self.list_layout.children:
            if isinstance(child, Button):
                child.background_color = (0.1, 0.1, 0.2, 1)

        # Подсвечиваем выбранное
        button.background_color = (0.1, 0.45, 0.9, 1)

        # Показываем статус
        name = self.app_names.get(package, package)
        self.status_label.text = f"✅ Выбрано: {name}"
        self.status_label.color = (0.3, 1, 0.3, 1)

    def crash_selected(self, instance):
        """Выплотаем выбранное приложение"""
        if not self.selected_package:
            self.status_label.text = "⚠️ Сначала выбери приложение!"
            self.status_label.color = (1, 0.8, 0, 1)
            return

        pkg = self.selected_package
        name = self.app_names.get(pkg, pkg)

        # Подтверждение
        from kivy.uix.popup import Popup
        from kivy.uix.label import Label as UILabel
        from kivy.uix.button import Button as UIButton

        content = BoxLayout(orientation='vertical', padding=20, spacing=10)
        content.add_widget(UILabel(
            text=f"Выплотеть {name}?",
            font_size='18sp'
        ))

        def confirm(*args):
            popup.dismiss()
            self.do_crash(pkg)

        def cancel(*args):
            popup.dismiss()

        btn_row = BoxLayout(size_hint_y=None, height=50, spacing=10)
        btn_row.add_widget(UIButton(
            text="✅ Да",
            background_color=(0.1, 0.7, 0.1, 1),
            color=(1, 1, 1, 1),
            on_press=confirm
        ))
        btn_row.add_widget(UIButton(
            text="❌ Нет",
            background_color=(0.7, 0.1, 0.1, 1),
            color=(1, 1, 1, 1),
            on_press=cancel
        ))
        content.add_widget(btn_row)

        popup = Popup(
            title="Подтверждение",
            content=content,
            size_hint=(0.8, 0.4)
        )
        popup.open()

    def do_crash(self, package):
        """Выполняем выпоту"""
        name = self.app_names.get(package, package)

        self.status_label.text = f"⚡ Выплотаем {name}..."
        self.status_label.color = (1, 0.7, 0, 1)
        self.crash_button.disabled = True

        def crash_thread():
            try:
                # am force-stop - работает без root на Android 12+
                result = subprocess.run(
                    ['am', 'force-stop', package],
                    capture_output=True,
                    text=True,
                    timeout=5
                )

                if result.returncode == 0:
                    success_msg = f"✅ {name} ВЫПЛЫЛА!"
                    self.status_label.text = success_msg
                    self.status_label.color = (0.2, 1, 0.2, 1)

                    # Показываем popup об успехе
                    self.show_popup("Успех!", success_msg, (0.2, 1, 0.2, 1))
                else:
                    # Пробуем kill -9
                    self.status_label.text = "Метод 2: kill -9..."
                    self.try_kill(package, name)

            except Exception as e:
                self.status_label.text = f"❌ Ошибка: {e}"
                self.status_label.color = (1, 0.2, 0.2, 1)

            finally:
                self.crash_button.disabled = False

        threading.Thread(target=crash_thread, daemon=True).start()

    def try_kill(self, package, name):
        """Убиваем процесс через PID"""
        try:
            pid_result = subprocess.run(
                ['pidof', package.split('.')[-1]],
                capture_output=True,
                text=True,
                timeout=5
            )
            pid = pid_result.stdout.strip()

            if pid:
                kill_result = subprocess.run(
                    ['kill', '-9', pid],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if kill_result.returncode == 0:
                    self.status_label.text = f"✅ {name} выплотела через kill!"
                    self.status_label.color = (0.2, 1, 0.2, 1)
                    self.show_popup("Успех!", f"{name} выплотела!", (0.2, 1, 0.2, 1))
                else:
                    self.status_label.text = "❌ Не удалось убить"
                    self.status_label.color = (1, 0.2, 0.2, 1)
            else:
                self.status_label.text = "⚠️ Process не найден"
                self.status_label.color = (1, 0.7, 0, 1)
        except:
            self.status_label.text = "❌ Ошибка kill"
            self.status_label.color = (1, 0.2, 0.2, 1)

    def show_popup(self, title, message, color):
        """Показываем popup"""
        from kivy.uix.popup import Popup
        from kivy.uix.label import Label as UILabel

        popup = Popup(
            title=title,
            content=UILabel(text=message, font_size='16sp', color=color),
            size_hint=(0.8, 0.3)
        )
        popup.open()


if __name__ == '__main__':
    AppCrasherApp().run()
