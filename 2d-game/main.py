import configuration as C
from pyglet import window, app, shapes, text, image, sprite
from DIPPID import SensorUDP
from enum import Enum
from typing import Callable
import math,os

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

class Point:
  def __init__(self, x: float, y: float) -> None:
    self.x = x
    self.y = y

class World:
  def __init__(self) -> None:
    self.top_left = Point(C.World.START_X, C.World.END_Y)
    self.top_right = Point(C.World.END_X, C.World.END_Y)
    self.bot_left = Point(C.World.START_X, C.World.START_Y)
    self.bot_right = Point(C.World.END_X, C.World.START_Y)

class Ball:
  def __init__(self, speed: float) -> None:
    self.radius = C.Ball.RADIUS
    self.ball = shapes.Circle(x=C.Ball.START_X, y=C.Ball.START_Y, radius=self.radius, color=C.Ball.COLOUR)
    self.dir_x = C.Ball.START_DIR_X
    self.dir_y = C.Ball.START_DIR_Y
    self.speed = speed

  def move(self) -> None:
    self.ball.x = self.ball.x + (self.dir_x * self.speed)
    self.ball.y = self.ball.y + (self.dir_y * self.speed)
                                 
  def draw(self) -> None:
    self.ball.draw()

  def change_direction(self, x: float, y: float) -> None:
    self.dir_x = x
    self.dir_y = y
  
  def get_coordinates(self) -> tuple[float, float, float]:
    return (self.ball.x, self.ball.y, self.ball.radius)

class Paddle:
  def __init__(self, speed: float) -> None:
    self.top_left = Point(C.Paddle.START_X,  C.Paddle.START_Y + C.Paddle.HEIGTH)
    self.top_right = Point(C.Paddle.START_X + C.Paddle.WIDTH, C.Paddle.START_Y + C.Paddle.HEIGTH)
    self.bot_left = Point(C.Paddle.START_X, C.Paddle.START_Y)
    self.bot_right = Point(C.Paddle.START_X + C.Paddle.WIDTH, C.Paddle.START_Y)
  
    self.paddle = shapes.Rectangle(x=C.Paddle.START_X, y=C.Paddle.START_Y, width=C.Paddle.WIDTH, height=C.Paddle.HEIGTH, color=C.Paddle.COLOUR)
    self.speed = speed
  
  def draw(self) -> None:
    self.paddle.draw()

  def move(self, angle_x: float, world: World) -> None:
    new_x = self.paddle.x + (angle_x * self.speed)

    if new_x >= world.bot_left.x and new_x <= world.bot_right.x - self.paddle.width:
      self.paddle.x = new_x

      self.top_left.x = self.paddle.x
      self.top_right.x = self.paddle.x + C.Paddle.WIDTH
      self.bot_left.x = self.paddle.x
      self.bot_right.x = self.paddle.x + C.Paddle.WIDTH

  def collides_with(self, ball: Ball) -> bool:
    ball_x, _, _ = ball.get_coordinates()

    return self.top_left.x <= ball_x and self.top_right.x >= ball_x

