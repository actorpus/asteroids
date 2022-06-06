import pygame
import win32api
import win32con
import win32gui


FUCHSIA = 255, 0, 128


def transparentify():
    hwnd = pygame.display.get_wm_info()["window"]
    win32gui.SetWindowLong(hwnd,
                           win32con.GWL_EXSTYLE,
                           win32gui.GetWindowLong(
                               hwnd,
                               win32con.GWL_EXSTYLE
                           )
                           | win32con.WS_EX_LAYERED
                           )
    win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(*FUCHSIA), 0, win32con.LWA_COLORKEY)


def fill_transparent(display):
    display.fill(FUCHSIA)
