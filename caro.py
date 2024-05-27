import copy
import random
import numpy as np
import tkinter as tk
from tkinter import messagebox

# --- Constants ---
DEFAULT_WIDTH = 700
DEFAULT_HEIGHT = 700

BG_COLOR = "#1CAAA8"
LINE_COLOR = "#179187"
CIRC_COLOR = "#EFE7C8"
CROSS_COLOR = "#424242"

class Board:
    def __init__(self, size):
        self.size = size
        self.squares = np.zeros((size, size))
        self.marked_sqrs = 0
        self.max_item_win = 5 if size > 5 else 3

    def final_state(self, marked_row, marked_col):
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]  # vertical, horizontal, main diagonal, anti-diagonal
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
        self.squares[row][col] = player
        self.marked_sqrs += 1

    def empty_sqr(self, row, col):
        return self.squares[row][col] == 0

    def get_empty_sqrs(self):
        empty_sqrs = [(r, c) for r in range(self.size) for c in range(self.size) if self.empty_sqr(r, c)]
        return empty_sqrs

    def is_full(self):
        return self.marked_sqrs == self.size * self.size

class AI:
    def __init__(self, level=1, player=2):
        self.level = level
        self.player = player

    def rnd(self, board):
        empty_sqrs = board.get_empty_sqrs()
        return random.choice(empty_sqrs)

    def alpha_beta(self, board, alpha, beta, maximizing, depth=3):
        if depth == 0 or board.is_full():
            return self.evaluate_board(board), None

        best_move = None
        if maximizing:
            max_eval = -99999
            empty_sqrs = board.get_empty_sqrs()

            for (row, col) in empty_sqrs:
                temp_board = copy.deepcopy(board)
                temp_board.mark_sqr(row, col, 1)
                eval, _ = self.alpha_beta(temp_board, alpha, beta, False, depth - 1)
                if eval > max_eval:
                    max_eval = eval
                    best_move = (row, col)
                alpha = max(alpha, eval)
                if alpha >= beta:
                    break
            return max_eval, best_move
        else:
            min_eval = 99999
            empty_sqrs = board.get_empty_sqrs()

            for (row, col) in empty_sqrs:
                temp_board = copy.deepcopy(board)
                temp_board.mark_sqr(row, col, self.player)
                eval, _ = self.alpha_beta(temp_board, alpha, beta, True, depth - 1)
                if eval < min_eval:
                    min_eval = eval
                    best_move = (row, col)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval, best_move

    def evaluate_position(self, board, row, col, player):
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
        score = 0
        for row in range(board.size):
            for col in range(board.size):
                if board.squares[row][col] == 1:
                    score += self.evaluate_position(board, row, col, 1)
                else:
                    score -= self.evaluate_position(board, row, col, 2)
        return score

    def eval(self, main_board):
        if self.level == 0:
            move = self.rnd(main_board)
        else:
            _, move = self.alpha_beta(main_board, -99999, 99999, True, 3)
        return move

