import tkinter as tk
from tkinter import ttk
import subprocess
import sys

class CaroGUI:

    def __init__(self, root):
        self.root = root
        self.root.title("Trò chơi Caro")
        self.root.resizable(False, False)
        self.game_process = None

        self.size_frame = ttk.LabelFrame(root, text="Kích thước bàn cờ")
        self.size_frame.grid(row=1, column=0, padx=50, pady=50)

        self.size_var = tk.StringVar()
        self.size_var.set("11x11")

        ttk.Radiobutton(self.size_frame, text="11x11", variable=self.size_var, value="11x11").grid(row=0, column=0, padx=5)

        ttk.Button(root, text="Bắt đầu trò chơi", command=self.start_game).grid(row=2, column=0, padx=10, pady=10)
        ttk.Button(root, text="Tắt", command=self.quit_game).grid(row=3, column=0, padx=10, pady=10)

    def start_game(self):
        selected_size = self.size_var.get()

        if self.game_process is not None:
            self.game_process.terminate()

        if selected_size == "11x11":
            self.game_process = subprocess.Popen(["python", "caro.py"])

    def quit_game(self):
        if self.game_process is not None:
            self.game_process.terminate()
        sys.exit()

if __name__ == "__main__":
    root = tk.Tk()
    app = CaroGUI(root)
    root.mainloop()
