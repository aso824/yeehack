![Logo](https://github.com/aso824/yeehack/blob/master/logo.png)

# Yeehack

Simple way to control your Yeelock bluetooth device, without official app.


## Installation

Note: you need to have Python 3.8+ and configured Bluetooth adapter.

1. Pull the source code
2. Activate virtualenv

       python3 -m venv venv
       source venv/bin/activate
       
3. Install required packages

       pip install -r requirements.txt
       
## Usage

Tip: run `python3 yeehack.py --help` to see all available options.

First, you need to acquire S/N and sign key for your lock(s). To do that, run:

    python3 yeehack.py fetch
    
and follow instructions on the screen. You should get list of your locks.  
**Copy and store somewhere S/N and sign key.**

Then you can interact with your lock using commands like:

    python3 yeehack.py battery [S/N]
    python3 yeehack.py do lock [S/N] [sign key]

## Web server

You can also run a simple webserver to control any lock in range of your PC/RPi etc.
This way, you can interact with your locks from Home Assistant, using NodeRED.

    python3 yeehack.py server
    
Default port is 8080, add `--port [PORT]` to change.  

Fetch info about lock (currently only battery state):

    curl -XPOST http://localhost:8080/info -d '{"sn": "...", "timeout": "5"}'
    
Lock or unlock:

    curl -XPOST http://localhost:8080/do -d '{"sn": "...", "sign_key": "...", "timeout": "5", "action": "unlock"}' 

Supported actions: `lock`, `unlock`, `temp_unlock` (unlock and lock after a while)

## Home Assistant
You can now use your Yeelock with Home Assistant. This requires using a Docker container to run the Yeehack server. The Yeehack server will use Bluetooth to communicate with your Yeelock.

### Known issues
Sometimes communication with Yeelock can fail. This seems to be due to Home Assistant, or some other application on the host, locking the Bluetooth adapter. This could be fixed in the future with the development of a Yeelock-specific Home Assistant integration.

### Steps
#### Create Docker container
1. Create file `docker-compose.yml` with contents:

```
version: '3'
services:
  yeehack:
    build:
      context: https://github.com/aso824/yeehack.git
      dockerfile: Dockerfile
    network_mode: host # this may not be necessary for all setups but works best with hosts bluetooth
    ports:
      - "8888:8080"
    volumes:
      - '/var/run/dbus:/run/dbus:ro'
```
2. Run `docker compose up -d`

Yeehack server will now be running on port 8888.

#### Add Home Assistant configuration
3. Obtain your Yeelock keys using the steps above.

4. Locate your `configuration.yaml` file and add the following, as an example, substituting in your keys:

```
input_boolean:
  yeelock_state:
    name: Yeelock State
    icon: mdi:lock
    initial: true

lock:
  - platform: template
    name: Yeelock Lock
    value_template: "{{ is_state('input_boolean.yeelock_state', 'on') }}"
    unique_id: yeelock
    lock:
      - service: rest_command.yeelock_lock
      - service: input_boolean.turn_on
        target:
          entity_id: input_boolean.yeelock_state
    unlock:
      - service: rest_command.yeelock_unlock
      - service: input_boolean.turn_off
        target:
          entity_id: input_boolean.yeelock_state

rest_command:
  yeelock_lock:
    url: http://127.0.0.1:8888/do
    method: POST
    content_type:  'application/json; charset=utf-8'
    payload: '{"sn": "YYYYY", "sign_key": "XXXXX", "timeout": "5", "action": "lock"}'
  yeelock_unlock:
    url: http://127.0.0.1:8888/do
    method: POST
    content_type:  'application/json; charset=utf-8'
    payload: '{"sn": "YYYYY", "sign_key": "XXXXX", "timeout": "5", "action": "unlock"}'
```

## Development

See [PROTOCOL.md](PROTOCOL.md) for details and feel free to create a pull request with improvements.  
Note: I don't plan to focus on this repo, because I'll try to create integration for Home Assistant.

## Credits

- [cnrd/yeelock](https://github.com/cnrd/yeelock)
- _jdobosz_ and his post [in this thread](https://community.home-assistant.io/t/xiaomi-mijia-yeelock-integration/92331/43)

## License

The Apache License 2.0. Please see [LICENSE](LICENSE) for more information.