class Game(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Classic Caro")
        self.geometry(f"{DEFAULT_WIDTH}x{DEFAULT_HEIGHT}")
        self.canvas = tk.Canvas(self, width=DEFAULT_WIDTH, height=DEFAULT_HEIGHT, bg=BG_COLOR)
        self.canvas.pack()

        self.size = 5
        self.sqsize = DEFAULT_WIDTH // self.size
        self.radius = self.sqsize // 4
        self.offset = self.sqsize // 4
        self.line_width = self.offset // 2
        self.circ_width = self.offset // 2
        self.cross_width = self.offset // 2

        self.board = Board(self.size)
        self.ai = AI()
        self.player = 1
        self.gamemode = 'ai'
        self.running = True
        self.show_lines()
        self.create_menu()
        self.canvas.bind("<Button-1>", self.handle_click)

    def create_menu(self):
        menu_frame = tk.Frame(self)
        menu_frame.pack(side=tk.TOP)

        mode_label = tk.Label(menu_frame, text="Mode:")
        mode_label.pack(side=tk.LEFT)

        self.mode_var = tk.StringVar(value="ai")
        pvp_radio = tk.Radiobutton(menu_frame, text="Player vs Player", variable=self.mode_var, value="pvp", command=self.change_gamemode)
        pvp_radio.pack(side=tk.LEFT)
        ai_radio = tk.Radiobutton(menu_frame, text="Player vs AI", variable=self.mode_var, value="ai", command=self.change_gamemode)
        ai_radio.pack(side=tk.LEFT)

        size_label = tk.Label(menu_frame, text="Board Size:")
        size_label.pack(side=tk.LEFT)

        self.size_var = tk.IntVar(value=5)
        size5_radio = tk.Radiobutton(menu_frame, text="5x5", variable=self.size_var, value=5, command=self.change_size)
        size5_radio.pack(side=tk.LEFT)
        size7_radio = tk.Radiobutton(menu_frame, text="7x7", variable=self.size_var, value=7, command=self.change_size)
        size7_radio.pack(side=tk.LEFT)
        size11_radio = tk.Radiobutton(menu_frame, text="11x11", variable=self.size_var, value=11, command=self.change_size)
        size11_radio.pack(side=tk.LEFT)

        reset_button = tk.Button(menu_frame, text="Reset", command=self.reset)
        reset_button.pack(side=tk.LEFT)

    def change_gamemode(self):
        self.gamemode = self.mode_var.get()

    def change_size(self):
        self.size = self.size_var.get()
        self.sqsize = DEFAULT_WIDTH // self.size
        self.radius = self.sqsize // 4
        self.offset = self.sqsize // 4
        self.line_width = self.offset // 2
        self.circ_width = self.offset // 2
        self.cross_width = self.offset // 2
        self.reset()

    def show_lines(self):
        self.canvas.delete("all")
        for col in range(1, self.size):
            x = col * self.sqsize
            self.canvas.create_line(x, 0, x, DEFAULT_HEIGHT, fill=LINE_COLOR, width=self.line_width)
        for row in range(1, self.size):
            y = row * self.sqsize
            self.canvas.create_line(0, y, DEFAULT_WIDTH, y, fill=LINE_COLOR, width=self.line_width)

    def draw_fig(self, row, col):
        if self.player == 1:
            start_desc = (col * self.sqsize + self.offset, row * self.sqsize + self.offset)
            end_desc = (col * self.sqsize + self.sqsize - self.offset, row * self.sqsize + self.sqsize - self.offset)
            self.canvas.create_line(*start_desc, *end_desc, fill=CROSS_COLOR, width=self.cross_width)

            start_asc = (col * self.sqsize + self.offset, row * self.sqsize + self.sqsize - self.offset)
            end_asc = (col * self.sqsize + self.sqsize - self.offset, row * self.sqsize + self.offset)
            self.canvas.create_line(*start_asc, *end_asc, fill=CROSS_COLOR, width=self.cross_width)
        elif self.player == 2:
            center = (col * self.sqsize + self.sqsize // 2, row * self.sqsize + self.sqsize // 2)
            self.canvas.create_oval(center[0] - self.radius, center[1] - self.radius,
                                    center[0] + self.radius, center[1] + self.radius,
                                    outline=CIRC_COLOR, width=self.circ_width)

    def make_move(self, row, col):
        self.board.mark_sqr(row, col, self.player)
        self.draw_fig(row, col)
        self.next_turn()

    def next_turn(self):
        self.player = self.player % 2 + 1

    def is_over(self, row, col):
        result = self.board.final_state(row, col)
        if result != 0:
            winner = "Player 1" if result == 1 else "Player 2"
            messagebox.showinfo("Game Over", f"{winner} wins!")
            return True
        elif self.board.is_full():
            messagebox.showinfo("Game Over", "It's a draw!")
            return True
        return False

    def reset(self):
        self.board = Board(self.size)
        self.ai = AI()
        self.player = 1
        self.running = True
        self.show_lines()

    def handle_click(self, event):
        col = event.x // self.sqsize
        row = event.y // self.sqsize
        if self.board.empty_sqr(row, col) and self.running:
            self.make_move(row, col)
            if self.is_over(row, col):
                self.running = False
            if self.gamemode == 'ai' and self.player == self.ai.player and self.running:
                row, col = self.ai.eval(self.board)
                self.make_move(row, col)
                if self.is_over(row, col):
                    self.running = False

if __name__ == '__main__':
    game = Game()
    game.mainloop()
