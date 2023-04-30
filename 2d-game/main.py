import os
from typing import Callable, TypedDict
from enum import Enum

from DIPPID import SensorUDP
from pyglet import window, app, image
from pyglet.text import Label
from pyglet.sprite import Sprite
from pyglet.shapes import *
from pyglet.graphics import Batch
from pyglet.math import Vec2
from pyglet.clock import schedule_once

import configuration as C

'''
  Ideas for Naming:
  - https://en.wikipedia.org/wiki/Breakout_(video_game)

  Image References:
  - sternenhimmel: https://unsplash.com/@guillepozzi
  - M5Stack: http://mac.x0.com/39mag.benesse.ne.jp/lifestyle/content/?TczWH/forgive710609/72of6tlo8yw
  
'''

#code reference: https://docs.pyglet.org/en/latest/programming_guide/resources.html: avoid that the resource can not be found due to starting the game from a different path. therefore introducing relative path to the resources folder.
script_dir = os.path.dirname(__file__)

class AppState(Enum):
  START = 1
  GAME = 2
  END = 3
  EXIT = 4

class Ball(Circle):

  def __init__(self, velocity: float, batch: Batch) -> None:
    super().__init__(x=C.Ball.START_X, y=C.Ball.START_Y, radius=C.Ball.RADIUS, color=C.Colour.BALL, batch=batch)
    self.dir_x = C.Ball.START_DIR_X
    self.dir_y = C.Ball.START_DIR_Y
    self.velocity = velocity

  def move(self) -> None:
    self.x = self.x + (self.dir_x * self.velocity)
    self.y = self.y + (self.dir_y * self.velocity)

  def change_dir_x(self, direction=-1) -> None:
    self.dir_x = self.dir_x * direction

  def change_dir_y(self, direction=-1) -> None:
    self.dir_y = self.dir_y * direction

  def check_distance(self, p_1: Vec2, p_2: Vec2) -> bool:
    '''
      calculate the distance between a side represented by two vectors and the ball. reducing the distance between the side and the center of the ball by the radius of the ball, yields if the ball collided with a side.
    '''
    ball_to_p1 = Vec2(p_1.x - self.x, p_1.y - self.y)
    ball_to_p2 = Vec2(p_2.x - self.x, p_2.y - self.y)

    cross_product = ball_to_p1.x * ball_to_p2.y - ball_to_p1.y * ball_to_p2.x

    distance = abs(cross_product) / ball_to_p1.distance(ball_to_p2)

    return distance - self.radius < 0

class World:
  def __init__(self) -> None:
    self.top_left = Vec2(C.World.START_X, C.World.END_Y)
    self.top_right = Vec2(C.World.END_X, C.World.END_Y)
    self.bot_left = Vec2(C.World.START_X, C.World.START_Y)
    self.bot_right = Vec2(C.World.END_X, C.World.START_Y)

  def collides_with(self, ball: Ball, on_game_over: Callable[[], None]) -> None:
    if ball.check_distance(self.bot_left, self.top_left):
      ball.change_dir_x()

    elif ball.check_distance(self.bot_right, self.top_right):
      ball.change_dir_x()

    elif ball.check_distance(self.top_left, self.top_right):
      ball.change_dir_y()

    elif ball.check_distance(self.bot_left, self.bot_right):
      on_game_over()

class Paddle(Rectangle):

  def __init__(self, velocity: float, batch: Batch) -> None:
    super().__init__(x=C.Paddle.START_X, y=C.Paddle.START_Y, width=C.Paddle.WIDTH, height=C.Paddle.HEIGTH, color=C.Colour.PADDLE, batch=batch)
    self._velocity = velocity
    '''
      after the paddle is hit it get immunity to interaction with the ball, therefore there are no possible further bounces in a defined timeframe. this is due to a bug where the ball sticks and flows over the paddle when it hit the paddle in a certain angle while the paddle is moving. immunity enforces that the ball left the area until the paddle can interact again.
    '''
    self._immunity = False

  def move(self, acc_x: float, world: World) -> None:
    new_x = self.x + (acc_x * self._velocity)

    if new_x >= world.bot_left.x and new_x <= world.bot_right.x - self.width:
      self.x = new_x

  def _reset_immunity(self, dt) -> None:
    self._immunity = False

  def collides_with(self, ball: Ball) -> None:
    if self._immunity:
      return
    
    v_top_right = Vec2(self.x + self.width, self.y + self.height)
    v_top_left = Vec2(self.x, self.y + self.height)
    v_bot_left = Vec2(self.x, self.y)
    v_bot_right = Vec2(self.x + self.width, self.y)

    if ball.check_distance(v_top_left, v_top_right) and self.x <= ball.x and self.x + self.width >= ball.x:
        ball.change_dir_y()
        self._immunity = True
        schedule_once(func=self._reset_immunity, delay=C.Paddle.IMMUNITY)

    #hitting the ball with the sides of the paddle pushes it straight back instead of bouncing it of with the negative angle which would lead to game over.
    elif (ball.check_distance(v_bot_left, v_top_left) or ball.check_distance(v_bot_right, v_top_right)) and self.y <= ball.y and self.y + self.height >= ball.y:
      ball.change_dir_y()
      ball.change_dir_x()

      self._immunity = True
      schedule_once(func=self._reset_immunity, delay=C.Paddle.IMMUNITY)

