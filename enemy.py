"""Enemy creation factory for Fire Up! game.

Available enemies:
- Basic: Moves across screen in random direction
- Speedy: Basic enemy with double speed
- Leaper: Moves two spots per move
- Helix: Creates a helix pattern
- Sine: Modified helix creating wave pattern
- Exploder: Creates explosion after delay
- Tracker: Secret enemy that pursues the player
"""
import random
import math


class Enemy:
    """Base enemy class that defines common behavior and attributes."""

    def __init__(self, direction, colour, coordinate_bounds, grid_size,
                 time_to_move):
        """Initialize base enemy with movement and display properties."""
        self.direction_map = {
            "U": (0, -1),
            "D": (0, 1),
            "L": (-1, 0),
            "R": (1, 0)
        }
        self.cell_size = grid_size
        self.min_coord, self.max_coord = coordinate_bounds
        self.time_to_move = time_to_move
        self.move_gauge = 0

        # Boundary coordinates
        self.up_bound = self.min_coord + 1
        self.down_bound = self.max_coord + 1
        self.left_bound = self.min_coord - 1
        self.right_bound = self.max_coord + 1

        self.direction = direction
        self.colour = colour
        self.coordinates = self._get_spawn_position()

    def _get_spawn_position(self):
        """Calculate spawn position based on direction."""
        if self.direction == "U":
            return [
                random.randint(self.min_coord, self.max_coord),
                self.down_bound
            ]
        if self.direction == "D":
            return [
                random.randint(self.min_coord, self.max_coord),
                self.up_bound
            ]
        if self.direction == "L":
            return [
                self.right_bound,
                random.randint(self.min_coord + 2, self.max_coord)
            ]
        if self.direction == "R":
            return [
                self.left_bound,
                random.randint(self.min_coord + 2, self.max_coord)
            ]

    def display(self, canvas):
        """Display enemy on the canvas."""
        x, y = self.coordinates
        canvas.create_rectangle(
            x * self.cell_size,
            y * self.cell_size,
            (x + 1) * self.cell_size,
            (y + 1) * self.cell_size,
            fill=self.colour,
            outline=''
        )

    def move(self):
        """Update enemy position based on movement timer and direction."""
        if self.time_to_move == self.move_gauge:
            dx, dy = self.direction_map[self.direction]
            x = self.coordinates[0] + dx
            y = self.coordinates[1] + dy
            self.coordinates = [x, y]
            self.move_gauge = 0
        else:
            self.move_gauge += 1

    def check_collision(self, coordinates):
        """Check if enemy has collided with given coordinates."""
        return self.coordinates == coordinates

    def check_boundaries(self):
        """Check if enemy has moved beyond screen boundaries."""
        x, y = self.coordinates
        if self.direction == 'U':
            return y <= self.up_bound
        if self.direction == 'D':
            return y >= self.down_bound
        if self.direction == 'L':
            return x <= self.left_bound
        if self.direction == 'R':
            return x >= self.right_bound


class Basic(Enemy):
    """Basic enemy that moves in a straight line at normal speed."""

    def __init__(self, direction, coordinate_bounds, grid_size):
        """Initialize basic enemy with default white color."""
        super().__init__(direction, "white", coordinate_bounds, grid_size, 3)


class Speedy(Enemy):
    """Fast enemy that moves at double the normal speed."""

    def __init__(self, direction, coordinate_bounds, grid_size):
        """Initialize speedy enemy with pink color."""
        super().__init__(
            direction, "#f1bbb0", coordinate_bounds, grid_size, 1
        )


class Leaper(Enemy):
    """Enemy that moves two grid spaces at a time."""

    def __init__(self, direction, coordinate_bounds, grid_size):
        """Initialize leaper with double-step movement."""
        super().__init__(
            direction, "#f1deb0", coordinate_bounds, grid_size, 2
        )
        self.direction_map = {
            "U": (0, -2),
            "D": (0, 2),
            "L": (-2, 0),
            "R": (2, 0)
        }


