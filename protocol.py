# protocol_server.py
import pickle

class Protocol:
    def __init__(self, socket):
        self.socket = socket

    def get_data(self):
        data = b''
        while True:
            try:
                packet = self.socket.recv(4096)
                if not packet:
                    break
                data += packet
                try:
                    return pickle.loads(data)
                except pickle.UnpicklingError:
                    continue
            except Exception as e:
                print(f"Receiving error: {e}")
                break
        return None

    def send_data(self, obj):
        try:
            self.socket.sendall(pickle.dumps(obj))
        except Exception as e:
            print(f"Sending error: {e}")