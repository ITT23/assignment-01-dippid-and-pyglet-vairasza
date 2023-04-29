import os
from typing import Callable
from enum import Enum

from DIPPID import SensorUDP
from pyglet import window, app, image
from pyglet.text import Label
from pyglet.sprite import Sprite
from pyglet.shapes import *
from pyglet.graphics import Batch
from pyglet.math import Vec2

import configuration as C

'''
  Code References:
  - https://en.wikipedia.org/wiki/Breakout_(video_game)

  Image References:
  - sternenhimmel: https://unsplash.com/@guillepozzi
  - M5Stack: http://mac.x0.com/39mag.benesse.ne.jp/lifestyle/content/?TczWH/forgive710609/72of6tlo8yw
  
'''

class AppState(Enum):
  START = 1
  GAME = 2
  END = 3
  EXIT = 4

class Ball(Circle):

  def __init__(self, speed: float, batch: Batch) -> None:
    super().__init__(x=C.Ball.START_X, y=C.Ball.START_Y, radius=C.Ball.RADIUS, color=C.Ball.COLOUR, batch=batch)
    self.dir_x = C.Ball.START_DIR_X
    self.dir_y = C.Ball.START_DIR_Y
    self.speed = speed

  def move(self) -> None:
    self.x = self.x + (self.dir_x * self.speed)
    self.y = self.y + (self.dir_y * self.speed)

  def change_dir_x(self) -> None:
    self.dir_x = self.dir_x * - 1

  def change_dir_y(self) -> None:
    self.dir_y = self.dir_y * - 1

  def distance(self, p_1: Vec2, p_2: Vec2) -> bool:
    ball_to_p1 = Vec2(p_1.x - self.x, p_1.y - self.y)
    ball_to_p2 = Vec2(p_2.x - self.x, p_2.y - self.y)

    cross_product = ball_to_p1.x * ball_to_p2.y - ball_to_p1.y * ball_to_p2.x

    distance = abs(cross_product) / ball_to_p1.distance(ball_to_p2)

    return distance - self.radius <= 0

class World:
  def __init__(self) -> None:
    self.top_left = Vec2(C.World.START_X, C.World.END_Y)
    self.top_right = Vec2(C.World.END_X, C.World.END_Y)
    self.bot_left = Vec2(C.World.START_X, C.World.START_Y)
    self.bot_right = Vec2(C.World.END_X, C.World.START_Y)

  def collides_with(self, ball: Ball, on_game_over: Callable[[], None]) -> None:
    if ball.distance(self.bot_left, self.top_left):
      ball.change_dir_x()

    elif ball.distance(self.bot_right, self.top_right):
      ball.change_dir_x()

    elif ball.distance(self.top_left, self.top_right):
      ball.change_dir_y()

    elif ball.distance(self.bot_left, self.bot_right):
      on_game_over()

class Paddle(Rectangle):

  def __init__(self, speed: float, batch: Batch) -> None:
    super().__init__(x=C.Paddle.START_X, y=C.Paddle.START_Y, width=C.Paddle.WIDTH, height=C.Paddle.HEIGTH, color=C.Paddle.COLOUR, batch=batch)
    self.speed = speed

  def move(self, acc_x: float, world: World) -> None:
    new_x = self.x + (acc_x * self.speed)

    if new_x >= world.bot_left.x and new_x <= world.bot_right.x - self.width:
      self.x = new_x

  def collides_with(self, ball: Ball) -> None:
    v_top_right = Vec2(self.x + self.width, self.y + self.height)
    v_top_left = Vec2(self.x, self.y + self.height)

    if ball.distance(v_top_left, v_top_right) and self.x <= ball.x and self.x + self.width >= ball.x:
      ball.change_dir_y()

class Brick(Rectangle):

  def __init__(self, x: float, y: float, colour: tuple[int, int, int], batch: Batch) -> None:
    super().__init__(x=x, y=y, width=C.Brick.WIDTH, height=C.Brick.HEIGTH, color=colour, batch=batch)

  def collides_with(self, ball: Ball) -> bool:
    v_bot_left = Vec2(self.x, self.y)
    v_bot_right = Vec2(self.x + self.width, self.y)
    v_top_right = Vec2(self.x + self.width, self.y + self.height)
    v_top_left = Vec2(self.x, self.y + self.height)
    
    if ball.distance(v_bot_left, v_bot_right) and v_bot_left.x <= ball.x and v_bot_right.x >= ball.x:
      ball.change_dir_y()
      self.delete()

      return True

    elif ball.distance(v_top_left, v_top_right) and v_top_left.x <= ball.x and v_top_right.x >= ball.x:
      ball.change_dir_y()
      self.delete()

      return True

    elif ball.distance(v_bot_left, v_top_left) and v_bot_left.y <= ball.y and v_top_left.y >= ball.y:
        ball.change_dir_x()
        self.delete()

        return True
          
    elif ball.distance(v_bot_right, v_top_right) and v_bot_right.y <= ball.y and v_top_right.y >= ball.y:
        ball.change_dir_x()
        self.delete()

        return True

    return False

