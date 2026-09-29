import tkinter as tk
from PIL import Image, ImageTk
import random
import threading
# VOICE
try:
    import pyttsx3
    VOICE_AVAILABLE = True
except:
    VOICE_AVAILABLE = False

voice_enabled = True
voice_lock = threading.Lock()
current_engine = None
voice_generation = 0


def speak_sync(text, callback=None):

    global current_engine
    global voice_generation

    # Voice library available 
    if not VOICE_AVAILABLE:

        if callback:
            root.after(0, callback)

        return

    my_generation = voice_generation

    def voice_thread():

        global current_engine

        engine = None

        try:

            with voice_lock:

                # Voice OFF
                if not voice_enabled:
                    return

                # Old voice cancel 
                if my_generation != voice_generation:
                    return

                engine = pyttsx3.init()

                current_engine = engine

                # Slow and clear English voice
                engine.setProperty(
                    "rate",
                    250
                )

                engine.setProperty(
                    "volume",
                    1.0
                )

                # English voice select
                voices = engine.getProperty(
                    "voices"
                )

                for voice in voices:

                    name = voice.name.lower()
                    vid = voice.id.lower()

                    if (
                        "english" in name
                        or
                        "english" in vid
                    ):

                        engine.setProperty(
                            "voice",
                            voice.id
                        )

                        break

                # Final check
                if (
                    voice_enabled
                    and
                    my_generation == voice_generation
                ):

                    engine.say(
                        str(text)
                    )

                    engine.runAndWait()

        except Exception as e:

            print(
                "Voice Error:",
                e
            )

        finally:

            try:

                if engine:
                    engine.stop()

            except:
                pass

            if current_engine == engine:
                current_engine = None

            # Animation continue karna zaroori hai
            if callback:

                try:

                    root.after(
                        0,
                        callback
                    )

                except:
                    pass

    threading.Thread(
        target=voice_thread,
        daemon=True
    ).start()


def speak(text):
    speak_sync(text)


def stop_voice():

    global current_engine
    global voice_generation

    voice_generation += 1

    engine = current_engine

    if engine:

        try:
            engine.stop()
        except:
            pass

    current_engine = None

# WINDOW
root = tk.Tk()

root.geometry("1400x800")

root.title("Snakes & Ladders")

root.resizable(True, True)

# Laptop maximize/minimize support
root.minsize(1200, 700)


# GAME VARIABLES

player1_pos = 1
player2_pos = 1

turn = 1

moving = False

game_over = False

Dice = []

Index = {}

# SNAKES

SNAKES = {

    98: 58,
    96: 56,
    93: 53,
    44: 3,
    46: 6,
    32: 9

}

# LADDERS

LADDERS = {

    11: 31,
    5: 36,
    22: 82,
    47: 73,
    51: 90,
    58: 98

}

# BOARD COORDINATES

def get_Index():

    global Index

    left = 44
    top = 60

    cell_w = 103.4
    cell_h = 69.7

    for row in range(10):

        for col in range(10):

            # Bottom row = 1 to 10
            if row % 2 == 0:

                number = (
                    row * 10
                    + col
                    + 1
                )

            # Next row = 20 to 11
            else:

                number = (
                    row * 10
                    + (10 - col)
                )

            x = (
                left
                + col * cell_w
                + cell_w / 2
            )

            y = (
                top
                + (9 - row) * cell_h
                + cell_h / 2
            )

            Index[number] = (
                int(x),
                int(y)
            )

# BOARD

board_canvas = tk.Canvas(

    root,

    width=1100,
    height=788,

    highlightthickness=0,
    bd=0

)

board_canvas.place(
    x=0,
    y=0
)

# BOARD IMAGE

try:

    board_image = Image.open(
        "images/final_cover.png"
    )

    board_image = board_image.resize(
        (1100, 788),
        Image.Resampling.LANCZOS
    )

    board_photo = ImageTk.PhotoImage(
        board_image
    )

    board_canvas.create_image(
        0,
        0,
        image=board_photo,
        anchor="nw"
    )

except Exception as e:

    board_canvas.create_text(

        550,
        394,

        text="Board image not found",

        font=(
            "Arial",
            25,
            "bold"
        ),

        fill="red"

    )

    print(
        "Board image error:",
        e
    )

# 3D COIN

