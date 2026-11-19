##############################################################
#   file : i18n.py
#   description: English / Hebrew texts for the UI.
#                Tk 8.6 on Linux has no right-to-left support, so Hebrew
#                text is reordered into its visual order by visual().
##############################################################

LANG = "he"  # the UI opens in Hebrew by default

STRINGS = {
    "app_title": ("Four in a Row", "ארבע בשורה"),
    "tagline": ("connect four to win", "חברו ארבעה כדי לנצח"),
    "menu_hotseat": ("Hot-seat (2 players, one screen)", "שני שחקנים על מסך אחד"),
    "menu_vs_pc": ("Player vs Computer", "שחקן נגד מחשב"),
    "menu_network": ("Play over network...", "משחק ברשת..."),
    "menu_about": ("About", "אודות"),
    "menu_quit": ("Quit", "יציאה"),
    "back": ("Back", "חזרה"),
    "back_to_menu": ("Back to menu", "חזרה לתפריט"),
    "net_title": ("Play over network", "משחק ברשת"),
    "net_host": ("Host a game", "אירוח משחק"),
    "net_join": ("Join a game", "הצטרפות למשחק"),
    "about_title": ("About", "אודות"),
    "about_text": (
        "Drop checkers into the columns of a 7x6 board.\n"
        "The first player to line up four checkers\n"
        "(horizontally, vertically or diagonally) wins.\n"
        "\n"
        "Modes\n"
        "  - Hot-seat: two players share one screen.\n"
        "  - Player vs Computer: the computer blocks your\n"
        "    wins and takes its own when it can.\n"
        "  - Over network: one player hosts and shares the\n"
        "    shown ip:port, the other joins with it.\n"
        "    (Both machines must be able to reach each other,\n"
        "    e.g. the same LAN, or a forwarded port.)",
        "מניחים דיסקיות בעמודות של לוח בגודל 7 על 6.\n"
        "השחקן הראשון שמסדר ארבע דיסקיות ברצף\n"
        "(אופקי, אנכי או אלכסוני) מנצח.\n"
        "\n"
        "מצבי משחק\n"
        "- שני שחקנים: שני שחקנים חולקים מסך אחד.\n"
        "- שחקן נגד מחשב: המחשב חוסם את הניצחון שלכם\n"
        "ומנצח בעצמו כשהוא יכול.\n"
        "- ברשת: שחקן אחד מארח ומשתף את כתובת ה-ip:port,\n"
        "והשני מצטרף אליה. (המחשבים צריכים לראות זה את זה,\n"
        "למשל באותה רשת מקומית או דרך פורט מועבר.)",
    ),
    "credits": (
        "Made by Meir Weizmann and Yoav Kostiner\n"
        "as final project at 'intro to CS' at the HUJI @2017",
        "נוצר על ידי מאיר ויצמן ויואב קוסטינר\n"
        'כפרויקט גמר בקורס "מבוא למדעי המחשב" באוניברסיטה העברית, 2017',
    ),
    "host_title": ("Host a game", "אירוח משחק"),
    "port": ("Port:", "פורט:"),
    "start_hosting": ("Start hosting", "התחל אירוח"),
    "host_waiting": (
        "Tell the other player to join this address.\nWaiting for opponent...",
        "ספרו לשחקן השני להתחבר לכתובת הזו.\nממתין ליריב...",
    ),
    "cannot_host": ("Cannot host", "לא ניתן לארח"),
    "join_title": ("Join a game", "הצטרפות למשחק"),
    "host_ip": ("Host IP:", "כתובת המארח:"),
    "connect": ("Connect", "התחבר"),
    "connecting": ("Connecting to %s:%d ...", "מתחבר אל %s:%d ..."),
    "bad_port_title": ("Invalid port", "פורט לא תקין"),
    "bad_port": (
        "Port must be a number between %d and %d.",
        "הפורט חייב להיות מספר בין %d ל-%d.",
    ),
    "bad_addr_title": ("Invalid address", "כתובת לא תקינה"),
    "bad_addr": ("Enter the host IP address.", "הזינו את כתובת המארח."),
    "disconnected": ("Disconnected", "התנתקות"),
    "opp_left": ("The other player left the game.", "השחקן השני עזב את המשחק."),
    "name_blue": ("Blue", "כחול"),
    "name_purple": ("Purple", "סגול"),
    "turn_hotseat": ("%s player's turn", "תור השחקן ה%s"),
    "turn_you_vs_pc": ("Your turn (Blue)", "התור שלך (כחול)"),
    "turn_pc": ("Computer is thinking...", "המחשב חושב..."),
    "turn_you_net": ("Your turn - you are %s", "התור שלך - אתה השחקן ה%s"),
    "turn_opp_net": ("Opponent's turn - you are %s", "תור היריב - אתה השחקן ה%s"),
    "end_title": ("The game is over", "המשחק נגמר"),
    "draw": ("It is a DRAW :'( ", "תיקו"),
    "you_won": ("You have won!!!  =)", "ניצחת!"),
    "opp_won": ("Your opponent has won...  =(", "היריב ניצח..."),
    "pc_won": ("The computer has won...  =(", "המחשב ניצח..."),
    "player_wins": ("%s player wins!", "השחקן ה%s ניצח!"),
    "toggle": ("עברית", "English"),  # label shows the OTHER language
}

_OPENERS = {"(": ")", "[": "]", "{": "}", "<": ">"}
_MIRROR = {**_OPENERS, **{v: k for k, v in _OPENERS.items()}}


def set_lang(lang):
    global LANG
    LANG = lang


def is_rtl():
    return LANG == "he"


def t(key, *args):
    """the text for key in the current language, ready to show in Tk"""
    index = 1 if is_rtl() else 0
    text = STRINGS[key][index]
    if args:
        text = text % args
    return visual(text) if (is_rtl() or key == "toggle") else text


def raw(key):
    """the text for key in the current language, NOT reordered - use it for
    values that are passed as arguments into another t() call"""
    return STRINGS[key][1 if is_rtl() else 0]


def _is_ltr_char(ch):
    return ch.isascii() and ch.isalnum()


def _visual_line(line):
    """reorders one logical right-to-left line into left-to-right display
    order: Hebrew runs are reversed, Latin / number runs stay as they are"""
    kinds = [
        "L" if _is_ltr_char(c) else ("R" if "֐" <= c <= "׿" else "N") for c in line
    ]
    # neutrals (spaces, punctuation) between two LTR chars stay LTR
    i = 0
    while i < len(kinds):
        if kinds[i] == "N":
            j = i
            while j < len(kinds) and kinds[j] == "N":
                j += 1
            before = kinds[i - 1] if i else "R"
            after = kinds[j] if j < len(kinds) else "R"
            fill = "L" if before == "L" and after == "L" else "R"
            kinds[i:j] = [fill] * (j - i)
            i = j
        else:
            i += 1
    runs, cur_kind, cur = [], None, ""
    for ch, kind in zip(line, kinds):
        if kind != cur_kind and cur:
            runs.append((cur_kind, cur))
            cur = ""
        cur_kind = kind
        cur += ch
    if cur:
        runs.append((cur_kind, cur))
    out = []
    for kind, text in reversed(runs):
        if kind == "R":
            text = "".join(_MIRROR.get(c, c) for c in reversed(text))
        out.append(text)
    return "".join(out)


def visual(text):
    return "\n".join(_visual_line(line) for line in text.split("\n"))
