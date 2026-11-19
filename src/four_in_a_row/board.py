import os
from .config import (
    AREA_COEFFECIENT_DICT,
    BOARD_INDEX_DIMENSIONS,
    COLUMN_LEGEND,
    EMPTY_CELL,
    STANDARD_BOARD_SIZE,
    WHITESPACE,
    WINNING_SEQUENCE_LEN,
)


# helper functions


def area_helper(ranges, cell, coeffecient):
    """helps find the coordinate tuples of an area that is from both sides of
       a cell.
    :param ranges: a tuple of the ranges before and after the cell
    :param cell: a tuple of (row, col)
    :param coeffecient: the coeffecient for the formula, depending on the
                        orientation of the area.
    """
    row, col = cell
    lists = []
    for arange in ranges:
        alist = []
        for index_helper in arange:
            alist.append((row + (coeffecient * index_helper), col + index_helper))
        lists.append(alist)

    return lists[0] + [cell] + lists[1]


def calc_diagonal(lower_lim, upper_lim, left_lim, right_lim):
    """the ranges for the diagonal (i.e. from low to high row indexes and from
    low to high column indexes) small area around the cell in the board.
    see the documentation for the get_ranges_for_small_areas function."""
    before = range(-min(left_lim, lower_lim), 0)
    after = range(1, min(right_lim, upper_lim) + 1)
    return (before, after)


def calc_sideways(left_lim, right_lim):
    """the ranges for the sideways (i.e. in the same row as the cell)
    small area around the cell in the board.
    see the documentation for the get_ranges_for_small_areas function."""
    before = range(-left_lim, 0)
    after = range(1, right_lim + 1)
    return (before, after)


def calc_reverse_diagonal(lower_lim, upper_lim, left_lim, right_lim):
    """the ranges for the reverse diagonal (i.e. from low to high column
    indexes, but from high to low row indexes) small area around the cell in
    the board. see the documentation for the get_ranges_for_small_areas
    function"""
    before = range(-min(left_lim, upper_lim), 0)
    after = range(1, min(right_lim, lower_lim) + 1)
    return (before, after)


def calc_up(upper_lim):
    """the up small area is special because it is only from ine side if the cell
    therefore it is treated differently in the get_small_areas_indexes function
    see the documentation for the get_ranges_for_small_areas
    function"""
    after = range(1, upper_lim + 1)
    return after


def get_ranges_for_small_areas(lower_lim, upper_lim, left_lim, right_lim):
    """returns a dictionary of the ranges for getting small areas around
    the cell on the board, using the area_helper function
    the limit parameters are according to the position of the cell on the
    board, such that the final product is indexes of positions on the board.
    see the documentation for the get_small_area_indexes method in Board class

    # explanation of the formulas:
    #       in general, the first range starts at the negative choice with the
    #       smallest absolute value, and end at zero. the second range,
    #       skipping the cell itself, starts at 1 and ends at limit with the
    #       smallest absolute value plus 1"""

    diagonal = calc_diagonal(lower_lim, upper_lim, left_lim, right_lim)
    sideways = calc_sideways(left_lim, right_lim)
    reverse_diagonal = calc_reverse_diagonal(lower_lim, upper_lim, left_lim, right_lim)
    up = calc_up(upper_lim)

    range_tuple_dict = {
        "diagonal": diagonal,
        "sideways": sideways,
        "reverse_diagonal": reverse_diagonal,
        "up": up,
    }

    return range_tuple_dict


# end of helper functions


