import customtkinter as ctk
import os
import psutil
import subprocess
import collections
import numpy as np
import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Базовые настройки UI
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("OpenGL Settings Manager PRO")
        self.geometry("1000x600")
        self.minsize(800, 500)

        # Сетка главного окна
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- ЛЕВАЯ ПАНЕЛЬ (SIDEBAR) ---
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(6, weight=1) # Пустое место перед нижними кнопками
        
        self.logo_label = ctk.CTkLabel(self.sidebar, text="⚙️ GL Manager", font=ctk.CTkFont(size=22, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 20))

        # Кнопки навигации
        self.create_nav_button("Инфо", "info", 1)
        self.create_nav_button("Настройки", "settings", 2)
        self.create_nav_button("Твики Mesa", "tweaks", 3)
        self.create_nav_button("Нагрузка", "graph", 4)
        self.create_nav_button("Процессы", "users", 5)

        # Нижние кнопки утилит
        self.btn_export = ctk.CTkButton(self.sidebar, text="💾 Сохранить отчет", command=self.export_report, fg_color="#27ae60", hover_color="#2ecc71")
        self.btn_export.grid(row=7, column=0, padx=20, pady=10)

        # --- ПРАВАЯ ЧАСТЬ (КОНТЕНТ) ---
        self.container = ctk.CTkFrame(self)
        self.container.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        
        self.frames = {}
        self.setup_all_frames()
        self.show_frame("info") # По умолчанию открываем Инфо

    def create_nav_button(self, text, frame_name, row):
        btn = ctk.CTkButton(self.sidebar, text=text, command=lambda: self.show_frame(frame_name))
        btn.grid(row=row, column=0, padx=20, pady=10)

    def show_frame(self, name):
        for frame in self.frames.values():
            frame.pack_forget()
        self.frames[name].pack(fill="both", expand=True)

    # ==========================================
    # ИНИЦИАЛИЗАЦИЯ ВСЕХ ВКЛАДОК
    # ==========================================
    def setup_all_frames(self):
        self.setup_info_frame()
        self.setup_settings_frame()
        self.setup_tweaks_frame()
        self.setup_graph_frame()
        self.setup_users_frame()

    # --- 1. Вкладка ИНФО ---
    def setup_info_frame(self):
        f_info = ctk.CTkScrollableFrame(self.container, fg_color="transparent")
        
        # Логотип
        try:
            from PIL import Image
            img_path = os.path.join(os.path.dirname(__file__), "logo.png")
            raw_img = Image.open(img_path)
            logo_img = ctk.CTkImage(light_image=raw_img, dark_image=raw_img, size=(150, 75))
            ctk.CTkLabel(f_info, image=logo_img, text="").pack(pady=10)
        except:
            ctk.CTkLabel(f_info, text="[ OpenGL LOGO ]", font=("Arial", 24, "bold"), text_color="#3498db").pack(pady=10)
        
        data = self.get_system_info()
        
        info_text = f"🖥 ВИДЕОКАРТА:\n{data['gpu']}\n\n"
        info_text += f"⚙️ DRIVER & OPENGL:\n{data['gl_info']}\n\n"
        info_text += f"🌡 ТЕМПЕРАТУРА:\n{data['temp']}\n\n"
        info_text += f"🧠 ПАМЯТЬ:\nRAM: {data['ram']} | SWAP: {data['swap']}"
        
        self.info_label = ctk.CTkLabel(f_info, text=info_text, font=("Courier New", 14), justify="left")
        self.info_label.pack(pady=10, padx=20, anchor="w")
        
        self.frames["info"] = f_info

    # --- 2. Вкладка НАСТРОЙКИ (UI и Система) ---
    def setup_settings_frame(self):
        f_settings = ctk.CTkScrollableFrame(self.container, fg_color="transparent")
        ctk.CTkLabel(f_settings, text="Внешний вид и система", font=("Arial", 20, "bold")).pack(pady=(10, 20))

        # Тема
        ctk.CTkLabel(f_settings, text="Тема оформления:").pack(anchor="w", padx=20)
        self.theme_menu = ctk.CTkOptionMenu(f_settings, values=["System", "Dark", "Light"], command=self.change_theme)
        self.theme_menu.pack(pady=5, padx=20, anchor="w")

        # Цвет
        ctk.CTkLabel(f_settings, text="Цветовой акцент:").pack(anchor="w", padx=20, pady=(10,0))
        self.color_menu = ctk.CTkOptionMenu(f_settings, values=["blue", "green", "dark-blue"], command=self.change_color)
        self.color_menu.pack(pady=5, padx=20, anchor="w")

        # Масштаб
        ctk.CTkLabel(f_settings, text="Масштаб интерфейса:").pack(anchor="w", padx=20, pady=(10,0))
        self.scale_slider = ctk.CTkSlider(f_settings, from_=0.8, to=1.5, command=self.change_scaling)
        self.scale_slider.set(1.0)
        self.scale_slider.pack(pady=5, padx=20, anchor="w")

        # Системные утилиты
        ctk.CTkLabel(f_settings, text="Системные утилиты:", font=("Arial", 16, "bold")).pack(anchor="w", padx=20, pady=(20,10))
        ctk.CTkButton(f_settings, text="🔄 Обновить пакеты (apt update)", command=lambda: os.system("gnome-terminal -- sudo apt update")).pack(pady=5, padx=20, anchor="w")
        ctk.CTkButton(f_settings, text="📊 Открыть системный монитор", command=lambda: os.system("gnome-system-monitor &")).pack(pady=5, padx=20, anchor="w")

        self.frames["settings"] = f_settings

    # --- 3. Вкладка ТВИКИ MESA (Новая) ---
    def setup_tweaks_frame(self):
        f_tweaks = ctk.CTkScrollableFrame(self.container, fg_color="transparent")
        ctk.CTkLabel(f_tweaks, text="Твики OpenGL / Mesa", font=("Arial", 20, "bold")).pack(pady=(10, 20))

        self.vsync_var = ctk.StringVar(value="off")
        ctk.CTkSwitch(f_tweaks, text="Принудительный VSync (vblank_mode)", variable=self.vsync_var, onvalue="on", offvalue="off").pack(pady=10, padx=20, anchor="w")

        self.hud_var = ctk.StringVar(value="off")
        ctk.CTkSwitch(f_tweaks, text="Включить Mesa HUD (FPS Overlay)", variable=self.hud_var, onvalue="on", offvalue="off").pack(pady=10, padx=20, anchor="w")

        ctk.CTkButton(f_tweaks, text="🧹 Очистить кэш шейдеров (~/.cache/mesa)", fg_color="#e74c3c", hover_color="#c0392b", command=self.clear_shader_cache).pack(pady=20, padx=20, anchor="w")
        
        self.frames["tweaks"] = f_tweaks

    # --- 4. Вкладка НАГРУЗКА ---
    def setup_graph_frame(self):
        f_graph = ctk.CTkFrame(self.container, fg_color="transparent")
        
        self.load_label = ctk.CTkLabel(f_graph, text="Загрузка CPU: 0% | RAM: 0%", font=("Arial", 18, "bold"))
        self.load_label.pack(pady=10)
        
        # Хранилище данных (теперь две линии)
        self.cpu_history = collections.deque([0]*50, maxlen=50)
        self.ram_history = collections.deque([0]*50, maxlen=50)
        
        # Настройка графика
        self.fig, self.ax = plt.subplots(figsize=(6, 4), dpi=100)
        self.fig.patch.set_facecolor('#2b2b2b')
        self.ax.set_facecolor('#1a1a1a')
        
        self.line_cpu, = self.ax.plot(self.cpu_history, color='#3498db', linewidth=2, label="CPU")
        self.line_ram, = self.ax.plot(self.ram_history, color='#2ecc71', linewidth=2, label="RAM")
        
        self.ax.set_ylim(0, 100)
        self.ax.get_xaxis().set_visible(False)
        self.ax.tick_params(axis='y', colors='white')
        self.ax.legend(loc="upper left", facecolor='#2b2b2b', edgecolor='none', labelcolor='white')
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=f_graph)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
        
        self.frames["graph"] = f_graph
        self.update_live_graph()

    # --- 5. Вкладка ПРОЦЕССЫ ---
    def setup_users_frame(self):
        f_users = ctk.CTkFrame(self.container, fg_color="transparent")
        
        top_frame = ctk.CTkFrame(f_users, fg_color="transparent")
        top_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(top_frame, text="Процессы на GPU", font=("Arial", 18, "bold")).pack(side="left", padx=10)
        ctk.CTkButton(top_frame, text="🔄 Обновить", width=100, command=self.update_processes).pack(side="right", padx=10)

        self.proc_box = ctk.CTkTextbox(f_users, height=200, font=("Consolas", 12))
        self.proc_box.pack(fill="both", expand=True, pady=10)
        
        # Убийство процессов
        kill_frame = ctk.CTkFrame(f_users, fg_color="transparent")
        kill_frame.pack(fill="x", pady=10)
        ctk.CTkLabel(kill_frame, text="Завершить процесс (PID):").pack(side="left", padx=10)
        self.pid_entry = ctk.CTkEntry(kill_frame, width=100)
        self.pid_entry.pack(side="left", padx=10)
        ctk.CTkButton(kill_frame, text="Убить 💀", fg_color="#e74c3c", hover_color="#c0392b", width=80, command=self.kill_process).pack(side="left")

        self.frames["users"] = f_users
        self.update_processes()

    # ==========================================
    # ЛОГИКА И ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
    # ==========================================

    def change_theme(self, new_theme):
        ctk.set_appearance_mode(new_theme)

    def change_color(self, new_color):
        ctk.set_default_color_theme(new_color)
        # Требует перезапуска для полного применения, но базовые элементы изменятся

    def change_scaling(self, new_scale):
        ctk.set_widget_scaling(new_scale)

    def clear_shader_cache(self):
        cache_path = os.path.expanduser("~/.cache/mesa_shader_cache")
        if os.path.exists(cache_path):
            os.system(f"rm -rf {cache_path}/*")
            print("Кэш шейдеров очищен!")
        else:
            print("Папка кэша не найдена.")

    def kill_process(self):
        pid = self.pid_entry.get()
        if pid.isdigit():
            os.system(f"kill -9 {pid}")
            self.pid_entry.delete(0, "end")
            self.update_processes()

    def get_system_info(self):
        info = {"gpu": "Не определено", "gl_info": "Установите mesa-utils", "temp": "Нет данных (нужен lm-sensors)", "ram": "", "swap": ""}
        
        try:
            gpu_model = subprocess.check_output("lspci | grep -E 'VGA|3D'", shell=True).decode()
            info["gpu"] = gpu_model.strip()
        except: pass

        try:
            gl_data = subprocess.check_output("glxinfo -B | grep -E 'OpenGL vendor|OpenGL version|Device'", shell=True).decode()
            info["gl_info"] = gl_data.strip()
        except: pass

        try:
            temp_data = subprocess.check_output("sensors | grep -E 'Core|temp1'", shell=True).decode()
            info["temp"] = temp_data.strip() if temp_data else "Датчики не обнаружены"
        except: pass

        mem = psutil.virtual_memory()
        info["ram"] = f"{mem.used // (1024**2)}MB / {mem.total // (1024**2)}MB"
        swap = psutil.swap_memory()
        info["swap"] = f"{swap.used // (1024**2)}MB / {swap.total // (1024**2)}MB"

        return info

    def update_processes(self):
        try:
            output = subprocess.check_output("lsof /dev/dri/renderD128 2>/dev/null", shell=True).decode()
            self.proc_box.delete("0.0", "end")
            self.proc_box.insert("0.0", output if output else "Процессы не найдены. Возможно, нужны права sudo.")
        except:
            self.proc_box.delete("0.0", "end")
            self.proc_box.insert("0.0", "Ошибка: Установите lsof (sudo apt install lsof)")

    def update_live_graph(self):
        try:
            cpu = psutil.cpu_percent()
            ram = psutil.virtual_memory().percent
            
            self.cpu_history.append(cpu)
            self.ram_history.append(ram)
            
            self.line_cpu.set_ydata(np.array(self.cpu_history))
            self.line_ram.set_ydata(np.array(self.ram_history))
            self.canvas.draw_idle() 
            
            self.load_label.configure(text=f"Загрузка CPU: {cpu}% | RAM: {ram}%")
            
            self.after(1000, self.update_live_graph)
        except Exception as e:
            print(f"Graph Error: {e}")

    def export_report(self):
        filename = f"opengl_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        data = self.get_system_info()
        with open(filename, "w", encoding="utf-8") as f:
            f.write("=== OPENGL SYSTEM REPORT ===\n\n")
            f.write(f"DATE: {datetime.datetime.now()}\n\n")
            f.write("--- GPU ---\n" + data['gpu'] + "\n\n")
            f.write("--- OPENGL ---\n" + data['gl_info'] + "\n\n")
            f.write("--- SENSORS ---\n" + data['temp'] + "\n")
        print(f"Отчет сохранен в файл: {filename}")
        self.btn_export.configure(text="✅ Сохранено!")
        self.after(3000, lambda: self.btn_export.configure(text="💾 Сохранить отчет"))

if __name__ == "__main__":
    app = App()
    app.mainloop()