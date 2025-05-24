from socket import *
import socket
import logging
import os
from concurrent.futures import ProcessPoolExecutor
from file_protocol import FileProtocol

logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s [PID:%(process)d] %(message)s',
    datefmt='%H:%M:%S'
)

def process_client(connection, address):
    fp = FileProtocol()
    pid = os.getpid()
    logging.warning(f"Process {pid} handling connection from {address}")
    data_received = b""
    try:
        while True:
            data = connection.recv(4096)
            if data:
                data_received += data
                logging.warning(f"Process {pid} received data chunk from {address}")
            else:
                break
       
        if data_received:
            d = data_received.decode()
            logging.warning(f"Process {pid} processing request from {address}")
            hasil = fp.proses_string(d)
            hasil = hasil + "\r\n\r\n"
            connection.sendall(hasil.encode())
            logging.warning(f"Process {pid} sent response to {address}")
        else:
            logging.warning(f"Process {pid}: No data received from {address}")
    except Exception as e:
        logging.error(f"Process {pid} error with {address}: {str(e)}")
    finally:
        logging.warning(f"Process {pid} closing connection with {address}")
        connection.close()

class Server:
    def __init__(self, ipaddress='0.0.0.0', port=8889, max_processes=10):
        self.ipinfo = (ipaddress, port)
        self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.process_pool = ProcessPoolExecutor(
            max_workers=max_processes,
            mp_context=None,
            initializer=lambda: logging.info("Process initialized")
        )

    def run(self):
        logging.warning(f"Server starting on {self.ipinfo} with process pool")
        self.my_socket.bind(self.ipinfo)
        self.my_socket.listen(1)
        try:
            while True:
                connection, client_address = self.my_socket.accept()
                logging.warning(f"Main process: New connection from {client_address}")
                
                self.process_pool.submit(process_client, connection, client_address)
        except KeyboardInterrupt:
            logging.warning("Server shutting down...")
        finally:
            self.process_pool.shutdown(wait=True)
            self.my_socket.close()

def main():
    svr = Server(ipaddress='0.0.0.0', port=6666)
    svr.run()

if __name__ == "__main__":
    main()