class Brick:
  def __init__(self, x: float, y: float, colour: tuple[int, int, int]) -> None:
    self.top_left = Point(x,  y + C.Brick.HEIGTH)
    self.top_right = Point(x + C.Brick.WIDTH, y + C.Brick.HEIGTH)
    self.bot_left = Point(x, y)
    self.bot_right = Point(x + C.Brick.WIDTH, y)

    self.brick = shapes.Rectangle(x=x, y=y, width=C.Brick.WIDTH, height=C.Brick.HEIGTH, color=colour)
   
  def draw(self) -> None:
    self.brick.draw()
  
  def delete(self) -> None:
    self.brick.delete()

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
  def __init__(self) -> None:
    self.background_hud = shapes.Rectangle(x=C.HUD.START_X, y=C.HUD.START_Y, width=C.HUD.WIDTH, height=C.HUD.HEIGTH, color=C.HUD.COLOUR)
    self.game_name = text.Label(text=C.HUD.TITLE, font_name=C.Font.NAME, font_size=C.Font.SIZE, color=C.HUD.TEXT_COLOUR, x=C.HUD.TEXT_X, y=C.HUD.TEXT_Y, bold=True)
    self.game_level = text.Label(text=f"{C.HUD.LEVEL_TEXT} 1", font_name=C.Font.NAME, font_size=C.Font.SIZE, color=C.HUD.TEXT_COLOUR, x=C.HUD.LEVEL_X, y=C.HUD.LEVEL_Y)
    self.game_score = text.Label(text=f"{C.HUD.SCORE_TEXT} 0", font_name=C.Font.NAME, font_size=C.Font.SIZE, color=C.HUD.TEXT_COLOUR, x=C.HUD.SCORE_X, y=C.HUD.SCORE_Y)

  def draw(self) -> None:
    self.background_hud.draw()
    self.game_name.draw()
    self.game_level.draw()
    self.game_score.draw()

  def update_level(self, level: int) -> None:
    self.game_level.text = f"{C.HUD.LEVEL_TEXT} {level}"

  def update_score(self, score: int) -> None:
    self.game_score.text = f"{C.HUD.SCORE_TEXT} {score}"

class Menu:
  def __init__(self) -> None:
    self._game_end_image = image.load(C.ASSET.GAME_END)
    self.game_end_sprite = sprite.Sprite(img=self._game_end_image, x=0, y=0, z=10)

    self._intro_image = image.load(C.ASSET.INTRO)
    self.intro_sprite = sprite.Sprite(img=self._intro_image, x=0, y=0, z=10)

    self._game_end_label = text.Label(text=C.HUD.GAME_END_BG_TEXT, font_name=C.Font.NAME, font_size=C.HUD.GAME_END_BG_TEXT_SIZE, bold=True, color=C.HUD.GAME_END_BG_TEXT_COLOUR, x=C.HUD.GAME_END_BG_TEXT_X, y=C.HUD.GAME_END_BG_TEXT_Y, z=11)

  def show_game_end(self, score: int, level: int) -> None:
    self.game_end_sprite.draw()
    self._game_end_label.text = C.HUD.GAME_END_BG_TEXT.replace("XX", str(score)).replace("YY", str(level))
    self._game_end_label.draw()

  def show_intro(self) -> None:
    self.intro_sprite.draw()

