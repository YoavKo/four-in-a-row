##############################################################
#   file : menu.py
#   description: main menu UI - hot-seat, vs computer, network play
#                (host / join) and an about page. Run via the four-in-a-row command
##############################################################

import os
import random
import socket
import tkinter as tk
import tkinter.font as tkfont
from tkinter import messagebox
from ipaddress import ip_address

from .config import (
    BOTTOM_PORT_NUM,
    TOP_PORT_NUM,
    DEFAULT_PORT,
    PLAYERS_COLORS,
    WIN_PLAYERS_COLORS,
)
from .game import Game
from .gui import GUI
from .ai import AI
from .communicator import Communicator
from .i18n import t, raw, set_lang, is_rtl

LOGO_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "assets", "huji_logo.png"
)

ICON_SIZE = 36
ICON_WIDTH = 110
MID = ICON_WIDTH // 2  # every icon is centered on this x
BLUE, PURPLE = PLAYERS_COLORS[0], PLAYERS_COLORS[1]
CLOUD_COLOR = "#e8f1fb"


def draw_box(c, x1, x2):
    c.create_rectangle(
        x1, 1, x2, ICON_SIZE - 1, fill="white", outline="gray30", width=2
    )


def draw_person(c, cx, color, dy=3):
    c.create_arc(
        cx - 8,
        18 + dy,
        cx + 8,
        38 + dy,
        start=0,
        extent=180,
        fill=color,
        outline="black",
    )
    c.create_oval(cx - 5, 5 + dy, cx + 5, 15 + dy, fill=color, outline="black")


def draw_robot(c, cx, dy=3):
    c.create_line(cx, 2 + dy, cx, 7 + dy, width=2)
    c.create_oval(cx - 2, dy, cx + 2, 4 + dy, fill="red", outline="")
    c.create_rectangle(
        cx - 9, 7 + dy, cx + 9, 23 + dy, fill="#b0b8c4", outline="black", width=2
    )
    c.create_oval(cx - 6, 11 + dy, cx - 2, 15 + dy, fill="white", outline="black")
    c.create_oval(cx + 2, 11 + dy, cx + 6, 15 + dy, fill="white", outline="black")
    c.create_line(cx - 5, 19 + dy, cx + 5, 19 + dy, width=2)
    c.create_rectangle(
        cx - 6, 24 + dy, cx + 6, 28 + dy, fill="#b0b8c4", outline="black"
    )


def icon_hotseat(c):
    draw_box(c, MID - 32, MID + 32)
    draw_person(c, MID - 12, BLUE)
    draw_person(c, MID + 12, PURPLE)


def icon_computer(c):
    draw_box(c, MID - 32, MID + 32)
    draw_person(c, MID - 12, BLUE)
    draw_robot(c, MID + 12)


def icon_network(c):
    draw_box(c, 1, 27)
    draw_person(c, 14, BLUE)
    draw_box(c, ICON_WIDTH - 27, ICON_WIDTH - 1)
    draw_person(c, ICON_WIDTH - 14, PURPLE)
    mid_y = ICON_SIZE // 2
    for x1, x2 in ((27, MID - 13), (MID + 13, ICON_WIDTH - 27)):
        c.create_line(x1, mid_y, x2, mid_y, dash=(3, 2), width=2, fill="gray30")
    blobs = [
        (MID - 17, 15, MID - 5, 27),
        (MID - 11, 9, MID + 1, 23),
        (MID - 5, 15, MID + 7, 27),
    ]
    blobs = [(x1 + 5, y1 + 1, x2 + 5, y2 + 1) for x1, y1, x2, y2 in blobs]
    blobs.append((MID - 6, 11, MID + 6, 25))
    for box in blobs:
        c.create_oval(*box, fill=CLOUD_COLOR, outline="gray30", width=2)
    for box in blobs:  # hide the inner outlines to get one cloud shape
        c.create_oval(
            box[0] + 2, box[1] + 2, box[2] - 2, box[3] - 2, fill=CLOUD_COLOR, outline=""
        )
    c.create_rectangle(MID - 11, 20, MID + 11, 27, fill=CLOUD_COLOR, outline="")


def icon_about(c):
    c.create_oval(MID - 14, 3, MID + 14, 31, fill="#4a90d9", outline="black", width=2)
    c.create_oval(MID - 2, 8, MID + 2, 12, fill="white", outline="")
    c.create_rectangle(MID - 2, 14, MID + 2, 26, fill="white", outline="")


