#!/usr/bin/python3

import argparse
import asyncio
import logging
from getpass import getpass

from tabulate import tabulate

from fetch import get_access_token, get_locks
from lock import Lock
from server import Server

parser = argparse.ArgumentParser(
    description='Control your Yeelock over Bluetooth.',
    epilog='Check for updates at https://github.com/aso824/yeehack'
)

parser.add_argument('--log-level', default='warning',
                    help='log level (default: warning)')

subparsers = parser.add_subparsers(help='Available commands:', dest='command', metavar='command', required=True)

parser_battery = subparsers.add_parser('battery', help='Get battery level')
parser_battery.add_argument('sn', help='Serial number (string) of your Yeelock - 8 alphanumeric characters')

parser_do = subparsers.add_parser('do', help='Execute lock/unlock/temp_unlock action')
parser_do.add_argument(
    'action', help='Action to do, can be "lock", "unlock" or "temp_unlock"',
    type=str, choices=['lock', 'unlock', 'temp_unlock'],
    metavar='action'
)
parser_do.add_argument('sn', help='Serial number (string) of your Yeelock - 8 alphanumeric characters')
parser_do.add_argument('sign_key', help='Bluetooth sign key from Yeelock server')

parser_battery = subparsers.add_parser('fetch', help='Get info about your locks from Yeelock server')

parser_server = subparsers.add_parser('server', help='Start HTTP server')
parser_server.add_argument(
    '-p', '--port',
    help='Set HTTP server listen port',
    type=int, default=8080, dest='http_port'
)

args = parser.parse_args()

log_levels = {
    'critical': logging.CRITICAL,
    'error': logging.ERROR,
    'warn': logging.WARNING,
    'warning': logging.WARNING,
    'info': logging.INFO,
    'debug': logging.DEBUG
}

logging.basicConfig(level=log_levels[args.log_level])


async def main():
    if args.command == 'battery':
        lock = await Lock.create(args.sn, bytearray())
        level = await lock.get_battery()

        print("Battery level: %d%%" % level)

    elif args.command == 'do':
        lock = await Lock.create(args.sn, bytearray.fromhex(args.sign_key))

        if args.action == 'lock':
            await lock.lock()
        elif args.action == 'unlock':
            await lock.unlock()
        elif args.action == 'temp_unlock':
            await lock.temp_unlock()

    elif args.command == 'fetch':
        zone = input('Zone (phone prefix without +): ')
        username = input('Username (phone number without prefix): ')
        password = getpass('Password: ')

        locks = get_locks(get_access_token(zone, username, password))

        print(tabulate(
            locks,
            headers={
                'name': 'Name',
                'sn': 'S/N',
                'sign_key': 'Sign key',
                'unlock_count': 'Unlock count',
                'add_time': 'Added at'
            },
            tablefmt="rounded_grid"
        ))
        print("Note: you have probably been logged off from all other devices")

    elif args.command == 'server':
        print("Listening on port %d..." % args.http_port)

        server = Server(args.http_port)

        await server.start()

try:
    asyncio.run(main())
except KeyboardInterrupt:
    pass
