# smarthome-api

## app.py
Microservice for communicating between management-api (Heroku Cloud) and smarthome-gateway (Raspberry Pi in local network).

Calls the RESTful API running on the Raspberry Pi to control smart home devices.

### Interface
Uses the AMQP exchange 'sh_exchange' with the queues 'sh_device_list' and 'sh_device'.

Handles the following routing keys:
- device_list.get
- device_list.add
- device.get
- device.set
- device.delete

#### device_list.get
Get list of all devices

Input: Empty

Output: List of all devices, e.g.
```json
 [
     {
        "device_id": "12",
        "device_name": "Hue ambiance lamp 2",
        "device_type": "Color temperature light (Hue)",
        "device_controller_address": "http://192.168.120.11/api/tAC901PfVfQMmNvrhc120uZeBa-Va8SNjc4vhtyh/lights/12",
        "device_data": {
            "on": true,
            "bri": 254,
            "ct": 230,
            "alert": "select",
            "colormode": "ct",
            "mode": "homeautomation",
            "reachable": true
        }
    },
    {
        "device_id": "42",
        "device_name": "Musikanlage",
        "device_type": "Chromecast Audio",
        "device_controller_address": "192.168.120.43",
        "device_data": {
            "port": "8009",
            "state": "paused",
            "volume": "0.1",
            "radio_station_url": "http://89.16.185.174:8000/autodj"
        }
    },
    ...
]
```

### device_list.add
Add a new device

Input: Json containing the following fields:
- **device_id** (str): Unique identifier. May not contain slashes or whitespace characters.
- **device_name** (str): Name of the device
- **device_type** (str): Type of the device. Currently supported: 'Chromecast Audio' and any string containing 'Hue'
- **device_controller_address** (str): Address needed to control the device, e.g. IP address of a smart light
- **device_data** (dict): Contains state information of the device (e.g. whether a light is on or off). May be empty.
```json
{
        "device_id": "123456abc",
        "device_name": "Something",
        "device_type": "Hue light",
        "device_controller_address": "192.168.120.50",
        "device_data": {}
}
```
Output: Json confirming data that was input

### device.get
Get data of specified device

Input: Json payload must contain 'device_id'

Output: Json data of device, e.g.
```json
{
    "uri": "http://smarthome.8wkc8cx8wzmkblhw.myfritz.net/devices/42",
    "device_id": "42",
    "device_name": "Musikanlage",
    "device_type": "Chromecast Audio",
    "device_controller_address": "192.168.120.43",
    "device_data": {
        "port": "8009",
        "state": "paused",
        "volume": "0.1",
        "radio_station_url": "http://89.16.185.174:8000/autodj"
    }
}
```

### device.set
Control device by changing its data (e.g. turning light on or off)

Input: 
- 'device_id' of the device you want to control
- data of the device you want to set, wrapped in 'device_data'
```json
{
"device_id": 3,
"device_data": {
        "on": true,
        ...
        }
}
```
Output: all of the device's data

### device.delete
Delete a device

Input:
- 'device_id' of the device you want to delete

Output:
- confirmation message (str), e.g. `"Deleted device {'device_id': '123', 'device_name': 'a', 'device_type': 'b s', 'device_controller_address': '192.168.120.43', 'device_data': {}}"`

