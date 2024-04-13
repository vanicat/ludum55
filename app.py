from typing import Optional
from arcade.application import Window

import arcade
import arcade.gui

from arcadeLDtk import read_LDtk

from consts import *
from game import Game

class GameWindow(arcade.Window):
    """ Main Window """

    def __init__(self, width, height, title):
        """ Create the variables """

        # Init the parent class
        super().__init__(width, height, title)

        arcade.set_background_color(arcade.csscolor.CORNFLOWER_BLUE)

        self.menu = Menu(self)


    def show_menu(self, go_back = None):
        if go_back is None:
            self.show_view(self.menu)
        else:
            self.show_view(Menu(self, go_back))


class Menu(arcade.View):
    def __init__(self, window: GameWindow, go_back = None):
        super().__init__(window)

        self.manager = arcade.gui.UIManager()
        self.v_box = arcade.gui.UIBoxLayout()

        start_button = arcade.gui.UIFlatButton(text="Start Game", width=200)
        self.v_box.add(start_button)
        start_button.on_click = self.start_game # type: ignore[method-assign]

        if go_back:
            continue_button = arcade.gui.UIFlatButton(text="Continue", width=200)
            self.v_box.add(continue_button)
            continue_button.on_click = go_back # type: ignore[method-assign]

        quit_button = arcade.gui.UIFlatButton(text="Quit", width=200)
        self.v_box.add(quit_button)
        quit_button.on_click = self.quit  # type: ignore[method-assign]

        self.text = arcade.Text("""
You are on your own, no help yet
""", 100, 400, multiline=True, width = 400)

        self.manager.add(self.v_box)
        self.levels = read_LDtk("assets/maps/world.ldtk")

    def start_game(self, event):
        g = Game(self.window, self.levels)
        self.window.show_view(g)


    def quit(self, event):
        arcade.exit()

    def on_hide_view(self):
        self.manager.disable()
        self.window.set_mouse_visible(False)
        return super().on_hide_view()
    
    def on_show_view(self):
        self.manager.enable()
        self.window.set_mouse_visible(True)
        return super().on_show_view()
    
    def on_draw(self):
        self.clear()
        self.manager.draw()
        self.text.draw()


def main():
    """ Main function """
    window = GameWindow(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.show_menu()
    arcade.run()


if __name__ == "__main__":
    main()