def create_3d_coin(
    x,
    y,
    main_color,
    dark_color
):

    # Shadow
    shadow = board_canvas.create_oval(

        x - 15,
        y - 5,

        x + 17,
        y + 10,

        fill="black",

        outline="",

        tags="coin"

    )

    # Bottom
    bottom = board_canvas.create_oval(

        x - 15,
        y - 15,

        x + 15,
        y + 15,

        fill=dark_color,

        outline="",

        tags="coin"

    )

    # Main coin
    main = board_canvas.create_oval(

        x - 14,
        y - 18,

        x + 14,
        y + 10,

        fill=main_color,

        outline="white",

        width=1,

        tags="coin"

    )

    # Highlight
    highlight = board_canvas.create_oval(

        x - 8,
        y - 13,

        x - 2,
        y - 7,

        fill="white",

        outline="",

        tags="coin"

    )

    return [
        shadow,
        bottom,
        main,
        highlight
    ]

# CREATE COINS

get_Index()

x1, y1 = Index[1]
x2, y2 = Index[1]


# Player 1
player1_coin = create_3d_coin(

    x1 - 17,
    y1,

    "#F44336",
    "#B71C1C"

)


# Player 2
player2_coin = create_3d_coin(

    x2 + 17,
    y2,

    "#1976D2",
    "#0D47A1"

)

# MOVE COIN

def move_coin_graphically(
    coin,
    number,
    side
):

    if number not in Index:
        return

    x, y = Index[number]

    if side == 1:

        x -= 17

    else:

        x += 17

    bbox = board_canvas.bbox(
        coin[0]
    )

    if bbox:

        current_x = (
            bbox[0]
            + bbox[2]
        ) / 2

        current_y = (
            bbox[1]
            + bbox[3]
        ) / 2

        dx = x - current_x
        dy = y - current_y

        for item in coin:

            board_canvas.move(
                item,
                dx,
                dy
            )

        # Coin board ke upar rahe
        for item in coin:

            board_canvas.tag_raise(
                item
            )


# ANIMATE ONE NUMBER + VOICE

def animate_steps(
    player,
    start,
    end,
    callback=None
):

    if start >= end:

        if callback:
            callback()

        return

    next_number = start + 1

    # STEP 1 - COIN MOVE

    if player == 1:

        move_coin_graphically(

            player1_coin,

            next_number,

            1

        )

    else:

        move_coin_graphically(

            player2_coin,

            next_number,

            2

        )

    # STEP 2 - SAME NUMBER VOICE
   
    if (
        voice_enabled
        and
        VOICE_AVAILABLE
    ):

        speak_sync(

            str(next_number),

            lambda: animate_steps(

                player,

                next_number,

                end,

                callback

            )

        )

    else:

        # Voice OFF
        root.after(

            180,

            lambda: animate_steps(

                player,

                next_number,

                end,

                callback

            )

        )

# SPECIAL MOVE

def animate_special(
    player,
    start,
    end
):

    global player1_pos
    global player2_pos

    if player == 1:

        move_coin_graphically(

            player1_coin,

            end,

            1

        )

        player1_pos = end

    else:

        move_coin_graphically(

            player2_coin,

            end,

            2

        )

        player2_pos = end

    # Special destination voice
    if voice_enabled:

        if end < start:

            speak_sync(

                f"Snake! Moving down from {start} to {end}.",

                finish_turn

            )

        else:

            speak_sync(

                f"Ladder! Climbing up from {start} to {end}.",

                finish_turn

            )

    else:

        root.after(
            600,
            finish_turn
        )

# CHECK SPECIAL

def check_special(
    player,
    position
):


    # SNAKE

    if position in SNAKES:

        new_position = SNAKES[position]

        status_label.config(

            text=(
                f"SNAKE!\n"
                f"{position} → {new_position}"
            )

        )

        speak_sync(

            f"Oh no! Snake! "
            f"Player {player} is bitten by the snake. "
            f"Moving down from {position} "
            f"to {new_position}.",

            lambda: root.after(

                500,

                lambda: animate_special(

                    player,
                    position,
                    new_position
                )

            )

        )

        return True


    # LADDER

    if position in LADDERS:

        new_position = LADDERS[position]

        status_label.config(

            text=(
                f"LADDER!\n"
                f"{position} → {new_position}"
            )

        )

        speak_sync(

            f"Great! Ladder! "
            f"Player {player} found a ladder. "
            f"Climbing up from {position} "
            f"to {new_position}.",

            lambda: root.after(

                500,

                lambda: animate_special(

                    player,
                    position,
                    new_position
                )

            )

        )

        return True


    finish_turn()

    return False

