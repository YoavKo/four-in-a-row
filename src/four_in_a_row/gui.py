from __future__ import annotations

import tkinter as tk
from typing import TYPE_CHECKING

from .config import (
    BAFER_WIDTH,
    CHECKER_DIAMETER,
    COLUMN_COLOR,
    EMPTY_CELL,
    EMPTY_CELL_COLOR,
    HOVER_COLOR,
    NUM_OF_COLUMNS,
    NUM_OF_ROWS,
    PLAYERS_COLORS,
    WIN_PLAYERS_COLORS,
)

if TYPE_CHECKING:
    from .game import Game


class Column:
    """handles all the graphical presesntation and events in a column"""

    def __init__(self, perent: tk.Misc, game: Game, board: Board, col_num: int) -> None:
        self.board = board
        self.game = game
        self.col_num = col_num
        self.checkers = [EMPTY_CELL for _ in range(NUM_OF_ROWS)]
        __height = NUM_OF_ROWS * CHECKER_DIAMETER + (NUM_OF_ROWS + 1) * BAFER_WIDTH
        __width = CHECKER_DIAMETER + BAFER_WIDTH * 2
        self.can = tk.Canvas(perent, width=__width, height=__height, bg=COLUMN_COLOR)
        self.can.bind("<Button-1>", self.on_mouse_left_clicked)
        self.can.bind("<Enter>", self.on_mouse_enter_hover)
        self.can.bind("<Leave>", self.on_mouse_leave_hover)

    def draw_checker(self, row: int, color: str) -> None:
        """draws a single checker in the this instance of a column, in the
        given row and color"""
        pos_y1 = row * CHECKER_DIAMETER + (row + 1) * BAFER_WIDTH
        pos_x1 = BAFER_WIDTH
        pos_y2 = pos_y1 + CHECKER_DIAMETER
        pos_x2 = pos_x1 + CHECKER_DIAMETER
        self.can.create_oval(pos_x1, pos_y1, pos_x2, pos_y2, fill=color)

    def draw_column(self) -> None:
        """draws the skeloten of the column"""
        self.can.grid(column=self.col_num, row=0)
        for row in range(NUM_OF_ROWS):
            self.draw_checker(row, EMPTY_CELL_COLOR)

    def emtpy_cells(self) -> list[int]:
        """returns a list of all empty cells' row coordinate in the column"""
        return [i for i, v in enumerate(self.checkers) if v == EMPTY_CELL]

    def add_checker(self, row: int, player: int) -> None:
        """adds a checker to the column checker list and draws it"""
        self.checkers[row] = player
        self.draw_checker(row, PLAYERS_COLORS[player])

    def on_mouse_left_clicked(self, _event: tk.Event[tk.Canvas]) -> None:
        """handle mouse left event- if able make move and present it"""
        if self.game.can_move_locally() and EMPTY_CELL in self.checkers:
            row = max(self.emtpy_cells())
            cell = ",".join([str(i) for i in (row, self.col_num)])
            self.game.handle_move_event(cell)

    def on_mouse_enter_hover(self, _event: tk.Event[tk.Canvas]) -> None:
        """handle mouse entering column event - fills the empty cells in the
        column with the players' hover color"""
        if self.game.can_move_locally():
            for cell in self.emtpy_cells():
                self.draw_checker(cell, HOVER_COLOR[self.game.current_player])

    def on_mouse_leave_hover(self, _event: tk.Event[tk.Canvas]) -> None:
        """handle mouse leaving column event - cleans the column by filling
        the empty cells in the column with the empty-cell color"""
        for cell in self.emtpy_cells():
            self.draw_checker(cell, EMPTY_CELL_COLOR)


class Board:
    """contains a list of columns and handles them, gets tkinter root as a
    parent and an instance of the Game class"""

    def __init__(self, parent: tk.Misc, game: Game) -> None:
        self.columns = [Column(parent, game, self, i) for i in range(NUM_OF_COLUMNS)]
        self.game = game

    def draw_board(self) -> None:
        """initializes the board by drawing empty columns for every column in
        the list"""
        for col in self.columns:
            col.draw_column()

    def mark_wining_seq(self, win_seq: list[tuple[int, int]] | None) -> None:
        """marks the sequence of checkers that caused the winning"""
        if win_seq and self.game.winner is not None:
            win_color = WIN_PLAYERS_COLORS[self.game.winner]
            for row, column in win_seq:
                self.columns[column].draw_checker(row, win_color)


class GUI:
    """contains all the GUI widgits, gets an instance of Game"""

    def __init__(
        self,
        game: Game,
        root: tk.Tk | None = None,
        parent: tk.Misc | None = None,
    ) -> None:
        self.game = game
        self.root = root or tk.Tk()
        self.board = Board(parent or self.root, game)
