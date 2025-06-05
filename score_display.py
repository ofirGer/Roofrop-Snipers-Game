import socket
from rpi_lcd import LCD
import protocol
import time


def display_score():
    try:
        while True:
            data = pro.get_udp_data()
            if data:
                score = data.decode()
                lcd.text("Score:", 1)
                lcd.text(score, 2)
                time.sleep(0.5)
    except KeyboardInterrupt:
        lcd.clear()
        sock.close()


if __name__ == "__main__":
    lcd = LCD()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0", 6000))
    pro = protocol.Protocol(sock)

    print("Listening for score updates...")
    display_score()