class Board:
    """holds all the board functionality and logic"""

    def __init__(self, matrix=None):
        if matrix:
            self.__board_matrix = matrix
        else:
            self.__board_matrix = self.make_board_matrix()

        self.move_counter = 0

        _rows = STANDARD_BOARD_SIZE[0]
        _columns = STANDARD_BOARD_SIZE[1]
        self.max_moves = _rows * _columns
        """ max_move is the amount of cells in teh board. if the board is 
        created  with a given matrix, this serves useful functionality"""

    def make_board_matrix(self):
        """creates a list of lists of empty cells for the initial gameboard"""
        width, hight = STANDARD_BOARD_SIZE
        # size tuple, first argument is width second is hight
        board_matrix = []
        for row_index in range(width):
            new_column = [EMPTY_CELL for column_index in range(hight)]
            board_matrix.append(new_column)

        return board_matrix

    def get_board(self):
        """returns the board matrix"""
        return self.__board_matrix

    def is_empty_cell(self, row, col):
        return self.__board_matrix[row][col] == EMPTY_CELL

    def add_checker(self, cell_location_tuple, player):
        """adds a checker to the chosen column by referring the cell to the
        player's value, and adding 1 to the move count
        :param cell_location_tuple: row, col"""
        row, column = cell_location_tuple
        self.__board_matrix[row][column] = player
        self.move_counter += 1

    def find_vacant_cell(self, column):
        """returns the row index of the empty cell with the highest
        index value"""
        hight = STANDARD_BOARD_SIZE[0]

        for row_index in range(hight - 1, -1, -1):
            # running through all possible row indexes, from
            if self.__board_matrix[row_index][column] == EMPTY_CELL:
                return row_index

        return False

    def get_checker(self, row, column):
        """returns the checker at the given location, or None if there is no
        checker"""
        checker = self.__board_matrix[row][column]
        if checker == EMPTY_CELL:
            return None
        else:
            return checker

    def check_for_a_draw(self):
        """checks if the board is full, returns boolean value
        -----------------------------------------------------
        the board may be full yet one of the players won, therefore a win
        should always be checked before a draw is checked"""
        return self.move_counter == self.max_moves

    @staticmethod
    def _build_bts_last_player_seq(last_player, seq_len):
        """returns the winning sequence of the last player in bytes,
        i.e. a list of the last player value * the winning sequence length,
        converted to bytes"""
        return bytes([last_player for _ in range(seq_len)])

    def _build_bts_board_val_seq(self, cells):
        """returns the values in the board in the given positions as
        a sequence in bytes"""
        board = self.__board_matrix
        return bytes([board[row][col] for row, col in cells])

    def _build_str_board_val_seq(self, cells):
        """returns the winning sequence of the last player as a string,
        i.e. a list of the last player value * the winning sequence length,
        joined to a string"""
        board = self.__board_matrix
        return "".join([str(board[row][col]) for row, col in cells])

    def _find_seq_index(self, seq, area_indexes):
        """returns a tuple of start and end values of the slice of the given
        string containing the string"""
        small_area = self._build_str_board_val_seq(area_indexes)
        seq_len = len(seq)
        maximum_slicing_index = len(small_area) - seq_len + 1
        for slicing_index in range(maximum_slicing_index):
            if seq == small_area[slicing_index : slicing_index + seq_len]:
                return slicing_index, slicing_index + seq_len

    def check_if_win(
        self, last_move_cell, current_player, winning_seq_len=WINNING_SEQUENCE_LEN
    ):
        """checks if there is a winning sequence in the area of the last move
        down, sideways or diagonally
        ------------------------------------------------------
        (see comments in the get_small_areas_indexes function)"""

        small_areas_indexes = self.get_small_areas_indexes(last_move_cell)

        winning_seq_bts = self._build_bts_last_player_seq(
            current_player, winning_seq_len
        )
        for area_indexes in small_areas_indexes:
            small_area_bts = self._build_bts_board_val_seq(area_indexes)
            if winning_seq_bts in small_area_bts:
                winning_seq_str = str(current_player) * winning_seq_len
                slicing_borders = self._find_seq_index(winning_seq_str, area_indexes)
                start_slice, end_slice = slicing_borders
                seq_coords = area_indexes[start_slice:end_slice]
                return (True, seq_coords)

        return (False, None)

    @staticmethod
    def _calc_searching_limits(cell):
        """calculates the search limits of the 4 small areas around the cell
        (with a maximum distance of the winning sequence length minus 1),
        according to restrictions caused by the position of the cell and it's
        proximity to the edges of the board"""

        row, col = cell
        board_hight_idx_lim, board_width_idx_lim = BOARD_INDEX_DIMENSIONS
        seq_suffix_len = WINNING_SEQUENCE_LEN - 1

        lower_lim = min(seq_suffix_len, row)
        upper_lim = min(seq_suffix_len, board_hight_idx_lim - row)
        left_lim = min(seq_suffix_len, col)
        right_lim = min(seq_suffix_len, board_width_idx_lim - col)

        return (lower_lim, upper_lim, left_lim, right_lim)

    def get_small_areas_indexes(self, cell):
        """returns the 4 small areas which may contain a winning sequence,
        as a list of lists of coordiante tuples
        ----------------------------------------------------------------
        getting the 4 small areas:
           assuming WINNING_SEQUENCE_LEN == X
           A. diagonal X down right + the last move cell + X up left = 2 * X + 1
           B. diagonal X down left + the last move cell + X up right = 2 * X + 1
           C. the last move cell + X up = X + 1
           D. X left + the last move cell + X right = 2 * X + 1
        all are subject to the limits of the board"""

        row, col = cell

        limits = self._calc_searching_limits(cell)
        lower_lim, upper_lim, left_lim, right_lim = limits

        areas_ranges = get_ranges_for_small_areas(
            lower_lim, upper_lim, left_lim, right_lim
        )
        small_areas_indexes = []

        for area in areas_ranges.keys():
            if area != "up":
                area_coords_list = area_helper(
                    areas_ranges[area], cell, AREA_COEFFECIENT_DICT[area]
                )
                small_areas_indexes.append(area_coords_list)
            else:
                """ the 'up' small area is not from both sides of the last move
                cell, hence it is unneccessary to make it go through the area
                helper function"""
                up = [cell]
                for index_helper in areas_ranges[area]:
                    up.append((row + index_helper, col))
                small_areas_indexes.append(up)

        return small_areas_indexes

    def print_to_console(self):
        """prints the board to the console"""
        os.system("cls||clear")
        for line in self.__board_matrix:
            line = [str(elem) for elem in line]
            print("|%s|" % "".join(line).replace(str(EMPTY_CELL), WHITESPACE))
        print(COLUMN_LEGEND)
