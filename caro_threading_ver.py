import copy
import random
import numpy as np
import tkinter as tk
from tkinter import messagebox
import time
from functools import lru_cache
import threading

# --- Constants ---
DEFAULT_WIDTH = 700
DEFAULT_HEIGHT = 700

BG_COLOR = "#F5F5DC"
LINE_COLOR = "#8B4513"
CIRC_COLOR = "#006400"
CROSS_COLOR = "#8B0000"

class Board:
    def __init__(self, size):
        self.size = size
        self.squares = np.zeros((size, size), dtype=int)
        self.marked_sqrs = 0
        self.max_item_win = 3 if size == 5 else 5

    def final_state(self, marked_row, marked_col):
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        player = self.squares[marked_row][marked_col]

        for dr, dc in directions:
            count = 0
            for delta in range(-self.max_item_win + 1, self.max_item_win):
                r = marked_row + delta * dr
                c = marked_col + delta * dc
                if 0 <= r < self.size and 0 <= c < self.size:
                    if self.squares[r][c] == player:
                        count += 1
                        if count == self.max_item_win:
                            return player
                    else:
                        count = 0
                else:
                    count = 0
        return 0

    def mark_sqr(self, row, col, player):
        self.squares[row][col] = player
        self.marked_sqrs += 1

    def empty_sqr(self, row, col):
        return self.squares[row][col] == 0

    def get_empty_sqrs(self):
        return [(r, c) for r in range(self.size) for c in range(self.size) if self.empty_sqr(r, c)]

    def is_full(self):
        return self.marked_sqrs == self.size * self.size

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
        self.opponent = 3 - player
        self.max_time = 5  # Time limit for thinking (seconds)
        self.evaluate_board = lru_cache(maxsize=10000)(self.evaluate_board)
        self.transposition_table = {}
        self.opening_book = {
            (5, 5): [(2, 2), (2, 3), (3, 2), (3, 3)],  # Center and adjacent moves
            (7, 7): [(3, 3), (3, 4), (4, 3), (4, 4)]   # Center and adjacent moves
        }

    def eval(self, main_board):
        start_time = time.time()
        
        # Check opening book
        if main_board.marked_sqrs < 2 and (main_board.size, main_board.size) in self.opening_book:
            return random.choice(self.opening_book[(main_board.size, main_board.size)])

        empty_sqrs = main_board.get_empty_sqrs()
        
        # Quick evaluation for early game
        if len(empty_sqrs) > main_board.size * main_board.size - 4:
            return self.quick_eval(main_board, empty_sqrs)

        # Check for immediate winning moves and blocks
        for row, col in empty_sqrs:
            if self.is_winning_move(main_board, row, col, self.player):
                return (row, col)
        for row, col in empty_sqrs:
            if self.is_winning_move(main_board, row, col, self.opponent):
                return (row, col)

        # Check for open threes and other complex threats
        threat_move = self.check_complex_threats(main_board)
        if threat_move:
            return threat_move

        # Use iterative deepening within time limit
        return self.iterative_deepening(main_board, 10, self.max_time - (time.time() - start_time))

    def quick_eval(self, board, empty_sqrs):
        center = board.size // 2
        best_move = None
        best_score = -float('inf')

        for row, col in empty_sqrs:
            score = -(abs(row - center) + abs(col - center))
            if score > best_score:
                best_score = score
                best_move = (row, col)

        return best_move

    def is_winning_move(self, board, row, col, player):
        temp_board = copy.deepcopy(board)
        temp_board.mark_sqr(row, col, player)
        return temp_board.final_state(row, col) == player

    def check_complex_threats(self, board):
        for row in range(board.size):
            for col in range(board.size):
                if board.empty_sqr(row, col):
                    if self.is_open_three(board, row, col, self.player):
                        return (row, col)
                    if self.is_open_three(board, row, col, self.opponent):
                        return (row, col)
        return None

    def is_open_three(self, board, row, col, player):
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        for dr, dc in directions:
            line = self.get_line(board, row, col, dr, dc)
            if self.is_open_three_pattern(line, player):
                return True
        return False

    def is_open_three_pattern(self, line, player):
        pattern = [0, player, player, player, 0]
        return pattern in [line[i:i+5] for i in range(len(line)-4)]

    def get_line(self, board, row, col, dr, dc):
        line = []
        for i in range(-board.max_item_win + 1, board.max_item_win):
            r, c = row + i * dr, col + i * dc
            if 0 <= r < board.size and 0 <= c < board.size:
                line.append(board.squares[r][c])
            else:
                break
        return line

    # Giữ lại các phương thức hiện có từ caro 1.txt
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

    def check_win(self, board, player):
        for row in range(board.size):
            for col in range(board.size):
                if board.squares[row][col] == player:
                    if self.win_condition(board, row, col, player):
                        return True
        return False

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

    #Update đoạn code mới
    def evaluate_sequences(self, board, player):
        score = 0
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        for row in range(board.size):
            for col in range(board.size):
                for dr, dc in directions:
                    score += self.evaluate_direction(board, row, col, dr, dc, player)
        return score

    def evaluate_direction(self, board, row, col, dr, dc, player):
        score = 0
        max_win = board.max_item_win
        line = []
        for i in range(max_win):
            r, c = row + i * dr, col + i * dc
            if 0 <= r < board.size and 0 <= c < board.size:
                line.append(board.squares[r][c])
            else:
                break
        if len(line) >= max_win:
            score += self.score_window(line, player, max_win)
        return score

    def score_window(self, window, player, max_win):
        score = 0
        opponent = 3 - player
        
        player_count = window.count(player)
        opponent_count = window.count(opponent)
        empty_count = window.count(0)
        
        if opponent_count == max_win - 1 and empty_count == 1:
            score -= 2000  # Prioritize blocking opponent's winning move
        elif player_count == max_win - 1 and empty_count == 1:
            score += 1000
        elif opponent_count == max_win - 2 and empty_count == 2:
            score -= 500   # Prioritize blocking opponent's potential threats
        elif player_count == max_win - 2 and empty_count == 2:
            score += 100
        elif player_count > 0 and opponent_count == 0:
            score += 10 * player_count
        elif opponent_count > 0 and player_count == 0:
            score -= 15 * opponent_count
        
        return score

    def evaluate_potential_threats(self, board, player):
        score = 0
        opponent = 3 - player
        for row in range(board.size):
            for col in range(board.size):
                if board.squares[row][col] == 0:
                    score += self.evaluate_future_threat(board, row, col, player)
                    score -= self.evaluate_future_threat(board, row, col, opponent)
        return score

    def evaluate_future_threat(self, board, row, col, player):
        score = 0
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        for dr, dc in directions:
            line = self.get_line(board, row, col, dr, dc)
            score += self.score_potential_threat(line, player, board.max_item_win)
        return score

    def score_potential_threat(self, line, player, max_win):
        score = 0
        opponent = 3 - player
        player_count = line.count(player)
        empty_count = line.count(0)
        
        if player_count == max_win - 2 and empty_count == 2:
            score += 50  # Potential future threat
        elif player_count == max_win - 3 and empty_count == 3:
            score += 10  # Developing threat
        
        return score

    def iterative_deepening(self, board, max_depth, max_time):
        best_move = None
        start_time = time.time()
        for depth in range(1, max_depth + 1):
            if time.time() - start_time > max_time:
                break
            score, move = self.minimax(board, depth, -float('inf'), float('inf'), True, start_time)
            if move:
                best_move = move
        return best_move

    def minimax(self, board, depth, alpha, beta, maximizing, start_time):
        if depth == 0 or board.is_full() or time.time() - start_time > self.max_time:
            return self.evaluate_board(board), None

        empty_sqrs = board.get_empty_sqrs()
        empty_sqrs.sort(key=lambda move: self.move_ordering_score(board, move[0], move[1]), reverse=maximizing)

        if maximizing:
            max_eval = -float('inf')
            best_move = None
            for (row, col) in empty_sqrs:
                temp_board = copy.deepcopy(board)
                temp_board.mark_sqr(row, col, self.player)
                eval, _ = self.minimax(temp_board, depth - 1, alpha, beta, False, start_time)
                if eval > max_eval:
                    max_eval = eval
                    best_move = (row, col)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval, best_move
        else:
            min_eval = float('inf')
            best_move = None
            for (row, col) in empty_sqrs:
                temp_board = copy.deepcopy(board)
                temp_board.mark_sqr(row, col, self.opponent)
                eval, _ = self.minimax(temp_board, depth - 1, alpha, beta, True, start_time)
                if eval < min_eval:
                    min_eval = eval
                    best_move = (row, col)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval, best_move

    def move_ordering_score(self, board, row, col):
        score = 0
        center = board.size // 2
        score += 10 - (abs(row - center) + abs(col - center))
        
        # Prioritize moves that form or block potential threats
        temp_board = copy.deepcopy(board)
        temp_board.mark_sqr(row, col, self.player)
        score += self.evaluate_potential_threats(temp_board, self.player)
        
        temp_board = copy.deepcopy(board)
        temp_board.mark_sqr(row, col, self.opponent)
        score += self.evaluate_potential_threats(temp_board, self.opponent)
        
        return score

