from RC28Controller import RC28Controller

def local_client():
    controller = RC28Controller()

    def on_button_press(button):
        print(f"Button {button} pressed")

    def on_button_release():
        print("Button released")

    def on_wheel(val):
        print(f"Wheel: {val}")

    controller.register_callback('button_press', on_button_press)
    controller.register_callback('button_release', on_button_release)
    controller.register_callback('wheel', on_wheel)

    # Example: Turn on all lights
    controller.set_lights(True, True, True)
    time.sleep(2)
    controller.set_lights(False, False, False)

    try:
        while True:
            time.sleep(1)  # Keep the client running
    except KeyboardInterrupt:
        controller.close()

if __name__ == "__main__":
    local_client()