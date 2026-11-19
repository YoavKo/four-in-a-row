from four_in_a_row import board, config
from four_in_a_row.game import Game

all_seq = []

hight = config.STANDARD_BOARD_SIZE[0]
width = config.STANDARD_BOARD_SIZE[1]

for _ in range(hight):
    for i in range(width):
        all_seq.append(i)

# print(all_seq)

if __name__ == "__main__":
    pass
pl1 = 0
pl2 = 0
for _ in range(100):
    game = Game()
    print()

    while not game.is_game_over:
        # game.board.print_to_console()
        # user_cmd = int(input()) - 1
        user_cmd = all_seq[config.RNG.randrange(len(all_seq))]
        if game.board.find_vacant_cell(user_cmd) is not False:
            game.make_move(user_cmd)
            # game.board.print_to_console()
        # elif _ > 20:20
        # # print(user_cmd)
        # print("rrr", user_cmd)
        # game.board.print_to_console()
        # print("%%%%%%%%%%%%%%")

    game.board.print_to_console()
    print(_)
    if game.get_winner() == game.PLAYER_ONE:
        pl1 += 1

    elif game.get_winner() == game.PLAYER_TWO:
        pl2 += 1
    print("winner", game.get_winner(), "seq_coords", game.winning_seq_coords)
    if game.get_winner() != 2:
        boar = game.board.get_board()
        for i in game.winning_seq_coords:
            boar[i[0]][i[1]] = 8
    z = board.Board(boar)
    z.print_to_console()
    print("********")

print("1", pl1, "2", pl2)

# ///board tester
