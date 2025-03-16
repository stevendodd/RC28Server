import hid
import threading
import time

class RC28Controller:
    # Mapping of light states to command bytes
    LIGHT_MAP = {
        (True, True, True): 0,    # Transmit, Left Orange, Right Orange on
        (False, True, True): 1,   # Left Orange, Right Orange on
        (True, False, True): 2,   # Transmit, Right Orange on
        (False, False, True): 3,  # Right Orange on
        (True, True, False): 4,   # Transmit, Left Orange on
        (False, True, False): 5,  # Left Orange on
        (True, False, False): 6,  # Transmit on
        (False, False, False): 7  # All off
    }

    def __init__(self, vendor_id=3110, product_id=30):
        """Initialize the controller with the device's vendor and product IDs."""
        self.h = hid.device()
        try:
            self.h.open(vendor_id, product_id)
            self.h.set_nonblocking(1)
            print(f"Connected to {self.h.get_product_string()}")
        except IOError as e:
            raise Exception(f"Failed to open device: {e}")

        self.callbacks = {
            'button_press': [],
            'button_release': [],
            'wheel': []
        }
        self.running = True
        self.thread = threading.Thread(target=self._read_loop, daemon=True)
        self.thread.start()

    def set_lights(self, transmit, left_orange, right_orange):
        """Set the state of the lights on the controller."""
        key = (bool(transmit), bool(left_orange), bool(right_orange))
        byte = self.LIGHT_MAP[key]
        try:
            self.h.write([0x0, 0x1, byte])
        except IOError as e:
            print(f"Failed to set lights: {e}")

    def register_callback(self, event_type, callback):
        """Register a callback function for a specific event type."""
        if event_type in self.callbacks:
            self.callbacks[event_type].append(callback)

    def _read_loop(self):
        """Continuously read data from the device and trigger callbacks."""
        while self.running:
            try:
                d = self.h.read(64)
                if len(d) == 32 and d[0] == 1:  # Valid frame
                    if d[3] > 0:  # Wheel event
                        val = d[1]
                        if d[3] == 2:
                            val = -val
                        for cb in self.callbacks['wheel']:
                            cb(val)
                    elif d[3] == 0:  # Button event
                        if d[5] == 5:
                            for cb in self.callbacks['button_press']:
                                cb('F1')
                        elif d[5] == 3:
                            for cb in self.callbacks['button_press']:
                                cb('F2')
                        elif d[5] == 6:
                            for cb in self.callbacks['button_press']:
                                cb('Transmit')
                        elif d[5] == 7:
                            for cb in self.callbacks['button_release']:
                                cb()
            except IOError:
                pass  # Ignore read errors
            time.sleep(0.01)  # Prevent CPU hogging

    def close(self):
        """Close the connection to the device."""
        self.running = False
        self.thread.join()
        self.h.close()