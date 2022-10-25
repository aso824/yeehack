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

    curl -XPOST http://localhost:8080/info -d '{"sn": "..."}'
    
Lock or unlock:

    curl -XPOST http://localhost:8080/do -d '{"sn": "...", "sign_key": "...", "action": "unlock"}' 

Supported actions: `lock`, `unlock`, `temp_unlock` (unlock and lock after a while)

## Development

See [PROTOCOL.md](PROTOCOL.md) for details and feel free to create a pull request with improvements.  
Note: I don't plan to focus on this repo, because I'll try to create integration for Home Assistant.

## Credits

- [cnrd/yeelock](https://github.com/cnrd/yeelock)
- _jdobosz_ and his post [in this thread](https://community.home-assistant.io/t/xiaomi-mijia-yeelock-integration/92331/43)

## License

The Apache License 2.0. Please see [LICENSE](LICENSE) for more information.
