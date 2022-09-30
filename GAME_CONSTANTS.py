"""Application configuration

TODO: Convert to YAML file
TODO: Optionally overwrite log level with command line argument to run
"""

# LOG_LEVEL can be set to any integer. ALl logs >= LOG_LEVEL will be shown.
# Here's a table of predefined log levels.
# 10 DEBUG
# 20 INFO
# 30 WARNING
# 40 ERROR
# 50 CRITICAL
LOG_LEVEL = 20

FPS = 30


# FIXME: Using even numbered tile dims causes the screen to center 0.5 tiles off
WINDOW_TILE_WIDTH = 32
WINDOW_TILE_HEIGHT = 18
TSIZE: int = 25  # Tile asset size in pixels


ANIMATIONS = True
PASSIVE_ANIMATION_SPEED_SECONDS = 1  # Speed at which sprites change without player input
PASSIVE_ANIMATION_SPEED = int(PASSIVE_ANIMATION_SPEED_SECONDS * 1000)
ANIMATION_LENGTH_SECONDS = 0.15  # Speed of a 'step' involving sprites moving between tiles
ANIMATION_LENGTH = int(ANIMATION_LENGTH_SECONDS * 1000)