def icon_quit(c):
    c.create_oval(MID - 14, 3, MID + 14, 31, fill="#d9534f", outline="black", width=2)
    c.create_line(MID - 6, 11, MID + 6, 23, width=4, fill="white", capstyle="round")
    c.create_line(MID + 6, 11, MID - 6, 23, width=4, fill="white", capstyle="round")


FLAG_W, FLAG_H = 48, 32


def draw_flag_il(c):
    c.create_rectangle(0, 0, FLAG_W, FLAG_H, fill="white", outline="")
    for y in (3, 25):
        c.create_rectangle(0, y, FLAG_W, y + 4, fill="#0038b8", outline="")
    cx, cy, r = FLAG_W / 2, FLAG_H / 2, 7
    dx = r * 0.866
    for sign in (1, -1):  # two triangles make the star of David
        c.create_polygon(
            cx,
            cy - sign * r,
            cx + dx,
            cy + sign * r / 2,
            cx - dx,
            cy + sign * r / 2,
            fill="",
            outline="#0038b8",
            width=2,
        )


def draw_flag_uk(c):
    c.create_rectangle(0, 0, FLAG_W, FLAG_H, fill="#012169", outline="")
    for x1, y1, x2, y2 in ((0, 0, FLAG_W, FLAG_H), (0, FLAG_H, FLAG_W, 0)):
        c.create_line(x1, y1, x2, y2, fill="white", width=6)
        c.create_line(x1, y1, x2, y2, fill="#c8102e", width=2)
    c.create_rectangle(0, 11, FLAG_W, 21, fill="white", outline="")
    c.create_rectangle(19, 0, 29, FLAG_H, fill="white", outline="")
    c.create_rectangle(0, 13, FLAG_W, 19, fill="#c8102e", outline="")
    c.create_rectangle(21, 0, 27, FLAG_H, fill="#c8102e", outline="")


