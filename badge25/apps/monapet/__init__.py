import sys
import os

sys.path.insert(0, "/system/apps/monapet")
os.chdir("/system/apps/monapet")


import ui
from mona import Mona
from badgeware import io, run, State

try:
    import network
    import ntptime
except ImportError:
    network = None
    ntptime = None

mona = Mona(82)  # create mona!

# speed at which each statistic goes from 100% to 0%
happiness_duration = 1800
hunger_duration = 1200
cleanliness_duration = 2400

wifi = None
wifi_started_at = None
clock_synced = False
wifi_ssid = None
wifi_password = None


def clock_update():
    global wifi, wifi_started_at, clock_synced

    if clock_synced or network is None or ntptime is None:
        return

    if wifi is None:
        wifi = network.WLAN(network.STA_IF)
        wifi.active(True)
        wifi_started_at = io.ticks
        if wifi.isconnected():
            return
        if wifi_ssid and wifi_password:
            wifi.connect(wifi_ssid, wifi_password)
        return

    if wifi.isconnected():
        try:
            ntptime.settime()
            clock_synced = True
        except OSError:
            wifi_started_at = io.ticks
        return

    if io.ticks - wifi_started_at >= 15000:
        wifi.disconnect()
        wifi.connect(wifi_ssid, wifi_password)
        wifi_started_at = io.ticks


def game_update():
    global mona

    if not mona.is_dead():
        # calculate mona's new stats based on the time since last update
        seconds = io.ticks_delta / 1000

        # work out how much mona's stats have reduce since the last frame
        happy_delta = (seconds / happiness_duration) * 100
        mona.happy(-happy_delta)
        hunger_delta = (seconds / hunger_duration) * 100
        mona.hunger(-hunger_delta)
        clean_delta = (seconds / cleanliness_duration) * 100
        mona.clean(-clean_delta)

        # play with mona!
        if io.BUTTON_A in io.pressed:
            mona.happy(30)
            mona.do_action("heart")

        # feed mona!
        if io.BUTTON_B in io.pressed:
            mona.hunger(30)
            mona.do_action("eating")

        # clean mona!
        if io.BUTTON_C in io.pressed:
            mona.clean(30)
            mona.do_action("dance")

        # every five seconds mona will move to a new location
        if mona.time_since_last_position_change() > 5:
            mona.move_to_random()

        # every eight seconds mona will select a new idle animation
        if mona.time_since_last_mood_change() > 8:
            mona.random_idle()

        # yikes, mona is in a bad way!
        if min(mona.hunger(), mona.happy(), mona.clean()) < 30:
            mona.set_mood("notify")

    else:
        mona.set_mood("dead")
        mona.move_to_center()

        # if user pressed button b then reset mona's stats
        if io.BUTTON_B in io.pressed:
            mona = Mona(82)


def update():
    clock_update()

    # update the game state based on user input and timed events
    game_update()

    # update monas state (position)
    mona.update()

    # draw the background scene
    ui.background(mona)

    # draw our little friend
    mona.draw()

    # draw the user interface elements
    if not mona.is_dead():
        ui.draw_bar("happy",  2, 41, mona.happy())
        ui.draw_bar("hunger", 2, 58, mona.hunger())
        ui.draw_bar("clean",  2, 75, mona.clean())

        ui.draw_button(4, 100,  "play", mona.current_action() == "heart")
        ui.draw_button(55, 100,  "feed", mona.current_action() == "eating")
        ui.draw_button(106, 100, "clean", mona.current_action() == "dance")
    else:
        ui.draw_button(55, 100, "reset", True)

    ui.draw_header()
    ui.draw_clock()


def init():
    global clock_synced, wifi_ssid, wifi_password

    try:
        import time
        clock_synced = time.gmtime()[0] >= 2025
    except (ImportError, OSError):
        clock_synced = False

    if not clock_synced:
        added_root = False
        try:
            sys.path.insert(0, "/")
            added_root = True
            from secrets import WIFI_PASSWORD, WIFI_SSID
            wifi_ssid = WIFI_SSID
            wifi_password = WIFI_PASSWORD
        except ImportError:
            wifi_ssid = None
            wifi_password = None
        finally:
            if added_root:
                sys.path.pop(0)

    state = {
        "happy": 100,
        "hunger": 100,
        "clean": 100,
    }
    if State.load("monapet", state):
        mona.load(state)

    del state


def on_exit():
    State.save("monapet", mona.save())


if __name__ == "__main__":
    run(update, init=init, on_exit=on_exit)