class Input:
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
  
  def update(self) -> dict:
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
    self.background_image = image.load(C.Asset.BACKGROUND)
    self.background_sprite = Sprite(img=self.background_image, x=0, y=0, batch=batch)
    self.background_hud = Rectangle(x=C.HUD.START_X, y=C.HUD.START_Y, width=C.HUD.WIDTH, height=C.HUD.HEIGTH, color=C.HUD.COLOUR, batch=batch)
    self.game_name = Label(text=C.HUD.TITLE, font_name=C.Font.NAME, font_size=C.Font.SIZE, color=C.HUD.TEXT_COLOUR, x=C.HUD.TEXT_X, y=C.HUD.TEXT_Y, bold=True, batch=batch)
    self.game_level = Label(text=f"{C.HUD.LEVEL_TEXT} 1", font_name=C.Font.NAME, font_size=C.Font.SIZE, color=C.HUD.TEXT_COLOUR, x=C.HUD.LEVEL_X, y=C.HUD.LEVEL_Y, batch=batch)
    self.game_score = Label(text=f"{C.HUD.SCORE_TEXT} 0", font_name=C.Font.NAME, font_size=C.Font.SIZE, color=C.HUD.TEXT_COLOUR, x=C.HUD.SCORE_X, y=C.HUD.SCORE_Y, batch=batch)

  def update_level(self, level: int) -> None:
    self.game_level.text = f"{C.HUD.LEVEL_TEXT} {level}"

  def update_score(self, score: int) -> None:
    self.game_score.text = f"{C.HUD.SCORE_TEXT} {score}"

class Menu:
  def __init__(self) -> None:
    self._game_end_image = image.load(C.Asset.GAME_END)
    self.game_end_sprite = Sprite(img=self._game_end_image, x=0, y=0, z=10)

    self._intro_image = image.load(C.Asset.INTRO)
    self.intro_sprite = Sprite(img=self._intro_image, x=0, y=0, z=10)

    self._game_end_label = Label(text=C.HUD.GAME_END_BG_TEXT, font_name=C.Font.NAME, font_size=C.HUD.GAME_END_BG_TEXT_SIZE, bold=True, color=C.HUD.GAME_END_BG_TEXT_COLOUR, x=C.HUD.GAME_END_BG_TEXT_X, y=C.HUD.GAME_END_BG_TEXT_Y, z=11)

  def show_game_end(self, score: int, level: int) -> None:
    self.game_end_sprite.draw()
    self._game_end_label.text = C.HUD.GAME_END_BG_TEXT.replace("XX", str(score)).replace("YY", str(level))
    self._game_end_label.draw()

  def show_intro(self) -> None:
    self.intro_sprite.draw()

class Game:

  def init(self) -> None:
    self.batch = Batch()
    self.world = World()
    self.hud = HUD(self.batch)
    self.ball = Ball(C.Level1.BALL_SPEED, self.batch)
    self.paddle = Paddle(C.Paddle.SPEED, self.batch)
    self.bricks = self._init_bricks()

    self.level = 1
    self.score = 0

  def _init_bricks(self) -> list[Brick]:
    brick_list = []

    for row in range(C.Level1.BRICKS_PER_ROW):
      for col in range(C.Level1.COLUMNS):
        brick_list.append(Brick(C.Level1.START_X + row * C.Brick.WIDTH + (row - 1) * C.Level1.GAP, C.Level1.START_Y - (col * C.Brick.HEIGTH + (col - 1) * C.Level1.GAP), C.Brick.COLOUR[1], self.batch))

    return brick_list
  
  def process(self, acc_x: float, on_game_over: Callable[[], None]) -> None:
    self.paddle.move(acc_x, self.world)
    self.ball.move()

    self._check_collisions(on_game_over)

    if len(self.bricks) == 0:
      on_game_over()

    self.batch.draw()

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
    self.input_state = self.input.update()
    self.app_state = AppState.START
  
  def run(self) -> None:
    app.run()

  def process_input_state(self) -> None:
    if self.input_state['button_1']:
      self.app_state = AppState.EXIT
    
    elif self.input_state['button_2']:
      self.app_state = AppState.GAME
      self.game.init()

  def on_game_over(self) -> None:
    self.app_state = AppState.END

  def on_draw(self) -> None:
    self.window.clear()

    self.input_state = self.input.update()
    self.process_input_state()

    if self.app_state == AppState.START:
      self.menu.show_intro()

    elif self.app_state == AppState.END:
      self.menu.show_game_end(self.game.score, self.game.level)

    elif self.app_state == AppState.EXIT:
      #Code Reference: https://stackoverflow.com/a/76374: choosing to use os._exit() here because pyglet.app.exit() does not terminate the application, while window.close() produced an error. quit() and exit() also did not work. this might be due to the event loop running in a different thread.
      os._exit(0)

    else:
      self.game.process(self.input_state['acc_x'], self.on_game_over)

application = Application()
application.run()