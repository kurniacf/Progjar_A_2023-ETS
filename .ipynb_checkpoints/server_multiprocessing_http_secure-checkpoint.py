import os
from socket import *
import socket
import multiprocessing
import time
import sys
import logging
import ssl

from http import HttpServer

httpserver = HttpServer()

def process_the_client(connection, address):
    rcv = ""
    while True:
        try:
            data = connection.recv(32)
            if data:
                d = data.decode()
                rcv = rcv + d
                if rcv[-2:] == '\r\n':
                    logging.warning("data dari client: {}".format(rcv))
                    hasil = httpserver.proses(rcv)
                    hasil = hasil + "\r\n\r\n".encode()
                    logging.warning("balas ke client: {}".format(hasil))
                    connection.sendall(hasil)
                    rcv = ""
                    connection.close()
            else:
                break
        except OSError as e:
            pass
    connection.close()


def server(hostname='testing.net'):
    the_clients = []
    hostname = hostname
    cert_location = os.getcwd() + '/certs/'
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile=cert_location + 'domain.crt',
                            keyfile=cert_location + 'domain.key')
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    my_socket.bind(('0.0.0.0', 8443))
    my_socket.listen(200)
    while True:
        connection, client_address = my_socket.accept()
        try:
            secure_connection = context.wrap_socket(connection, server_side=True)
            logging.warning("connection from {}".format(client_address))
            process = multiprocessing.Process(target=process_the_client, args=(secure_connection, client_address))
            process.start()
            the_clients.append(process)
        except ssl.SSLError as essl:
            print(str(essl))


def main():
    server()

if __name__ == "__main__":
    main()
