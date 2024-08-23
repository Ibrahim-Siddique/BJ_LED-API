import requests
import re


class LEDController:
    def __init__(self, base_url, auth_password):
        self.base_url = base_url
        self.auth_password = auth_password
        self.headers = {'Authorization': auth_password}

    def _send_request(self, endpoint, method='POST', json=None):
        url = f"{self.base_url}/{endpoint}"
        response = requests.request(
            method, url, headers=self.headers, json=json)

        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    def power_on(self):
        """Turn on the LED lights."""
        return self._send_request('power_on')

    def power_off(self):
        """Turn off the LED lights."""
        return self._send_request('power_off')

    def set_color(self, hex_code):
        """Set the color of the LED lights."""
        if not self._is_valid_hex(hex_code):
            raise ValueError(
                "Invalid hex code format. Must be #RRGGBB or #RGB.")
        return self._send_request('set_color', json={'color': hex_code})

    def _is_valid_hex(self, hex_code):
        """Check if the hex code is valid."""
        return bool(re.match(r'^#(?:[0-9a-fA-F]{3}){1,2}$', hex_code))


# Example usage
if __name__ == "__main__":
    import os
    import time
    from dotenv import load_dotenv

    load_dotenv()

    auth_password = os.environ["AUTH_PASSWORD"]
    base_url = 'http://localhost:5000'  # Flask server URL

    led_controller = LEDController(base_url, auth_password)

    try:
        # Power on the lights
        print(led_controller.power_on())

        time.sleep(1)

        # Set the LED color to red
        print(led_controller.set_color('#FF0000'))

        time.sleep(3)

        # Power off the lights
        print(led_controller.power_off())
    except Exception as e:
        print(f"An error occurred: {e}")
