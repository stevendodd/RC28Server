import time
from RemoteRC28Controller import RemoteRC28Controller
from RC28Controller import RC28Controller


def create_app(use_remote=False, host='localhost', port=5100):
    if use_remote:
        controller = RemoteRC28Controller(host, port)
    else:
        controller = RC28Controller()

    # Light controls
    transmit_var = False
    left_var = False
    right_var = False

    def set_lights():
        controller.set_lights(transmit_var, left_var, right_var)

    def on_button_press(button):
        nonlocal transmit_var, left_var, right_var
        if button == 'Transmit':
            print(transmit_var)
            transmit_var = not transmit_var
            controller.set_lights(transmit_var, left_var, right_var)
        print(f"Button {button} pressed")

    def on_button_release():
        print("Button released")

    def on_wheel(val):
        print(f"Wheel: {val}")

    controller.register_callback('button_press', on_button_press)
    controller.register_callback('button_release', on_button_release)
    controller.register_callback('wheel', on_wheel)

    while True:
        time.sleep(0.1)


if __name__ == "__main__":
    # For local use
    create_app(use_remote=True)
    # For remote use, uncomment and adjust host/port
    # create_app(use_remote=True, host='server_host', port=5000)