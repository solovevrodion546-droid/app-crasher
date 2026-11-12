import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import threading

class AppCrasher:
    def __init__(self, root):
        self.root = root
        self.root.title("App Crasher")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        # Получаем список установленных приложений
        self.packages = self.get_installed_apps()
        
        # Заголовок
        title_frame = tk.Frame(root)
        title_frame.pack(fill=tk.X, padx=10, pady=10)
        
        title_label = tk.Label(title_frame, text="App Crasher", font=("Segoe UI", 20, "bold"))
        title_label.pack()
        
        subtitle = tk.Label(title_frame, text="Выберите приложение для вылета", font=("Segoe UI", 10), fg="gray")
        subtitle.pack()
        
        # Поле поиска
        search_frame = tk.Frame(root)
        search_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(search_frame, text="Поиск:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self.filter_apps)
        self.search_entry = tk.Entry(search_frame, textvariable=self.search_var, font=("Segoe UI", 11))
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        
        # Список приложений
        list_frame = tk.Frame(root)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.app_listbox = tk.Listbox(list_frame, selectmode=tk.SINGLE, font=("Segoe UI", 10), 
                                       yscrollcommand=scrollbar.set, exportselection=0)
        self.app_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.app_listbox.yview)
        
        # Заполняем список
        self.all_packages = []
        for pkg in self.packages:
            name = self.get_app_name(pkg)
            self.all_packages.append((pkg, name))
            self.app_listbox.insert(tk.END, name)
        
        # Кнопки управления
        btn_frame = tk.Frame(root)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.crash_btn = tk.Button(btn_frame, text="💥 ВЫПЛЕТЕТЬ!", font=("Segoe UI", 14, "bold"), 
                                    bg="#ff4444", fg="white", command=self.crash_app,
                                    activebackground="#ff2222", activeforeground="white")
        self.crash_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))
        
        self.close_btn = tk.Button(btn_frame, text="Закрыть", font=("Segoe UI", 11), 
                                    command=root.quit)
        self.close_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Статус
        self.status_var = tk.StringVar(value="Выберите приложение и нажмите кнопку")
        status_frame = tk.Frame(root)
        status_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(status_frame, textvariable=self.status_var, font=("Segoe UI", 9), fg="blue").pack(side=tk.LEFT)
        
        # Отображение выбранного приложения
        self.selected_pkg = tk.StringVar(value="Не выбрано")
        tk.Label(root, textvariable=self.selected_pkg, font=("Segoe UI", 9), fg="gray").pack(pady=(0, 10))
        
        # Bind selection
        self.app_listbox.bind('<<ListboxSelect>>', self.on_select)
        
    def get_installed_apps(self):
        """Получить список установленных приложений через ADB"""
        try:
            result = subprocess.run(
                ["adb", "shell", "pm", "list", "packages", "-3"],
                capture_output=True, text=True, timeout=10
            )
            packages = []
            for line in result.stdout.strip().split('\n'):
                if line.startswith('package:'):
                    packages.append(line.split(':', 1)[1])
            return packages
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось получить список приложений:\n{e}")
            return []
    
    def get_app_name(self, package_name):
        """Получить имя приложения"""
        try:
            result = subprocess.run(
                ["adb", "shell", "pm", "label", package_name],
                capture_output=True, text=True, timeout=5
            )
            # Формат: Name: [AppName]
            if result.stdout.startswith("Name: "):
                return result.stdout[6:].strip()
            return package_name
        except:
            return package_name
    
    def filter_apps(self, *args):
        """Фильтровать приложения по поиску"""
        query = self.search_var.get().lower()
        self.app_listbox.delete(0, tk.END)
        
        for pkg, name in self.all_packages:
            if query in name.lower() or query in pkg.lower():
                self.app_listbox.insert(tk.END, name)
    
    def on_select(self, event):
        """Обработка выбора приложения"""
        selection = self.app_listbox.curselection()
        if selection:
            index = selection[0]
            # Найти оригинальный пакет
            query = self.search_var.get().lower()
            matched = []
            for pkg, name in self.all_packages:
                if query in name.lower() or query in pkg.lower():
                    matched.append((pkg, name))
            
            if index < len(matched):
                pkg, name = matched[index]
                self.selected_pkg.set(f"Выбрано: {name} ({pkg})")
    
    def crash_app(self):
        """Выплотеть выбранное приложение"""
        selection = self.app_listbox.curselection()
        if not selection:
            messagebox.showwarning("Внимание", "Выберите приложение!")
            return
        
        index = selection[0]
        query = self.search_var.get().lower()
        matched = []
        for pkg, name in self.all_packages:
            if query in name.lower() or query in pkg.lower():
                matched.append((pkg, name))
        
        if index >= len(matched):
            return
        
        pkg, name = matched[index]
        
        if messagebox.askyesno("Подтверждение", f"Выплотеть {name}?\n\nЭто завершит процесс приложения."):
            self.status_var.set(f"Работаем... {name}")
            self.crash_btn.config(state=tk.DISABLED)
            
            def do_crash():
                try:
                    # Метод 1: Uid crash (наиболее эффективный)
                    self.status_var.set(f"Выплотаем {name}...")
                    
                    # Попробуем несколько методов
                    methods = [
                        # Метод 1: Send SIGKILL
                        ("kill через ADB", lambda: subprocess.run(
                            ["adb", "shell", "am", "force-stop", pkg],
                            capture_output=True, text=True, timeout=5
                        )),
                        
                        # Метод 2: Send SIGKILL через pid
                        ("kill через pid", lambda: self.kill_by_pid(pkg)),
                        
                        # Метод 3: Crash через binder
                        ("binder crash", lambda: subprocess.run(
                            ["adb", "shell", "su", "-c", f"kill -9 $(pgrep -f {pkg})"],
                            capture_output=True, text=True, timeout=5
                        ) if self.has_root() else None),
                    ]
                    
                    success = False
                    for method_name, method_func in methods:
                        try:
                            result = method_func()
                            if result is None:
                                continue
                            if result.returncode == 0 or "force" in method_name.lower():
                                success = True
                                self.status_var.set(f"✓ {name} выплетела методом: {method_name}")
                                break
                        except:
                            continue
                    
                    if not success:
                        self.status_var.set(f"✗ Не удалось выплотеть {name}")
                        messagebox.showerror("Ошибка", f"Не удалось выплотеть {name}")
                    
                except Exception as e:
                    self.status_var.set(f"Ошибка: {e}")
                    messagebox.showerror("Ошибка", str(e))
                finally:
                    self.root.after(0, lambda: self.crash_btn.config(state=tk.NORMAL))
            
            thread = threading.Thread(target=do_crash, daemon=True)
            thread.start()
    
    def kill_by_pid(self, package_name):
        """Убить процесс по PID"""
        try:
            # Найти PID процесса
            result = subprocess.run(
                ["adb", "shell", "pidof", package_name.split('.')[-1]],
                capture_output=True, text=True, timeout=5
            )
            pid = result.stdout.strip()
            if pid:
                subprocess.run(
                    ["adb", "shell", "kill", "-9", pid],
                    capture_output=True, text=True, timeout=5
                )
                return True
            return False
        except:
            return False
    
    def has_root(self):
        """Проверить наличие root прав"""
        try:
            result = subprocess.run(
                ["adb", "shell", "su", "-c", "echo test"],
                capture_output=True, text=True, timeout=3
            )
            return result.returncode == 0
        except:
            return False

if __name__ == "__main__":
    root = tk.Tk()
    app = AppCrasher(root)
    root.mainloop()
