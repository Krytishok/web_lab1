# protocol.py
import socket
from config import BUFFER_SIZE, ENCODING

class SocketStream:
    """Обертка над сокетом для надежной передачи данных по нашему протоколу."""
    
    def __init__(self, conn: socket.socket):
        self.conn = conn

    def send_line(self, message: str):
        """Отправляет строку с завершающим \n"""
        data = (message + "\n").encode(ENCODING)
        self.conn.sendall(data)

    def recv_line(self) -> str:
        """Получает строку до \n"""
        data = b""
        while True:
            chunk = self.conn.recv(1)
            if not chunk:
                raise ConnectionError("Connection lost while reading line")
            if chunk == b'\n':
                break
            data += chunk
        return data.decode(ENCODING).strip()

    def send_data(self, data: bytes):
        """Отправляет сырые байты"""
        self.conn.sendall(data)

    def recv_data(self, size: int) -> bytes:
        """Получает ровно size байт"""
        data = b""
        remaining = size
        while remaining > 0:
            chunk = self.conn.recv(min(BUFFER_SIZE, remaining))
            if not chunk:
                raise ConnectionError("Connection lost while reading data")
            data += chunk
            remaining -= len(chunk)
        return data

    def close(self):
        self.conn.close()