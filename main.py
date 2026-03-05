import customtkinter as ctk
import os
import psutil
import subprocess
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import collections
import numpy as np

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("OpenGL Settings Manager")
        self.geometry("900x500")

        # Настройка сетки (Grid)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- ЛЕВАЯ ПАНЕЛЬ (SIDEBAR) ---
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        self.btn_info = ctk.CTkButton(self.sidebar, text="Инфо", command=lambda: self.show_frame("info"))
        self.btn_info.pack(pady=10, padx=10)
        
        self.logo_label = ctk.CTkLabel(self.sidebar, text="OpenGL Tool", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.pack(pady=20, padx=10)

        self.btn_settings = ctk.CTkButton(self.sidebar, text="Настройки", command=lambda: self.show_frame("settings"))
        self.btn_settings.pack(pady=10, padx=10)

        self.btn_graph = ctk.CTkButton(self.sidebar, text="Нагрузка", command=lambda: self.show_frame("graph"))
        self.btn_graph.pack(pady=10, padx=10)

        self.btn_users = ctk.CTkButton(self.sidebar, text="Кто использует", command=lambda: self.show_frame("users"))
        self.btn_users.pack(pady=10, padx=10)

        # --- ПРАВАЯ ЧАСТЬ (КОНТЕНТ) ---
        self.container = ctk.CTkFrame(self)
        self.container.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        
        self.frames = {}
        self.setup_frames()
        self.show_frame("settings")

    def setup_frames(self):
        # 1. Вкладка Настройки
        f_settings = ctk.CTkFrame(self.container, fg_color="transparent")
        ctk.CTkLabel(f_settings, text="Настройки системы", font=("Arial", 20)).pack(pady=10)
        ctk.CTkButton(f_settings, text="Обновить драйверы", command=lambda: print("Updating...")).pack(pady=5)
        self.frames["settings"] = f_settings

        # 2. Вкладка Нагрузка
        f_graph = ctk.CTkFrame(self.container, fg_color="transparent")
        self.load_label = ctk.CTkLabel(f_graph, text="Загрузка CPU: 0%", font=("Arial", 20))
        self.load_label.pack(pady=20)
        
        # Интегрируем график во вкладку Нагрузка
        self.setup_resource_graph(f_graph)
        self.update_stats()
        self.frames["graph"] = f_graph

        # 3. Вкладка Кто использует
        f_users = ctk.CTkFrame(self.container, fg_color="transparent")
        ctk.CTkLabel(f_users, text="Процессы использующие GPU/OpenGL", font=("Arial", 18)).pack(pady=10)
        self.proc_box = ctk.CTkTextbox(f_users, width=500, height=250)
        self.proc_box.pack(pady=10)
        
        # Загружаем список процессов
        self.update_processes()
        self.frames["users"] = f_users

        # info
        f_info = ctk.CTkFrame(self.container, fg_color="transparent")
        # Попытка загрузить логотип
        try:
            from PIL import Image
            img_path = os.path.join(os.path.dirname(__file__), "logo.png")
            raw_img = Image.open(img_path)
            logo_img = ctk.CTkImage(light_image=raw_img, dark_image=raw_img, size=(200, 100))
            logo_label = ctk.CTkLabel(f_info, image=logo_img, text="")
            logo_label.pack(pady=20)
        except:
            ctk.CTkLabel(f_info, text="[ OpenGL Logo ]", font=("Arial", 24, "bold")).pack(pady=20)
        
        # Вывод данных о железе
        data = self.get_gpu_info()
        
        info_text = f"🖥 Видеокарта:\n{data['gpu']}\n\n"
        info_text += f"⚙️ Драйвер и OpenGL:\n{data['info']}"
        
        self.info_label = ctk.CTkLabel(f_info, text=info_text, font=("Consolas", 14), justify="left")
        self.info_label.pack(pady=10, padx=20)
        
        self.frames["info"] = f_info

    def show_frame(self, name):
        for frame in self.frames.values():
            frame.pack_forget()
        self.frames[name].pack(fill="both", expand=True)

    # ==========================================
    # БЛОК РАБОТЫ С ГРАФИКАМИ И МОНИТОРИНГОМ
    # ==========================================
    
    def setup_resource_graph(self, parent_frame):
        # Хранилище для последних 50 точек данных (очередь)
        self.data_history = collections.deque([0]*50, maxlen=50)
        
        # Создаем фигуру Matplotlib
        self.fig, self.ax = plt.subplots(figsize=(5, 3), dpi=100)
        self.fig.patch.set_facecolor('#2b2b2b') # Цвет под темную тему
        self.ax.set_facecolor('#1a1a1a')
        
        # Настройка осей
        self.line, = self.ax.plot(self.data_history, color='#1f538d', linewidth=2)
        self.ax.set_ylim(0, 100)
        self.ax.get_xaxis().set_visible(False) # Скрываем X
        self.ax.tick_params(axis='y', colors='white')
        
        # Интеграция графика в Tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, master=parent_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
        
        # Запуск цикла обновления
        self.update_live_graph()
        
    def update_live_graph(self):
        try:
            # Получаем нагрузку CPU
            cpu_usage = psutil.cpu_percent()
            self.data_history.append(cpu_usage)
            
            # Обновляем данные линии и перерисовываем холст
            self.line.set_ydata(np.array(self.data_history))
            self.canvas.draw_idle() 
            
            # Планируем следующий запуск (1000 мс = 1 секунда)
            self.after(1000, self.update_live_graph)
            
        except Exception as e:
            print(f"Ошибка обновления графика: {e}")

    # ==========================================
    # БЛОК ВСПОМОГАТЕЛЬНЫХ ФУНКЦИЙ
    # ==========================================

    def get_gpu_info(self):
        try:
            # Получаем модель видеокарты
            gpu_model = subprocess.check_output("lspci | grep -E 'VGA|3D'", shell=True).decode()
            gpu_name = gpu_model.split(':')[-1].strip()
            
            # Получаем версию OpenGL и драйвера через glxinfo
            gl_info = subprocess.check_output("glxinfo | grep -E 'OpenGL version string|OpenGL vendor string'", shell=True).decode()
            
            return {
                "gpu": gpu_name,
                "info": gl_info.strip()
            }
        except:
            return {"gpu": "Не определено", "info": "Установите mesa-utils"}
    
    def update_stats(self):
        cpu_load = psutil.cpu_percent()
        self.load_label.configure(text=f"Загрузка CPU: {cpu_load}%")
        self.after(1000, self.update_stats)

    def update_processes(self):
        try:
            output = subprocess.check_output("lsof /dev/dri/renderD128 2>/dev/null | awk '{print $1}' | sort -u", shell=True).decode()
            self.proc_box.delete("0.0", "end")
            self.proc_box.insert("0.0", "Приложения на GPU:\n" + (output if output else "Никого нет"))
        except:
            self.proc_box.insert("0.0", "Установите lsof: sudo apt install lsof")

if __name__ == "__main__":
    app = App()
    app.mainloop()