class Game:

  def init(self):
    self.world = World()
    self.hud = HUD()
    self.ball = Ball(C.Level1.BALL_SPEED)
    self.paddle = Paddle(C.Paddle.SPEED)
    self.bricks = self._init_bricks()

    self.level = 1
    self.score = 0

  def _init_bricks(self) -> list[Brick]:
    brick_list = []

    for row in range(C.Level1.BRICKS_PER_ROW):
      for col in range(C.Level1.COLUMNS):
        brick_list.append(Brick(C.Level1.START_X + row * C.Brick.WIDTH + (row - 1) * C.Level1.GAP, C.Level1.START_Y - (col * C.Brick.HEIGTH + (col - 1) * C.Level1.GAP), C.Brick.COLOUR[1]))

    return brick_list

  def _check_collision_side(self, p_1: Point, p_2: Point, ball: Ball) -> bool:
    ball_x, ball_y, ball_radius = ball.get_coordinates()
    ball_to_p1 = (p_1.x - ball_x, p_1.y - ball_y)
    ball_to_p2 = (p_2.x - ball_x, p_2.y - ball_y)

    cross_product = ball_to_p1[0] * ball_to_p2[1] - ball_to_p1[1] * ball_to_p2[0]

    distance = abs(cross_product) / math.dist(ball_to_p1, ball_to_p2)    

    return distance - ball_radius <= 0
  
  def _check_boundry(self, p_1: Point, p_2: Point, ball: Ball) -> bool:
    ball_x, ball_y, ball_radius = ball.get_coordinates()

    if p_1.x <= ball_x + ball_radius and p_2.x >= ball_x - ball_radius:
      return True
    
    elif p_1.y <= ball_y + ball_radius and p_2.y >= ball_y - ball_radius:
      return True
  
    return False

  def _remove_brick(self, brick: Brick) -> None:
    brick.delete()
    self.bricks.remove(brick)
    self.score = self.score + 1
    self.hud.update_score(self.score)

  def _check_collision(self, on_game_over: Callable[[], None]) -> None:
    if self._check_collision_side(self.world.bot_left, self.world.top_left, self.ball) or self._check_collision_side(self.world.bot_right, self.world.top_right, self.ball):
      self.ball.change_direction(x=(self.ball.dir_x * - 1), y=self.ball.dir_y)

    elif self._check_collision_side(self.world.top_left, self.world.top_right, self.ball):
      self.ball.change_direction(x=self.ball.dir_x, y=(self.ball.dir_y * - 1))

    elif self._check_collision_side(self.world.bot_left, self.world.bot_right, self.ball):
      on_game_over()

    #change ejecting angle depending on distance from mid hit
    elif self._check_collision_side(self.paddle.top_left, self.paddle.top_right, self.ball):
      if self.paddle.collides_with(self.ball):
        self.ball.change_direction(x=self.ball.dir_x, y=(self.ball.dir_y * - 1)) 

    else:
      ball_x, ball_y, _ = self.ball.get_coordinates()
      for brick in self.bricks:
        if self._check_collision_side(brick.bot_left, brick.bot_right, self.ball) and brick.bot_left.x <= ball_x and brick.bot_right.x >= ball_x:
          self.ball.change_direction(x=self.ball.dir_x, y=(self.ball.dir_y * - 1))
          self._remove_brick(brick)
        
        elif self._check_collision_side(brick.top_left, brick.top_right, self.ball) and brick.top_left.x <= ball_x and brick.top_right.x >= ball_x :
          self.ball.change_direction(x=self.ball.dir_x, y=(self.ball.dir_y * - 1))
          self._remove_brick(brick)
          
        elif self._check_collision_side(brick.bot_left, brick.top_left, self.ball) and brick.bot_left.y <= ball_y and brick.top_left.y >= ball_y :
          self.ball.change_direction(x=(self.ball.dir_x * -1), y=self.ball.dir_y)    
          self._remove_brick(brick)

        elif self._check_collision_side(brick.bot_right, brick.top_right, self.ball) and brick.bot_right.y <= ball_y and brick.top_right.y >= ball_y :
          self.ball.change_direction(x=(self.ball.dir_x * -1), y=self.ball.dir_y)
          self._remove_brick(brick)
          
  def _draw(self) -> None:
    self.hud.draw()
    self.ball.draw()
    self.paddle.draw()
    for brick in self.bricks:
      brick.draw()

  def process(self, input_acc: float, on_game_over: Callable[[], None]) -> None:
    self.paddle.move(input_acc, self.world)
    self.ball.move()
    self._check_collision(on_game_over)
    if len(self.bricks) == 0:
      on_game_over()
    self._draw()

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

  def _process_input_state(self) -> None:
    if self.input_state['button_1']:
      self.app_state = AppState.EXIT
    
    elif self.input_state['button_2']:
      self.app_state = AppState.GAME
      self.game.init()

  def _on_game_over(self):
    self.app_state = AppState.END

  def on_draw(self) -> None:
    self.window.clear()

    self.input_state = self.input.update()
    self._process_input_state()

    if self.app_state == AppState.START:
      self.menu.show_intro()

    elif self.app_state == AppState.END:
      self.menu.show_game_end(self.game.score, self.game.level)

    elif self.app_state == AppState.EXIT:
      #Code Reference: https://stackoverflow.com/a/76374: choosing to use os._exit() here because pyglet.app.exit() does not terminate the application, while window.close() produced an error. quit() and exit() also did not work. this might be due to the event loop running in a different thread.
      os._exit(0)

    else:
      self.game.process(self.input_state['acc_x'], self._on_game_over)

application = Application()
application.run()