# CHECK WINNER

def check_winner():

    global game_over

    if player1_pos == 100:

        game_over = True

        status_label.config(
            text="PLAYER 1 WINS!"
        )

        b1.config(
            state="disabled"
        )

        b2.config(
            state="disabled"
        )

        dice_button.config(
            state="disabled"
        )

        speak_sync(

            "Congratulations! "
            "Player 1 is the winner. "
            "You reached number one hundred."

        )

        return True


    if player2_pos == 100:

        game_over = True

        status_label.config(
            text="PLAYER 2 WINS!"
        )

        b1.config(
            state="disabled"
        )

        b2.config(
            state="disabled"
        )

        dice_button.config(
            state="disabled"
        )

        speak_sync(

            "Congratulations! "
            "Player 2 is the winner. "
            "You reached number one hundred."

        )

        return True

    return False

# FINISH TURN

def finish_turn():

    global turn
    global moving

    if check_winner():

        moving = False

        return


    if turn == 1:

        turn = 2

        b1.config(
            state="disabled"
        )

        b2.config(
            state="normal"
        )

        speak_sync(
            "Player 2 turn."
        )

    else:

        turn = 1

        b2.config(
            state="disabled"
        )

        b1.config(
            state="normal"
        )

        speak_sync(
            "Player 1 turn."
        )

    update_status()

    moving = False

# ROLL DICE

def roll_dice(player):

    global player1_pos
    global player2_pos
    global moving

    if game_over:
        return

    if moving:
        return

    if player != turn:
        return

    moving = True

    # DICE NUMBER

    number = random.randint(
        1,
        6
    )

    dice_button.config(

        image=Dice[number - 1]

    )

    speak_sync(

        f"Player {player} rolled {number}."

    )

    # PLAYER 1

    if player == 1:

        old_position = player1_pos

        new_position = (
            old_position
            + number
        )

        # Beyond 100
        if new_position > 100:

            status_label.config(

                text=(
                    f"🎲 Player 1 rolled {number}\n"
                    f"Exact number needed"
                )

            )

            speak_sync(

                "Player 1 needs an exact "
                "number to reach one hundred."

            )

            moving = False

            finish_turn()

            return

        player1_pos = new_position

        status_label.config(

            text=(
                f"Player 1 → "
                f"{new_position}"
            )

        )

        animate_steps(

            1,

            old_position,

            new_position,

            lambda: after_normal_move(
                1,
                new_position
            )

        )


    # PLAYER 2

    else:

        old_position = player2_pos

        new_position = (
            old_position
            + number
        )

        if new_position > 100:

            status_label.config(

                text=(
                    f"Player 2 rolled {number}\n"
                    f"Exact number needed"
                )

            )

            speak_sync(

                "Player 2 needs an exact "
                "number to reach one hundred."

            )

            moving = False

            finish_turn()

            return

        player2_pos = new_position

        status_label.config(

            text=(
                f"Player 2 → "
                f"{new_position}"
            )

        )

        animate_steps(

            2,

            old_position,

            new_position,

            lambda: after_normal_move(
                2,
                new_position
            )

        )


# AFTER NORMAL MOVE

def after_normal_move(
    player,
    position
):

    global moving

    if check_winner():

        moving = False

        return

    check_special(
        player,
        position
    )

# STATUS

def update_status():

    if game_over:
        return

    status_label.config(

        text=(
            f"Player 1: "
            f"{player1_pos}\n"

            f"Player 2: "
            f"{player2_pos}\n\n"

            f"Player {turn} Turn"
        )

    )

# VOICE ON / OFF

def toggle_voice():

    global voice_enabled

    voice_enabled = not voice_enabled

    if not voice_enabled:

        stop_voice()

        voice_button.config(

            text="VOICE OFF",

            bg="light gray"

        )

        return


    voice_button.config(

        text="VOICE ON",

        bg="light green"

    )

    speak_sync(
        "Voice is on."
    )

# LOAD DICE

for i in range(1, 7):

    try:

        img = Image.open(

            f"images/{i}.png"

        )

        img = img.resize(

            (65, 65),

            Image.Resampling.LANCZOS

        )

        Dice.append(

            ImageTk.PhotoImage(
                img
            )

        )

    except Exception as e:

        print(

            f"Dice {i} image error:",
            e

        )

