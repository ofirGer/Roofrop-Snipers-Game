# protocol_server.py
import pickle


class Protocol:
    def __init__(self, socket):
        self.socket = socket

    def get_data(self):
        try:
            length = self.socket.recv(4).decode()
            data = self.socket.recv(int(length))
            return data
        except Exception as e:
            print(f"Receiving error: {e}")
            return None

    def send_data(self, data):
        try:
            length = str(len(data))
            zfill_length = length.zfill(4).encode()
            self.socket.sendall(zfill_length + data)
        except Exception as e:
            print(f"Sending error: {e}")

    def get_udp_data(self):
        try:
            packet, addr = self.socket.recvfrom(1024)  # large enough buffer
            length = int(packet[:4].decode())
            data = packet[4:4 + length]
            return data
        except Exception as e:
            print(f"Receiving error: {e}")
            return None

    def send_udp_data(self, data, ip, port):
        try:
            length = str(len(data)).zfill(4).encode()
            packet = length + data
            self.socket.sendto(packet, (ip, port))
        except Exception as e:
            print(f"Sending error: {e}")