class Brick(Rectangle):

  def __init__(self, x: float, y: float, colour: tuple[int, int, int], batch: Batch) -> None:
    super().__init__(x=x, y=y, width=C.Brick.WIDTH, height=C.Brick.HEIGTH, color=colour, batch=batch)

  def collides_with(self, ball: Ball) -> bool:
    v_bot_left = Vec2(self.x, self.y)
    v_bot_right = Vec2(self.x + self.width, self.y)
    v_top_right = Vec2(self.x + self.width, self.y + self.height)
    v_top_left = Vec2(self.x, self.y + self.height)
    
    if ball.check_distance(v_bot_left, v_bot_right) and v_bot_left.x <= ball.x and v_bot_right.x >= ball.x:
      ball.change_dir_y()
      self.delete()

      return True

    elif ball.check_distance(v_top_left, v_top_right) and v_top_left.x <= ball.x and v_top_right.x >= ball.x:
      ball.change_dir_y()
      self.delete()

      return True

    elif ball.check_distance(v_bot_left, v_top_left) and v_bot_left.y <= ball.y and v_top_left.y >= ball.y:
        ball.change_dir_x()
        self.delete()

        return True
          
    elif ball.check_distance(v_bot_right, v_top_right) and v_bot_right.y <= ball.y and v_top_right.y >= ball.y:
        ball.change_dir_x()
        self.delete()

        return True

    return False

class Input:

  T_Input_State = TypedDict('InputState', { 'acc_x': float, 'button_1': bool, 'button_2': bool })

  def __init__(self) -> None:
    self._sensor = SensorUDP(C.Input.PORT)
    self._button_pressed = {
      'button_1': False,
      'button_2': False
    }

  def _get_acc_x(self) -> float:
    '''
      sensor might return a None value that raises an exception when trying to cast to float returning 0 in the case.
    '''
    try:
      return float(self._sensor.get_value('accelerometer')['x'])
    except:
      return 0
  
  def _get_button(self, button_name: str) -> bool:
    '''
      returns boolean value that indicates if button_1 from M5Stack was pressed. if M5Stack returns a value that can not be type cast to boolean, it returns `False`. As M5Stack returns `True` as long as a button is held, therefore button_1_pressed was introduced. all `True` values except the first and until the button is released are turned to `False`. Therefore get_button_1 only returns `True` once for the switch from not pressed to pressed. button_1 is used to quit the game and only one `True` value is required for that.
    '''
    try:
      pressed = bool(self._sensor.get_value(button_name))

      if pressed and not self._button_pressed[button_name]:
        self._button_pressed[button_name] = True

        return True
      
      elif not pressed and self._button_pressed[button_name]:
        self._button_pressed[button_name] = False

      return False

    except:
      return False
  
  def get_state(self) -> T_Input_State:
    acc_x = self._get_acc_x()
    button_1 = self._get_button('button_1')
    button_2 = self._get_button('button_2')

    return {
      'acc_x': acc_x,
      'button_1': button_1,
      'button_2': button_2
    }

class HUD:
  def __init__(self, batch: Batch) -> None:
    path = os.path.join(script_dir, C.Asset.BACKGROUND)
    background_image = image.load(path)
    self._background_sprite = Sprite(img=background_image, x=0, y=0, batch=batch)
    self._background_hud = Rectangle(x=C.HUD.START_X, y=C.HUD.START_Y, width=C.HUD.WIDTH, height=C.HUD.HEIGTH, color=C.Colour.HUD, batch=batch)
    self._game_name = Label(text=C.HUD.TITLE, font_name=C.Font.NAME, font_size=C.Font.SMALL, color=C.Colour.TEXT, x=C.HUD.TEXT_X, y=C.HUD.TEXT_Y, bold=True, batch=batch)
    self._game_level = Label(text=f"{C.HUD.LEVEL_TEXT} 1", font_name=C.Font.NAME, font_size=C.Font.SMALL, color=C.Colour.TEXT, x=C.HUD.LEVEL_X, y=C.HUD.LEVEL_Y, batch=batch)
    self._game_score = Label(text=f"{C.HUD.SCORE_TEXT} 0", font_name=C.Font.NAME, font_size=C.Font.SMALL, color=C.Colour.TEXT, x=C.HUD.SCORE_X, y=C.HUD.SCORE_Y, batch=batch)

  def update_level(self, level: int) -> None:
    self._game_level.text = f"{C.HUD.LEVEL_TEXT} {level}"

  def update_score(self, score: int) -> None:
    self._game_score.text = f"{C.HUD.SCORE_TEXT} {score}"