class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Four in a Row")
        self.root.resizable(False, False)
        self.container = tk.Frame(self.root, padx=30, pady=20)
        self.container.pack()
        self.com = None
        self.game = None
        self.show_main_menu()

    def run(self):
        self.root.mainloop()

    # ---------- helpers ----------
    def cleanup(self):
        if self.com:
            self.com.close()
            self.com = None
        if self.game:
            self.game.closed = True
            self.game = None

    def clear(self):
        self.cleanup()
        for w in self.container.winfo_children():
            w.destroy()

    def title(self, text, size=22):
        tk.Label(self.container, text=text, font=("Helvetica", size, "bold")).pack(
            pady=(0, 15)
        )

    @staticmethod
    def side():
        """pack side for the first element of a row - the layout is the same
        in both languages, so toggling the language never moves anything"""
        return "left"

    def lang_toggle(self, redraw):
        """small English / Hebrew switch at the top of a screen"""

        def toggle():
            set_lang("en" if is_rtl() else "he")
            self.root.title(raw("app_title"))
            redraw()

        # the flag shows the language you will switch TO
        flag = tk.Canvas(
            self.container,
            width=FLAG_W,
            height=FLAG_H,
            highlightthickness=1,
            highlightbackground="gray40",
            cursor="hand2",
        )
        (draw_flag_uk if is_rtl() else draw_flag_il)(flag)
        flag.bind("<Button-1>", lambda e: toggle())
        flag.pack(anchor="e", pady=(0, 6))

    def fancy_title(self):
        """the main-menu logo: the game name in styled colored letters"""
        width, height = 380, 76
        c = tk.Canvas(
            self.container,
            width=width,
            height=height,
            highlightthickness=0,
            bg=self.container.cget("bg"),
        )
        c.pack(pady=(0, 14))
        # name with a soft shadow, each word in its own color
        font = tkfont.Font(family="Helvetica", size=30, weight="bold")
        if is_rtl():  # visual order, left to right: בשורה ארבע
            words = [
                (t("app_title").split(" ")[0], WIN_PLAYERS_COLORS[1]),
                (" ", "gray35"),
                (t("app_title").split(" ")[1], WIN_PLAYERS_COLORS[0]),
            ]
        else:
            words = [
                ("FOUR", WIN_PLAYERS_COLORS[0]),
                (" IN A ", "gray35"),
                ("ROW", WIN_PLAYERS_COLORS[1]),
            ]
        x = (width - sum(font.measure(w) for w, _ in words)) // 2
        for word, color in words:
            c.create_text(x + 2, 32, text=word, font=font, anchor="w", fill="gray70")
            c.create_text(x, 30, text=word, font=font, anchor="w", fill=color)
            x += font.measure(word)
        c.create_text(
            width // 2,
            64,
            text=t("tagline"),
            font=("Helvetica", 10, "italic"),
            fill="gray40",
        )

    def button(self, text, command, width=28, icon=None):
        if icon is None:
            b = tk.Button(
                self.container, text=text, command=command, width=width, pady=6
            )
            b.pack(pady=4)
            return b
        row = tk.Frame(self.container)
        row.pack(pady=4)
        canvas = tk.Canvas(
            row,
            width=ICON_WIDTH,
            height=ICON_SIZE,
            highlightthickness=0,
            cursor="hand2",
            bg=self.container.cget("bg"),
        )
        canvas.pack(side=self.side(), padx=(0, 4))
        icon(canvas)
        canvas.bind("<Button-1>", lambda e: command())
        b = tk.Button(row, text=text, command=command, width=width, pady=6)
        b.pack(side=self.side())
        return b

    # ---------- screens ----------
    def show_main_menu(self):
        self.clear()
        self.root.title(raw("app_title"))
        self.lang_toggle(self.show_main_menu)
        self.fancy_title()
        self.button(
            t("menu_hotseat"), lambda: self.start_game("hotseat"), icon=icon_hotseat
        )
        self.button(
            t("menu_vs_pc"), lambda: self.start_game("vs_ai"), icon=icon_computer
        )
        self.button(t("menu_network"), self.show_network_menu, icon=icon_network)
        self.button(t("menu_about"), self.show_about, icon=icon_about)
        self.button(t("menu_quit"), self.root.destroy, icon=icon_quit)

    def show_network_menu(self):
        self.clear()
        self.lang_toggle(self.show_network_menu)
        self.title(t("net_title"))
        self.button(t("net_host"), self.show_host)
        self.button(t("net_join"), self.show_join)
        self.button(t("back"), self.show_main_menu)

    def show_about(self):
        self.clear()
        self.lang_toggle(self.show_about)
        self.title(t("about_title"))
        justify = "right" if is_rtl() else "left"
        tk.Label(self.container, text=t("about_text"), justify=justify).pack(
            anchor="e" if is_rtl() else "w"
        )
        try:
            self.logo_img = tk.PhotoImage(file=LOGO_PATH)
            tk.Label(self.container, image=self.logo_img).pack(pady=(14, 4))
        except tk.TclError:
            pass
        tk.Label(self.container, text=t("credits"), justify="center").pack(pady=(0, 6))
        tk.Button(
            self.container,
            text=t("back"),
            width=28,
            pady=6,
            command=self.show_main_menu,
        ).pack(pady=(10, 0))

    def _port_entry(self, port=DEFAULT_PORT):
        row = tk.Frame(self.container)
        row.pack(pady=4)
        tk.Label(row, text=t("port")).pack(side=self.side())
        port_var = tk.StringVar(value=str(port))
        tk.Entry(row, textvariable=port_var, width=8).pack(side=self.side(), padx=5)
        return port_var

    @staticmethod
    def _parse_port(text):
        text = text.strip()
        if text.isdigit() and BOTTOM_PORT_NUM <= int(text) <= TOP_PORT_NUM:
            return int(text)
        messagebox.showerror(
            raw("bad_port_title"), t("bad_port", BOTTOM_PORT_NUM, TOP_PORT_NUM)
        )
        return None

    def show_host(self, port=DEFAULT_PORT, auto=False):
        """auto=True starts hosting right away (used by the command line)"""
        self.clear()
        self.title(t("host_title"))
        port_var = self._port_entry(port)
        status = tk.Label(self.container, text="", justify="center")
        addr_var = tk.StringVar()

        def start():
            port = self._parse_port(port_var.get())
            if port is None:
                return
            try:
                com = Communicator(self.root, port)
            except OSError as e:
                messagebox.showerror(raw("cannot_host"), str(e))
                return
            self.com = com
            start_btn.config(state="disabled")
            addr_var.set(com.address)
            status.config(text=t("host_waiting"))
            addr_entry.pack(pady=4, before=status)
            com.on_connected = lambda: self.start_game("network", com, "server")
            com.connect()

        start_btn = self.button(t("start_hosting"), start)
        addr_entry = tk.Entry(
            self.container,
            textvariable=addr_var,
            state="readonly",
            justify="center",
            font=("Courier", 16),
            width=22,
        )
        status.pack(pady=4)
        self.button(t("back"), self.show_network_menu)
        if auto:
            self.root.after(100, start)

    def show_join(self, host="", port=DEFAULT_PORT, auto=False):
        """auto=True connects right away (used by the command line)"""
        self.clear()
        self.title(t("join_title"))
        row = tk.Frame(self.container)
        row.pack(pady=4)
        tk.Label(row, text=t("host_ip")).pack(side=self.side())
        ip_var = tk.StringVar(value=host)
        tk.Entry(row, textvariable=ip_var, width=18).pack(side=self.side(), padx=5)
        port_var = self._port_entry(port)
        status = tk.Label(self.container, text="")

        def connect():
            host = ip_var.get().strip()
            port_text = port_var.get()
            if ":" in host:  # allow pasting "ip:port"
                host, port_text = host.rsplit(":", 1)
                host = host.strip()
            port = self._parse_port(port_text)
            if port is None:
                return
            try:
                ip_address(host)
            except ValueError:
                try:
                    host = socket.gethostbyname(host)
                except OSError:
                    messagebox.showerror(raw("bad_addr_title"), t("bad_addr"))
                    return
            com = Communicator(self.root, port, host)
            self.com = com
            connect_btn.config(state="disabled")
            status.config(text=t("connecting", host, port))
            com.on_connected = lambda: self.start_game("network", com, "client")
            com.connect()

        connect_btn = self.button(t("connect"), connect)
        status.pack(pady=4)
        self.button(t("back"), self.show_network_menu)
        if auto:
            self.root.after(100, connect)

    # ---------- game ----------
    def start_game(self, kind, com=None, mode="server"):
        # the connection is handed over to the game, so don't let clear()
        # close it as part of leaving the host/join screen
        self.com = None
        self.clear()
        self.com = com
        game = Game(mode, "human", kind)
        game.root = self.root
        self.game = game

        # mode icon (hot-seat / vs computer / network) above the status line
        mode_icon = {
            "hotseat": icon_hotseat,
            "vs_ai": icon_computer,
            "network": icon_network,
        }[kind]
        icon_canvas = tk.Canvas(
            self.container,
            width=ICON_WIDTH,
            height=ICON_SIZE,
            highlightthickness=0,
            bg=self.container.cget("bg"),
        )
        icon_canvas.pack(pady=(0, 6))
        mode_icon(icon_canvas)
        status = tk.Label(self.container, font=("Helvetica", 14))
        status.pack(pady=(0, 8))
        board_frame = tk.Frame(self.container)
        board_frame.pack()
        gui = GUI(game, self.root, board_frame)
        game.gui = gui
        game.communicator = com

        def update_status():
            if game.is_game_over:
                text = game.end_message()
            elif kind == "hotseat":
                text = t(
                    "turn_hotseat",
                    raw("name_purple" if game.current_player else "name_blue"),
                )
            elif kind == "vs_ai":
                text = t("turn_you_vs_pc" if game.current_player == 0 else "turn_pc")
            else:
                me = raw("name_purple" if game.player else "name_blue")
                text = t(
                    "turn_you_net"
                    if game.player == game.current_player
                    else "turn_opp_net",
                    me,
                )
            status.config(text=text)

        game.on_update = update_status
        if kind == "vs_ai":
            game.ai = AI()
            game.ai_player = Game.PLAYER_TWO
        if com:
            com.bind_action_to_message(game.handle_message)
            com.on_disconnected = self.opponent_left
            self.root.title(
                raw("app_title") + " - " + ("host" if mode == "server" else "client")
            )

        # who starts is random; the host decides and tells the client
        if mode == "server" or not com:
            game.current_player = random.choice([Game.PLAYER_ONE, Game.PLAYER_TWO])
            if com:
                com.send_message("first:%d" % game.current_player)

        gui.board.draw_board()
        update_status()
        if kind == "vs_ai" and game.current_player == game.ai_player:
            self.root.after(600, game._ai_move)
        tk.Button(
            self.container, text=t("back_to_menu"), pady=4, command=self.show_main_menu
        ).pack(pady=(10, 0))

    def opponent_left(self):
        messagebox.showinfo(raw("disconnected"), t("opp_left"))
        self.show_main_menu()
