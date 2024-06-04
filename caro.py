import copy
import random
import numpy as np
import tkinter as tk
from tkinter import messagebox

# --- Constants ---
DEFAULT_WIDTH = 700     #Chiều rộng
DEFAULT_HEIGHT = 700    #Chiều cao

BG_COLOR = "#F5F5DC" # Beige background color
LINE_COLOR = "#8B4513" # Dark Brown line color
CIRC_COLOR = "#006400" # Dark Green circle (O) color
CROSS_COLOR = "#8B0000" # Dark Red cross (X) color

# Bảng caro
class Board:
    def __init__(self, size):
        self.size = size
        self.squares = np.zeros((size, size))  # Tạo bảng kích thước size x size với các ô giá trị 0
        self.marked_sqrs = 0  # Số ô đã được đánh dấu
        self.max_item_win = 5 if size > 5 else 3  # Số lượng ký hiệu cần để thắng (5 cho bàn lớn hơn 5x5, 3 cho bàn nhỏ)

    def final_state(self, marked_row, marked_col):
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]  # Các hướng kiểm tra (dọc, ngang, chéo phải, chéo trái)
        for dr, dc in directions:
            count = 0
            for delta in range(-self.max_item_win + 1, self.max_item_win):
                r = marked_row + delta * dr
                c = marked_col + delta * dc
                if 0 <= r < self.size and 0 <= c < self.size:
                    if self.squares[r][c] == self.squares[marked_row][marked_col]:
                        count += 1
                        if count == self.max_item_win:
                            return self.squares[marked_row][marked_col] 
                    else:
                        count = 0
        return 0

    def mark_sqr(self, row, col, player):
         # Đánh dấu ô với giá trị của người chơi
        self.squares[row][col] = player
        self.marked_sqrs += 1

    def empty_sqr(self, row, col):
        # Kiểm tra ô trống
        return self.squares[row][col] == 0

    def get_empty_sqrs(self):
        # Lấy danh sách các ô trống
        return [(r, c) for r in range(self.size) for c in range(self.size) if self.empty_sqr(r, c)]

    def is_full(self):
        # Kiểm tra xem bảng có đầy đủ chưa
        return self.marked_sqrs == self.size * self.size
    
#Artificial Intelligence
class AI:
    def __init__(self, player=2):
        self.player = player # Người chơi mà AI sẽ đóng vai

    def rnd(self, board):
        # Chọn ngẫu nhiên một ô trống
        empty_sqrs = board.get_empty_sqrs()
        return random.choice(empty_sqrs)
    
    #Minimax algorithm with Alpha–beta pruning
    def minimax(self, board, depth, alpha, beta, maximizing):
        if depth == 0 or board.is_full():
            return self.evaluate_board(board), None

        best_move = None
        if maximizing:
            max_eval = -float('inf')
            empty_sqrs = board.get_empty_sqrs()
            for (row, col) in empty_sqrs:
                temp_board = copy.deepcopy(board)
                temp_board.mark_sqr(row, col, 1)
                eval, _ = self.minimax(temp_board, depth - 1, alpha, beta, False)
                if eval > max_eval:
                    max_eval = eval
                    best_move = (row, col)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval, best_move
        else:
            min_eval = float('inf')
            empty_sqrs = board.get_empty_sqrs()
            for (row, col) in empty_sqrs:
                temp_board = copy.deepcopy(board)
                temp_board.mark_sqr(row, col, self.player)
                eval, _ = self.minimax(temp_board, depth - 1, alpha, beta, True)
                if eval < min_eval:
                    min_eval = eval
                    best_move = (row, col)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval, best_move

    def evaluate_position(self, board, row, col, player):
         # Đánh vị trí bảng
        score = 0
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        for dr, dc in directions:
            count = 0
            for delta in range(-3, 1):
                r = row + delta * dr
                c = col + delta * dc
                if 0 <= r < board.size and 0 <= c < board.size:
                    if board.squares[r][c] == player:
                        count += 1
                    elif board.squares[r][c] != 0:
                        count = 0
                        break
                else:
                    count = 0
                    break
            score += count
        return score

    def evaluate_board(self, board):
        #Đánh toàn bộ bảng
        score = 0
        for row in range(board.size):
            for col in range(board.size):
                if board.squares[row][col] == 1:
                    score += self.evaluate_position(board, row, col, 1)
                else:
                    score -= self.evaluate_position(board, row, col, 2)
        return score

    def eval(self, main_board):
        #Điều chỉnh kích thước 
        if main_board.size == 5:
            depth = 3
        elif main_board.size == 7:
            depth = 2
        else:
            depth = 1

        eval_value, move = self.minimax(main_board, depth, -float('inf'), float('inf'), True)
        
        return move

