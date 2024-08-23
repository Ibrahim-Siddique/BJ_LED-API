const axios = require("axios");

class LEDController {
  constructor(baseUrl, authPassword) {
    this.baseUrl = baseUrl;
    this.authPassword = authPassword;
    this.headers = { Authorization: authPassword };
  }

  async _sendRequest(endpoint, method = "POST", data = null) {
    const url = `${this.baseUrl}/${endpoint}`;
    try {
      const response = await axios({
        method: method,
        url: url,
        headers: this.headers,
        data: data,
      });

      if (response.status === 200) {
        return response.data;
      } else {
        throw new Error(`Request failed with status code ${response.status}`);
      }
    } catch (error) {
      throw new Error(`Error in request: ${error.message}`);
    }
  }

  powerOn() {
    return this._sendRequest("power_on");
  }

  powerOff() {
    return this._sendRequest("power_off");
  }

  setColor(hexCode) {
    return this._sendRequest("set_color", "POST", { color: hexCode });
  }
}

// Example usage
(async () => {
  const authPassword = "auth_password";
  const baseUrl = "http://localhost:5000"; // Flask server URL

  const ledController = new LEDController(baseUrl, authPassword);

  try {
    // Power on the lights
    console.log(await ledController.powerOn());

    await new Promise((resolve) => setTimeout(resolve, 1000));

    // Set the LED color to red
    console.log(await ledController.setColor("#FF0000"));

    await new Promise((resolve) => setTimeout(resolve, 3000));

    // Power off the lights
    console.log(await ledController.powerOff());
  } catch (error) {
    console.error(`An error occurred: ${error.message}`);
  }
})();
