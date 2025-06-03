import socket
from rpi_lcd import LCD

lcd = LCD()
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("0.0.0.0", 6000))

print("Listening for score updates...")

try:
    while True:
        data, addr = sock.recvfrom(1024)
        score = data.decode()
        lcd.text("Score:", 1)
        lcd.text(score, 2)
except KeyboardInterrupt:
    lcd.clear()
    sock.close()