class Game(tk.Tk):
    def __init__(self, size=5, gamemode='ai'):
        super().__init__()
        self.title("CARO CỔ ĐIỂN")
        self.geometry(f"{DEFAULT_WIDTH}x{DEFAULT_HEIGHT + 100}")
        self.canvas = tk.Canvas(self, width=DEFAULT_WIDTH, height=DEFAULT_HEIGHT, bg=BG_COLOR)
        self.canvas.pack()

        self.size = size
        self.sqsize = DEFAULT_WIDTH // self.size
        self.radius = self.sqsize // 4
        self.offset = self.sqsize // 4
        self.line_width = self.offset // 2
        self.circ_width = self.offset // 2
        self.cross_width = self.offset // 2

        self.board = Board(self.size)
        self.ai = AI()
        self.player = 1
        self.gamemode = gamemode
        self.running = True
        self.ai_thinking = False
        self.show_lines()
        self.canvas.bind("<Button-1>", self.handle_click)

        self.reset_button = tk.Button(self, text="Chơi lại", command=self.reset, font=("Times New Roman", 16, "bold"), padx=20, pady=10)
        self.reset_button.pack(side=tk.LEFT, padx=20, pady=20)

        self.back_button = tk.Button(self, text="Trở về", command=self.back, font=("Times New Roman", 16, "bold"), padx=20, pady=10)
        self.back_button.pack(side=tk.RIGHT, padx=20, pady=20)

        self.status_label = tk.Label(self, text="", font=("Times New Roman", 14))
        self.status_label.pack(pady=10)

    def show_lines(self):
        self.canvas.delete("all")
        for col in range(1, self.size):
            x = col * self.sqsize
            self.canvas.create_line(x, 0, x, DEFAULT_HEIGHT, fill=LINE_COLOR, width=self.line_width)
        for row in range(1, self.size):
            y = row * self.sqsize
            self.canvas.create_line(0, y, DEFAULT_WIDTH, y, fill=LINE_COLOR, width=self.line_width)

    def draw_fig(self, row, col):
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
        if self.board.empty_sqr(row, col):
            self.board.mark_sqr(row, col, self.player)
            self.draw_fig(row, col)
            self.next_turn()
            return True
        return False

    def next_turn(self):
        self.player = self.player % 2 + 1
        self.status_label.config(text=f"Lượt của Người chơi {self.player}")

    def is_over(self, row, col):
        result = self.board.final_state(row, col)
        if result != 0:
            winner = "Người chơi 1" if result == 1 else "Người chơi 2"
            messagebox.showinfo("Kết quả", f"{winner} đã thắng")
            self.running = False
            self.status_label.config(text=f"{winner} đã thắng")
        elif self.board.is_full():
            messagebox.showinfo("Kết quả", "Hòa")
            self.running = False
            self.status_label.config(text="Hòa")

    def handle_click(self, event):
        if not self.running or self.ai_thinking:
            return

        col = event.x // self.sqsize
        row = event.y // self.sqsize

        if self.board.empty_sqr(row, col):
            if self.gamemode == 'pvp' or self.player == 1:
                if self.make_move(row, col):
                    if not self.is_over(row, col):
                        if self.gamemode == 'ai' and self.running:
                            self.status_label.config(text="AI đang suy nghĩ...")
                            self.after(100, self.ai_turn)
        else:
            self.status_label.config(text="Ô này đã được đánh!")

    def ai_turn(self):
        self.ai_thinking = True
        
        def ai_move():
            move = self.ai.eval(self.board)
            if move:
                self.after(0, lambda: self.make_ai_move(move))
            else:
                self.after(0, self.handle_ai_no_move)

        threading.Timer(0.5, ai_move).start()

    def make_ai_move(self, move):
        row, col = move
        self.make_move(row, col)
        self.is_over(row, col)
        self.ai_thinking = False
        self.status_label.config(text="Lượt của bạn")

    def handle_ai_no_move(self):
        print("AI không tìm được nước đi hợp lệ!")
        empty_sqrs = self.board.get_empty_sqrs()
        if empty_sqrs:
            move = random.choice(empty_sqrs)
            self.make_ai_move(move)
        else:
            self.status_label.config(text="Hòa - Không còn nước đi!")
            self.running = False
        self.ai_thinking = False

    def reset(self):
        self.board = Board(self.size)
        self.player = 1
        self.running = True
        self.ai_thinking = False
        self.show_lines()
        self.status_label.config(text="Bắt đầu trò chơi mới")

    def back(self):
        self.destroy()
        import caro_menu
        root = tk.Tk()
        caro_menu.CaroUI(root)
        root.mainloop()

    def update(self):
        self.canvas.update()
        self.update_idletasks()

if __name__ == '__main__':
    game = Game()
    game.mainloop()