class Game(tk.Tk):
    def __init__(self, size=5, gamemode='ai'):
        super().__init__()
        self.title("CARO CỔ ĐIỂN")
        self.geometry(f"{DEFAULT_WIDTH}x{DEFAULT_HEIGHT + 100}")  # Increase height to accommodate buttons
        self.canvas = tk.Canvas(self, width=DEFAULT_WIDTH, height=DEFAULT_HEIGHT, bg=BG_COLOR)
        self.canvas.pack()

        self.size = size
        self.sqsize = DEFAULT_WIDTH // self.size  # Kích thước mỗi ô vuông trên bảng
        self.radius = self.sqsize // 4 # Bán kính của dấu tròn (O)
        self.offset = self.sqsize // 4  # Khoảng cách bù trừ cho việc vẽ dấu
        self.line_width = self.offset // 2 # Độ dày của các đường kẻ
        self.circ_width = self.offset // 2  # Độ dày của đường kẻ dấu tròn (O)
        self.cross_width = self.offset // 2 # Độ dày của đường kẻ dấu chéo (X)

        self.board = Board(self.size) # Tạo bảng chơi với kích thước được chỉ định
        self.ai = AI() # Tạo đối tượng AI
        self.player = 1 # Người chơi bắt đầu
        self.gamemode = gamemode # Chế độ chơi (Player vs Player or Player vs A.I)
        self.running = True # Trạng thái trò chơi đang chạy
        self.ai_thinking = False  # Trạng thái AI đang suy nghĩ
        self.show_lines() # Hiển thị các đường kẻ trên bảng
        self.canvas.bind("<Button-1>", self.handle_click) # Ràng buộc sự kiện click chuột trên canvas

        # Reset button and Back button
        self.reset_button = tk.Button(self, text="Chơi lại", command=self.reset, font=("Times New Roman", 16, "bold"), padx=20, pady=10)
        self.reset_button.pack(side=tk.LEFT, padx=20, pady=20)

        self.back_button = tk.Button(self, text="Trở về", command=self.back, font=("Times New Roman", 16, "bold"), padx=20, pady=10)
        self.back_button.pack(side=tk.RIGHT, padx=20, pady=20)

    def show_lines(self):
        # Hiển thị các đường kẻ trên bảng
        self.canvas.delete("all")
        for col in range(1, self.size):
            x = col * self.sqsize
            self.canvas.create_line(x, 0, x, DEFAULT_HEIGHT, fill=LINE_COLOR, width=self.line_width)
        for row in range(1, self.size):
            y = row * self.sqsize
            self.canvas.create_line(0, y, DEFAULT_WIDTH, y, fill=LINE_COLOR, width=self.line_width)

    def draw_fig(self, row, col):
        # Vẽ ký hiệu X hoặc O
        if self.board.squares[row][col] == 1:
            start_desc = (col * self.sqsize + self.offset, row * self.sqsize + self.offset)
            end_desc = (col * self.sqsize + self.sqsize - self.offset, row * self.sqsize + self.sqsize - self.offset)
            self.canvas.create_line(*start_desc, *end_desc, fill=CROSS_COLOR, width=self.cross_width)

            start_asc = (col * self.sqsize + self.offset, row * self.sqsize + self.sqsize - self.offset)
            end_asc = (col * self.sqsize + self.sqsize - self.offset, row * self.sqsize + self.offset)
            self.canvas.create_line(*start_asc, *end_asc, fill=CROSS_COLOR, width=self.cross_width)
        elif self.board.squares[row][col] == 2:
            center = (col * self.sqsize + self.sqsize // 2, row * self.sqsize + self.sqsize // 2)
            self.canvas.create_oval(center[0] - self.radius, center[1] - self.radius,
                                    center[0] + self.radius, center[1] + self.radius,
                                    outline=CIRC_COLOR, width=self.circ_width)

    def make_move(self, row, col):
        self.board.mark_sqr(row, col, self.player)
        self.draw_fig(row, col)
        self.next_turn()

    def next_turn(self):
        # Chuyển lượt chơi
        self.player = self.player % 2 + 1

    def is_over(self, row, col):
        # Kiểm tra trò chơi kết thúc hay chưa
        result = self.board.final_state(row, col)
        if result != 0:
            winner = "Người chơi 1" if result == 1 else "Người chơi 2"
            messagebox.showinfo("Kết quả", f"{winner} đã thắng")
            return True
        elif self.board.is_full():
            messagebox.showinfo("Kết quả", "Hòa")
            return True
        return False

    def handle_click(self, event):
        #Xử lý sự kiện click chuột
        if not self.running or self.ai_thinking:
            return
        col = event.x // self.sqsize
        row = event.y // self.sqsize
        if self.board.empty_sqr(row, col):
            self.make_move(row, col)
            if self.is_over(row, col):
                self.running = False
            elif self.gamemode == 'ai' and self.running and self.player == 2:
                self.ai_thinking = True
                self.after(500, self.ai_move)

    def ai_move(self):
        if self.running and self.player == 2:
            row, col = self.ai.eval(self.board)
            self.make_move(row, col)
            if self.is_over(row, col):
                self.running = False
        self.ai_thinking = False

    def reset(self):
        self.board = Board(self.size)
        self.player = 1
        self.running = True
        self.ai_thinking = False
        self.show_lines()

    def back(self):
        self.destroy()
        import caro_menu  # Quay lại form menu
        root = tk.Tk()
        caro_menu.CaroUI(root)
        root.mainloop()

if __name__ == '__main__':
    game = Game()
    game.mainloop()
