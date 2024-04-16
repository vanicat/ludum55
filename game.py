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
        self.change_x = 0
        self.change_y = 0
        if arcade.key.W in self.game.keys or arcade.key.UP in self.game.keys:
            self.change_y = 1
        if arcade.key.A in self.game.keys or arcade.key.LEFT in self.game.keys:
            self.change_x = -1
        if arcade.key.S in self.game.keys or arcade.key.DOWN in self.game.keys:
            self.change_y = -1
        if arcade.key.D in self.game.keys or arcade.key.RIGHT in self.game.keys:
            self.change_x = 1

        if self.change_x and self.change_y:
            self.change_y *= INV_SQRT2
            self.change_x *= INV_SQRT2

        self.center_x += self.change_x
        if self.collides_with_list(self.game.cur_scene["Wall"]):
            self.center_x -= self.change_x

        self.center_y += self.change_y        
        if self.collides_with_list(self.game.cur_scene["Wall"]):
            self.center_y -= self.change_y

        assert not(self.collides_with_list(self.game.cur_scene["Wall"]))
    

        return super().on_update(delta_time)


class Monster(arcade.Sprite):
    def __init__(self, species:arcadeLDtk.EnumValue, *, center_x:float, center_y:float, path:list[tuple[float, float]], speed:float=10):
        super().__init__(species.tile, center_x=center_x, center_y=center_y)
        self.path = path
        self.next_index = 0
        self.speed = speed
        self.next_point()
    
    def next_point(self):
        self.start = (self.center_x, self.center_y)
        self.end = self.path[self.next_index]
        self.next_index = (self.next_index + 1) % len(self.path)
        self.dist = arcade.math.get_distance(*self.start, *self.end)
        self.temps = 0
        self.duree = self.dist / self.speed

    def on_update(self, delta_time: float = 1 / 60) -> None:
        self.temps += delta_time
        if self.temps >= self.duree:
            self.next_point()
        x, y = arcade.math.lerp_2d(self.start, self.end, self.temps/self.duree)
        self.center_x = x
        self.center_y = y
        return super().on_update(delta_time)


class Invocator(arcade.Sprite):
    desc: arcadeLDtk.EntityInstance
    time: float
    path: list[tuple[float, float]]
    scene: arcade.Scene

    def __init__(self, scene:arcade.Scene, entity:arcadeLDtk.EntityInstance):
        self.desc = entity
        self.path = entity.fields["Patrol"].value
        self.repeat = entity.fields["Repeat"].value
        self.time = self.repeat
        species_type = entity.fields["Specie"].type[len("LocalEnum")+1:]
        enum_type = entity.defs.enums[species_type].values
        self.species = enum_type[entity.fields["Specie"].value]

        self.scene = scene

        super().__init__(entity.def_.tile, center_x=entity.px[0], center_y=entity.px[1])


    def on_update(self, delta_time: float = 1 / 60) -> None:
        self.time += delta_time
        if self.time > self.repeat:
            self.scene.add_sprite("Monster", Monster(self.species, center_x=self.center_x, center_y=self.center_y, path=self.path))
            self.time -= self.repeat
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
        self.keys = set()

        self.start_level(start_level, start.px)

    def camera_to_player(self):
        self.camera.left = max(0, self.player.center_x - self.camera.viewport_width / (2 * ZOOM))
        if self.camera.right > self.cur_level.width:
            self.camera.right = self.cur_level.width
            
        self.camera.bottom = max(0, self.player.center_y - self.camera.viewport_height / (2 * ZOOM))
        if self.camera.top > self.cur_level.height:
            self.camera.top = self.cur_level.height


    def start_level(self, start_level:arcadeLDtk.Level, pos:tuple[float, float]):
        self.cur_level = start_level
        self.cur_scene = self.cur_level.make_scene()
        self.cur_scene.add_sprite_list("Invocation")
        self.cur_scene.add_sprite_list("Monster")
        for entity in self.cur_level.layers_by_identifier["Invocations"].entity_list:
            self.cur_scene.add_sprite("Invocation", Invocator(self.cur_scene, entity))
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
        if not self.cur_level.contains_coord(self.player.center_x, self.player.center_y):
            x, y = self.cur_level.to_world_coord(self.player.center_x, self.player.center_y)
            levels = self.world.get_levels_at_point(x, y)   
            if len(levels) != 1:
                raise NotImplementedError("level not implemeted here: there be dragon") 
            level = levels[0]
            self.start_level(level, level.from_world_coord(x, y))
            
        self.camera_to_player()
        return super().on_update(delta_time)

    def on_key_press(self, symbol: int, modifiers: int):
        self.keys.add(symbol)
        return super().on_key_press(symbol, modifiers)
    
    def on_key_release(self, symbol: int, _modifiers: int):
        if symbol in self.keys:
            self.keys.remove(symbol)
        return super().on_key_release(symbol, _modifiers)