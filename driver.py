#!/usr/bin/env python3
import logging
import subprocess

logging.basicConfig(filename='info.log', level=logging.INFO, datefmt='%H:%M:%S', format='%(asctime)s %(levelname)s: %(message)s')

def scan_start(addresses, completed, path):
    scans = []
    scans_new = []
    completed_scans = 0
    for index, address in enumerate(addresses):
        if address in completed:
            continue
        while True:
            if len(scans) < 10:
                logging.info('starting scan for {}'.format(address))
                scan = subprocess.Popen(['nmap', '-qqqq', '-sV', '-sC', '-oN', 'report.txt', '--append-output', address], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                scans.append(scan)
                break
            for scan in scans:
                if scan.poll() is not None:
                    completed_scans += 1
                    logging.info('completed scan: {}'.format(scan.args[7]))
                    logging.info('total completed: {} remaining: {}'.format(completed_scans, len(addresses) - index + 1))
                    with open(path, 'a') as f:
                        f.write(scan.args[7])
                        f.write('\n')
                else:
                    scans_new.append(scan)
            scans = scans_new
            scans_new = []
    for scan in scans:
        if scan.wait():
            logging.info('completed scan: {}'.format(scan.args[7]))
            with open(path, 'a') as f:
                f.write(scan.args[7])
                f.write('\n')

def parse_addresses(path, completed):
    with open(path) as f:
        addresses_string = f.read()
    with open(completed) as f:
        completed_string = f.read()
    addresses = addresses_string.split('\n')
    completed = completed_string.split('\n')
    logging.info('{} addresses parsed'.format(len(addresses)))
    return addresses, completed


addresses, completed = parse_addresses('addresses.txt', 'completed.txt')
scan_start(addresses, completed, 'completed.txt')
