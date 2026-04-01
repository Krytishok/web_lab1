# client.py
import socket
import sys
import os
from protocol import SocketStream
from config import BUFFER_SIZE

# --- НАСТРОЙКИ КЛИЕНТА ---
TARGET_HOST = '127.0.0.1' 
TARGET_PORT = 65432
CLIENT_DATA_DIR = './client_data'

class FileClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = None
        self.stream = None
        self._ensure_data_dir()

    def _ensure_data_dir(self):
        """Создает директорию для клиентских файлов, если её нет."""
        if not os.path.exists(CLIENT_DATA_DIR):
            os.makedirs(CLIENT_DATA_DIR)
            print(f"[CLIENT] Директория {CLIENT_DATA_DIR} создана.")

    def _get_file_path(self, filename):
        """Возвращает полный путь к файлу в директории клиента."""
        return os.path.join(CLIENT_DATA_DIR, os.path.basename(filename))

    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            print(f"[CLIENT] Подключение к {self.host}:{self.port}...")
            self.socket.connect((self.host, self.port))
            self.stream = SocketStream(self.socket)
            welcome = self.stream.recv_line()
            print(f"[SERVER] {welcome}")
            return True
        except ConnectionRefusedError:
            print("[CLIENT] Ошибка: Сервер недоступен (отказ в подключении).")
            return False
        except Exception as e:
            print(f"[CLIENT] Ошибка подключения: {e}")
            return False

    def download_file(self, filename, size):
        """Сохраняет файл в клиентскую директорию."""
        filepath = self._get_file_path(filename)
        try:
            with open(filepath, 'wb') as f:
                received = 0
                while received < size:
                    chunk = self.stream.recv_data(min(BUFFER_SIZE, size - received))
                    f.write(chunk)
                    received += len(chunk)
            print(f"[CLIENT] Файл {filename} сохранен в {CLIENT_DATA_DIR} ({size} байт).")
        except Exception as e:
            print(f"[CLIENT] Ошибка записи файла: {e}")
            if os.path.exists(filepath):
                os.remove(filepath)

    def run(self):
        if not self.connect():
            return

        try:
            while True:
                try:
                    cmd = input(f"\nCommand (LIST, UPLOAD <file>, DOWNLOAD <file>, EXIT) [{CLIENT_DATA_DIR}]: ").strip()
                except (EOFError, KeyboardInterrupt):
                    print("\n[CLIENT] Ввод прерван.")
                    break
                    
                if not cmd:
                    continue

                parts = cmd.split(maxsplit=1)
                action = parts[0].upper()
                arg = parts[1] if len(parts) > 1 else ""

                if action == "EXIT":
                    self.stream.send_line("EXIT")
                    try:
                        print(f"[SERVER] {self.stream.recv_line()}")
                    except:
                        pass
                    break

                elif action == "LIST":
                    self.stream.send_line("LIST")
                    print(f"[SERVER] {self.stream.recv_line()}")

                elif action == "UPLOAD" and arg:
                    # Ищем файл в папке client_data
                    filepath = self._get_file_path(arg)
                    if not os.path.exists(filepath):
                        print(f"[CLIENT] Ошибка: Файл '{arg}' не найден в {CLIENT_DATA_DIR}")
                        # Подсказка: покажем, что есть в папке
                        try:
                            files = os.listdir(CLIENT_DATA_DIR)
                            if files:
                                print(f"[CLIENT] Доступные файлы: {', '.join(files)}")
                            else:
                                print(f"[CLIENT] Папка {CLIENT_DATA_DIR} пуста.")
                        except:
                            pass
                        continue
                    
                    size = os.path.getsize(filepath)
                    if size == 0:
                        print("[CLIENT] Ошибка: Пустые файлы запрещены.")
                        continue

                    self.stream.send_line(f"UPLOAD {arg}")
                    resp = self.stream.recv_line()
                    print(f"[SERVER] {resp}")

                    if resp.startswith("OK"):
                        self.stream.send_line(str(size))
                        with open(filepath, 'rb') as f:
                            self.stream.send_data(f.read())
                        # Ждем финального подтверждения
                        print(f"[SERVER] {self.stream.recv_line()}")

                elif action == "DOWNLOAD" and arg:
                    self.stream.send_line(f"DOWNLOAD {arg}")
                    resp = self.stream.recv_line()
                    print(f"[SERVER] {resp}")

                    if resp.startswith("OK"):
                        try:
                            f_size = int(resp.split()[-1])
                            self.download_file(arg, f_size)
                        except (ValueError, IndexError):
                            print("[CLIENT] Ошибка протокола: неверный размер файла.")
                    elif resp.startswith("ERR"):
                        continue
                else:
                    # Отправляем команду серверу, пусть он вернет ошибку
                    self.stream.send_line(cmd)
                    print(f"[SERVER] {self.stream.recv_line()}")

        except ConnectionError as e:
            print(f"\n[CLIENT] Соединение разорвано: {e}")
        except KeyboardInterrupt:
            print("\n[CLIENT] Прервано пользователем.")
        finally:
            if self.socket:
                self.socket.close()
                print("[CLIENT] Соединение закрыто.")

if __name__ == "__main__":
    client = FileClient(TARGET_HOST, TARGET_PORT)
    client.run()