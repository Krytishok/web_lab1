# server.py
import socket
import threading
import sys
from config import HOST, PORT
from protocol import SocketStream
from storage import StorageService
from commands import get_handler

class ClientSession(threading.Thread):
    """Поток для обработки одного клиента."""
    
    def __init__(self, conn, addr, storage: StorageService):
        super().__init__(daemon=True)
        self.conn = conn
        self.addr = addr
        self.storage = storage
        self.stream = SocketStream(conn)

    def run(self):
        print(f"[SERVER] Клиент подключен: {self.addr}")
        try:
            self.stream.send_line("OK Welcome to HTML File Server")
            
            while True:
                try:
                    command_line = self.stream.recv_line()
                except ConnectionError:
                    break

                if not command_line:
                    continue

                parts = command_line.split(maxsplit=1)
                cmd = parts[0].upper()
                args = parts[1] if len(parts) > 1 else ""

                print(f"[SERVER] {self.addr} -> {cmd}")

                handler = get_handler(cmd, self.stream, self.storage)
                
                if handler:
                    if cmd == 'EXIT':
                        handler.execute(args)
                        break
                    else:
                        handler.execute(args)
                else:
                    self.stream.send_line("ERR Unknown command")

        except Exception as e:
            print(f"[SERVER] Ошибка сессии {self.addr}: {e}")
        finally:
            self.stream.close()
            print(f"[SERVER] Клиент отключен: {self.addr}")

class FileServer:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.storage = StorageService()

    def start(self):
        try:
            self.socket.bind((HOST, PORT))
            self.socket.listen(5)
            print(f"[SERVER] Запущен на {HOST}:{PORT}")
            print(f"[SERVER] Директория хранения: {self.storage._ensure_directory.__self__}") # Просто инфо

            while True:
                conn, addr = self.socket.accept()
                session = ClientSession(conn, addr, self.storage)
                session.start()

        except KeyboardInterrupt:
            print("\n[SERVER] Остановка...")
        finally:
            self.socket.close()

if __name__ == "__main__":
    # Небольшой фикс для вывода пути в start
    import config
    print(f"[SERVER] Путь хранения: {config.STORAGE_DIR}")
    server = FileServer()
    server.start()