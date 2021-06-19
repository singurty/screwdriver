#!/usr/bin/env python3
import logging
from os import walk
from bcoding import bencode, bdecode
import hashlib
from struct import pack, unpack
import socket
from urllib.parse import urlparse
import random
import ipaddress
import subprocess

logging.basicConfig(filename='info.log', level=logging.INFO, datefmt='%H:%M:%S', format='%(asctime)s %(levelname)s: %(message)s')
peer_id = b'-qB4170-t-FvepUJaWBf'

def tracker_connect_udp(torrent):
    info_binary = bencode(torrent['info'])
    info_hash = hashlib.sha1(info_binary).digest()
    connection_id = pack('>Q', 0x41727101980)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.settimeout(2)
    action = pack('>I', 0)
    peers = []
    for tracker in torrent['announce-list']:
        tracker = tracker[0]
        if not tracker.startswith('udp'):
            continue
        parsed = urlparse(tracker)
        ip, port = socket.gethostbyname(parsed.hostname), parsed.port
        transaction_id = pack('>I', random.getrandbits(32))
        message = connection_id + action + transaction_id
        response = send_message_udp(sock, (ip, port), message, action, transaction_id, len(message))
        if response:
           peers += tracker_announce_udp(response[8:16], (ip, port), sock, info_hash)
    logging.info('number of peers: ' + str(len(peers)))
    return peers

def tracker_announce_udp(connection_id, connection, sock, info_hash):
    action = pack('>I', 1)
    ip_address = pack('>I', 0)
    num_want = pack('>i', -1)
    port = pack('>H', 8000)
    downloaded = pack('>Q', 0)
    left = pack('>Q', 100000000)
    uploaded = pack('>Q', 0)
    event = pack('>I', 0)
    key = pack('>I', 0)
    transaction_id = pack('>I', random.getrandbits(32))
    message = connection_id + action + transaction_id + info_hash + peer_id + downloaded + left + uploaded + event + ip_address + key + num_want + port
    response = send_message_udp(sock, connection, message, action, transaction_id, 20)
    if response and len(response) > 20:
        extra_bytes = len(response) - 20
        address_length = extra_bytes // 6
        addresses = []
        for offset in range(0, address_length):
            ip = format(ipaddress.IPv4Address(response[20 + (6 * offset) : 24 + (6 * offset)]))
            addresses.append(ip)
        return addresses
    return []


def send_message_udp(sock, connection, message, action, transaction_id, full_size):
    sock.sendto(message, connection)
    response = b''
    try:
        while True:
            buff = sock.recv(4096)
            response += buff
    except socket.timeout:
        pass
    if len(response) < full_size:
        return
    if action != response[:4] or transaction_id != response[4:8]:
        return
    return response


def scan_directory():
    files = []
    path = './torrents'
    for (dirpath, dirnames, filenames) in walk(path):
        files.extend(filenames)
    return files


def torrent_start():
    addresses = []
    for f in scan_directory():
        if f.endswith('.torrent'):
            logging.info('processing torrent: {}'.format(f))
            with open('./torrents/' + f, 'rb') as tb:
                torrent = bdecode(tb)
                peers = tracker_connect_udp(torrent)
                addresses.extend(peers)
                addresses = list(set(addresses))
    logging.info('total addresses to scan: {}'.format(len(addresses)))
    return addresses

def write_to_file(addresses):
    logging.info('writing addresses to file')
    with open('addresses.txt', 'w') as f:
        f.write('\n'.join(addresses))


addresses = torrent_start()
write_to_file(addresses)
