import time
import socket
import threading

class RemoteRC28Controller:
    def __init__(self, host='localhost', port=5100):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.connect((host, port))
            print(f"Connected to server at {host}:{port}")
        except Exception as e:
            raise Exception(f"Failed to connect: {e}")

        self.callbacks = {
            'button_press': [],
            'button_release': [],
            'wheel': []
        }
        self.running = True
        self.thread = threading.Thread(target=self._read_loop, daemon=True)
        self.thread.start()

    def set_lights(self, transmit, left_orange, right_orange):
        command = f"SET_LIGHTS {int(transmit)} {int(left_orange)} {int(right_orange)}\n"
        self.sock.sendall(command.encode())

    def register_callback(self, event_type, callback):
        if event_type in self.callbacks:
            self.callbacks[event_type].append(callback)

    def _read_loop(self):
        buffer = ""
        while self.running:
            try:
                data = self.sock.recv(1024).decode()
                if not data:
                    break
                buffer += data
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    parts = line.strip().split()
                    if parts[0] == 'button_press':
                        for cb in self.callbacks['button_press']:
                            cb(parts[1])
                    elif parts[0] == 'button_release':
                        for cb in self.callbacks['button_release']:
                            cb()
                    elif parts[0] == 'wheel':
                        val = int(parts[1])
                        for cb in self.callbacks['wheel']:
                            cb(val)
            except:
                break

    def close(self):
        self.running = False
        self.thread.join()
        self.sock.close()