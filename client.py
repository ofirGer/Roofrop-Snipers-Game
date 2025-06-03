import pygame
import socket
import pickle
import player
import gun
import config
import protocol
import camera


class GameClient:
    def __init__(self):
        # Networking setup
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.pro = protocol.Protocol(self.client_socket)
        self.running = True
        self.connected = False
        self.connect_to_server()
        self.camera = camera.Camera()
        self.roof_image = pygame.image.load("assets/roof.png").convert_alpha()

        self.player1_score = 0
        self.player2_score = 0
        self.score_to_win = 5
        self.game_over = False
        self.font = pygame.font.SysFont(None, 48)

        self.local_player_out = False

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

                self.local_player = player.Player(config.ROOF_X + 350, config.ROOF_Y, int(self.player_id))
                self.local_gun = gun.Gun(self.local_player, self.screen, int(self.player_id))

                self.enemy_player = player.Player(config.ROOF_X + config.ROOF_WIDTH - 70, config.ROOF_Y, 1 - int(self.player_id))
                self.enemy_gun = gun.Gun(self.enemy_player, self.screen, 1- int(self.player_id), mirror=True)

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
                    self.enemy_player.out_of_roof = enemy_data["player"]["out_of_roof"]

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
        self.send_and_receive_data()
        # Check if a player fell off the roof
        if not self.game_over:
            if self.local_player.out_of_roof:
                self.player2_score += 1
                self.check_win()
            elif self.enemy_player.out_of_roof:
                self.player1_score += 1
                self.check_win()

    def check_win(self):
        if self.player1_score >= self.score_to_win:
            #self.game_over = True
            self.display_win("Player 1")
        elif self.player2_score >= self.score_to_win:
            #self.game_over = True
            self.display_win("Player 2")
        else:
            # Pause briefly before resetting round
            pygame.time.delay(1000)
            self.reset_round()

    def reset_round(self):
        self.local_player.x = config.ROOF_X + 350
        self.local_player.y = config.ROOF_Y
        self.local_player.vel_x = 0
        self.local_player.vel_y = 0
        self.local_player.lean_angle = 0
        self.local_player.lean_speed = 0
        self.local_player.change_max_angle = False
        self.local_player.on_ground = True
        self.local_player.out_of_roof = False


    def display_win(self, winner):
        win_text = self.font.render(f"{winner} Wins!", True, (255, 215, 0))
        self.screen.blit(win_text, (config.WIDTH // 2 - win_text.get_width() // 2, config.HEIGHT // 2))
        pygame.display.flip()
        pygame.time.wait(3000)

    def draw(self):
        self.screen.fill(config.BACKGROUND_COLOR)

        self.camera.update((self.local_player.x, self.local_player.y), (self.enemy_player.x, self.enemy_player.y))

        # Draw roof
        roof_pos = self.camera.apply((config.ROOF_X, config.ROOF_Y))
        roof_scaled = self.camera.apply_surface(self.roof_image)
        self.screen.blit(roof_scaled, roof_pos)

        # Draw players and guns using transformed coordinates
        self.local_player.draw(self.screen, camera=self.camera)
        self.local_gun.draw(camera=self.camera)
        self.enemy_player.draw(self.screen, mirror=True, camera=self.camera)
        self.enemy_gun.update_position()
        self.enemy_gun.draw(camera=self.camera)
        score_text = self.font.render(f"{self.player1_score} : {self.player2_score}", True, (255, 255, 255))
        self.screen.blit(score_text, (config.WIDTH // 2 - score_text.get_width() // 2, 20))
        pygame.display.flip()


    def run(self):
        if not self.connected:
            return

        while self.running:
            self.clock.tick(config.FPS)
            self.handle_events()
            self.local_player.check_hit_by_bullet(self.enemy_gun)
           # self.send_and_receive_data()
            self.update_game_logic()
            self.draw()

        pygame.quit()

if __name__ == "__main__":
    game = GameClient()
    game.run()