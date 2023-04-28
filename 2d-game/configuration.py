class Font:
  NAME = "Verdana"
  SIZE = 12

class Window:
  WIDTH = 600
  HEIGTH = 800

class ASSET:
  INTRO = "./asset/intro.png"
  GAME_END = "./asset/game_end.png"

class HUD:
  TITLE = "BREAKOUT"
  HEIGTH = 40
  WIDTH = 600
  START_X = 0
  START_Y = Window.HEIGTH - HEIGTH
  COLOUR = (180, 30, 30)

  TEXT_COLOUR = (255, 255, 255, 255)
  TEXT_X = START_X + 20
  TEXT_Y = START_Y + 15

  LEVEL_TEXT = "LEVEL: "
  LEVEL_X = START_X + 300
  LEVEL_Y = TEXT_Y

  SCORE_TEXT = "SCORE: "
  SCORE_X = START_X + 450
  SCORE_Y = TEXT_Y

  GAME_END_BG_COLOUR = (255, 255, 255, 255)
  GAME_END_BG_TEXT = "You scored XX points on level YY."
  GAME_END_BG_TEXT_SIZE = 24
  GAME_END_BG_TEXT_COLOUR = (0, 0, 0, 255)
  GAME_END_BG_TEXT_X = 20
  GAME_END_BG_TEXT_Y = 400

class Brick:
  WIDTH = 40
  HEIGTH = 10
  #red, orange, green, yellow
  COLOUR = [(163, 30, 10), (194, 133, 10), (10, 133, 51), (194, 194, 42)]

class Paddle:
  WIDTH = 100
  HEIGTH = 15
  START_X = (Window.WIDTH / 2) - (WIDTH / 2)
  START_Y = 10
  #blue
  COLOUR = (10, 133, 194)
  SPEED = 15

class Ball:
  RADIUS = 7
  START_X = (Window.WIDTH / 2) + (RADIUS / 2)
  START_Y = Paddle.START_Y + Paddle.HEIGTH + RADIUS
  COLOUR = (255, 255, 255)
  START_DIR_X = 1
  START_DIR_Y = 1

class World:
  START_X = 0
  END_X = Window.WIDTH
  START_Y = 0
  END_Y = Window.HEIGTH - HUD.HEIGTH
  COLOUR = (11, 11, 11)

class Input:
  PORT = 5700

class Level1:
  BALL_SPEED = 5
  BRICKS_PER_ROW = 14
  COLUMNS = 8
  START_X = World.START_X
  START_Y = World.END_Y - 40
  GAP = (Window.WIDTH - (BRICKS_PER_ROW * Brick.WIDTH)) / (BRICKS_PER_ROW - 1)
  