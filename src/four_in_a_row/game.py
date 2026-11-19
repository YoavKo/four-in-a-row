from .config import ILLEGAL_MOVE_MSG
from .board import Board
from tkinter import messagebox
from .i18n import t, raw


def illegal_move_error():
    """raises an illegal move exception"""
    raise Exception(ILLEGAL_MOVE_MSG)


class Game:
    """main backend game logic handler"""

    PLAYER_ONE = 0
    PLAYER_TWO = 1
    DRAW = 2

    def __init__(self, mode, player_type, kind="network"):
        # kind: 'network' (two machines), 'hotseat' (2 humans, one screen),
        #       'vs_ai' (human is PLAYER_ONE, computer is PLAYER_TWO)
        self.kind = kind
        self.ai_player = None
        self.root = None
        self.on_update = None
        self.closed = False
        self.board = Board()
        self.last_move = None
        self.current_player = self.PLAYER_ONE
        self.is_game_over = False
        self.winner = None
        self.winning_seq_coords = None
        self.mode = None
        self.player = self.PLAYER_ONE if mode == "server" else self.PLAYER_TWO
        self.communicator = None
        self.gui = None
        self.player_type = player_type
        self.ai = None

    def update_game(self, last_move_cell):
        """updates the last_move attribute, checks if the game is over, and
        toggles players"""
        self.last_move = (last_move_cell, self.current_player)
        self.check_if_game_over()

    def if_move_legal_find_vacant_cell_row(self, column):
        """
        checks if any move can be made (if the game is not over)
        and then if the specific given move can be made.
        returns False if the move is illegal or not possible, otherwise
        the row of the desired vacant cell
        """

        if self.is_game_over:
            return False

        row = self.board.find_vacant_cell(column)
        # if the move is possible this is the row index value, otherwise False
        return row

    def make_move(self, column):
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

    def get_winner(self):
        """returns the values of: self.PLAYER_ONE, self.PLAYER_TWO,
        or self.DRAW if the game is over, otherwise None"""
        return self.winner

    def get_player_at(self, row, col):
        """returns the player value (self.PLAYER_ONE or self.PLAYER_TWO) which owns
        the checker at the given location, or None if no player owns it"""
        return self.board.get_checker(row, col)

    def get_current_player(self):
        """returns the current player"""
        return self.current_player

    def toggle_player(self):
        """toggles between players, gets called after a move"""
        pl1, pl2 = self.PLAYER_ONE, self.PLAYER_TWO
        is_current_player_pl2 = self.current_player == self.PLAYER_TWO
        self.current_player = pl1 if is_current_player_pl2 else pl2

    def check_if_game_over(self):
        """checks whether the game is over, either by a draw or by one winner"""
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
    def brack_cell_msg(cell):
        """splits standard coordinate msg to row, col int tuple"""
        if cell.count(",") > 1:
            # ugly hotfix debug, we didn't have enough time to fix it properly
            cell = cell[-3:]
        row, col = cell.split(",")
        return int(row), int(col)

    def can_move_locally(self):
        """True if a local mouse click may currently place a checker"""
        if self.is_game_over or self.closed:
            return False
        if self.kind == "hotseat":
            return True
        if self.kind == "vs_ai":
            return self.current_player == self.PLAYER_ONE
        return self.player == self.current_player

    def end_message(self):
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

    def handle_message(self, msg):
        """handles a raw message from the other machine: either who goes
        first ("first:<player>") or a move ("row,col")"""
        if msg.startswith("first:"):
            self.current_player = int(msg[6:])
            if self.on_update:
                self.on_update()
        else:
            self.handle_move_event(msg, True)

    def _ai_move(self):
        if (
            not self.closed
            and not self.is_game_over
            and self.current_player == self.ai_player
        ):
            self.ai.find_legal_move(self, self.handle_move_event)

    def handle_move_event(self, a_cell, remote=False):
        """general move operator. updates game data, GUI and communicator
        the commands come from one of the following: GUI, ai, or communicator"""
        if self.closed:
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

            elif self.kind == "vs_ai" and self.current_player == self.ai_player:
                self.root.after(400, self._ai_move)

            elif (
                self.kind == "network"
                and self.player_type == "ai"
                and not self.player == self.last_move[1]
            ):
                self.ai.find_legal_move(self, self.handle_move_event)
