class Input:
  PORT = 5700

class Font:
  NAME = "Verdana"
  SMALL = 15
  LARGE = 24

class Asset:
  INTRO = "./asset/intro.png"
  GAME_END = "./asset/game_end.png"
  BACKGROUND = "./asset/background.png"

class Colour:
  TEXT = (255, 255, 255, 255)
  BALL = (255, 255, 255)
  PADDLE = (10, 133, 194)
  HUD = (180, 30, 30)
  R = (163, 30, 10)
  O = (194, 133, 10)
  G = (10, 133, 51)
  Y = (194, 194, 42)

class Window:
  WIDTH = 600
  HEIGTH = 800

class HUD:
  TITLE = "BREAKOUT"
  HEIGTH = 40
  WIDTH = 600
  START_X = 0
  START_Y = Window.HEIGTH - HEIGTH

  TEXT_COLOUR = Colour.TEXT
  TEXT_X = START_X + 20
  TEXT_Y = START_Y + 15

  LEVEL_TEXT = "LEVEL: "
  LEVEL_X = START_X + 300
  LEVEL_Y = TEXT_Y

  SCORE_TEXT = "SCORE: "
  SCORE_X = START_X + 450
  SCORE_Y = TEXT_Y

  GAME_END_TEXT_LEVEL = "You reached level XXX."
  GAME_END_TEXT_SCORE = "You scored XXX points."
  GAME_END_TEXT_X = 70
  GAME_END_TEXT_LEVEL_Y = 435
  GAME_END_TEXT_SCORE_Y = 385

class World:
  START_X = 0
  END_X = Window.WIDTH
  START_Y = 0
  END_Y = Window.HEIGTH - HUD.HEIGTH

class Brick:
  WIDTH = 70
  HEIGTH = 20
  START_X = World.START_X
  START_Y = World.END_Y - 30
  BRICKS_PER_ROW = 8
  GAP = (Window.WIDTH - (BRICKS_PER_ROW * WIDTH)) / (BRICKS_PER_ROW - 1)

class Paddle:
  WIDTH = 100
  HEIGTH = 15
  START_X = (Window.WIDTH / 2) - (WIDTH / 2)
  START_Y = 10
  VELOCITY = 15
  IMMUNITY = 0.5

class Ball:
  RADIUS = 7
  START_X = (Window.WIDTH / 2) + (RADIUS / 2)
  START_Y = Paddle.START_Y + Paddle.HEIGTH + RADIUS
  START_DIR_X = 1
  START_DIR_Y = 1

class Level1:
  BALL_VELOCITY = 5
  MAP = [
    [None, None, None, None, None, None, None, None],
    [None, None, None, None, None, None, None, None],
    [None, Colour.R, Colour.R, Colour.R, Colour.R, Colour.R, Colour.R, None],
    [None, Colour.G, Colour.G, Colour.G, Colour.G, Colour.G, Colour.G, None],
    [None, None, Colour.Y, Colour.Y, Colour.Y, Colour.Y, None, None],
    [None, None, Colour.G, Colour.G, Colour.G, Colour.G, None, None],
    [None, None, None, None, None, None, None, None],
    [Colour.R, Colour.R, Colour.R, None, None, Colour.R, Colour.R, Colour.R],
    [Colour.R, Colour.R, Colour.R, None, None, Colour.R, Colour.R, Colour.R],
    [None, None, None, None, None, None, None, None],
    [None, None, None, None, None, None, None, None],
    [None, None, None, None, None, None, None, None]
  ]

class Level2:
  BALL_VELOCITY = 7
  MAP = [
    [Colour.Y, None, None, None, None, None, None, Colour.Y],
    [None, None, None, None, None, None, None, None],
    [None, Colour.G, Colour.G, Colour.G, Colour.G, Colour.G, Colour.G, None],
    [None, Colour.G, Colour.G, Colour.G, Colour.G, Colour.G, Colour.G, None],
    [Colour.Y, Colour.Y, Colour.Y, Colour.Y, Colour.Y, Colour.Y, Colour.Y, Colour.Y],
    [Colour.R, Colour.R, None, None, None, None, Colour.R, Colour.R],
    [Colour.R, Colour.R, None, None, None, None, Colour.R, Colour.R],
    [Colour.R, Colour.R, Colour.G, None, None, Colour.G, Colour.R, Colour.R],
    [Colour.R, Colour.R, Colour.G, None, None, Colour.G, Colour.R, Colour.R],
    [Colour.R, Colour.R, None, None, None, None, Colour.R, Colour.R],
    [Colour.R, Colour.R, None, Colour.Y, Colour.Y, None, Colour.R, Colour.R],
    [None, None, None, None, None, None, None, None]
  ]

class Level3:
  BALL_VELOCITY = 10
  MAP = [
    [Colour.Y, Colour.Y, Colour.Y, Colour.Y, Colour.Y, Colour.Y, Colour.Y, Colour.Y],
    [Colour.Y, Colour.Y, Colour.Y, Colour.Y, Colour.Y, Colour.Y, Colour.Y, Colour.Y],
    [None, None, None, None, None, None, None, None],
    [Colour.R, Colour.R, Colour.R, Colour.R, Colour.R, Colour.R, Colour.R, Colour.R],
    [Colour.R, Colour.R, Colour.R, Colour.R, Colour.R, Colour.R, Colour.R, Colour.R],
    [None, None, None, None, None, None, None, None],
    [Colour.G, Colour.G, Colour.G, Colour.G, Colour.G, Colour.G, Colour.G, Colour.G],
    [Colour.G, Colour.G, Colour.G, Colour.G, Colour.G, Colour.G, Colour.G, Colour.G],
    [None, None, None, None, None, None, None, None],
    [Colour.O, Colour.O, Colour.O, Colour.O, Colour.O, Colour.O, Colour.O, Colour.O],
    [Colour.O, Colour.O, Colour.O, Colour.O, Colour.O, Colour.O, Colour.O, Colour.O],
    [None, None, None, None, None, None, None, None],
    [None, None, None, None, None, None, None, None],
    [None, None, None, None, None, None, None, None]
  ]

  