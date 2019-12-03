'''
useage
    from interface.Receiver import Receiver

    r = Receiver()
    while 1:
        data_list = r.get_data()
        for data in data_list:
            print(data)
'''


import datetime
import socket
import os.path, time
# get start time
import queue

HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 3333  # Port to listen on (non-privileged ports are > 1023)
file_name = "D:\\program files\\Lithic\\data\\live.txt"
modTimesinceEpoc = os.path.getmtime(file_name)
start_time = datetime.datetime.fromtimestamp(modTimesinceEpoc)
print("last modified live: ", start_time)

# get titile of each data
with open(file_name) as f:
    title = f.readline().rstrip("\n")
title_list = title.split(',')

class Receiver:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((HOST, PORT))
        self.sock.listen(1)
        self.conn, self.addr = self.sock.accept()
        self.msg_len = 1024
        self.list = list()



    def get_data(self):
        data_raw = self.conn.recv(self.msg_len)
        if not data_raw:
            print('connection broken')
            raise StopIteration

        # look all the data received at this time
        data_list = data_raw.split()

        # process the chopped data into list, lis[0] is previous last element
        data_end = data_list[-1].decode("utf-8")
        data_first = data_list[0].decode("utf-8")
        self.list.append(data_end)
        if len(self.list) > 2:
            self.list.pop(0)


        # process data into dictionary
        for data in data_list:

            # check for chopping data
            data = data.decode("utf-8")

            if data == data_first and len(data.split()) < len(title_list):
                good_data = self.list[0] + data
                data = good_data

            if data == data_end and len(data.split()) < len(title_list):
                continue

            data = data.split(',')
            dictionary = dict(zip(title_list, data))
            try:
                this_data_time = start_time + datetime.timedelta(milliseconds=int(dictionary['Timestamp']))
            except ValueError:
                print('ValueError: invalid literal for int()')
                continue
            dictionary['DateTime'] = this_data_time.strftime("%m-%d-%Y %H:%M:%S")

            yield dictionary

if __name__ == "__main__":

    r = Receiver()
    while 1:
        data_list = r.get_data()
        for data in data_list:
            print(data)