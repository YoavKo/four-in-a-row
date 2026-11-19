from __future__ import annotations

from tkinter import messagebox
from typing import TYPE_CHECKING, Callable, NoReturn

from .board import Board
from .config import ILLEGAL_MOVE_MSG
from .i18n import raw, t

if TYPE_CHECKING:
    import tkinter as tk

    from .ai import AI
    from .communicator import Communicator
    from .gui import GUI


class IllegalMoveError(Exception):
    """raised when a move cannot be made"""


def illegal_move_error() -> NoReturn:
    """raises an illegal move exception"""
    raise IllegalMoveError(ILLEGAL_MOVE_MSG)


class Game:
    """main backend game logic handler"""

    PLAYER_ONE = 0
    PLAYER_TWO = 1
    DRAW = 2

    def __init__(self, mode: str, player_type: str, kind: str = "network") -> None:
        # kind is one of: network (two machines), hotseat (2 humans on one
        # screen), vs_ai (human is PLAYER_ONE, computer is PLAYER_TWO)
        self.kind = kind
        self.ai_player: int | None = None
        self.root: tk.Tk | None = None
        self.on_update: Callable[[], None] | None = None
        self.closed = False
        self.board = Board()
        self.last_move: tuple[tuple[int, int], int] | None = None
        self.current_player = self.PLAYER_ONE
        self.is_game_over = False
        self.winner: int | None = None
        self.winning_seq_coords: list[tuple[int, int]] | None = None
        self.mode: str | None = None
        self.player = self.PLAYER_ONE if mode == "server" else self.PLAYER_TWO
        self.communicator: Communicator | None = None
        self.gui: GUI | None = None
        self.player_type = player_type
        self.ai: AI | None = None

    def update_game(self, last_move_cell: tuple[int, int]) -> None:
        """updates the last_move attribute, checks if the game is over, and
        toggles players"""
        self.last_move = (last_move_cell, self.current_player)
        self.check_if_game_over()

    def if_move_legal_find_vacant_cell_row(self, column: int) -> int | bool:
        """
        checks if any move can be made (if the game is not over)
        and then if the specific given move can be made.
        returns False if the move is illegal or not possible, otherwise
        the row of the desired vacant cell
        """

        if self.is_game_over:
            return False

        return self.board.find_vacant_cell(column)
        # if the move is possible this is the row index value, otherwise False

    def make_move(self, column: int) -> None:
        """
        updates the board if possible and then updates the game, otherwise
        raises illegal_move_error
        """
        row = self.if_move_legal_find_vacant_cell_row(column)
        if row is not False:
            # preventing the zero index from being treated as False
            new_cell_location = (row, column)
            self.board.add_checker(new_cell_location, self.current_player)
            self.update_game(new_cell_location)

        else:
            illegal_move_error()

    def get_winner(self) -> int | None:
        """returns the values of: self.PLAYER_ONE, self.PLAYER_TWO,
        or self.DRAW if the game is over, otherwise None"""
        return self.winner

    def get_player_at(self, row: int, col: int) -> int | None:
        """returns the player value (self.PLAYER_ONE or self.PLAYER_TWO) which owns
        the checker at the given location, or None if no player owns it"""
        return self.board.get_checker(row, col)

    def get_current_player(self) -> int:
        """returns the current player"""
        return self.current_player

    def toggle_player(self) -> None:
        """toggles between players, gets called after a move"""
        pl1, pl2 = self.PLAYER_ONE, self.PLAYER_TWO
        is_current_player_pl2 = self.current_player == self.PLAYER_TWO
        self.current_player = pl1 if is_current_player_pl2 else pl2

    def check_if_game_over(self) -> bool:
        """checks whether the game is over, either by a draw or by one winner"""
        if self.last_move is None:
            return self.is_game_over
        last_move_cell = self.last_move[0]
        last_player = self.last_move[1]

        win_tuple = self.board.check_if_win(last_move_cell, last_player)
        # win tuple contains a boolean value at location [0] and the winning
        # sequence coordinates at index [1]
        if win_tuple[0]:
            self.winner = last_player
            self.winning_seq_coords = win_tuple[1]
            self.is_game_over = True
        # first checks if there is a win, because the board may be full and
        # with a win

        elif self.board.check_for_a_draw():
            self.winner = self.DRAW
            self.is_game_over = True

        return self.is_game_over

    @staticmethod
    def brack_cell_msg(cell: str) -> tuple[int, int]:
        """splits standard coordinate msg to row, col int tuple"""
        if cell.count(",") > 1:
            # ugly hotfix debug, we didn't have enough time to fix it properly
            cell = cell[-3:]
        row, col = cell.split(",")
        return int(row), int(col)

    def can_move_locally(self) -> bool:
        """True if a local mouse click may currently place a checker"""
        if self.is_game_over or self.closed:
            return False
        if self.kind == "hotseat":
            return True
        if self.kind == "vs_ai":
            return self.current_player == self.PLAYER_ONE
        return self.player == self.current_player

    def end_message(self) -> str:
        """text shown when the game is over"""
        if self.winner == self.DRAW:
            return t("draw")
        if self.kind == "hotseat":
            return t(
                "player_wins", raw("name_blue" if self.winner == 0 else "name_purple")
            )
        if self.kind == "vs_ai":
            return t("you_won" if self.winner == self.PLAYER_ONE else "pc_won")
        return t("you_won" if self.winner == self.player else "opp_won")

    def handle_message(self, msg: str) -> None:
        """handles a raw message from the other machine: either who goes
        first ("first:<player>") or a move ("row,col")"""
        if msg.startswith("first:"):
            self.current_player = int(msg[6:])
            if self.on_update:
                self.on_update()
        else:
            self.handle_move_event(msg, True)

    def ai_move(self) -> None:
        if (
            not self.closed
            and not self.is_game_over
            and self.current_player == self.ai_player
            and self.ai is not None
        ):
            self.ai.find_legal_move(self, self.handle_move_event)

    def handle_move_event(self, a_cell: str, remote: bool = False) -> None:
        """general move operator. updates game data, GUI and communicator
        the commands come from one of the following: GUI, ai, or communicator"""
        if self.closed or self.gui is None:
            return
        row, col = self.brack_cell_msg(a_cell)
        if self.board.is_empty_cell(row, col):
            self.make_move(col)
            self.gui.board.columns[col].add_checker(row, self.current_player)
            if self.communicator and not remote:
                self.communicator.send_message(a_cell)
            self.toggle_player()
            if self.on_update:
                self.on_update()

            if self.is_game_over:
                if self.winner != self.DRAW:
                    self.gui.board.mark_wining_seq(self.winning_seq_coords)
                messagebox.showinfo(raw("end_title"), self.end_message())

            elif (
                self.kind == "vs_ai"
                and self.current_player == self.ai_player
                and self.root is not None
            ):
                self.root.after(400, self.ai_move)

            elif (
                self.kind == "network"
                and self.player_type == "ai"
                and self.ai is not None
                and self.last_move is not None
                and self.player != self.last_move[1]
            ):
                self.ai.find_legal_move(self, self.handle_move_event)
