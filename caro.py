import copy
import sys
import random
import numpy as np
import tkinter as tk
from tkinter import messagebox

# --- Constants ---
WIDTH = 700
HEIGHT = 700

SIZE_BOARD = 11
ROWS = SIZE_BOARD
COLS = SIZE_BOARD

SQSIZE = WIDTH // COLS
RADIUS = SQSIZE // 4
OFFSET = SQSIZE // 4

LINE_WIDTH = OFFSET // 2
CIRC_WIDTH = OFFSET // 2
CROSS_WIDTH = OFFSET // 2

BG_COLOR = "#1CAAA8"
LINE_COLOR = "#179187"
CIRC_COLOR = "#EFE7C8"
CROSS_COLOR = "#424242"

# --- Class Definitions ---

class Board:
    def __init__(self):
        self.squares = np.zeros((ROWS, COLS))
        self.marked_sqrs = 0
        self.max_item_win = 5

    def final_state(self, marked_row, marked_col):
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]  # vertical, horizontal, main diagonal, anti-diagonal

        for dr, dc in directions:
            count = 0
            for delta in range(-self.max_item_win + 1, self.max_item_win):
                r = marked_row + delta * dr
                c = marked_col + delta * dc

                if 0 <= r < SIZE_BOARD and 0 <= c < SIZE_BOARD:
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

    def get_empty_sqrs(self, row, col):
        empty_sqr = []

        for r in range(row - 2, row + 3):
            for c in range(col - 2, col + 3):
                if 0 <= r < ROWS and 0 <= c < COLS:
                    if self.empty_sqr(r, c):
                        empty_sqr.append((r, c))

        return empty_sqr

    def is_full(self):
        return self.marked_sqrs == ROWS * COLS


class AI:
    def __init__(self, level=1, player=2):
        self.level = level
        self.player = player

    def rnd(self, board):
        empty_sqrs = board.get_empty_sqrs()
        return random.choice(empty_sqrs)

    def alpha_beta(self, r, c, board, alpha, beta, maximizing, depth=3):
        case = board.final_state(r, c)

        if depth == 0 or case != 0 or board.is_full():
            return self.evaluate_board(board), None

        best_move = None
        if maximizing:
            max_eval = -99999
            empty_sqrs = board.get_empty_sqrs(r, c)

            for (row, col) in empty_sqrs:
                temp_board = copy.deepcopy(board)
                temp_board.mark_sqr(row, col, 1)

                eval, _ = self.alpha_beta(row, col, temp_board, alpha, beta, False, depth - 1)
                if eval > max_eval:
                    max_eval = eval
                    best_move = (row, col)

                alpha = max(alpha, eval)
                if alpha >= beta:
                    break
            return max_eval, best_move
        else:
            min_eval = 99999
            empty_sqrs = board.get_empty_sqrs(r, c)

            for (row, col) in empty_sqrs:
                temp_board = copy.deepcopy(board)
                temp_board.mark_sqr(row, col, self.player)

                eval, _ = self.alpha_beta(row, col, temp_board, alpha, beta, True, depth - 1)
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
            for delta in range(-3, 1):  # Check 4 consecutive squares in each direction
                r = row + delta * dr
                c = col + delta * dc

                if 0 <= r < ROWS and 0 <= c < COLS:
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
        for row in range(ROWS):
            for col in range(COLS):
                if board.squares[row][col] == 1:
                    score += self.evaluate_position(board, row, col, 1)
                else:
                    score -= self.evaluate_position(board, row, col, 2)
        return score

    def eval(self, main_board, row, col):
        if self.level == 0:
            eval = 'random'
            move = self.rnd(main_board)
        elif self.level == 1:
            eval, move = self.alpha_beta(row, col, main_board, -99999, 99999, False, 3)

        print(f'AI has chosen to mark the square in pos {move} with an eval of: {eval}')
        return move


class Game(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("TIC TAC TOE AI")
        self.geometry(f"{WIDTH}x{HEIGHT}")

        self.canvas = tk.Canvas(self, width=WIDTH, height=HEIGHT, bg=BG_COLOR)
        self.canvas.pack()

        self.board = Board()
        self.ai = AI()
        self.player = 1
        self.gamemode = 'ai'
        self.running = True
        self.show_lines()

        self.canvas.bind("<Button-1>", self.handle_click)
        self.bind("<Key>", self.handle_keypress)

    def show_lines(self):
        for col in range(1, COLS):
            x = col * SQSIZE
            self.canvas.create_line(x, 0, x, HEIGHT, fill=LINE_COLOR, width=LINE_WIDTH)
        for row in range(1, ROWS):
            y = row * SQSIZE
            self.canvas.create_line(0, y, WIDTH, y, fill=LINE_COLOR, width=LINE_WIDTH)

    def draw_fig(self, row, col):
        if self.player == 1:
            start_desc = (col * SQSIZE + OFFSET, row * SQSIZE + OFFSET)
            end_desc = (col * SQSIZE + SQSIZE - OFFSET, row * SQSIZE + SQSIZE - OFFSET)
            self.canvas.create_line(*start_desc, *end_desc, fill=CROSS_COLOR, width=CROSS_WIDTH)

            start_asc = (col * SQSIZE + OFFSET, row * SQSIZE + SQSIZE - OFFSET)
            end_asc = (col * SQSIZE + SQSIZE - OFFSET, row * SQSIZE + OFFSET)
            self.canvas.create_line(*start_asc, *end_asc, fill=CROSS_COLOR, width=CROSS_WIDTH)
        elif self.player == 2:
            center = (col * SQSIZE + SQSIZE // 2, row * SQSIZE + SQSIZE // 2)
            self.canvas.create_oval(
                center[0] - RADIUS, center[1] - RADIUS,
                center[0] + RADIUS, center[1] + RADIUS,
                outline=CIRC_COLOR, width=CIRC_WIDTH
            )

    def make_move(self, row, col):
        self.board.mark_sqr(row, col, self.player)
        self.draw_fig(row, col)
        self.next_turn()

    def next_turn(self):
        self.player = self.player % 2 + 1

    def change_gamemode(self):
        self.gamemode = 'ai' if self.gamemode == 'pvp' else 'pvp'

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
        self.canvas.delete("all")
        self.__init__()

    def handle_click(self, event):
        if not self.running:
            return

        col = event.x // SQSIZE
        row = event.y // SQSIZE

        if self.board.empty_sqr(row, col):
            self.make_move(row, col)
            if self.is_over(row, col):
                self.running = False

            if self.gamemode == 'ai' and self.player == self.ai.player and self.running:
                row, col = self.ai.eval(self.board, row, col)
                self.make_move(row, col)
                if self.is_over(row, col):
                    self.running = False

    def handle_keypress(self, event):
        if event.char == 'g':
            self.change_gamemode()
        if event.char == 'r':
            self.reset()
        if event.char == '0':
            self.ai.level = 0
        if event.char == '1':
            self.ai.level = 1
        if event.char == '2':
            self.ai.level = 2


if __name__ == '__main__':
    game = Game()
    game.mainloop()