class Exploder(Enemy):
    """Enemy that creates an explosive area effect after a delay."""

    EXPLOSION_COLORS = ['#ff0000', '#ffbb00', '#fcff00', '#3dff00', '#00ffcc']
    EXPLOSION_COLOR = "#ff8852"

    def __init__(self, direction, coordinate_bounds, grid_size):
        """Initialize exploder with countdown mechanics."""
        super().__init__(
            direction, "#000000", coordinate_bounds, grid_size, 3
        )
        self.explode_time = 10
        self.explode_gauge = 0
        self.exploded = False

    def move(self):
        """Handle both movement and explosion countdown."""
        if self.time_to_move == self.move_gauge:
            dx, dy = self.direction_map[self.direction]
            x = self.coordinates[0] + dx
            y = self.coordinates[1] + dy
            self.coordinates = [x, y]
            self.move_gauge = 0

            if not self.exploded:
                if self.explode_gauge < self.explode_time:
                    self.explode_gauge += 1
                if self.explode_gauge == self.explode_time:
                    self.exploded = True
        else:
            self.move_gauge += 1

    def display(self, canvas):
        """Display the enemy, showing explosion charging or detonation."""
        x, y = self.coordinates
        if not self.exploded:
            color_index = math.floor(
                4 * (self.explode_gauge / self.explode_time)
            )
            self.colour = self.EXPLOSION_COLORS[color_index]
            canvas.create_rectangle(
                x * self.cell_size,
                y * self.cell_size,
                (x + 1) * self.cell_size,
                (y + 1) * self.cell_size,
                fill=self.colour,
                outline=''
            )
        else:
            canvas.create_rectangle(
                (x - 1) * self.cell_size,
                (y - 1) * self.cell_size,
                (x + 2) * self.cell_size,
                (y + 2) * self.cell_size,
                fill=self.EXPLOSION_COLOR,
                outline=''
            )
            self.explode_gauge += 1

    def check_collision(self, coordinates):
        """Check for collision with either the enemy or its explosion."""
        if not self.exploded:
            return self.coordinates == coordinates
        x_diff = abs(self.coordinates[0] - coordinates[0])
        y_diff = abs(self.coordinates[1] - coordinates[1])
        return x_diff <= 1 and y_diff <= 1

    def check_boundaries(self):
        """Check if enemy is out of bounds or explosion is complete."""
        if self.exploded and self.explode_gauge > self.explode_time:
            return True
        x, y = self.coordinates
        if self.direction == 'U':
            return y <= self.up_bound
        if self.direction == 'D':
            return y >= self.down_bound
        if self.direction == 'L':
            return x <= self.left_bound
        if self.direction == 'R':
            return x >= self.right_bound


