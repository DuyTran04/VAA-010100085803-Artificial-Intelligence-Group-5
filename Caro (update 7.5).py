import copy
import random
import numpy as np
import tkinter as tk
from tkinter import messagebox

# --- Constants ---
DEFAULT_WIDTH = 700     # Chiều rộng của cửa sổ ứng dụng
DEFAULT_HEIGHT = 700    # Chiều cao của cửa sổ ứng dụng

BG_COLOR = "#F5F5DC"    # Beige background color
LINE_COLOR = "#8B4513"  # Dark Brown line color
CIRC_COLOR = "#006400"  # Dark Green circle (O) color
CROSS_COLOR = "#8B0000" # Dark Red cross (X) color

# Bảng caro
class Board:
    def __init__(self, size):
        self.size = size
        self.squares = np.zeros((size, size))  # Tạo bảng kích thước size x size với các ô giá trị 0
        self.marked_sqrs = 0  # Số ô đã được đánh dấu
        self.max_item_win = 3 if size == 5 else 5   # Số lượng ký hiệu cần để thắng (3 cho bàn 5x5, 5 cho các bàn khác)

    # Kiểm tra trạng thái kết thúc (thắng/thua) sau khi đánh một nước
    def final_state(self, marked_row, marked_col):
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]  # Các hướng kiểm tra (dọc, ngang, chéo phải, chéo trái)
        player = self.squares[marked_row][marked_col]  # Player to check for winning condition

        # Kiểm tra các hướng khác nhau để tìm dãy liên tiếp của người chơi
        for dr, dc in directions:
            count = 0 # Khởi tạo biến đếm số ô liên tiếp

            for delta in range(-self.max_item_win + 1, self.max_item_win):  # Duyệt qua khoảng giá trị từ -max_item_win + 1 đến max_item_win
                r = marked_row + delta * dr # Tính toán vị trí dọc
                c = marked_col + delta * dc # Tính toán vị trí ngang
                if 0 <= r < self.size and 0 <= c < self.size: # Kiểm tra vị trí có nằm trong bàn cờ hay không
                    if self.squares[r][c] == player: # Nếu ô tại vị trí đó cùng giá trị với người chơi
                        count += 1 # Tăng biến đếm
                        if count == self.max_item_win: # Nếu số ô liên tiếp đạt giá trị cần thiết để thắng
                            return player # Trả về giá trị người chơi (thắng)
                    else:
                        count = 0  # Nếu không cùng giá trị, đặt lại biến đếm
                else:
                    count = 0 # Nếu vượt ra ngoài bàn cờ, đặt lại biến đếm
        return 0 # Nếu không có người chơi nào thắng, trả về 0

    # Đánh dấu ô tại vị trí `row`, `col` với giá trị `player`
    def mark_sqr(self, row, col, player):
        self.squares[row][col] = player
        self.marked_sqrs += 1

    # Kiểm tra xem ô tại vị trí `row`, `col` có trống hay không
    def empty_sqr(self, row, col):
        return self.squares[row][col] == 0

    # Trả về danh sách các ô trống trên bàn cờ
    def get_empty_sqrs(self):
        return [(r, c) for r in range(self.size) for c in range(self.size) if self.empty_sqr(r, c)]

    # Kiểm tra xem bàn cờ đã đầy hay chưa
    def is_full(self):
        return self.marked_sqrs == self.size * self.size

    # Tính độ dài dây liên tiếp dài nhất của một người chơi trên bàn cờ
    def longest_sequence(self, player):
        longest = 0
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        for row in range(self.size):
            for col in range(self.size):
                if self.squares[row][col] == player:
                    for dr, dc in directions:
                        count = 0
                        for delta in range(-self.max_item_win + 1, self.max_item_win):
                            r = row + delta * dr
                            c = col + delta * dc
                            if 0 <= r < self.size and 0 <= c < self.size and self.squares[r][c] == player:
                                count += 1
                                longest = max(longest, count)
                            else:
                                count = 0
        return longest
        
    
