import customtkinter as ctk
import os

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("OpenGL Settings Manager")
        self.geometry("500x400")
        ctk.set_appearance_mode("dark")

        # Заголовок
        self.label = ctk.CTkLabel(self, text="Управление OpenGL", font=("Arial", 24, "bold"))
        self.label.pack(pady=20)

        # Кнопка: Проверить версию
        self.btn_info = ctk.CTkButton(self, text="Проверить версию OpenGL", command=self.check_opengl)
        self.btn_info.pack(pady=10)

        # Кнопка: Установить драйверы
        self.btn_install = ctk.CTkButton(self, text="Установить/Обновить Mesa Dev", fg_color="green", command=self.install_drivers)
        self.btn_install.pack(pady=10)

        # Поле вывода логов
        self.textbox = ctk.CTkTextbox(self, width=400, height=150)
        self.textbox.pack(pady=20)

    def check_opengl(self):
        # Команда glxinfo требует пакет mesa-utils
        info = os.popen("glxinfo | grep 'OpenGL version'").read()
        self.textbox.insert("0.0", info if info else "Ошибка: установите mesa-utils\n")

    def install_drivers(self):
        self.textbox.insert("0.0", "Запуск обновления драйверов...\n")
        # В реальном приложении здесь был бы вызов через sudo
        self.textbox.insert("0.0", "Используйте: sudo apt install --reinstall libgl1-mesa-glx\n")

if __name__ == "__main__":
    app = App()
    app.mainloop()