import queue
import select
import socket
import threading
import time

from RC28Controller import RC28Controller


def run_server(vendor_id=3110, product_id=30, port=5100):
    event_queue = queue.Queue()
    controller = RC28Controller(vendor_id, product_id)

    # Define callback functions for RC28Controller events
    def on_button_press(button):
        event_queue.put(("button_press", button))

    def on_button_release():
        event_queue.put(("button_release",))

    def on_wheel(val):
        print(val)
        event_queue.put(("wheel", val))

    # Register callbacks with the controller
    controller.register_callback("button_press", on_button_press)
    controller.register_callback("button_release", on_button_release)
    controller.register_callback("wheel", on_wheel)

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("0.0.0.0", port))
    server_socket.listen(5)
    print(f"Server listening on port {port}")
    clients = []

    while True:
        readable, _, _ = select.select([server_socket] + clients, [], [], 0.1)
        for sock in readable:
            if sock is server_socket:
                client_sock, addr = server_socket.accept()
                clients.append(client_sock)
                print(f"Client connected: {addr}")
            else:
                try:
                    data = sock.recv(1024)
                    if not data:
                        clients.remove(sock)
                        sock.close()
                        print("Client disconnected")
                    else:
                        command = data.decode().strip()
                        if command.startswith("SET_LIGHTS "):
                            parts = command.split()
                            if len(parts) == 4:
                                T, L, R = map(int, parts[1:])
                                controller.set_lights(T, L, R)
                except:
                    clients.remove(sock)
                    sock.close()

        try:
            while True:
                event = event_queue.get(block=False)
                event_str = " ".join(map(str, event)) + "\n"
                for client in list(clients):
                    try:
                        client.sendall(event_str.encode())
                    except:
                        clients.remove(client)
                        client.close()
        except queue.Empty:
            pass


if __name__ == "__main__":
    run_server()
