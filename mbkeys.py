import os
import sys
import time

import winsound
import win32api
import win32con
import win32gui
# import keyboard

from pynput.keyboard import Key, Listener
# from keyboard import is_pressed
from mbk_config import MBKConfig

version = "0.1.2"   # Program version
author = 'By Massimo Mula, 2021-24'
soundstatus = {True: 'ON', False: 'OFF'}
keys_down = []
key_down = None
# activation_key = 145        # 145 = Scroll Lock

# TODO - Implement QUIT key

emu_enabled = False         # Boolean, used to tell whether the mouse emulation is active (True) or not (False).
setup_mode = False          # Boolean. True: program is in "key mapping" mode" (listening for keys to be assigned to mouse buttons)

# Read configuration from INI file
programsettings = MBKConfig()   # TODO - Implement configuration menu


# Apply Key  configuration
setup_key = [['Key.ctrl_l', "'\\x13'"], ['Key.ctrl_r', "'\\x13'"]]
reset_key = ['<88>', 'Key.ctrl_l', 'Key.shift', 'Key.alt_l']
sound_key = ['<83>', 'Key.ctrl_l', 'Key.shift', 'Key.alt_l']

# activation_key = f"Key.{programsettings.get_option('Settings','ActivationKey')}"
activation_key = int(programsettings.get_option('Settings', 'ActivationKey'))   # Key used to toggle emulation.
sound_enable = bool(programsettings.get_option('Settings', 'ClickSound'))       # True: Enable sound; False: disable.

click_freq = programsettings.get_option('Settings', 'ClickSoundFrequency')
click_sound = [int(click_freq), 2]


mouse_mapping = {
    'left': int(programsettings.get_option('MouseButtons', 'Left')),
    'right': int(programsettings.get_option('MouseButtons', 'Right'))
}


# --------------------------------------------------------------------------------------------------
def clear():
    lambda: os.system('cls')  # on Windows System
    # os.system('clear') #on Linux System


def print_configuration():
    welcome_msg = f"MouseButton Keys v.{version}  --  {author}"
    print('\n')
    print(welcome_msg)
    print('\n')
    print(f"    Left Mouse Button  is mapped to '{mouse_mapping['left']}' key")
    print(f"    Right Mouse Button is mapped to '{mouse_mapping['right']}' key")
    print('\n')
    print(f'\rSound is {soundstatus[sound_enable]}              ')
    print("\n Press CTRL+S to change configuration.")
    print('\n')


def key_vk(key):
    # Returns the Virtual Key (VK) code of the pressed key
    if isinstance(key, Key):
        vk = key.value.vk
    else:
        vk = key.vk
    return vk

    
def toggle_emulation():
    """
    Toggles emu_enabled flag when activation key is pressed (default: Scroll Lock)
    :return:
    """
    global emu_enabled
    
    emu_status = ''
    emu_enabled = not emu_enabled
    clear()
    if emu_enabled:
        emu_status = '\rEmulation is ACTIVE.            \n'
        if sound_enable:
            winsound.Beep(3000, 20)
    else:
        emu_status = '\rEmulation is inactive.          \n'
        if sound_enable:
            winsound.Beep(800, 20)
    
    print(emu_status, end='')
    time.sleep(.005)
    

def toggle_setupmode():
    """
    Toggles setup_mode flag when Setup key is pressed (CTRL+S)
    :return:
    """
    global setup_mode
    
    setup_mode = not setup_mode
    setup_status = ''
    if setup_mode:
        clear()
        setup_status = '\nEntering Setup Mode.\n'
        if sound_enable:
            winsound.Beep(3000, 20)
    else:
        sys.stdout.write('\nExiting Setup Mode.\n')
        if sound_enable:
            winsound.Beep(500, 20)
    print(setup_status)


def toggle_sound():
    """
    Turns key sound on/off
    :return:
    """
    global sound_enable
    
    sound_enable = not sound_enable
    sys.stdout.write(f'\rSound is {soundstatus[sound_enable]}              ')
    if sound_enable:
        winsound.Beep(3000, 20)
    time.sleep(0.5)
    

def check_reset():
    global keys_down
    
    reset = True
    for k in reset_key:
        if k not in keys_down:
            reset = False
            break

    if reset:
        sys.stdout.write('\rResetting Keys_Down')
        keys_down = []
        sys.stdout.write(f'\r{keys_down}            ')
        if sound_enable:
            winsound.Beep(3000, 10)
        time.sleep(0.5)


def check_sound():
    toggle = True
    for k in sound_key:
        if k not in keys_down:
            toggle = False
            break
    if toggle:
        toggle_sound()
        

def on_press(key):
    """
    Detect pressed key
    :param key:     Key pressed (KeyCode)
    :return:
    """
    global key_down
    global keys_down
    global listener
    
    listener._suppress = False
    kp = key_vk(key)
    
    if kp == activation_key:
        toggle_emulation()
    
    if emu_enabled:
        if kp not in keys_down:
            keys_down.append(kp)
            sys.stdout.write(f'\r{keys_down}            ')
            check_reset()
            check_sound()
        
            if kp == mouse_mapping['left']:
                # Left mouse button down
                click(win32con.MOUSEEVENTF_LEFTDOWN)
        
            elif kp == mouse_mapping['right']:
                # Right mouse button down
                click(win32con.MOUSEEVENTF_RIGHTDOWN)
            else:
                listener._suppress = False
    else:
        hw = window_under_cursor()
        wt = title(hw)
        got_focus = my_title == wt
        
        if kp not in keys_down:
            keys_down.append(kp)
            if emu_enabled:
                sys.stdout.write(f'\r{keys_down}            ')
        
            if got_focus and keys_down in setup_key:
                toggle_setupmode()
    # time.sleep(0.002)


def on_release(key):
    """
    Detect released key
    :param key:     Key released (KeyCode)
    :return:
    """
    global key_down
    global keys_down
    global listener
    
    kr = key_vk(key)
    
    if emu_enabled:
        if kr == mouse_mapping['left']:
            # Left mouse button up
            click(win32con.MOUSEEVENTF_LEFTUP)
        
        elif kr == mouse_mapping['right']:
            # Left mouse button up
            click(win32con.MOUSEEVENTF_RIGHTUP)

    if kr in keys_down:
        keys_down.remove(kr)
        if emu_enabled:
            sys.stdout.write(f'\r{keys_down}            ')

    # time.sleep(0.002)


def click(mouseevent):
    curpos = win32api.GetCursorPos()
    win32api.mouse_event(mouseevent, curpos[0], curpos[1], 0, 0)
    time.sleep(.005)
    if sound_enable:
        winsound.Beep(click_sound[0], click_sound[1])


def window_under_cursor():
    """
    Grabs the window under the cursor. Returns the window on success; Returns None on error
    """
    
    try:
        hw = win32gui.WindowFromPoint(win32api.GetCursorPos())
        return hw
    except win32gui.error:
        pass
    except win32api.error:
        pass


def title(hwnd):
    return win32gui.GetWindowText(hwnd)

# -----------------------------------------------------------------------------------------------------
#


my_hwnd = win32gui.GetForegroundWindow()
my_title = win32gui.GetWindowText(my_hwnd)

print_configuration()

# Get Activaton key status
if win32api.GetKeyState(activation_key):
    toggle_emulation()

if not emu_enabled:
    print('Emulation is inactive.\n')

# Listen to events until released
with Listener(on_press=on_press, on_release=on_release) as listener:  #, win32_event_filter=win32_event_filter) as listener:
    listener.join()