# ROLL IMAGE

try:

    roll_img = Image.open(

        "images/roll.png"

    )

    roll_img = roll_img.resize(

        (65, 65),

        Image.Resampling.LANCZOS

    )

    roll_image = ImageTk.PhotoImage(

        roll_img

    )

except Exception as e:

    print(
        "Roll image error:",
        e
    )

    roll_image = None

# EXIT

exit_button = tk.Button(

    root,

    text="EXIT GAME",

    height=2,

    width=18,

    bg="dark orange",

    fg="black",

    font=(
        "Arial",
        13,
        "bold"
    ),

    command=root.destroy

)

exit_button.place(

    x=1150,

    y=20

)


# VOICE BUTTON

voice_button = tk.Button(

    root,

    text="VOICE ON",

    height=2,

    width=18,

    bg="light green",

    fg="black",

    font=(
        "Arial",
        13,
        "bold"
    ),

    command=toggle_voice

)

voice_button.place(

    x=1150,

    y=90

)


# DICE

if roll_image:

    dice_button = tk.Button(

        root,

        image=roll_image,

        height=80,

        width=80,

        bd=2,

        relief="raised",

        command=lambda: roll_dice(turn)

    )

else:

    dice_button = tk.Button(

        root,

        text="",

        font=(
            "Arial",
            25,
            "bold"
        ),

        command=lambda: roll_dice(turn)

    )


dice_button.place(

    x=1200,

    y=150

)

# PLAYER 1

b1 = tk.Button(

    root,

    text="PLAYER - 1\nROLL DICE",

    height=3,

    width=20,

    fg="white",

    bg="dark red",

    font=(
        "Arial",
        13,
        "bold"
    ),

    command=lambda: roll_dice(1)

)

b1.place(

    x=1150,

    y=400

)


# PLAYER 2

b2 = tk.Button(

    root,

    text="PLAYER - 2\nROLL DICE",

    height=3,

    width=20,

    fg="white",

    bg="dark blue",

    font=(
        "Arial",
        13,
        "bold"
    ),

    state="disabled",

    command=lambda: roll_dice(2)

)

b2.place(

    x=1150,

    y=530

)


# RESET

reset_button = tk.Button(

    root,

    text="RESET GAME",

    height=2,

    width=18,

    bg="light green",

    fg="black",

    font=(
        "Arial",
        13,
        "bold"
    ),

    command=lambda: reset_game()

)

reset_button.place(

    x=1150,

    y=660

)

# STATUS

status_label = tk.Label(

    root,

    text="Player 1 Turn",

    font=(
        "Arial",
        11,
        "bold"
    ),

    justify="center"

)

status_label.place(

    x=1130,

    y=730,

    width=250,

    height=60

)

# RESET FUNCTION

def reset_game():

    global player1_pos
    global player2_pos
    global turn
    global game_over
    global moving

    # Stop current voice
    stop_voice()

    player1_pos = 1
    player2_pos = 1

    turn = 1

    game_over = False

    moving = False

    # PLAYER 1 POSITION

    x1, y1 = Index[1]

    bbox = board_canvas.bbox(

        player1_coin[0]

    )

    if bbox:

        cx = (
            bbox[0]
            + bbox[2]
        ) / 2

        cy = (
            bbox[1]
            + bbox[3]
        ) / 2

        for item in player1_coin:

            board_canvas.move(

                item,

                x1 - 17 - cx,

                y1 - cy

            )


    # PLAYER 2 POSITION
   
    x2, y2 = Index[1]

    bbox = board_canvas.bbox(

        player2_coin[0]

    )

    if bbox:

        cx = (
            bbox[0]
            + bbox[2]
        ) / 2

        cy = (
            bbox[1]
            + bbox[3]
        ) / 2

        for item in player2_coin:

            board_canvas.move(

                item,

                x2 + 17 - cx,

                y2 - cy

            )

    # RESET DICE
    
    if roll_image:

        dice_button.config(

            image=roll_image

        )


    
    # BUTTONS
    
    b1.config(
        state="normal"
    )

    b2.config(
        state="disabled"
    )

    dice_button.config(
        state="normal"
    )


    # STATUS

    update_status()

    if voice_enabled:

        speak_sync(

            "Game reset. "
            "Player 1 turn."

        )

# START GAME
root.mainloop()
