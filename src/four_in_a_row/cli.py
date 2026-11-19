from __future__ import annotations

import argparse
import sys
from ipaddress import ip_address

from .ai import AI
from .communicator import Communicator
from .config import (
    BOTTOM_PORT_NUM,
    DEFAULT_PORT,
    IP_FORMAT_ERR,
    NUM_OF_ARGS_ERR,
    PLAYER_MODE_ERR_MSG,
    PLAYERS_MODE_OPTIONS,
    PORT_FORMAT_ERR,
    TOP_PORT_NUM,
    USAGE_MSG,
    seed_rng,
)
from .game import Game
from .gui import GUI
from .i18n import raw, set_lang
from .menu import App


def input_validation() -> tuple[str, str, int, str | None]:
    """reads command line arguments, checks their validation, if needed
    terminates the program and prints proper error messages and a proper usage
    message"""
    is_the_input_valid = True

    if len(sys.argv) not in [3, 4]:
        print(NUM_OF_ARGS_ERR)
        is_the_input_valid = False

    else:
        player_mode = sys.argv[1]
        if player_mode not in PLAYERS_MODE_OPTIONS:
            print(PLAYER_MODE_ERR_MSG)
            is_the_input_valid = False
        else:
            player_type = player_mode

        port_text = sys.argv[2]
        port = 0
        if not (
            port_text.isdigit() and (BOTTOM_PORT_NUM <= int(port_text) <= TOP_PORT_NUM)
        ):
            print(PORT_FORMAT_ERR)
            is_the_input_valid = False
        else:
            port = int(port_text)
        if len(sys.argv) == 4:
            try:
                ip = sys.argv[3]
                ip_address(ip)
                player_mode = "client"

            except ValueError:
                print(IP_FORMAT_ERR)
                is_the_input_valid = False
        else:
            player_mode = "server"
            ip = None

    if not is_the_input_valid:
        print(USAGE_MSG)
        sys.exit(1)

    else:
        return (player_mode, player_type, port, ip)


def run_cli() -> None:
    """legacy command line mode: player_mode port [host_ip]"""
    player_mode, player_type, port, ip = input_validation()

    game = Game(player_mode, player_type)
    if player_type == "ai":
        game.ai = AI()

    gui = GUI(game)
    gui.root.title(player_mode)
    com = Communicator(gui.root, port, ip)
    com.connect()
    com.bind_action_to_message(game.handle_message)
    game.communicator = com
    game.gui = gui

    gui.board.draw_board()
    if player_mode == "server" and game.ai is not None:
        # if the server if ai - execute first move
        game.ai.find_legal_move(game, game.handle_move_event)

    gui.root.mainloop()


def port_arg(text: str) -> int:
    """argparse type: a valid port number"""
    if text.isdigit() and BOTTOM_PORT_NUM <= int(text) <= TOP_PORT_NUM:
        return int(text)
    raise argparse.ArgumentTypeError(PORT_FORMAT_ERR)


def build_parser() -> argparse.ArgumentParser:
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument(
        "--seed",
        type=int,
        default=argparse.SUPPRESS,
        help="seed the random number generator (reproducible games)",
    )
    common.add_argument(
        "--lang",
        choices=["he", "en"],
        default=argparse.SUPPRESS,
        help="interface language (default: he)",
    )

    parser = argparse.ArgumentParser(
        prog="four-in-a-row",
        parents=[common],
        description="Four in a Row. Run without a command to open the main menu.",
        epilog="legacy form still supported: four-in-a-row human|ai PORT [HOST_IP]",
    )
    sub = parser.add_subparsers(dest="command", metavar="COMMAND")

    sub.add_parser("hotseat", parents=[common], help="two players on one screen")
    sub.add_parser(
        "vs-robot",
        aliases=["vs_robot"],
        parents=[common],
        help="play against the computer",
    )

    host = sub.add_parser(
        "host", parents=[common], help="host a network game and show ip:port"
    )
    host.add_argument(
        "--port",
        type=port_arg,
        default=DEFAULT_PORT,
        help="port to listen on (default: %(default)s)",
    )

    join = sub.add_parser(
        "join", parents=[common], help="join another player's network game"
    )
    join.add_argument("ip", help="the host's IP address")
    join.add_argument(
        "--port",
        type=port_arg,
        default=DEFAULT_PORT,
        help="the host's port (default: %(default)s)",
    )

    sub.add_parser(
        "about",
        aliases=["info"],
        parents=[common],
        help="print information about the project",
    )
    return parser


def print_about() -> None:
    """project info, printed to the terminal"""
    print(raw("app_title"))
    print("=" * len(raw("app_title")))
    print(raw("about_text"))
    print()
    print(raw("credits"))


def main() -> None:
    # legacy command line mode: human|ai PORT [HOST_IP]
    if len(sys.argv) > 1 and sys.argv[1] in PLAYERS_MODE_OPTIONS:
        run_cli()
        return

    args = build_parser().parse_args()
    if hasattr(args, "seed"):
        seed_rng(args.seed)
    if getattr(args, "lang", None):
        set_lang(args.lang)
    command = args.command
    if command in ("about", "info"):
        if not getattr(args, "lang", None):
            set_lang("en")  # terminals often mishandle right-to-left text
        print_about()
        return

    app = App()
    if command == "hotseat":
        app.start_game("hotseat")
    elif command in ("vs-robot", "vs_robot"):
        app.start_game("vs_ai")
    elif command == "host":
        app.show_host(args.port, auto=True)
    elif command == "join":
        app.show_join(args.ip, args.port, auto=True)
    app.run()


if __name__ == "__main__":
    main()
