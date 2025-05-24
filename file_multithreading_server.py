from socket import *
import socket
import logging
import threading
from concurrent.futures import ThreadPoolExecutor
from file_protocol import FileProtocol

logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s [%(threadName)s] %(message)s',
    datefmt='%H:%M:%S'
)

fp = FileProtocol()

class ProcessTheClient:
    def __init__(self, connection, address):
        self.connection = connection
        self.address = address
        self.worker_id = threading.current_thread().name

    def run(self):
        logging.warning(f"Worker {self.worker_id} handling connection from {self.address}")
        data_received = b""
        try:
            while True:
                data = self.connection.recv(4096)
                if data:
                    data_received += data
                    logging.warning(f"Worker {self.worker_id} received data chunk from {self.address}")
                else:
                    break
           
            if data_received:
                d = data_received.decode()
                logging.warning(f"Worker {self.worker_id} processing request from {self.address}")
                hasil = fp.proses_string(d)
                hasil = hasil + "\r\n\r\n"
                self.connection.sendall(hasil.encode())
                logging.warning(f"Worker {self.worker_id} sent response to {self.address}")
            else:
                logging.warning(f"Worker {self.worker_id}: No data received from {self.address}")
        except Exception as e:
            logging.error(f"Worker {self.worker_id} error with {self.address}: {str(e)}")
        finally:
            logging.warning(f"Worker {self.worker_id} closing connection with {self.address}")
            self.connection.close()

class Server:
    def __init__(self, ipaddress='0.0.0.0', port=8889, max_threads=1):
        self.ipinfo = (ipaddress, port)
        self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.thread_pool = ThreadPoolExecutor(
            max_workers=max_threads,
            thread_name_prefix='Worker'
        )

    def run(self):
        logging.warning(f"Server starting on {self.ipinfo} with thread pool")
        self.my_socket.bind(self.ipinfo)
        self.my_socket.listen(1)
        try:
            while True:
                connection, client_address = self.my_socket.accept()
                logging.warning(f"Main thread: New connection from {client_address}")
                
                client_handler = ProcessTheClient(connection, client_address)
                self.thread_pool.submit(client_handler.run)
        except KeyboardInterrupt:
            logging.warning("Server shutting down...")
        finally:
            self.thread_pool.shutdown(wait=True)
            self.my_socket.close()

def main():
    svr = Server(ipaddress='0.0.0.0',port=6666)
    svr.run()

if __name__ == "__main__":
    main()