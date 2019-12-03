from interface.file_play import FilePlay
from modules.heart_info import HeartInfo
from data_processor.PPG import PPG
from data_processor.position import Position
from modules.position_detection import PositionDetection
import datetime
import heartpy as hp
import numpy as np
import sqlite3
from interface.Receiver import Receiver
import json
'''
to view data in db:
	sqlite3 sleep_lab.db
	SELECT * FROM heart_info;
	.quit
'''


class Processor:

    def __init__(self):
        self.receiver = Receiver()
        self.ppg_list = list()

        self.position_x = list()
        self.position_y = list()
        self.position_z = list()

        # set up for database
        self.conn = sqlite3.connect('sleep_lab.db')
        self.c = self.conn.cursor()

        # if table exists, delete and recreate
        self.c.execute(''' SELECT count(name) FROM sqlite_master WHERE \
        type='table' AND name='heart_info' ''')
        
        if self.c.fetchone()[0] == 1:
            print('Table exists, delete first')
            self.c.execute('''
            DROP TABLE heart_info
            ''')
            self.conn.commit()
        
        self.c.execute(''' SELECT count(name) FROM sqlite_master WHERE \
        type='table' AND name='position_info' ''')
        
        if self.c.fetchone()[0] == 1:
            print('Table exists, delete first')
            self.c.execute('''
            DROP TABLE position_info
            ''')
            self.conn.commit()

        self.c.execute(''' SELECT count(name) FROM sqlite_master WHERE \
        type='table' AND name='live' ''')

        if self.c.fetchone()[0] == 1:
            print('Table exists, delete first')
            self.c.execute('''
            DROP TABLE live
            ''')
            self.conn.commit()
        
        # create heart_info table
        self.c.execute('''CREATE TABLE heart_info(
            bpm FLOAT,
            time_stamp text,
            id INTEGER
        )''')
        self.conn.commit()
        
        # create motion info table
        self.c.execute('''CREATE TABLE position_info(
            position text,
            time_stamp text,
            id INTEGER
        )''')
        self.conn.commit()


        # create live table
        self.c.execute('''CREATE TABLE live(
            id INTEGER UNIQUE,
            heart_raw FLOAT
        )''')
        self.conn.commit()
        
        # set up position
        order = 6
        fs = 500.0  # sample rate, Hz
        cutoff = 1  # desired cutoff frequency of the filter, Hz
        self.posi = PositionDetection(order, fs, cutoff)
    

    def insert_position_info(self, position):
        with self.conn:
            self.c.execute("INSERT INTO position_info VALUES (:position, :time_stamp, :id)", {'position': position.position,
                                                                                    'time_stamp': position.time_stamp,
                                                                                    'id': position.id})
    
    
    def insert_heart_info(self, PPG):
        with self.conn:
            self.c.execute("INSERT INTO heart_info VALUES (:bpm, :time_stamp, :id)", {'bpm': PPG.bpm, 'time_stamp': PPG.time_stamp,
                                                                                 'id':PPG.id})

    def insert_live(self, id, heart_raw):
        with self.conn:
            self.c.execute("INSERT INTO live VALUES ( :heart_raw, :id)", {'heart_raw': heart_raw, 'id': id})
    
    def clear_live_table(self):
        with self.conn:
            self.c.execute("DELETE FROM live where id > -1")
    
    
    def get_position_info(self, acc_x_data, acc_y_data, acc_z_data,time, id):
        # 5000*4 = 20 seconds
        seconds = 5
        points = seconds / 0.004

        if len(self.position_x) >= points:
            filtered_x, filtered_y, filtered_z =  self.posi.filter( self.position_x,
                                                                    self.position_y,
                                                                    self.position_z)
            measures = self.posi.get_posture(filtered_x, filtered_y, filtered_z, 5)
    
            position_obj = Position(measures, time, id)
            self.insert_position_info(position_obj)
            print(measures)
            self.position_x.clear()
            self.position_y.clear()
            self.position_z.clear()
            return measures
    
        self.position_x.append(acc_x_data)
        self.position_y.append(acc_y_data)
        self.position_z.append(acc_z_data)
        return 0
    
    
    def get_ppg_info(self, ppg_data,time, id):
        # 5000*4 = 20 seconds
        seconds = 5
        points = seconds / 0.004
        bpm = 0
        if len(self.ppg_list) >= points:
            try:
                working_data, measures = hp.process(np.array(self.ppg_list), 250.0)
                bpm = measures['bpm']
            except:
                print('bad signal: check connection')
            self.ppg_list.clear()
            ppg = PPG(bpm, time,id)
            self.insert_heart_info(ppg)
            print(ppg.bpm)
            return ppg
    
        self.ppg_list.append(float(ppg_data))
        return 0



if __name__ == '__main__':
    # skip the first line
    P = Processor()
    live_id = 0
    data_json = {'id': [0], 'heart_raw': [0]}
    while 1:
        data_list =P.receiver.get_data()
        for data in data_list:
            # process live
            print(live_id)
            if live_id == 0:
                data_json = {'id': [0], 'heart_raw': [0]}
                with open('live.txt', 'w') as outfile:
                    json.dump(data_json, outfile)
                live_id = 1
            elif live_id > 1000:
                data_json['id'] = []
                data_json['heart_raw'] = []
                if 'id' not in data_json.keys():
                    continue
                with open('live.txt', 'a') as outfile:
                    json.dump(data_json, outfile)
                    outfile.write('\n')
                live_id = 1
            else:
                data_json['id'].append(live_id)
                data_json['heart_raw'].append(float(data['Analog1_chA']))
                if 'id' not in data_json.keys():
                    continue
                with open('live.txt', 'a') as outfile:
                    json.dump(data_json, outfile)
                    outfile.write('\n')
                live_id = live_id + 1
            # clear table when id > 5000

            # process ppg
            position = P.get_position_info(float(data['IMU1_acc_x']), float(data['IMU1_acc_y']), float(data['IMU1_acc_z'])
                                           ,data['DateTime'],data['Timestamp'])
            ppg = P.get_ppg_info(data['Analog1_chA'],data['DateTime'], data['Timestamp'])




    print('done')