class Menu:
  def __init__(self) -> None:
    path = os.path.join(script_dir, C.Asset.GAME_END)
    game_end_image = image.load(path)
    self._game_end_sprite = Sprite(img=game_end_image, x=0, y=0, z=10)

    path = os.path.join(script_dir, C.Asset.INTRO)
    intro_image = image.load(path)
    self._intro_sprite = Sprite(img=intro_image, x=0, y=0, z=10)

    self._game_end_level = Label(text=C.HUD.GAME_END_TEXT_LEVEL, font_name=C.Font.NAME, font_size=C.Font.LARGE, bold=True, color=C.Colour.TEXT, x=C.HUD.GAME_END_TEXT_X, y=C.HUD.GAME_END_TEXT_LEVEL_Y, z=11)
    self._game_end_score = Label(text=C.HUD.GAME_END_TEXT_SCORE, font_name=C.Font.NAME, font_size=C.Font.LARGE, bold=True, color=C.Colour.TEXT, x=C.HUD.GAME_END_TEXT_X, y=C.HUD.GAME_END_TEXT_SCORE_Y, z=11)

  def show_game_end(self, level: int, score: int) -> None:
    self._game_end_sprite.draw()
    self._game_end_level.text = C.HUD.GAME_END_TEXT_LEVEL.replace("XXX", str(level))
    self._game_end_score.text = C.HUD.GAME_END_TEXT_SCORE.replace("XXX", str(score))

    self._game_end_level.x = C.Window.WIDTH / 2 - (self._game_end_level.content_width / 2)
    self._game_end_score.x = C.Window.WIDTH / 2 - (self._game_end_score.content_width / 2)

    self._game_end_level.draw()
    self._game_end_score.draw()

  def show_intro(self) -> None:
    self._intro_sprite.draw()

class Game:

  def init(self) -> None:
    self.levels = [C.Level1, C.Level2, C.Level3]
    self.level = 1
    self.score = 0

    self.batch = Batch()
    self.world = World()
    self.hud = HUD(self.batch)
    self.ball = Ball(self.levels[0].BALL_VELOCITY, self.batch)
    self.paddle = Paddle(C.Paddle.VELOCITY, self.batch)
    self.bricks = []
    self._init_bricks(self.levels[0].MAP)

  def _init_bricks(self, bricks_map: list[list]) -> None:
    self.bricks = []

    for row_key, row_val in enumerate(bricks_map):
      for col_key, col_val in enumerate(row_val):
        if col_val is not None:
          x = C.Brick.START_X + col_key * C.Brick.WIDTH + (col_key - 1) * C.Brick.GAP
          y = C.Brick.START_Y - row_key * C.Brick.HEIGTH - (row_key - 1) * C.Brick.GAP
          self.bricks.append(Brick(x=x, y=y, colour=col_val, batch=self.batch))
  
  def run(self, acc_x: float, on_game_over: Callable[[], None]) -> None:
    self.paddle.move(acc_x, self.world)
    self.ball.move()

    self._check_collisions(on_game_over)

    if len(self.bricks) == 0:
      if len(self.levels) == self.level:
        on_game_over()
      else:
        self._next_level()

    self.batch.draw()

  def _next_level(self) -> None:
    self.level = self.level + 1
    self.hud.update_level(self.level)
    self.ball.velocity = self.levels[self.level - 1].BALL_VELOCITY
    self._init_bricks(self.levels[self.level - 1].MAP)


  def _check_collisions(self, on_game_over: Callable[[], None]) -> None:
    self.world.collides_with(self.ball, on_game_over)
    self.paddle.collides_with(self.ball)
    for brick in self.bricks:
      if brick.collides_with(self.ball):
        self.bricks.remove(brick)
        self.score = self.score + 1
        self.hud.update_score(self.score)

class Application():

  def __init__(self):
    self.window = window.Window(C.Window.WIDTH, C.Window.HEIGTH)
    #code reference: https://stackoverflow.com/a/24641645: how to manually apply a decorator so that you can use on draw in a class.
    self.on_draw = self.window.event(self.on_draw)
    
    self.input = Input()
    self.game = Game()
    self.menu = Menu()
    self.input_state = self.input.get_state()
    self.app_state = AppState.START
  
  def run(self) -> None:
    app.run()

  def _on_game_over(self) -> None:
    self.app_state = AppState.END

  def on_draw(self) -> None:
    self.window.clear()

    self.input_state = self.input.get_state()

    #process button presses
    if self.input_state['button_1']:
      self.app_state = AppState.EXIT
    
    elif self.input_state['button_2']:
      self.app_state = AppState.GAME
      self.game.init()

    #appstate defines if intro, game or game_end screen is shown
    if self.app_state == AppState.START:
      self.menu.show_intro()

    elif self.app_state == AppState.END:
      self.menu.show_game_end(self.game.level, self.game.score)

    elif self.app_state == AppState.EXIT:
      #Code Reference: https://stackoverflow.com/a/76374: choosing to use os._exit() here because pyglet.app.exit() does not terminate the application, while window.close() produced an error. quit() and exit() also did not work. this might be due to the event loop running in a different thread.
      os._exit(0)

    elif self.app_state == AppState.GAME:
      self.game.run(self.input_state['acc_x'], self._on_game_over)

application = Application()
application.run()