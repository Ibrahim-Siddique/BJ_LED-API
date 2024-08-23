import asyncio
import re
import os
import atexit
from flask import Flask, request, jsonify
from bleak import BleakClient
from dotenv import load_dotenv
from threading import Thread

load_dotenv()


class LEDController:
    def __init__(self, device_address):
        self.device_address = device_address
        self.client = BleakClient(self.device_address)
        self.characteristic_write = "0000ee01-0000-1000-8000-00805f9b34fb"
        self.loop = asyncio.new_event_loop()

    async def connect(self):
        await self.client.connect()
        print("Connected to the device")

    async def disconnect(self):
        if self.client and self.client.is_connected:
            await self.client.disconnect()
            print("Client disconnected")

    async def send_command(self, command):
        try:
            if self.client and self.client.is_connected:
                await self.client.write_gatt_char(self.characteristic_write, command)
                print(f"Sent command: {command.hex()}")
            else:
                print("Client is not connected.")
        except Exception as e:
            print(f"Failed to send command: {e}")

    def start_event_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.connect())
        self.loop.run_forever()

    def run_command(self, command):
        asyncio.run_coroutine_threadsafe(self.send_command(command), self.loop)


class FlaskServer:
    def __init__(self, led_controller, auth_password):
        self.led_controller = led_controller
        self.auth_password = auth_password
        self.app = Flask(__name__)
        self._setup_routes()

    def _setup_routes(self):
        @self.app.before_request
        def authenticate():
            password = request.headers.get('Authorization')
            if password != self.auth_password:
                return jsonify({"error": "Unauthorized"}), 401

        @self.app.route('/power_on', methods=['POST'])
        def power_on():
            self.led_controller.run_command(
                bytearray.fromhex("69 96 02 01 01"))
            return jsonify({"status": "Lights turned on"})

        @self.app.route('/power_off', methods=['POST'])
        def power_off():
            self.led_controller.run_command(
                bytearray.fromhex("69 96 02 01 00"))
            return jsonify({"status": "Lights turned off"})

        @self.app.route('/set_color', methods=['POST'])
        def set_color():
            hex_code = request.json.get('color')
            if not re.match(r'^#(?:[0-9a-fA-F]{3}){1,2}$', hex_code):
                return jsonify({"error": "Invalid hex code"}), 400
            rgb = self.hex_to_rgb(hex_code)
            command = self.create_color_command(rgb)
            self.led_controller.run_command(command)
            return jsonify({"status": "Color set", "color": hex_code})

    @staticmethod
    def hex_to_rgb(hex_value):
        hex_value = hex_value.lstrip('#')
        return tuple(int(hex_value[i:i + 2], 16) for i in (0, 2, 4))

    @staticmethod
    def create_color_command(rgb):
        red, green, blue = rgb
        command = bytearray.fromhex("69 96 05 02")
        command.extend([red, green, blue])
        return command

    def run(self, host='0.0.0.0', port=5000):
        self.app.run(host=host, port=port, threaded=True)


class Application:
    def __init__(self, led_device_address, auth_password):
        self.led_controller = LEDController(led_device_address)
        self.server = FlaskServer(self.led_controller, auth_password)

    def start(self):
        loop_thread = Thread(target=self.led_controller.start_event_loop)
        loop_thread.start()

        atexit.register(self.cleanup)

        self.server.run()

    def cleanup(self):
        asyncio.run_coroutine_threadsafe(
            self.led_controller.disconnect(), self.led_controller.loop).result()


if __name__ == "__main__":
    # Load environment variables
    auth_password = os.getenv("AUTH_PASSWORD", "")
    led_device_address = os.getenv("LED_DEVICE_ADDRESS", "")

    # Initialize and start the application
    app = Application(led_device_address, auth_password)
    app.start()
