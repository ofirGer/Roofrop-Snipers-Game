# camera.py
import pygame
import config
class Camera:
    def __init__(self, zoom=1):
        self.zoom = zoom
        self.offset = pygame.Vector2(0, 0)
        self.offset.y =  0

    def update(self, player1_pos, player2_pos):
        # Focus on midpoint between players
        midpoint = (pygame.Vector2(player1_pos) + pygame.Vector2(player2_pos)) / 2
        self.offset.x = midpoint.x - config.WIDTH / (2 * self.zoom)

        # Adjust zoom based on distance between players
        distance = abs(player1_pos[0] - player2_pos[0])

        # Distance-to-zoom logic
        max_distance = 800  # Distance at which zoom reaches minimum
        min_zoom = 0.8
        max_zoom = 1.0

        # Linear interpolation of zoom based on distance
        normalized = min(distance / max_distance, 1)
        self.zoom = max_zoom - (max_zoom - min_zoom) * normalized

    def apply(self, pos):
        # Adjust position based on offset and zoom
        return (
            (pos[0] - self.offset.x) * self.zoom,
            (pos[1] - self.offset.y) * self.zoom
        )

    def apply_rect(self, rect):
        # For drawing rectangles like the roof
        new_rect = rect.copy()
        new_rect.x, new_rect.y = self.apply((rect.x, rect.y))
        new_rect.width *= self.zoom
        new_rect.height *= self.zoom
        return new_rect

    def apply_surface(self, surface):
        w = int(surface.get_width() * self.zoom)
        h = int(surface.get_height() * self.zoom)
        return pygame.transform.smoothscale(surface, (w, h))
