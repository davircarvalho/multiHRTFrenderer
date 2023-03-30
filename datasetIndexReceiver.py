# %% import libs
import socket
import time
import threading


class DatasetIndexReceiver():
    def __init__(self, IP='0.0.0.0', PORT=5556):
        self.sock = socket.socket(socket.AF_INET,  # Internet
                                  socket.SOCK_DGRAM)  # UDP
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((IP, PORT))
        self.latest = 0

        self.t = threading.Thread(target=self.reader, daemon=True).start()

    def reader(self):
        print('HRTF manager initialized')
        while True:
            data, addr = self.sock.recvfrom(1024)
            if len(data) > 0:
                tmp = data.decode()
                self.latest = int(list(filter(str.isdigit, tmp))[0])
                print(f'Dataset: {self.latest}')
            time.sleep(1)


if __name__ == '__main__':
    a = DatasetIndexReceiver()

# %%
