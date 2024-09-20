import curses
import random
import locale
import time

# Directions for movement
UP = 'UP'
DOWN = 'DOWN'
LEFT = 'LEFT'
RIGHT = 'RIGHT'

# Global high score tracking
high_score = 0

# Initialize the game setup
def setup():
    locale.setlocale(locale.LC_ALL, '')
    stdscr = curses.initscr()
    curses.cbreak()
    curses.noecho()
    stdscr.keypad(True)
    stdscr.timeout(100)  # Start with a slow speed, can be increased for difficulty
    curses.curs_set(0)

    height, width = stdscr.getmaxyx()
    width = (width + 1) // 2

    # Snake setup
    snk = [(width // 2, height // 2)]
    length = 1
    direction = RIGHT

    # Food setup
    food_x, food_y = place_food(snk, width, height)

    # Initial game variables
    gameover = False
    score = 0
    level = 1
    speed = 100  # Initial speed

    random.seed(time.time())

    return stdscr, height, width, snk, length, direction, food_x, food_y, gameover, score, level, speed

# Function to place food on the screen
def place_food(snake, width, height):
    while True:
        food_x = random.randint(0, width - 2)  # Avoid placing food on the boundary
        food_y = random.randint(1, height - 2)  # Avoid placing food on the boundary
        if (food_x, food_y) not in snake:
            return food_x, food_y

# Function to handle snake movement and boundary logic for each level
def move_snake(snake, direction, width, height, level, grow=False):
    head_x, head_y = snake[0]
    
    if direction == UP:
        head_y -= 1
    elif direction == DOWN:
        head_y += 1
    elif direction == LEFT:
        head_x -= 1
    elif direction == RIGHT:
        head_x += 1

    # Apply boundary conditions based on the level
    if level == 1:
        head_x %= width
        head_y %= height
    elif level == 2 or level == 3:
        if head_x < 0 or head_x >= width or head_y < 1 or head_y >= height - 1:
            return None  # Game over if boundary is hit
    
    new_head = (head_x, head_y)
    
    # If snake eats food, don't remove the tail (grow snake)
    if grow:
        return [new_head] + snake
    else:
        return [new_head] + snake[:-1]

# Check if snake ate the food
def check_food(snake, food_x, food_y):
    return snake[0][0] == food_x and snake[0][1] == food_y

# Function to handle level progression
def level_up(stdscr, score, level, speed):
    if score >= level * 10:  # Increase level every 10 points
        level += 1
        speed -= 10  # Increase speed by reducing timeout (higher difficulty)
        show_level_message(stdscr, level)
        return level, max(speed, 30)  # Make sure the speed doesn’t go too fast (min 30 ms)
    return level, speed

# Display a message on level up
def show_level_message(stdscr, level):
    stdscr.clear()
    stdscr.addstr(5, 10, f"Level {level} - Press Enter to start!")
    stdscr.addstr(7, 10, f"Threshold: {level * 10}")  # Show threshold value
    stdscr.refresh()
    while True:
        key = stdscr.getch()
        if key == 10:  # Enter key to continue
            break

# Main game function
def game_loop(stdscr):
    global high_score

    stdscr, height, width, snake, length, direction, food_x, food_y, gameover, score, level, speed = setup()

    while not gameover:
        # Render the game state
        stdscr.clear()
        stdscr.addstr(0, 0, f'Score: {score}  Level: {level}  High Score: {high_score}  Threshold: {level * 10}')  # Display threshold next to high score

        # Draw the snake (using '■' for the snake body)
        for (x, y) in snake:
            stdscr.addch(y, x * 2, '■')

        # Draw the food (using '●' as the food ball)
        stdscr.addch(food_y, food_x * 2, '●')

        # Draw red boundary in level 2
        if level == 2:
            for x in range(width):
                stdscr.addch(1, x * 2, '-')  # Top boundary
                stdscr.addch(height - 2, x * 2, '-')  # Bottom boundary
            for y in range(1, height - 1):
                stdscr.addch(y, 0, '|')  # Left boundary
                stdscr.addch(y, (width - 1) * 2, '|')  # Right boundary

        # Handle input for movement
        key = stdscr.getch()
        if key == curses.KEY_UP and direction != DOWN:
            direction = UP
        elif key == curses.KEY_DOWN and direction != UP:
            direction = DOWN
        elif key == curses.KEY_LEFT and direction != RIGHT:
            direction = LEFT
        elif key == curses.KEY_RIGHT and direction != LEFT:
            direction = RIGHT

        # Check if the snake ate the food
        grow = check_food(snake, food_x, food_y)

        # Move the snake
        new_snake = move_snake(snake, direction, width, height, level, grow=grow)
        if new_snake is None:
            gameover = True  # Snake hit a boundary or obstacle (game over)
        else:
            snake = new_snake

        # If the snake eats food, place new food
        if grow:
            score += 1
            food_x, food_y = place_food(snake, width, height)  # Place new food

        # Check for collisions (with self)
        if len(snake) != len(set(snake)):  # Check if there are overlapping positions
            gameover = True

        # Level up when reaching certain scores
        level, speed = level_up(stdscr, score, level, speed)

        # Reset the snake to its initial position and size after leveling up
        if score >= level * 10:  # Reset for each new level
            snake = [(width // 2, height // 2)]  # Reset snake position
            length = 1  # Reset length
            food_x, food_y = place_food(snake, width, height)  # Place new food

        stdscr.timeout(speed)

        # Update the screen
        stdscr.refresh()

    # Game Over screen
    stdscr.clear()
    stdscr.addstr(height // 2, (width // 2) * 2 - 5, f"GAME OVER! Score: {score}")
    if score > high_score:
        stdscr.addstr(height // 2 + 1, (width // 2) * 2 - 5, "Hurray, congratulations for beating the high score!")
        high_score = score  # Update the high score
    else:
        stdscr.addstr(height // 2 + 1, (width // 2) * 2 - 5, "Better luck next time!")
    
    stdscr.refresh()
    time.sleep(2)  # Pause for 2 seconds before displaying options

    # Wait for player to choose to replay or exit
    stdscr.addstr(height // 2 + 3, (width // 2) * 2 - 5, "Press P to play again or Q to quit.")
    stdscr.refresh()

    while True:
        key = stdscr.getch()
        if key == ord('p'):
            game_loop(stdscr)  # Restart the game
            break
        elif key == ord('q'):
            break

# Example usage (run the game loop with curses)
if __name__ == "__main__":
    curses.wrapper(game_loop)
