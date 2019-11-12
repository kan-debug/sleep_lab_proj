from interface.file_play import FilePlay
from modules.heart_info import HeartInfo
from data_processor.PPG import PPG
import datetime
import heartpy as hp
import numpy as np
import sqlite3

# set up for interface
heart_info =  HeartInfo()
#file_name = "D:\\program files\\Lithic\\data\\live.txt"
file_name = "D:\\program files\\Lithic\\data\\Data_1\\heart_and_motion_Data_1_2019-11-01T21-24-06.txt"
file = FilePlay(file_name)
X = list()
X.append(0)
Y = list()
Y.append(0)

# set up for database
conn = sqlite3.connect('heart_info.db')
c = conn.cursor()

#if table exists, delete and recreate
c.execute(''' SELECT count(name) FROM sqlite_master WHERE \
type='table' AND name='heart_info' ''')

if c.fetchone()[0]==1 :
	print('Table exists, delete first')
	c.execute('''
	DROP TABLE heart_info
	''')
	conn.commit()

c.execute('''CREATE TABLE heart_info(
    bpm FLOAT,
    time_stamp text
)''')
conn.commit()



def insert_heart_info(PPG):
    with conn:
        c.execute("INSERT INTO heart_info VALUES (:bpm, :time_stamp)", {'bpm': PPG.bpm, 'time_stamp': PPG.time_stamp})

def process_time(y):
    # 5000/4
    if len(X) >= 5000:
        try:
            working_data, measures = hp.process(np.array(Y), 250.0)
        except:
            return -1
        X.clear()
        X.append(0)
        Y.clear()
        Y.append(0)
        print(measures)
        ppg = PPG(measures['bpm'],datetime.datetime.now().strftime("%m/%d/%Y-%H:%M:%S"))
        print(datetime.datetime.now().strftime("%m/%d/%Y-%H:%M:%S"))
        return ppg
    X.append(X[-1]+4)
    Y.append(y)
    return 0

if __name__ == '__main__':
    # skip the first line
    next_line = file.next()
    for i in range(43599):
        next_line = file.next()
        this_y = float(next_line.split(',')[2])
        ppg = process_time(this_y)
        if ppg == -1:
            print('noisy signal')
        elif ppg != 0:
            insert_heart_info(ppg)
            print(ppg.bpm, ppg.time_stamp)
    conn.close()
    print('done')