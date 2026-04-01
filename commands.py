# commands.py
from abc import ABC, abstractmethod
from protocol import SocketStream
from storage import StorageService
from config import MAX_FILE_SIZE

class CommandHandler(ABC):
    def __init__(self, stream: SocketStream, storage: StorageService):
        self.stream = stream
        self.storage = storage

    @abstractmethod
    def execute(self, args: str):
        pass

class ListCommand(CommandHandler):
    def execute(self, args: str):
        files = self.storage.list_files()
        if files:
            self.stream.send_line(f"OK {', '.join(files)}")
        else:
            self.stream.send_line("OK EMPTY")

class UploadCommand(CommandHandler):
    def execute(self, args: str):
        if not args:
            self.stream.send_line("ERR Filename required")
            return

        filename = args.strip()
        self.stream.send_line("OK Ready for upload")

        try:
            # Чтение размера файла
            size_line = self.stream.recv_line()
            file_size = int(size_line)

            if file_size <= 0:
                self.stream.send_line("ERR Empty files are not allowed")
                return
            
            if file_size > MAX_FILE_SIZE:
                self.stream.send_line("ERR File too large")
                return

            # Чтение контента
            content = self.stream.recv_data(file_size)
            self.storage.save_file(filename, content)
            self.stream.send_line(f"OK File {filename} saved")
            
        except ValueError:
            self.stream.send_line("ERR Invalid file size format")
        except Exception as e:
            self.stream.send_line(f"ERR Upload failed: {str(e)}")

class DownloadCommand(CommandHandler):
    def execute(self, args: str):
        if not args:
            self.stream.send_line("ERR Filename required")
            return

        filename = args.strip()

        if not self.storage.file_exists(filename):
            self.stream.send_line(f"ERR File {filename} not found")
            return

        try:
            # ИСПРАВЛЕНО: file_size -> get_file_size
            file_size = self.storage.get_file_size(filename)
            
            if file_size == 0:
                self.stream.send_line("ERR File is empty")
                return

            self.stream.send_line(f"OK Sending {file_size}")
            content = self.storage.read_file(filename)
            self.stream.send_data(content)

        except Exception as e:
            self.stream.send_line(f"ERR Download failed: {str(e)}")

class ExitCommand(CommandHandler):
    def execute(self, args: str):
        self.stream.send_line("OK Goodbye")

# Фабрика команд
COMMAND_REGISTRY = {
    'LIST': ListCommand,
    'UPLOAD': UploadCommand,
    'DOWNLOAD': DownloadCommand,
    'EXIT': ExitCommand
}

def get_handler(cmd_name: str, stream: SocketStream, storage: StorageService) -> CommandHandler:
    handler_class = COMMAND_REGISTRY.get(cmd_name.upper())
    if handler_class:
        return handler_class(stream, storage)
    return None