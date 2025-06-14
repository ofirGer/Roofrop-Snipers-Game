import pygame

class Gun:
    def __init__(self, player1, screen,id, mirror=False):
        self.id = id
        self.image = pygame.image.load(f"assets/arm{self.id + 1}.png").convert_alpha()
        self.mirror = mirror
        self.bullet_frames = [pygame.image.load(f"assets/bullets/bullet{i}.png").convert_alpha() for i in range(1, 7)]
        for i in range(0, 6):
            self.bullet_frames[i] = pygame.transform.scale(self.bullet_frames[i], (4, 1500))
        self.bullet_angle = 0

        self.screen = screen
        self.player1 = player1
        self.angle = 0
        self.rotation_speed = 5
        self.max_angle = 180
        self.need_fire = False

        self.firing = False
        self.current_bullet_frame = 0
        self.bullet_timer = 0
        self.bullet_frame_delay = 5

        self.returning_to_normal = False
        self.return_speed = 5

    def update_position(self):
        # You can move the enemy hand more rightward by increasing x_offset when mirrored
        x_offset = 15
        y_offset = 45
        if self.mirror:
            x_offset += 10  # Move hand 15 pixels to the right for mirrored player

        self.x = self.player1.x + x_offset
        self.y = self.player1.y + y_offset

    def shoot(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_e]:
            if self.returning_to_normal:
                self.angle = 0
                self.returning_to_normal = False

            self.need_fire = True
            if self.angle < self.max_angle:
                self.angle += self.rotation_speed
                self.angle = min(self.angle, self.max_angle)
        else:
            if self.need_fire:
                self.start_bullet_animation()
                self.need_fire = False
                self.returning_to_normal = True

            if self.returning_to_normal:
                target_angle = self.player1.lean_angle
                if self.angle < target_angle:
                    self.angle += self.return_speed
                    if self.angle > target_angle:
                        self.angle = target_angle
                        self.returning_to_normal = False
                elif self.angle > target_angle:
                    self.angle -= self.return_speed
                    if self.angle < target_angle:
                        self.angle = target_angle
                        self.returning_to_normal = False
            else:
                self.angle = self.player1.lean_angle

    def start_bullet_animation(self):
        self.firing = True
        self.current_bullet_frame = 0
        self.bullet_timer = 0
        self.bullet_angle = self.angle

    def update_bullet_animation(self):
        if self.firing:
            self.bullet_timer += 1
            if self.bullet_timer >= self.bullet_frame_delay:
                self.bullet_timer = 0
                self.current_bullet_frame += 1
                if self.current_bullet_frame >= len(self.bullet_frames):
                    self.firing = False

    def draw_bullet(self, camera=None):
        if self.firing:
            frame = self.bullet_frames[self.current_bullet_frame]
            pivot = pygame.math.Vector2(self.x, self.y)
            offset = pygame.math.Vector2(0, 650)

            rotated_frame = pygame.transform.rotozoom(frame, self.bullet_angle, 1)
            rotated_offset = offset.rotate(-self.bullet_angle)
            bullet_pos = pivot + rotated_offset

            if camera:
                bullet_pos = camera.apply(bullet_pos)
                rotated_frame = camera.apply_surface(rotated_frame)

            rect = rotated_frame.get_rect(center=bullet_pos)
            self.screen.blit(rotated_frame, rect)

    def draw(self, camera=None):
        self.draw_bullet(camera=camera)  # Assuming draw_bullet will also need camera

        pivot = [self.x, self.y]
        offset = pygame.math.Vector2(0, 17)

        if self.mirror:
            image = pygame.transform.flip(self.image, True, False)
            rotated_image = pygame.transform.rotozoom(image, -self.angle, 1)
            rotated_offset = pygame.math.Vector2(-offset.x, offset.y).rotate(self.angle)
        else:
            rotated_image = pygame.transform.rotozoom(self.image, self.angle, 1)
            rotated_offset = offset.rotate(-self.angle)

        draw_x = pivot[0] + rotated_offset.x
        draw_y = pivot[1] + rotated_offset.y

        # Apply camera offset and zoom
        if camera:
            draw_x, draw_y = camera.apply((draw_x, draw_y))
            rotated_image = camera.apply_surface(rotated_image)

        rect = rotated_image.get_rect(center=(draw_x, draw_y))
        self.screen.blit(rotated_image, rect)

    def apply_gun_movement(self):
        self.update_position()
        self.shoot()
        self.update_bullet_animation()

    def get_data(self):
        return {
            'angle': self.angle,
            'firing': self.firing,
            'bullet_frame': self.current_bullet_frame,
            'bullet_angle': self.bullet_angle
        }
