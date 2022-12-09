#!/usr/bin/env python
import argparse
import platform
import validators
import subprocess as sp
import time


ICMP_HEADER_SIZE = 8
IP_HEADER_SIZE = 20


def parse_args():
    parser = argparse.ArgumentParser(description='Find min MTU between localhost and specified host')
    parser.add_argument('host', type=str, help='Hostname or IPv4 address')
    return parser.parse_args()


def validate_args(args):
    assert validators.domain(args.host) or validators.ipv4(args.host), 'Host should be valid hostname or IPv4 address'
    assert Ping(args.host).ok, 'Host is not reachable'


class Ping:
    def __init__(self, host, mtu=56):
        self.proc = sp.run(['ping', host, '-c', '1', '-t', '100', '-D', '-s', str(mtu)],
                            stdout=sp.PIPE, stderr=sp.PIPE)

    @property
    def ok(self):
        return self.proc.returncode == 0

    @property
    def timeout_reached(self):
        # https://stackoverflow.com/a/921441/20136417
        code = 1 if platform.system() == 'Darwin' else 2
        return self.proc.returncode == code

    @property
    def error(self):
        return self.proc.stderr


# https://www.comparitech.com/net-admin/determine-mtu-size-using-ping/
def find_min_mtu(host):
    l = 0
    r = 2001
    while r - l > 1:
        m = l + (r - l) // 2
        ping = Ping(host, m)
        if ping.timeout_reached:
            raise RuntimeError('Timeout reached: {}'.format(ping.error))
        if ping.ok:
            l = m
        else:
            r = m
        time.sleep(0.5)
    return l + ICMP_HEADER_SIZE + IP_HEADER_SIZE


def main():
    args = parse_args()
    validate_args(args)
    min_mtu = find_min_mtu(args.host)
    print('Min MTU:', min_mtu)


if __name__ == '__main__':
    main()
