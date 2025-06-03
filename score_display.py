from rpi_lcd import LCD
from threading import Lock


class ScoreDisplay:
    def __init__(self):
        self.lcd = LCD()
        self.lock = Lock()

    def update(self, player1_score, player2_score):
        with self.lock:
            try:
                self.lcd.text(f"GAME SCORE:", 1)
                self.lcd.text(f"P1: {player1_score} | P2: {player2_score}", 2)
            except Exception as e:
                print(f"Failed to update LCD: {e}")

    def clear(self):
        with self.lock:
            self.lcd.clear()
