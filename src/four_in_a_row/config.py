# ##### BOARD #####
STANDARD_BOARD_SIZE = (6, 7)
# hight is 6, width is 7
BOARD_INDEX_DIMENSIONS = STANDARD_BOARD_SIZE[0] - 1, STANDARD_BOARD_SIZE[1] - 1
# this is for getting range values
EMPTY_CELL = 3
ONE_ABOVE = -1
ONE_LOWER = 1
FIRST_ROW_INDEX = 0
WINNING_SEQUENCE_LEN = 4
COLUMN_LEGEND = " 1234567"
WHITESPACE = " "

AREA_COEFFECIENT_LIST = [1, 0, -1]
AREA_COEFFECIENT_DICT = {}
AREA_COEFFECIENT_DICT["diagonal"] = AREA_COEFFECIENT_LIST[0]
AREA_COEFFECIENT_DICT["sideways"] = AREA_COEFFECIENT_LIST[1]
AREA_COEFFECIENT_DICT["reverse_diagonal"] = AREA_COEFFECIENT_LIST[2]
# for use in the area_helper function in the board.py module, determines if
# the row index grows when the column index grows, shrinks, or does not change

# #### GAME ####
ILLEGAL_MOVE_MSG = "Illegal move"
OPP_WON_MSG = "Your opponent has won...  =("
YOU_WON_MSG = "You have won!!!  =)"
END_GAME_TITLE_MSG = "The game is over"
DRAW_MSG = "It is a DRAW :'( "
# #### ///GAME###

# ######  GUI #####
CHECKER_DIAMETER = 60
NUM_OF_COLUMNS = 7
NUM_OF_ROWS = 6
BAFER_WIDTH = 10
COLUMN_COLOR = "lavender"
EMPTY_CELL_COLOR = "white"
PLAYERS_COLORS = {1: "DarkOrchid1", 0: "dodger blue"}
WIN_PLAYERS_COLORS = {1: "purple4", 0: "medium blue"}
HOVER_COLOR = {1: "mediumPurple1", 0: "light sky blue"}
# ######  ////GUI #####

# ### AI ####
NO_MOVES_MSG = "No possible AI moves"
ONE_UNIT_LESS_LONG = -1
# ### ///AI ####

# #### main  ####
PLAYERS_MODE_OPTIONS = ["human", "ai"]
PLAYER_MODE_ERR_MSG = "Unknown player_mode"
NUM_OF_ARGS_ERR = "Invalid number of arguments"
BOTTOM_PORT_NUM = 1000
TOP_PORT_NUM = 65535
PORT_FORMAT_ERR = "Port is out of range [%s, %s]" % (BOTTOM_PORT_NUM, TOP_PORT_NUM)
IP_FORMAT_ERR = "IP address inaccurate"
USAGE_MSG = """-------------------------------------------------------------
usage: four-in-a-row player_mode port [host_ip]
       - player_mode: human | ai
       - port: int (e.g. 8090)
       - host_ip: ipv4 address """
# ### /// main ###

PLAYER_NAMES = {0: "Blue", 1: "Purple"}
DEFAULT_PORT = 8090