class Helix(Enemy):
    """Enemy that creates a helix pattern with two moving points."""

    def __init__(self, direction, coordinate_bounds, grid_size):
        """Initialize helix movement parameters."""
        super().__init__(
            direction, "#fefb7f", coordinate_bounds, grid_size, 4
        )
        self.offset = 0
        self.max_offset = 1
        self.offset_direction = 1
        self.phase = 0

        self.perpendicular_map = {
            "U": [(1, 0), (-1, 0)],
            "D": [(-1, 0), (1, 0)],
            "L": [(0, -1), (0, 1)],
            "R": [(0, 1), (0, -1)]
        }

        self.coordinates_list = [[0, 0], [0, 0]]
        self._initialize_helix_points()

    def _initialize_helix_points(self):
        """Set initial positions for both helix points."""
        offset = self.max_offset * random.choice([-1, 1])
        if self.direction == "U":
            self.coordinates = [
                random.randint(self.min_coord, self.max_coord),
                self.down_bound
            ]
            self.coordinates_list[1] = [
                self.coordinates_list[1][0] + offset,
                self.down_bound
            ]
        elif self.direction == "D":
            self.coordinates = [
                random.randint(self.min_coord, self.max_coord),
                self.up_bound
            ]
            self.coordinates_list[1] = [
                self.coordinates_list[1][0] + offset,
                self.up_bound
            ]
        elif self.direction == "L":
            self.coordinates = [
                self.right_bound,
                random.randint(self.min_coord + 2, self.max_coord)
            ]
            self.coordinates_list[1] = [
                self.right_bound,
                self.coordinates_list[1][1] + offset
            ]
        elif self.direction == "R":
            self.coordinates = [
                self.left_bound,
                random.randint(self.min_coord + 2, self.max_coord)
            ]
            self.coordinates_list[1] = [
                self.left_bound,
                self.coordinates_list[1][1] + offset
            ]
        self.coordinates_list[0] = self.coordinates

    def move(self):
        """Update positions of both helix points."""
        if self.time_to_move == self.move_gauge:
            base_dx, base_dy = self.direction_map[self.direction]
            perp_offsets = self.perpendicular_map[self.direction]
            perp_dx1, perp_dy1 = perp_offsets[self.phase // 2]
            perp_dx2, perp_dy2 = perp_offsets[self.phase // 2]

            x1 = (self.coordinates[0] + base_dx +
                  (perp_dx1 * self.offset))
            y1 = (self.coordinates[1] + base_dy +
                  (perp_dy1 * self.offset))
            x2 = (self.coordinates[0] + base_dx +
                  (perp_dx2 * self.offset))
            y2 = (self.coordinates[1] + base_dy +
                  (perp_dy2 * self.offset))

            self.offset += self.offset_direction * 0.5

            if abs(self.offset) > self.max_offset:
                self.offset_direction *= -1
                self.phase = (self.phase + 1) % 4

            self.coordinates_list[0] = [round(x1), round(y1)]
            self.coordinates_list[1] = [round(x2), round(y2)]
            self.coordinates = self.coordinates_list[0]

            self.move_gauge = 0
        else:
            self.move_gauge += 1

    def display(self, canvas):
        """Display both points of the helix."""
        for x, y in self.coordinates_list:
            canvas.create_rectangle(
                x * self.cell_size,
                y * self.cell_size,
                (x + 1) * self.cell_size,
                (y + 1) * self.cell_size,
                fill=self.colour,
                outline=''
            )

    def check_collision(self, coordinates):
        """Check if either helix point collides with given coordinates."""
        return (self.coordinates_list[0] == coordinates or
                self.coordinates_list[1] == coordinates)

    def check_boundaries(self):
        """Check if both helix points are out of bounds."""
        x1, y1 = self.coordinates_list[0]
        x2, y2 = self.coordinates_list[1]
        offset = self.max_offset

        if self.direction == 'U':
            return (y1 <= self.up_bound - offset and
                    y2 <= self.up_bound - offset)
        if self.direction == 'D':
            return (y1 >= self.down_bound + offset and
                    y2 >= self.down_bound + offset)
        if self.direction == 'L':
            return (x1 <= self.left_bound - offset and
                    x2 <= self.left_bound - offset)
        if self.direction == 'R':
            return (x1 >= self.right_bound + offset and
                    x2 >= self.right_bound + offset)


class Sine(Helix):
    """Enemy that creates a wave-like pattern of movement."""

    def __init__(self, direction, coordinate_bounds, grid_size):
        """Initialize sine wave movement parameters."""
        super().__init__(direction, coordinate_bounds, grid_size)
        self.colour = "#ff005a"
        self.max_offset = 2

    def move(self):
        """Create sine-wave movement by using fixed perpendicular offsets."""
        if self.time_to_move == self.move_gauge:
            base_dx, base_dy = self.direction_map[self.direction]
            perp_offsets = self.perpendicular_map[self.direction]
            perp_dx1, perp_dy1 = perp_offsets[0]
            perp_dx2, perp_dy2 = perp_offsets[1]

            x1 = (self.coordinates[0] + base_dx +
                  (perp_dx1 * self.offset))
            y1 = (self.coordinates[1] + base_dy +
                  (perp_dy1 * self.offset))
            x2 = (self.coordinates[0] + base_dx +
                  (perp_dx2 * self.offset))
            y2 = (self.coordinates[1] + base_dy +
                  (perp_dy2 * self.offset))

            self.offset += self.offset_direction * 0.5

            if abs(self.offset) >= self.max_offset:
                self.offset_direction *= -1
                self.phase = (self.phase + 1) % 4

            self.coordinates_list[0] = [round(x1), round(y1)]
            self.coordinates_list[1] = [round(x2), round(y2)]
            self.coordinates = self.coordinates_list[0]

            self.move_gauge = 0
        else:
            self.move_gauge += 1


class Tracker(Enemy):
    """Secret enemy that actively pursues the player."""

    def __init__(self, direction, coordinate_bounds, grid_size,
                 track_delay, max_moves):
        """Initialize tracker with pursuit parameters."""
        super().__init__(
            direction, "#00ff00", coordinate_bounds, grid_size, 4
        )
        self.up_bound = self.min_coord
        self.down_bound = self.max_coord
        self.left_bound = self.min_coord
        self.right_bound = self.max_coord

        self.target_coordinates = [0, 0]
        self.phase = 0
        self.track_delay = track_delay
        self.max_moves = max_moves
        self.moves_made = 0

    def set_target(self, player_coordinates):
        """Update the coordinates that the tracker is pursuing."""
        self.target_coordinates = player_coordinates

    def move(self):
        """Calculate direction to target and move, updating color with age."""
        if self.time_to_move == self.move_gauge:
            if (self.target_coordinates and
                    self.phase % self.track_delay == 0):
                # Calculate move direction
                dx = (1 if self.target_coordinates[0] > self.coordinates[0]
                      else -1 if self.target_coordinates[0] < self.coordinates[0]
                      else 0)
                dy = (1 if self.target_coordinates[1] > self.coordinates[1]
                      else -1 if self.target_coordinates[1] < self.coordinates[1]
                      else 0)

                self.coordinates = [
                    self.coordinates[0] + dx,
                    self.coordinates[1] + dy
                ]
                self.moves_made += 1

            self.phase += 1
            self.move_gauge = 0

            # Update color based on remaining lifespan
            life_remaining = 1 - (self.moves_made / self.max_moves)
            red = int(255 * (1 - life_remaining))
            green = int(255 * life_remaining)
            self.colour = f"#{red:02x}{green:02x}00"
        else:
            self.move_gauge += 1

    def check_boundaries(self):
        """Check if tracker has expired or left the grid."""
        x, y = self.coordinates
        return (x <= self.left_bound or
                x >= self.right_bound or
                y <= self.up_bound or
                y >= self.down_bound or
                self.moves_made >= self.max_moves)

    def display(self, canvas):
        """Display tracker with pulsing effect."""
        x, y = self.coordinates
        pulse = abs(math.sin(self.phase * 0.1))
        size_mod = pulse * 0.3 * self.cell_size

        canvas.create_rectangle(
            x * self.cell_size - size_mod,
            y * self.cell_size - size_mod,
            (x + 1) * self.cell_size + size_mod,
            (y + 1) * self.cell_size + size_mod,
            fill=self.colour,
            outline=''
        )
