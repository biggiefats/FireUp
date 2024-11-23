# Dodge Em' Up  - Fire Up!

"""
Fire Up!
        
This is a game where you have a cube, Mr Fire. \n
You have to move Mr Fire around and ensure that you do not get hit by any other enemies.
        
Play this game whilst doing work!
Play this game while revising!
Play this game on the toilet! (Good luck with that one.)

Also there is a secret mode. You can try to figure out where it is by navigating the code.
The secret mode introduces its own game mode.
"""

# Imports
from tkinter import *
from PIL import Image, ImageTk
import sys
import random
import math
import enemy  # custom module
import time
import json

# Classes


class Game:
    def __init__(self, root):
        """
        Fire Up!

        This is a game where you have a cube, Mr Fire. \n
        You have to move Mr Fire around and ensure that you do not get hit by any other enemies.

        Play this game whilst doing work!
        Play this game while revising!
        Play this game on the toilet! (Good luck with that one.)
        """
        self.root = root

        # Changeable attributes
        self.GRID_DIMENSIONS = (20, 20)  # Ideally make a square
        self.CELL_SIZE = 15
        self.WIDTH = self.GRID_DIMENSIONS[0] * self.CELL_SIZE
        self.HEIGHT = self.GRID_DIMENSIONS[1] * self.CELL_SIZE
        self.GEOMETRY = f"{self.WIDTH}x{self.HEIGHT}"

        # Setup
        self.root.geometry(self.GEOMETRY)
        self.root.resizable(width=False, height=False)
        self.root.title("Fire Up!")
        self.update_id = None

        self.MRRED = "#ff5722"
        self.MRREDACTIVE = "#ff8552"
        # Dark versions
        self.DMRRED = "#582c1c"
        self.DMRREDACTIVE = "#623b20"

        # Animation settings
        self.FPS = 30
        self.FRAME_TIME = int(1000 / self.FPS)

        # Metrics
        self.score = 0

        # Player and enemy stuffs
        self.player_coordinates = [self.GRID_DIMENSIONS[0] // 2,
                                   # Start in middle of grid
                                   self.GRID_DIMENSIONS[1] // 2]
        self.enemies = []
        self.enemy_directions = ["U", "D", "L", "R"]

        self.MIN_CHANCE = 5
        self.basic_chance = 50
        self.speedy_chance = 90
        self.leaper_chance = 130
        self.sine_chance = 170
        self.helix_chance = 200
        self.exploder_chance = 240

        self.basic_difficulty_increase_threshold = 8
        self.speedy_difficulty_increase_threshold = 14
        self.leaper_difficulty_increase_threshold = 23
        self.sine_difficulty_increase_threshold = 30
        self.helix_difficulty_increase_threshold = 37
        self.exploder_difficulty_increase_threshold = 50

        self.basic_flag = False
        self.speedy_flag = False
        self.leaper_flag = False
        self.sine_flag = False
        self.helix_flag = False
        self.exploder_flag = False

        # Items
        # Big Boy Canvas
        self.canvas = Canvas(
            master=self.root,
            width=self.WIDTH,
            height=self.HEIGHT,
            bg="black",
            borderwidth=0,
            highlightthickness=0
        )

        # Grid cells and drawing
        self.grid_cells = list()

        # Le Paused and Le Boss KEy with LE GAme start
        self.is_paused = False
        self.in_game = False
        self.boss_key_active = False

        # Secret
        self.secret = False

        # Circles for Background
        self.MINCIRCLERADIUS = 1
        self.MAXCIRCLERADIUS = 20
        self.circles = list()
        self.create_circles()
        self.STOPCIRCLES = False

        # Lone Image
        img1 = Image.open(fp="logo.png")
        self.logo = ImageTk.PhotoImage(img1)

        # Subroutine calls
        self.canvas.pack(fill=BOTH, expand=True)

# Save and load
    def load_keybinds(self):
        """Load keybinds from file or return defaults."""
        try:
            with open('keybinds.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            # Default keybinds
            return {
                'up': 'w',
                'down': 's',
                'left': 'a',
                'right': 'd'
            }

    def save_keybinds(self):
        """Save current keybinds to file."""
        with open('keybinds.json', 'w') as f:
            json.dump(self.keybinds, f)

        # Check for FIRE cheat code
        if (self.keybinds['up'] == 'f' and
            self.keybinds['left'] == 'i' and
            self.keybinds['down'] == 'r' and
                self.keybinds['right'] == 'e'):
            # spawn the secret and heavily reduce other chances of enemies - gamemode
            self.secret = True
            return True

    def save_score(self, score):
        """Save score to leaderboard file."""
        try:
            # Choose the correct leaderboard file based on game mode
            filename = 'secret_leaderboard.json' if self.secret else 'leaderboard.json'
            with open(filename, 'r') as f:
                scores = json.load(f)
        except FileNotFoundError:
            scores = []

        scores.append(round(score))
        scores.sort(reverse=True)
        scores = scores[:3]  # Keep only top 3

        with open(filename, 'w') as f:
            json.dump(scores, f)

        return scores

    def create_circles(self):
        """Create initial circles"""
        if len(self.circles) < 35:
            for _ in range(35):
                radius = random.randint(
                    self.MINCIRCLERADIUS, self.MAXCIRCLERADIUS)
                circle = {
                    'x': random.randint(radius, self.WIDTH - radius),
                    'y': random.randint(radius, self.HEIGHT - radius),
                    'radius': radius,
                    'fill': random.choice([self.DMRRED, self.DMRREDACTIVE]),
                    'outline': '',
                    'phase': random.uniform(0, 180),
                    'current_radius': radius
                }
                self.circles.append(circle)

    def construct_menu_button(self, text, command):
        """Creates a menu button to be displayed."""
        return Button(
            self.root,
            text=text,
            fg=self.MRRED,
            bg="black",
            activeforeground=self.MRREDACTIVE,
            activebackground='black',
            font=("Pixellari",),
            relief='groove',
            overrelief='ridge',
            command=eval(f'self.{command}'))

    def update_circles(self):
        """Update circle properties."""
        if random.randint(0, 1) == 1:
            self.create_circles()

        for circle in self.circles:
            size_range = (self.MAXCIRCLERADIUS - self.MINCIRCLERADIUS) / 2
            mid_size = (self.MAXCIRCLERADIUS + self.MINCIRCLERADIUS) / 2
            circle['current_radius'] = mid_size + \
                (math.sin(math.radians(circle['phase'])) * size_range)
            circle['phase'] = (circle['phase'] + 2) % 360

    def draw_circles(self):
        """Draw all circles."""
        self.canvas.delete("all")

        for circle in self.circles:
            self.canvas.create_oval(
                circle['x'] - circle['current_radius'],
                circle['y'] - circle['current_radius'],
                circle['x'] + circle['current_radius'],
                circle['y'] + circle['current_radius'],
                fill=circle['fill'],
                outline=circle['outline']
            )

        # Draw logo
        self.canvas.create_image(
            self.WIDTH // 2, 20, image=self.logo, anchor='n')

    def animate_main_menu(self):
        """Main animation loop"""
        if not self.STOPCIRCLES:
            self.update_circles()
            self.draw_circles()
            self.root.after(self.FRAME_TIME, self.animate_main_menu)

    def capture_key(self, action, button):
        """Capture a new key press for the given action."""
        button.configure(text="PRESS KEY")

        def on_key_press(event):
            if event.keysym.lower() in ['escape', 'return']:
                # Cancel key capture
                button.configure(text=self.keybinds[action].upper())
            else:
                # Update keybind
                right_key = event.keysym[0].upper() + event.keysym[1:]
                self.keybinds[action] = (event.keysym.lower() if len(
                    event.keysym) == 1 else right_key)
                button.configure(text=event.keysym.upper())
                # make noted that secret is unlocked
                if self.save_keybinds():
                    # Green shades
                    self.MRRED = "#39ff22"
                    self.MRREDACTIVE = "#52ff54"
                    self.DMRRED = "#1d581c"
                    self.DMRREDACTIVE = "#216220"
                    # Reset everything to apply colours
                    self.root.unbind('<Key>')
                    self.root.bind('<Key>', on_key_press)
                    self.circles = list()
                    self.canvas.delete("all")
                    self.root.title("Fire Up!")
                    self.reset_keybinds()
                    self.main_menu()

            # Remove temporary binding
            self.root.unbind('<Key>')

        # Create temporary binding
        self.root.bind('<Key>', on_key_press)

    def reset_keybinds(self):
        """Reset keybinds to defaults."""
        self.keybinds = {
            'up': 'w',
            'down': 's',
            'left': 'a',
            'right': 'd'
        }
        self.save_keybinds()
        self.settings_menu()  # Refresh menu

    def setup_controls(self):
        """Modified setup_controls to use custom keybinds."""
        if not hasattr(self, 'keybinds'):
            self.keybinds = self.load_keybinds()

        # Clear existing bindings
        for key in self.keybinds.keys():
            self.root.unbind(key)

        # Set new bindings
        # Lambda with argument not used helps to activate function
        self.root.bind(f'<{self.keybinds["up"]}>',
                       lambda e: self.move_player(0, -1))
        self.root.bind(f'<{self.keybinds["down"]}>',
                       lambda e: self.move_player(0, 1))
        self.root.bind(f'<{self.keybinds["left"]}>',
                       lambda e: self.move_player(-1, 0))
        self.root.bind(f'<{self.keybinds["right"]}>',
                       lambda e: self.move_player(1, 0))
        self.root.bind(f'<p>', lambda e: self.set_game_paused())

    # Main menu stuffs
    def move_player(self, dx, dy):
        """Move the player cube in a certain direction."""
        if not self.is_paused:
            new_x = self.player_coordinates[0] + dx
            new_y = self.player_coordinates[1] + dy

            # Check if the new position is within bounds
            if (0 <= new_x < self.GRID_DIMENSIONS[0] and
                    # Start from row 2 to stay below the score area
                    2 <= new_y < self.GRID_DIMENSIONS[1]):
                self.player_coordinates = [new_x, new_y]

    def draw_player(self):
        """Draw the player cube on the canvas."""
        x, y = self.player_coordinates
        self.canvas.create_rectangle(
            x * self.CELL_SIZE,
            y * self.CELL_SIZE,
            (x + 1) * self.CELL_SIZE,
            (y + 1) * self.CELL_SIZE,
            fill=self.MRRED,
            outline=''
        )

    def draw_top_visuals(self):
        """
        Drawing the score text, and the line, for the main loop.
        """

        # Rectangle to cover squares
        self.canvas.create_rectangle(
            0,
            0,
            self.WIDTH,
            2 * self.CELL_SIZE - 0,
            fill='black',
            outline=''
        )

        # Draw the score and line
        self.canvas.create_text(
            self.WIDTH // 2,
            self.CELL_SIZE,
            text=f"Score: {round(self.score)}",
            fill=self.MRREDACTIVE,
            font=("Pixellari", 15)
        )

        self.canvas.create_line(
            0,
            2 * self.CELL_SIZE - 1,
            self.WIDTH,
            2 * self.CELL_SIZE - 1,
            fill=self.MRRED
        )

    def draw_grid(self):
        """
        Draw the grid for the main loop.
        """
        for row in range(2, self.GRID_DIMENSIONS[1]):
            for col in range(self.GRID_DIMENSIONS[0]):
                cell = self.canvas.create_rectangle(
                    col * self.CELL_SIZE,
                    row * self.CELL_SIZE,
                    (col + 1) * self.CELL_SIZE,
                    (row + 1) * self.CELL_SIZE,
                    fill='black',
                    outline='#333333'  # Subtle grid lines
                )
                self.grid_cells.append(cell)

    def draw_enemy(self):
        """
        Draws enemies onto the grid, based on chance.
        It also updates enemies.
        """
        coordinate_bounds = (0, self.GRID_DIMENSIONS[0])
        grid_size = self.CELL_SIZE

        # Enemy generation
        basic_chance = random.randint(1, self.basic_chance)
        speedy_chance = random.randint(1, self.speedy_chance)
        leaper_chance = random.randint(1, self.leaper_chance)
        sine_chance = random.randint(1, self.sine_chance)
        helix_chance = random.randint(1, self.helix_chance)
        exploder_chance = random.randint(1, self.exploder_chance)

        if basic_chance == self.basic_chance:
            direction = random.choice(self.enemy_directions)
            basic = enemy.Basic(
                direction=direction, coordinate_bounds=coordinate_bounds, grid_size=grid_size)
            self.enemies.append(basic)

        if speedy_chance == self.speedy_chance:
            direction = random.choice(self.enemy_directions)
            speedy = enemy.Speedy(
                direction=direction, coordinate_bounds=coordinate_bounds, grid_size=grid_size)
            self.enemies.append(speedy)

        if leaper_chance == self.leaper_chance:
            direction = random.choice(self.enemy_directions)
            leaper = enemy.Leaper(
                direction=direction, coordinate_bounds=coordinate_bounds, grid_size=grid_size)
            self.enemies.append(leaper)

        if helix_chance == self.helix_chance:
            direction = random.choice(self.enemy_directions)
            helix = enemy.Helix(
                direction=direction, coordinate_bounds=coordinate_bounds, grid_size=grid_size)
            self.enemies.append(helix)

        if sine_chance == self.sine_chance:
            direction = random.choice(self.enemy_directions)
            sine = enemy.Sine(
                direction=direction, coordinate_bounds=coordinate_bounds, grid_size=grid_size)
            self.enemies.append(sine)

        if exploder_chance == self.exploder_chance:
            direction = random.choice(self.enemy_directions)
            exploder = enemy.Exploder(
                direction=direction, coordinate_bounds=coordinate_bounds, grid_size=grid_size)
            self.enemies.append(exploder)

        # SECRET TRACKER ENEMY only if SECRET was fondc
        if hasattr(self, 'tracker_chance'):
            tracker_chance = random.randint(1, self.tracker_chance)
            tracker_stat = random.randint(2, 10)
            if tracker_chance == self.tracker_chance:
                direction = random.choice(self.enemy_directions)
                tracker = enemy.Tracker(direction=direction,
                                        coordinate_bounds=coordinate_bounds,
                                        grid_size=grid_size,
                                        track_delay=max(2, tracker_stat // 2),
                                        max_moves=(tracker_stat + 4))
                tracker.set_target(self.player_coordinates)
                self.enemies.append(tracker)

        # Area familiarisation
        for enemy_instance in self.enemies:
            # Check if the enemy has collided with the player
            if enemy_instance.check_collision(self.player_coordinates):
                self.is_game_over = True
                self.root.after_cancel(self.update_id)
                self.game_over()
                return

            # Check if enemy has gone off the boundaries
            if enemy_instance.check_boundaries():
                self.enemies.remove(enemy_instance)
                del enemy_instance
            else:
                if isinstance(enemy_instance, enemy.Tracker):
                    enemy_instance.set_target(self.player_coordinates)
                enemy_instance.move()
                enemy_instance.display(self.canvas)

    def update_game(self):
        """Update game state and redraw."""
        if not self.STOPCIRCLES:
            return

        if not self.is_paused:
            # Remove anything and everything
            self.logo = None
            self.canvas.delete("all")

            # Draw the grid
            self.draw_grid()

            # Draw the player
            self.draw_player()

            # Draw enemies
            self.draw_enemy()

            # Draw the score and line
            self.draw_top_visuals()

            # Change difficulty when needed
            self.difficulty_change()

            self.score += 0.1

            # Schedule the next update
            self.update_id = self.root.after(self.FRAME_TIME, self.update_game)

    # Backend methods
    def exit(self):
        """In need of exiting the program."""
        sys.exit()

    def set_game_paused(self):
        """
        Toggle the paused state for the game loop.
        """
        self.is_paused = not self.is_paused

        # cant have people moving around in time
        if self.is_paused and self.in_game:
            self.boss_k = Button(
                self.root,
                text='?',
                fg=self.MRRED,
                bg="black",
                activeforeground=self.MRREDACTIVE,
                activebackground='black',
                font=("Pixellari", 15),
                relief='groove',
                overrelief='ridge',
                command=self.boss_key)
            # make a cool button ??
            self.boss_k.place(width=30, height=20, x=5, y=5)

        if not self.is_paused:
            self.boss_k.destroy()
            self.boss_k = None
            self.setup_controls()
            self.update_game()

    def clear_screen(self):
        """Clear all widgets except canvas."""
        for widget in self.root.winfo_children():
            if widget != self.canvas:
                widget.destroy()
                widget = None

    def print_info(self):
        """Print some information about the game, for developer purpose."""
        print(f"Dimensions: {self.WIDTH} x {self.HEIGHT}")

    def difficulty_change(self):
        """
        Change difficulty relative to score.
        """
        score = int(self.score)

        # Flags are needed so that score does not decrease drastically

        if score % self.basic_difficulty_increase_threshold == 0 and not self.basic_flag:
            self.basic_chance = max(self.MIN_CHANCE, self.basic_chance - 1)
            self.basic_flag = True
        elif score % self.basic_difficulty_increase_threshold != 0:
            self.basic_flag = False

        if score % self.speedy_difficulty_increase_threshold == 0 and not self.speedy_flag:
            self.speedy_chance = max(self.MIN_CHANCE, self.speedy_chance - 1)
            self.speedy_flag = True
        elif score % self.speedy_difficulty_increase_threshold != 0:
            self.speedy_flag = False

        if score % self.leaper_difficulty_increase_threshold == 0 and not self.leaper_flag:
            self.leaper_chance = max(self.MIN_CHANCE, self.leaper_chance - 1)
            self.leaper_flag = True
        elif score % self.leaper_difficulty_increase_threshold != 0:
            self.leaper_flag = False

        if score % self.helix_difficulty_increase_threshold == 0 and not self.helix_flag:
            self.helix_chance = max(self.MIN_CHANCE, self.helix_chance - 1)
            self.helix_flag = True
        elif score % self.helix_difficulty_increase_threshold != 0:
            self.helix_flag = False

        if score % self.exploder_difficulty_increase_threshold == 0 and not self.exploder_flag:
            self.exploder_chance = max(
                self.MIN_CHANCE, self.exploder_chance - 1)
            self.exploder_flag = True
        elif score % self.exploder_difficulty_increase_threshold != 0:
            self.exploder_flag = False

    # Menus
    def boss_key(self):
        """
        Screen with time on it - make sure your professors dont know your stuff!5
        """
        if not self.boss_key_active:
            self.root.title("Clock")
            self.canvas.delete("all")
            self.clear_screen()
            self.boss_key_active = True

            self.canvas.create_rectangle(
                0,
                0,
                self.WIDTH,
                self.HEIGHT,
                fill='white'
            )
            current_time = time.strftime("%H:%M:%S")

            self.time = Button(master=self.root,
                               text=f"{current_time}",
                               fg='black',
                               bg='white',
                               activebackground='white',
                               activeforeground='black',
                               highlightthickness=0,
                               font=('Roboto', 40),
                               command=self.main_loop)
            self.time.place(width=self.WIDTH, height=self.HEIGHT, x=0, y=0)
            self.root.after(self.FRAME_TIME, self.boss_key)

        # Emulate a clock - do not call other stuff
        # Recreating a button is inefficientS
        elif self.is_paused:
            current_time = time.strftime("%H:%M:%S")
            self.time.config(text=f"{current_time}")
            self.update_time = self.root.after(500, self.boss_key)

    def game_over(self):
        """
        Display game over screen and handle reset.
        """
        self.is_paused = True

        self.canvas.delete("all")
        self.clear_screen()

        # Save and get top scores
        top_scores = self.save_score(self.score)

        # Background
        self.canvas.create_rectangle(
            0,
            0,
            self.WIDTH,
            self.HEIGHT,
            fill='black',
            outline=''
        )

        # Game Over text
        self.canvas.create_text(
            self.WIDTH // 2,
            self.HEIGHT // 2 - 60,
            text="GAME OVER",
            fill=self.MRRED,
            font=("Pixellari", 30)
        )

        # Score text
        self.canvas.create_text(
            self.WIDTH // 2,
            self.HEIGHT // 2 - 20,
            text=f"Final Score: {round(self.score)}",
            fill=self.MRREDACTIVE,
            font=("Pixellari", 20)
        )

        # Leaderboard title
        self.canvas.create_text(
            self.WIDTH - 70,
            self.HEIGHT // 2 + 20,
            text="TOP SCORES",
            fill=self.MRRED,
            font=("Pixellari", 15)
        )

        # Display top 3 scores in normal mode
        if not self.secret:
            for i, score in enumerate(top_scores):
                self.canvas.create_text(
                    self.WIDTH - 70,
                    200 + i * 25,
                    text=f"#{i+1}: {score}",
                    fill=self.MRREDACTIVE,
                    font=("Pixellari", 12)
                )

        # Additional leaderboard display if in secret mode
        if self.secret:
            try:
                with open('leaderboard.json', 'r') as f:
                    normal_scores = json.load(f)
            except FileNotFoundError:
                normal_scores = []

            for i, score in enumerate(top_scores):
                self.canvas.create_text(
                    self.WIDTH - 70,
                    200 + i * 25,
                    text=f"#{i+1}: {score}",
                    fill=self.MRREDACTIVE,
                    font=("Pixellari", 12)
                )

        # Restart button
        restart_button = Button(
            self.root,
            text="RESTART",
            fg=self.MRRED,
            bg="black",
            activeforeground=self.MRREDACTIVE,
            activebackground='black',
            font=("Pixellari", 15),
            relief='groove',
            overrelief='ridge',
            command=self.main_loop
        )
        restart_button.place(
            width=120,
            height=30,
            x=30,
            y=self.HEIGHT//2 + 20
        )

        # Main menu button
        menu_button = Button(
            self.root,
            text="MAIN MENU",
            fg=self.MRRED,
            bg="black",
            activeforeground=self.MRREDACTIVE,
            activebackground='black',
            font=("Pixellari", 15),
            relief='groove',
            overrelief='ridge',
            command=self.reset_and_return_to_menu
        )
        menu_button.place(
            width=120,
            height=30,
            x=30,
            y=self.HEIGHT//2 + 60
        )

    def reset_and_return_to_menu(self):
        """
        Reset game state and return to main menu.
        """
        self.score = 0
        self.player_coordinates = [
            self.GRID_DIMENSIONS[0] // 2, self.GRID_DIMENSIONS[1] // 2]
        self.enemies = []
        self.is_paused = False
        self.STOPCIRCLES = False

        img1 = Image.open(fp="logo.png")
        self.logo = ImageTk.PhotoImage(img1)

        self.basic_chance = 40
        self.speedy_chance = 80
        self.leaper_chance = 120
        self.sine_chance = 160
        self.helix_chance = 180

        self.basic_flag = False
        self.speedy_flag = False
        self.leaper_flag = False
        self.sine_flag = False
        self.helix_flag = False

        self.clear_screen()
        self.main_menu()

    def main_menu(self):
        """Enter the main menu."""
        self.canvas.delete("all")
        self.clear_screen()
        img1 = Image.open(fp="logo.png")
        self.logo = ImageTk.PhotoImage(img1)

        self.in_game = False

        # Create buttons
        play = self.construct_menu_button(text="PLAY", command="main_loop")
        play.place(width=60, height=30, x=self.WIDTH//2 - 30, y=self.HEIGHT//2)

        settings = self.construct_menu_button(
            text="SETTINGS", command='settings_menu')
        settings.place(width=110, height=30, x=self.WIDTH //
                       2 - 55, y=self.HEIGHT//2 + 40)

        exit = self.construct_menu_button(text="EXIT", command='exit')
        exit.place(width=60, height=30, x=self.WIDTH //
                   2 - 30, y=self.HEIGHT//2 + 80)

        # Start animation
        self.animate_main_menu()

    def settings_menu(self):
        """
        Creates a settings menu, where keybinds are stored and saved for later use.
        """
        self.logo = None
        self.canvas.delete("all")
        self.clear_screen()

        # make some keybinds if they are not made already
        if not hasattr(self, 'keybinds'):
            self.keybinds = self.load_keybinds()

        self.canvas.create_rectangle(
            0,
            0,
            self.WIDTH,
            self.HEIGHT,
            fill='black'
        )

        # Title
        title = Label(
            self.root,
            text="CONTROLS",
            fg=self.MRRED,
            bg="black",
            relief='sunken',
            highlightthickness=1,
            highlightcolor=self.MRRED,
            font=("Pixellari", 20)
        )
        title.place(
            x=self.WIDTH // 2,
            y=20,
            anchor="center"
        )

        # Text underneath to indicate pause
        pause_text = Label(
            self.root,
            text="(Pause is bound to 'P')",
            fg=self.MRRED,
            bg="black",
            relief='sunken',
            highlightthickness=1,
            highlightcolor=self.MRRED,
            font=("Pixellari", 10)
        )
        pause_text.place(
            x=self.WIDTH // 2,
            y=40,
            anchor="center"
        )

        # Create buttons for each keybind
        actions = ['down', 'right', 'up', 'left']
        for i, action in enumerate(actions):
            # Create label
            label = Label(
                self.root,
                text=action.upper(),
                fg=self.MRREDACTIVE,
                bg="black",
                highlightthickness=1,
                highlightcolor=self.MRRED,
                font=("Pixellari", 12)
            )
            label.place(
                x=[69, (self.WIDTH + 90) // 2 + 35][i % 2],
                y=[(self.HEIGHT // 2) - 10, (self.HEIGHT // 3) - 10][i > 1],
                anchor='center'
            )

            btn = Button(
                self.root,
                text=self.keybinds[action].upper(),
                fg=self.MRRED,
                bg="black",
                activeforeground=self.MRREDACTIVE,
                activebackground='black',
                font=("Pixellari", 12),
                relief='groove',
                overrelief='ridge'
            )
            btn.place(
                width=90,
                height=30,
                x=[25, (self.WIDTH + 40) // 2 + 20][i % 2],
                y=[self.HEIGHT // 2, self.HEIGHT // 3][i > 1]
            )
            btn.bind('<Button-1>', lambda e, a=action,
                     b=btn: self.capture_key(a, b))

        reset_btn = Button(
            self.root,
            text="RESET",
            fg=self.MRRED,
            bg="black",
            activeforeground=self.MRREDACTIVE,
            activebackground='black',
            font=("Pixellari", 12),
            relief='groove',
            overrelief='ridge',
            command=self.reset_keybinds
        )
        reset_btn.place(
            width=80,
            height=30,
            x=self.WIDTH//2 - 40,
            y=self.HEIGHT - 100
        )

        back_btn = Button(
            self.root,
            text="BACK",
            fg=self.MRRED,
            bg="black",
            activeforeground=self.MRREDACTIVE,
            activebackground='black',
            font=("Pixellari", 12),
            relief='groove',
            overrelief='ridge',
            command=self.main_menu
        )
        back_btn.place(
            width=80,
            height=30,
            x=self.WIDTH//2 - 40,
            y=self.HEIGHT - 50
        )

    def main_loop(self):
        """Main game loop."""
        # Clear screen
        # Some things are for the boss key
        self.circles = list()
        self.canvas.delete("all")
        self.STOPCIRCLES = True
        self.root.title("Fire Up!")
        self.is_game_over = False
        self.is_paused = False
        self.clear_screen()

        # Reset - for every new game - only if boss key isn't active
        if not self.boss_key_active:
            self.score = 0
            self.player_coordinates = [
                self.GRID_DIMENSIONS[0] // 2, self.GRID_DIMENSIONS[1] // 2]
            self.enemies = []
            self.is_paused = False
            self.basic_chance = 40
            self.speedy_chance = 80
            self.leaper_chance = 120
            self.sine_chance = 160
            self.helix_chance = 180

            self.basic_flag = False
            self.speedy_flag = False
            self.leaper_flag = False
            self.sine_flag = False
            self.helix_flag = False

        # Boss key should not pop up after we go off it
        if hasattr(self, 'update_time'):
            self.root.after_cancel(self.update_time)

        # if secret is found, make spawn chances different
        if self.secret:
            self.basic_chance = 10000
            self.speedy_chance = 11500
            self.leaper_chance = 13000
            self.sine_chance = 17000
            self.helix_chance = 20000
            self.exploder_chance = 15
            self.tracker_chance = 15
            self.exploder_difficulty_increase_threshold = 10  # go crazy

        self.boss_key_active = False
        self.in_game = True

        # Setup controls
        self.setup_controls()

        # Make the button to work on the thing
        pause = Button(
            self.root,
            text='II',
            fg=self.MRRED,
            bg="black",
            activeforeground=self.MRREDACTIVE,
            activebackground='black',
            font=("Pixellari", 15),
            relief='groove',
            overrelief='ridge',
            command=self.set_game_paused)

        pause.place(width=30, height=20, x=self.WIDTH - 35, y=5)

        # Start game updates
        self.update_game()


# is this the main file?
if __name__ == "__main__":
    root = Tk()
    game = Game(root)
    game.main_menu()
    root.mainloop()
