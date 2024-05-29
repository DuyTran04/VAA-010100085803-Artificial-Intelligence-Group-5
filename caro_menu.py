import tkinter as tk
from tkinter import font as tkfont
from caro import Game

class CaroUI:
    def __init__(self, root):
        self.root = root
        self.root.title("CARO CỔ ĐIỂN")
        self.root.geometry("500x400") # Đặt kích thước cửa sổ
        
        # Định nghĩa màu sắc
        self.bg_color = "#F5F5DC"  # Beige background color
        self.text_color = "#8B4513"  # SaddleBrown text color
        self.button_color = "#A0522D"  # Sienna button color
        self.button_text_color = "#FFFFFF"  # White text color
        
        self.root.configure(bg=self.bg_color) # Cấu hình màu nền của cửa sổ

        self.custom_font = tkfont.Font(family="Helvetica", size=12, weight="bold") #Font-size tùy chỉnh
        
        # Tiêu đề
        self.label = tk.Label(root, text="CHÀO MỪNG ĐẾN CỜ CARO", font=("Helvetica", 24, "bold"), fg=self.text_color, bg=self.bg_color)
        self.label.pack(pady=20)
        
        # Chọn kích thước bàn cờ
        self.size_label = tk.Label(root, text="Chọn kích thước bàn cờ:", font=self.custom_font, fg=self.text_color, bg=self.bg_color)
        self.size_label.pack(pady=10)
        
        self.size_var = tk.IntVar(value=5)
        self.size_frame = tk.Frame(root, bg=self.bg_color)
        self.size_frame.pack()
        self.size5_radio = tk.Radiobutton(self.size_frame, text="5x5", variable=self.size_var, value=5, font=self.custom_font, fg=self.text_color, bg=self.bg_color, selectcolor=self.bg_color)
        self.size7_radio = tk.Radiobutton(self.size_frame, text="7x7", variable=self.size_var, value=7, font=self.custom_font, fg=self.text_color, bg=self.bg_color, selectcolor=self.bg_color)
        self.size11_radio = tk.Radiobutton(self.size_frame, text="11x11", variable=self.size_var, value=11, font=self.custom_font, fg=self.text_color, bg=self.bg_color, selectcolor=self.bg_color)
        self.size5_radio.pack(side=tk.LEFT, padx=10)
        self.size7_radio.pack(side=tk.LEFT, padx=10)
        self.size11_radio.pack(side=tk.LEFT, padx=10)
        
        # Chọn chế độ chơi
        self.mode_label = tk.Label(root, text="Chọn chế độ chơi", font=self.custom_font, fg=self.text_color, bg=self.bg_color)
        self.mode_label.pack(pady=10)
        self.mode_var = tk.StringVar(value="ai")
        self.mode_frame = tk.Frame(root, bg=self.bg_color)
        self.mode_frame.pack()
        self.pvp_radio = tk.Radiobutton(self.mode_frame, text="Người đấu Người", variable=self.mode_var, value="pvp", font=self.custom_font, fg=self.text_color, bg=self.bg_color, selectcolor=self.bg_color)
        self.ai_radio = tk.Radiobutton(self.mode_frame, text="Người đấu A.I", variable=self.mode_var, value="ai", font=self.custom_font, fg=self.text_color, bg=self.bg_color, selectcolor=self.bg_color)
        self.pvp_radio.pack(side=tk.LEFT, padx=10)
        self.ai_radio.pack(side=tk.LEFT, padx=10)

        # Nút bắt đầu và thoát
        self.start_button = tk.Button(root, text="Bắt đầu chơi", command=self.start_game, font=self.custom_font, fg=self.button_text_color, bg=self.button_color)
        self.start_button.pack(pady=20)
        
        self.exit_button = tk.Button(root, text="Thoát", command=self.exit_game, font=self.custom_font, fg=self.button_text_color, bg=self.button_color)
        self.exit_button.pack(pady=5)

    def start_game(self):
        size = self.size_var.get() 
        mode = self.mode_var.get()
        self.root.destroy()
        game = Game(size=size, gamemode=mode)
        game.mainloop()

    def exit_game(self):
        self.root.destroy() # Đóng cửa sổ hiện tại và thoát ứng dụng
        

if __name__ == "__main__":
    root = tk.Tk()
    ui = CaroUI(root)
    root.mainloop()