# Artificial Intelligence
# Lớp AI đại diện cho trí tuệ nhân tạo trong trò chơi Caro
class AI:
    def __init__(self, player=2):
        self.player = player
        self.opponent = 1
        
    # Đánh giá tình trạng của bàn cờ từ quan điểm của người chơi
    def evaluate_board(self, board):
        score = 0
        if self.check_win(board, self.player):
            score += 10000
        if self.check_win(board, self.opponent):
            score -= 10000
        for row in range(board.size):
            for col in range(board.size):
                if board.squares[row][col] == self.player:
                    score += self.evaluate_position(board, row, col, self.player)
                elif board.squares[row][col] == self.opponent:
                    score -= self.evaluate_position(board, row, col, self.opponent)
        return score

    # Đánh giá vị trí của một ô trên bàn cờ từ quan điểm của người chơi
    def evaluate_position(self, board, row, col, player):
        score = 0
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        for dr, dc in directions:
            count = 0
            block_count = 0
            for delta in range(-3, 4):
                r = row + delta * dr
                c = col + delta * dc
                if 0 <= r < board.size and 0 <= c < board.size:
                    if board.squares[r][c] == player:
                        count += 1
                    elif board.squares[r][c] != 0:
                        block_count += 1
                        break
                else:
                    block_count += 1
                    break
            if block_count < 2:
                score += count ** 2
        return score
    # Kiểm tra xem người chơi đã thắng hay chưa
    def check_win(self, board, player):
        for row in range(board.size):
            for col in range(board.size):
                if board.squares[row][col] == player:
                    if self.win_condition(board, row, col, player):
                        return True
        return False
    # Kiểm tra xem có thỏa mãn điều kiện thắng hay không
    def win_condition(self, board, row, col, player):
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        for dr, dc in directions:
            count = 0
            for delta in range(-board.max_item_win + 1, board.max_item_win):
                r = row + delta * dr
                c = col + delta * dc
                if 0 <= r < board.size and 0 <= c < board.size:
                    if board.squares[r][c] == player:
                        count += 1
                        if count == board.max_item_win:
                            return True
                    else:
                        count = 0
        return False
    # Thuật toán minimax với cắt tỉa alpha-beta
    def minimax(self, board, depth, alpha, beta, maximizing):
        # Nếu đã đạt độ sâu tìm kiếm hoặc bàn cờ đã đầy, thì hàm sẽ trả về điểm đánh giá của bàn cờ hiện tại và None cho nước đi tiếp theo
        if depth == 0 or board.is_full():
            return self.evaluate_board(board), None

        
        if maximizing:
            max_eval = -float('inf')
            best_move = None
            empty_sqrs = board.get_empty_sqrs()
            random.shuffle(empty_sqrs)

            for (row, col) in empty_sqrs:
                temp_board = copy.deepcopy(board) # Tạo một bản sao sâu (deep copy) của bàn cờ hiện tại là để đảm bảo rằng bất kỳ thay đổi nào được thực hiện trên bàn cờ tạm thời sẽ không ảnh hưởng đến bàn cờ gốc.
                temp_board.mark_sqr(row, col, self.player) # Đánh dấu ô tại vị trí (row, col) với giá trị của AI trên bàn cờ tạm thời.
                eval, _ = self.minimax(temp_board, depth - 1, alpha, beta, False) # Gọi đệ quy minimax với bàn cờ tạm thời, giảm độ sâu xuống 1, và đặt maximizing là False (vì lượt chơi tiếp theo sẽ thuộc về đối thủ). Giá trị trả về là điểm đánh giá eval và nước đi tốt nhất (không cần lưu ở đây).
                if eval > max_eval:
                    max_eval = eval
                    best_move = (row, col)
                alpha = max(alpha, max_eval) # Cập nhật giá trị alpha (giá trị điểm tối đa cho AI).
                if beta <= alpha: #Nếu beta nhỏ hơn hoặc bằng alpha, thực hiện cắt tỉa alpha-beta bằng cách dừng vòng lặp.
                    break 
            return max_eval, best_move

        else:
            min_eval = float('inf')
            best_move = None
            empty_sqrs = board.get_empty_sqrs() #Lấy danh sách các ô trống (empty_sqrs) và trộn ngẫu nhiên.
            random.shuffle(empty_sqrs)

            for (row, col) in empty_sqrs:
                temp_board = copy.deepcopy(board)
                temp_board.mark_sqr(row, col, self.opponent)
                eval, _ = self.minimax(temp_board, depth - 1, alpha, beta, True)
                if eval < min_eval:
                    min_eval = eval
                    best_move = (row, col)
                beta = min(beta, min_eval)
                if beta <= alpha: #Nếu beta nhỏ hơn hoặc bằng alpha, thực hiện cắt tỉa alpha-beta bằng cách dừng vòng lặp.
                    break 
            return min_eval, best_move

    # Đánh giá bàn cờ và trả về nước đi tốt nhất
    def eval(self, main_board):
        depth = 2 if main_board.size > 7 else 3 # Giảm độ sâu tìm kiếm cho bàn cờ lớn hơn 7x7
        empty_sqrs = main_board.get_empty_sqrs()
        random.shuffle(empty_sqrs)
        #update
        max_empty_sqrs = 20  # Giới hạn số lượng ô trống được xét là 20.Nó sẽ giúp giảm thời gian tính toán, đặc biệt là trên bàn cờ lớn.
        empty_sqrs = empty_sqrs[:max_empty_sqrs]

        for row, col in empty_sqrs:
            temp_board = copy.deepcopy(main_board)
            temp_board.mark_sqr(row, col, self.player)
            if temp_board.final_state(row, col) == self.player:
                return (row, col)

        for row, col in empty_sqrs:
            temp_board = copy.deepcopy(main_board)
            temp_board.mark_sqr(row, col, self.opponent)
            if temp_board.final_state(row, col) == self.opponent:
                return (row, col)

        _, best_move = self.minimax(main_board, depth, -float('inf'), float('inf'), True)
        return best_move



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

    # Hiển thị các đường kẻ trên bảng
    def show_lines(self):
        self.canvas.delete("all")
        for col in range(1, self.size):
            x = col * self.sqsize
            self.canvas.create_line(x, 0, x, DEFAULT_HEIGHT, fill=LINE_COLOR, width=self.line_width)
        for row in range(1, self.size):
            y = row * self.sqsize
            self.canvas.create_line(0, y, DEFAULT_WIDTH, y, fill=LINE_COLOR, width=self.line_width)

    # Kiểm tra tính hợp lệ của nước đi (nghĩa là hàm kiểm tra xem nước đi của người chơi/A.I có hợp lệ hay không)
    def is_valid_move(self, row, col):
        if not self.board.empty_sqr(row, col):
            return False

        for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (-1, -1), (1, -1), (-1, 1)]:
            r, c = row + dr, col + dc
        if 0 <= r < self.size and 0 <= c < self.size and self.board.squares[r][c] != 0:
            return True

        return False
    # Vẽ ký hiệu X hoặc O lên bàn cờ
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

    # Thực hiện nước đi
    def make_move(self, row, col):
        self.board.mark_sqr(row, col, self.player)
        self.draw_fig(row, col)
        self.next_turn()

    # Chuyển lượt chơi
    def next_turn(self):
        self.player = self.player % 2 + 1

    def is_over(self, row, col):
        # Kiểm tra trò chơi kết thúc hay chưa
        result = self.board.final_state(row, col)
        if result != 0:
            winner = "Người chơi 1" if result == 1 else "Người chơi 2"
            messagebox.showinfo("Kết quả", f"{winner} đã thắng")
            self.running = False
        elif self.board.is_full():
            messagebox.showinfo("Kết quả", "Hòa")
            self.running = False

    def handle_click(self, event):
        if not self.running or self.ai_thinking:
            return

        col = event.x // self.sqsize
        row = event.y // self.sqsize

        if self.board.empty_sqr(row, col):
            if self.gamemode == 'pvp' or self.player == 1:
                self.make_move(row, col)
            if not self.is_over(row, col):
                if self.gamemode == 'ai' and self.running:
                    self.after(500, self.ai_turn)

    def ai_turn(self):
        self.ai_thinking = True
        move = self.ai.eval(self.board)
        if move:
            self.make_move(*move)
            self.is_over(*move)
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
