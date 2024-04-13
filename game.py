from typing import Any
import arcade
import arcade.camera.camera_2d
import arcadeLDtk

from consts import *

class Player(arcade.Sprite):
    game: "Game"

    def __init__(self, game:"Game"):
        self.game = game
        super().__init__(game.world.defs.tilesets["Player"].set[0])

    def on_update(self, delta_time: float = 1 / 60) -> None:
        self.velocity = (0, 0)
        if arcade.key.W in self.game.keys:
            self.velocity = (0, 1)
        if arcade.key.A in self.game.keys:
            self.velocity = (-1, 0)
        if arcade.key.S in self.game.keys:
            self.velocity = (0, -1)
        if arcade.key.D in self.game.keys:
            self.velocity = (1, 0)

        self.center_x += self.change_x
        self.center_y += self.change_y

        if self.collides_with_list(self.game.cur_scene["Wall"]):
            self.center_x -= self.change_x
            self.center_y -= self.change_y

            assert not(self.collides_with_list(self.game.cur_scene["Wall"]))
    

        return super().on_update(delta_time)

class Game(arcade.View):
    window: arcade.Window
    world: arcadeLDtk.LDtk
    cur_level: arcadeLDtk.Level
    cur_scene: arcade.Scene
    keys: set[int]
    
    def __init__(self, window: arcade.Window, world: arcadeLDtk.LDtk) -> None:
        super().__init__(window)

        self.window = window
        self.world = world
        start_iids = world.toc["Start"]["instancesData"][0]["iids"]
        start_level, _, start = world.get_entity(start_iids)

        self.player = Player(self)

        self.camera = arcade.camera.Camera2D()

        self.camera.zoom = ZOOM

        self.start_level(start_level, start.px)

    def camera_to_player(self):
        self.camera.left = max(0, self.player.center_x - WIDTH / 2)
        self.camera.right = min(self.cur_level.width, self.camera.right)
        self.camera.bottom = max(0, self.player.center_y - HEIGHT / 2)
        self.camera.top = min(self.cur_level.height, self.camera.top)


    def start_level(self, start_level:arcadeLDtk.Level, pos:tuple[float, float]):
        self.keys = set()
        self.cur_level = start_level
        self.cur_scene = self.cur_level.make_scene(regenerate=True)
        arcade.set_background_color(self.cur_level.bg_color)
        self.cur_scene.add_sprite("Player", self.player)
        self.player.center_x = pos[0]
        self.player.center_y = pos[1]

        self.cur_scene


    def on_draw(self):
        self.clear()
        self.camera.use()

        self.cur_scene.draw()
        return super().on_draw()
    
    def on_update(self, delta_time: float):
        self.cur_scene.on_update(delta_time)
        self.camera_to_player()
        return super().on_update(delta_time)

    def on_key_press(self, symbol: int, modifiers: int):
        self.keys.add(symbol)
        return super().on_key_press(symbol, modifiers)
    
    def on_key_release(self, symbol: int, _modifiers: int):
        self.keys.remove(symbol)
        return super().on_key_release(symbol, _modifiers)