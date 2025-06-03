import pygame
import config
import math


class Player:
    def __init__(self, x, y, player_id):
        self.id = player_id
        self.image = pygame.image.load(f"assets/player{self.id + 1}.png")
        self.width, self.height = self.image.get_size()
        self.x = x
        self.y = y - self.height  # Adjust to sit on the roof
        self.vel_y = 0
        self.vel_x = 0  # Horizontal velocity
        self.gravity = 0.8
        self.jump_strength = -16
        self.on_ground = True

        # Leaning mechanics
        self.lean_angle = 0  # Starts upright
        self.lean_speed = 0  # Initial lean speed
        self.lean_direction = 1  # 1 = right, -1 = left
        self.max_lean = 100  # Max tilt angle
        self.change_max_angle = False
        self.recently_hit = False
        self.hit_cooldown = 0  # frames remaining until allowed to be hit again
        self.out_of_roof = False

    def jump(self):
        """Make the player jump if on the ground and lean direction is considered."""
        if self.on_ground:
            # Apply horizontal jump direction based on lean angle
            jump_direction = -1 if self.lean_angle > 0 else 1
            self.vel_y = self.jump_strength
            self.vel_x = jump_direction * abs(self.lean_angle) * 0.1  # Horizontal movement smoothened
            self.on_ground = False
            # reset leaning
            self.max_lean = abs(self.lean_angle) + 40
            if self.lean_angle == 0:
                self.lean_speed = 1
            else:
                self.lean_speed = abs(self.lean_angle) * 0.15  # Initial lean speed

            self.change_max_angle = False

    def apply_gravity(self):
        """Applies gravity and checks for roof collision."""
        self.vel_y += self.gravity
        self.y += self.vel_y

        # Check if player lands on the roof
        if self.y + self.height >= config.ROOF_Y and config.ROOF_X <= self.x <= config.ROOF_X + config.ROOF_WIDTH - self.width:
            self.y = config.ROOF_Y - self.height  # Place player on top of the roof
            self.vel_y = 0
            self.on_ground = True

            # Don't reset horizontal velocity if sliding from a hit
            if not self.recently_hit:
                self.vel_x = 0

    def lean_and_move(self):
        if self.change_max_angle and abs(self.lean_angle) < 10:
            self.max_lean *= 0.6
            self.change_max_angle = False

        if self.on_ground:
            if self.max_lean < 7:
                self.lean_angle = 0
                self.lean_speed = 0

            # Lean back and forth until slowing down
            self.lean_angle += self.lean_speed * self.lean_direction

            # If leaning too much, switch direction

            if abs(self.lean_angle) >= self.max_lean:
                self.lean_angle = (self.max_lean) * self.lean_direction
                self.lean_direction *= -1  # Reverse direction
                self.lean_speed = max(self.lean_speed * 0.65, 0.6)
                self.change_max_angle = True

    def update_position(self):
        """Update the player's position with smooth horizontal movement."""
        self.x += self.vel_x

    def draw(self, screen, mirror=False, camera=None):
        angle_to_draw = -self.lean_angle if mirror else self.lean_angle
        rotated_image = pygame.transform.rotate(self.image, angle_to_draw)
        if mirror:
            rotated_image = pygame.transform.flip(rotated_image, True, False)
        image_rect = rotated_image.get_rect(center=(self.x + self.width // 2, self.y + self.height // 2))

        draw_pos = image_rect.topleft
        if camera:
            draw_pos = camera.apply(draw_pos)
            rotated_image = camera.apply_surface(rotated_image)

        screen.blit(rotated_image, draw_pos)

    def apply_movement(self):
        self.apply_gravity()
        self.lean_and_move()
        self.update_position()

        # Handle hit cooldown
        if self.recently_hit:
            self.hit_cooldown -= 1
            if self.hit_cooldown <= 0:
                self.recently_hit = False
        if self.on_ground and abs(self.vel_x) > 0.1:
            self.vel_x *= 0.95  # Apply friction when sliding
        elif self.on_ground:
            self.vel_x = 0  # Snap to zero to avoid endless tiny sliding

        fall_threshold = config.ROOF_Y + 400
        if self.y >= fall_threshold:
            self.out_of_roof = True
        else:
            self.out_of_roof = False

    def check_hit_by_bullet(self, gun):
        """Check if this player is hit by the first frame of the opponent's bullet animation."""
        if self.recently_hit:
            return False

        if not gun.firing or gun.current_bullet_frame != 0:
            return False

        # Calculate bullet start and end points using angle
        angle_rad = math.radians(-gun.bullet_angle - 90)
        m = math.tan(angle_rad)
        hit_y = m * self.x - m * gun.x + gun.y

        if (self.y - 10 <= hit_y <= self.y + self.height + 10) and self.x < gun.x:
            print("You got hit!")
            self.apply_knockback(angle_rad)
            self.recently_hit = True
            self.hit_cooldown = 20  # ~0.33 seconds if running at 60 FPS
            return True

        return False

    def apply_knockback(self, angle, x_force=10.0, y_force=60.0, change_angle=True):
        knockback_x = -math.cos(angle) * x_force
        knockback_y = -math.sin(angle) * y_force

        self.vel_x += knockback_x
        self.vel_y += knockback_y
        self.on_ground = False
        if change_angle:
            direction = -1 if knockback_x > 0 else 1
            self.lean_angle = direction * 20
            self.lean_direction = -direction
            self.lean_speed = abs(self.lean_angle) * 0.15
            self.max_lean = abs(self.lean_angle) + 40
            self.change_max_angle = False
        print(f"Knockback applied: vx={self.vel_x:.2f}, vy={self.vel_y:.2f}, lean={self.lean_angle}")

    def handle_collision_with(self, other):
        """Push the other player if this player collides with them, and apply leaning."""
        # Simple AABB collision detection
        if (
                self.x < other.x + other.width and
                self.x + self.width > other.x and
                self.y < other.y + other.height and
                self.y + self.height > other.y
        ):
            # Calculate overlap
            overlap_x = (self.x + self.width / 2) - (other.x + other.width / 2)
            push_dir = 1 if overlap_x > 0 else -1
            push_amount = (self.width + other.width) / 2 - abs(overlap_x)

            # Push both players apart
            self.x += push_dir * push_amount / 2

    def get_data(self):
        return {
            "x": self.x,
            "y": self.y,
            "lean_angle": self.lean_angle,
            "out_of_roof": self.out_of_roof,
        }
