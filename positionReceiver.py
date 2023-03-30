# %% import libs
import socket
import time
import threading


class PositionReceiver():
    def __init__(self, IP='0.0.0.0', PORT=5555):
        self.sock = socket.socket(socket.AF_INET,  # Internet
                                  socket.SOCK_DGRAM)  # UDP
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((IP, PORT))
        self.yaw = 0
        self.pitch = 0
        self.roll = 0
        self.x = 0
        self.y = 1
        self.z = 1

        self.t = threading.Thread(target=self.reader, daemon=True).start()

    def reader(self):
        print('position receiver initialized')
        while True:
            data, addr = self.sock.recvfrom(1024)
            if len(data) > 0:
                self.latest = data.decode()
                self.str2pos()
            # time.sleep(0.2)

    def str2pos(self):
        splitStr = self.latest.split(',')
        yaw = float(splitStr[0])
        self.yaw = yaw
        self.pitch = float(splitStr[1])
        self.roll = float(splitStr[2])
        self.x = float(splitStr[3])
        self.y = float(splitStr[4])
        self.z = float(splitStr[5])


if __name__ == '__main__':
    a = PositionReceiver()
# %%
