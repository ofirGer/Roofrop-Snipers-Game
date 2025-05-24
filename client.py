import pygame
import socket
import pickle
import player
import gun
import config
import protocol

class GameClient:
    def __init__(self):
        # Networking setup
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.pro = protocol.Protocol(self.client_socket)
        self.running = True
        self.connected = False
        self.connect_to_server()

    def connect_to_server(self):
        try:
            self.client_socket.connect((config.SERVER_IP, config.PORT))
            self.player_id = self.pro.get_data().decode()
            print(f"Connected to server as Player {self.player_id}")

            print("Waiting for a second player...")
            start_signal = self.pro.get_data().decode()
            if start_signal != "start":
                print("Unexpected server response. Exiting.")
                self.running = False
                return
            else:
                print("Both players connected. Game starting!")
                self.connected = True

                # Initialize Pygame after both players connect
                pygame.init()
                self.screen = pygame.display.set_mode((config.WIDTH, config.HEIGHT))
                pygame.display.set_caption(f"Rooftop Snipers - Player  {int(self.player_id) + 1}")
                self.clock = pygame.time.Clock()

                self.local_player = player.Player(config.ROOF_X + 20, config.ROOF_Y)
                self.local_gun = gun.Gun(self.local_player, self.screen)

                self.enemy_player = player.Player(config.ROOF_X + config.ROOF_WIDTH - 70, config.ROOF_Y)
                self.enemy_gun = gun.Gun(self.enemy_player, self.screen, mirror=True)

        except Exception as e:
            print(f"Failed to connect to server: {e}")
            self.running = False

    def send_and_receive_data(self):
            try:
                player_data = self.local_player.get_data()
                gun_data = self.local_gun.get_data()
                combined_data = {
                    "player": player_data,
                    "gun": gun_data
                }

                self.pro.send_data(pickle.dumps(combined_data))

                enemy_data = pickle.loads(self.pro.get_data())
                if "player" in enemy_data:
                    original_x = enemy_data["player"]["x"]
                    self.enemy_player.x = config.WIDTH - original_x - self.enemy_player.width
                    self.enemy_player.y = enemy_data["player"]["y"]
                    self.enemy_player.lean_angle = -enemy_data["player"]["lean_angle"]

                if "gun" in enemy_data:
                    self.enemy_gun.angle = enemy_data["gun"]["angle"]
                    self.enemy_gun.bullet_angle = -enemy_data["gun"]["bullet_angle"]
                    self.enemy_gun.firing = enemy_data["gun"]["firing"]
                    self.enemy_gun.current_bullet_frame = enemy_data["gun"]["bullet_frame"]

            except Exception as e:
                print(f"Connection error: {e}")
                self.running = False

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_w:
                self.local_player.jump()

    def update_game_logic(self):
        self.local_player.apply_movement()
        self.local_gun.apply_gun_movement()
        self.local_player.handle_collision_with(self.enemy_player)

    def draw(self):
        self.screen.fill(config.BACKGROUND_COLOR)
        pygame.draw.rect(
            self.screen, config.ROOF_COLOR,
            (config.ROOF_X, config.ROOF_Y, config.ROOF_WIDTH, config.ROOF_HEIGHT)
        )
        self.local_player.draw(self.screen)
        self.local_gun.draw()
        self.enemy_player.draw(self.screen, mirror=True)
        self.enemy_gun.update_position()
        self.enemy_gun.draw()
        pygame.display.flip()

    def run(self):
        if not self.connected:
            return

        while self.running:
            self.clock.tick(config.FPS)
            self.handle_events()
            self.update_game_logic()
            self.send_and_receive_data()
            self.draw()
            self.local_player.check_hit_by_bullet(self.enemy_gun)
        pygame.quit()

if __name__ == "__main__":
    game = GameClient()
    game.run()