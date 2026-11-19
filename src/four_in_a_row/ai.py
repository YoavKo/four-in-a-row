from __future__ import annotations

from typing import TYPE_CHECKING, Callable, NoReturn

from . import board, config

if TYPE_CHECKING:
    from .game import Game


class NoMovesError(Exception):
    """raised when the AI has no legal move to make"""


# helper functions
def no_moves_error() -> NoReturn:
    """raises the no availible moves exception"""
    raise NoMovesError(config.NO_MOVES_MSG)


class AI:
    """holds AI logic, makes moves when called according to the inner
    algorithms"""

    def find_legal_move(self, g: Game, func: Callable[[str], None]) -> None:
        """finds the best legal move and executes it
        :param g: the given instance of the game
        :param func: the function to be executied with the chosen move
        """
        chosen_move = self.naive_calc_move(g)
        if chosen_move:
            # converting chosen move coordinates to string for data transfer
            # compatibility
            cell = ",".join([str(i) for i in chosen_move])
            func(cell)
        else:
            no_moves_error()

    def naive_calc_move(self, game_obj: Game) -> tuple[int, int] | None:
        """calculates the best next move accordinng to the priorities:
        (1) next move is immediate win
        (2) next move is blocking immediate win for the opponent
        (3) random legal choice
        (1) and (2) are also random choices, if there are more than
        one options"""

        ai_player = (
            game_obj.player if game_obj.ai_player is None else game_obj.ai_player
        )
        is_ai_player_one = ai_player == game_obj.PLAYER_ONE
        pl2, pl1 = game_obj.PLAYER_TWO, game_obj.PLAYER_ONE
        opponent_player = pl2 if is_ai_player_one else pl1
        board_matrix = game_obj.board.get_board()
        temp_board_obj = board.Board(board_matrix)

        all_legal_moves = self.make_legal_move_lst(temp_board_obj, board_matrix)

        # immediate winning moves
        moves = self.cells_near_winning_sequence_suffixes(
            all_legal_moves, board_matrix, ai_player
        )
        if not moves:
            # immediate preventing loss moves
            moves = self.cells_near_winning_sequence_suffixes(
                all_legal_moves, board_matrix, opponent_player
            )
        if not moves:
            moves = all_legal_moves

        return self.random_move(moves)

    def random_move(
        self, list_of_moves: list[tuple[int, int]]
    ) -> tuple[int, int] | None:
        """returns a random choice if the list is not empty otherwise
        returns None"""
        return config.RNG.choice(list_of_moves) if list_of_moves else None

    def make_legal_move_lst(
        self, board_obj: board.Board, board_matrix: list[list[int]]
    ) -> list[tuple[int, int]]:
        """returns a list of all cells that are legal next moves"""

        board_width = len(board_matrix[config.FIRST_ROW_INDEX])
        legal_moves = []
        for column in range(board_width):
            row = board_obj.find_vacant_cell(column)
            if row is not False:
                legal_moves.append((row, column))

        return legal_moves

    def cells_near_winning_sequence_suffixes(
        self,
        legal_moves: list[tuple[int, int]],
        board_matrix: list[list[int]],
        player: int,
    ) -> list[tuple[int, int]]:
        """returns list of cells that are legal next moves that cause an
        immediate win, because they are near winning sequence suffixes"""

        temp_board_obj = board.Board(board_matrix)
        winning_moves = []
        for move_cell in legal_moves:
            row, col = move_cell
            temp_cache = board_matrix[row][col]
            temp_board_obj.add_checker(move_cell, player)
            if temp_board_obj.check_if_win(move_cell, player)[0]:
                winning_moves.append(move_cell)

            # returning the board to the previous setting
            temp_board_obj.add_checker(move_cell, temp_cache)
            # the move counter attribute of the board counts all these moves,
            # but every run of this function is smaller than the maximum amount
            # of moves

        return winning_moves
