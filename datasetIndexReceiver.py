# %% import libs
import socket
import time
import keyboard
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

        # start threads
        self.t1 = threading.Thread(target=self.reader, daemon=True).start()
        self.t2 = threading.Thread(target=self.controlHotKeys, daemon=True).start()

    # Receive messages from external app
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


    # Hotkey control
    def controlHotKeys(self): 
        savepos = False  
        send0 = False
        send1 = False  
        send2 = False   
        send3 = False   
        send4 = False  
        while True:
            time.sleep(0.1)  
            if keyboard.is_pressed('space'):
                savepos = True


            if keyboard.is_pressed('alt gr+0'):
                send0 = True
            if keyboard.is_pressed('alt gr+1'):
                send1 = True
            if keyboard.is_pressed('alt gr+2'):
                send2 = True
            if keyboard.is_pressed('alt gr+3'):
                send3 = True
            if keyboard.is_pressed('alt gr+4'):
                send4 = True

            # take action after key release
            if (not keyboard.is_pressed('space') and savepos):  # capture position
                savepos = False
                # print('space') 
                self.sock_send.sendto('captur'.encode(), self.ADDR_snd)


            if (not keyboard.is_pressed('alt gr+0') and send0):  # dataset index
                send0 = False
                self.latest = 0
                print(f'Dataset: {self.latest}')
                    
            if (not keyboard.is_pressed('alt gr+1') and send1):  # dataset index
                send1 = False
                self.latest = 1
                print(f'Dataset: {self.latest}')

            if (not keyboard.is_pressed('alt gr+2') and send2):  # dataset index 
                send2 = False           
                self.latest = 2
                print(f'Dataset: {self.latest}')

            if (not keyboard.is_pressed('alt gr+3') and send3):  # dataset index
                send3 = False
                self.latest = 3
                print(f'Dataset: {self.latest}')

            if (not keyboard.is_pressed('alt gr+4') and send4):  # dataset index
                send4 = False
                self.latest = 4
                print(f'Dataset: {self.latest}')

if __name__ == '__main__':
    a = DatasetIndexReceiver()

# %%
