# %% import libs
import socket
import time
import threading


class DatasetIndexReceiver():
    def __init__(self, IP_rcv='0.0.0.0', PORT_rcv=5556,
                       IP_snd='127.0.0.1', PORT_snd=5555):
        self.latest = 0

        # receiver socket
        self.sock = socket.socket(socket.AF_INET,  # Internet
                                  socket.SOCK_DGRAM)  # UDP
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((IP_rcv, PORT_rcv))

        # sender socket
        self.sock_send = socket.socket(socket.AF_INET,  # Internet
                                       socket.SOCK_DGRAM)  # UDP
        self.ADDR_snd = (IP_snd, PORT_snd)

        # start thread
        self.t = threading.Thread(target=self.reader, daemon=True).start()

    def reader(self):
        print('HRTF manager initialized')
        while True:
            data, addr = self.sock.recvfrom(1024)
            if len(data) > 0:
                tmp = data.decode()
                print
                if 'captur' in tmp.lower():  # if received cmd to capture position, request the pos receiver
                    self.sock_send.sendto(data, self.ADDR_snd)
                else:
                    self.latest = int(list(filter(str.isdigit, tmp))[0])
                    print(f'Dataset: {self.latest}')
            time.sleep(1)


if __name__ == '__main__':
    a = DatasetIndexReceiver()

# %%
