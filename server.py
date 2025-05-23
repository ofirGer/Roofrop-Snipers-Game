import socket
import threading
import protocol

SERVER_IP = "0.0.0.0"
PORT = 5555

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((SERVER_IP, PORT))
server_socket.listen(2)
print(f"Server started on {SERVER_IP}:{PORT}. Waiting for players...")

players = [{}, {}]
connected_event = threading.Event()
connected_clients = [None, None]


def handle_client(client_socket, player_id):
    global players
    print(f"Player {player_id} connected.")

    pro = protocol.Protocol(client_socket)
    client_socket.send(str(player_id).encode())

    connected_clients[player_id] = client_socket
    if all(connected_clients):
        connected_event.set()

    connected_event.wait()

    try:
        pro.send_data("start")
    except Exception as e:
        print(f"Failed to send start to player {player_id}: {e}")
        return

    try:
        while True:
            data = pro.get_data()
            if data is None:
                print(f"Player {player_id} disconnected.")
                break

            players[player_id] = data
            enemy_data = players[1 - player_id]
            pro.send_data(enemy_data)

    except Exception as e:
        print(f"Player {player_id} caused error: {e}")

    players[player_id] = {}
    client_socket.close()

def start_server():
    player_count = 0

    while True:
        client_socket, addr = server_socket.accept()
        print(f"Connected to {addr}")

        if player_count < 2:
            thread = threading.Thread(target=handle_client, args=(client_socket, player_count), daemon=True)
            thread.start()
            player_count += 1
        else:
            print("Server full. Rejecting new connection.")
            client_socket.send(b'Server full')
            client_socket.close()

start_server()
