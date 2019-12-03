
import heartpy as hp
from matplotlib import pyplot as plt
from scipy.signal import butter, lfilter, freqz
import numpy
import csv

import heartpy as hp
from matplotlib import pyplot as plt
from scipy.signal import butter, lfilter, freqz
import numpy
import csv

# notes Need to change x-axis scale
# Need to reduce change by average?
# low pass filter for eliminate fast changes, derivative filter to enhance changes
class PositionDetection:
    def __init__(self, order, fs, cufoff):
        self.order = order
        self.fs = fs
        self.cutoff = cufoff

    def butter_lowpass_filter(self, data):
        nyq = 0.5 * self.fs
        # normalized nyquist rate, limited to 0-1 in digital
        normal_cutoff = self.cutoff / nyq
        b,a = butter(self.order, normal_cutoff, btype='low', analog=False)
        filtered_data = lfilter(b, a, data)
        return filtered_data


    def data_util(self, txt_file_address):
        # change the extension to csv
        csv_file_address = txt_file_address.replace('txt', 'csv')
        in_txt = csv.reader(open(txt_file_address, "r"), delimiter=',')
        out_csv = csv.writer(open(csv_file_address, 'w'))
        out_csv.writerows(in_txt)

        acc_x_data = hp.get_data(csv_file_address, column_name='IMU1_acc_x')
        acc_y_data = hp.get_data(csv_file_address, column_name='IMU1_acc_y')
        acc_z_data = hp.get_data(csv_file_address, column_name='IMU1_acc_z')
        gyro_x_data = hp.get_data(csv_file_address, column_name='IMU1_gyro_x')
        gyro_y_data = hp.get_data(csv_file_address, column_name='IMU1_gyro_y')
        gyro_z_data = hp.get_data(csv_file_address, column_name='IMU1_gyro_z')
        timerdata = hp.get_data(csv_file_address, column_name='Timestamp')

        return [acc_x_data, acc_y_data, acc_z_data, gyro_x_data, gyro_y_data, gyro_z_data, timerdata]


    def filter(self, acc_x_data, acc_y_data, acc_z_data):
        filtered_x = self.butter_lowpass_filter(acc_x_data)
        filtered_y = self.butter_lowpass_filter(acc_y_data)
        filtered_z = self.butter_lowpass_filter(acc_z_data)

        return [filtered_x, filtered_y, filtered_z]


    def get_posture(self, x_list, y_list, z_list,period):
        # defines limit for making a decision of posture
        cut_off_level = 0.618
        dict_posture = {
            0: "facing up",
            1: "facing left",
            2: "facing right",
            3: "facing down",
            4: "transition",
            5: "Look, this guy just did a flip during sleep!"
        }

        # size is number of points
        size = int(period * self.fs)
        average_x = self.average_from_end(x_list, size)
        average_y = self.average_from_end(y_list, size)
        average_z = self.average_from_end(z_list, size)

        if average_z > cut_off_level:
            return dict_posture[0]
        elif average_x > cut_off_level:
            return dict_posture[1]
        elif average_x < -cut_off_level:
            return dict_posture[2]
        elif average_z < -cut_off_level:
            return dict_posture[3]
        elif average_y < -cut_off_level or average_y > cut_off_level:
            return dict_posture[3]
        else:
            return dict_posture[4]


    def average_from_end(self, list, size):
        # select tail of list start at length-size to end
        '''
        sample usage:
        average = average_from_end(filtered_z, 30)
        output: filtered_z with the last thirty forming a list
        '''
        list_tail = list[(len(list) - size):]
        average = sum(list_tail) / len(list_tail)
        return average


if __name__ == "__main__":
    # main
    # Filter requirements.
    order = 6
    fs = 250.0  # sample rate, Hz
    cutoff = 1  # desired cutoff frequency of the filter, Hz

    # convert txt file to csv
    # need to change address with file changing

    pode = PositionDetection(order, fs, cutoff)

    acc_x_data, acc_y_data, acc_z_data, gyro_x_data, gyro_y_data, gyro_z_data, timerdata = pode.data_util(
        '/content/drive/My Drive/4th_Year_Project/Raw_data/Motion_Raw/GyroTest_WASD_2019-10-03T16-15-40.txt')
    filtered_x, filtered_y, filtered_z = pode.filter(acc_x_data, acc_y_data, acc_z_data)

    print(pode.get_posture(filtered_x[5000:10000], filtered_y[5000:10000], filtered_z[5000:10000], 1))
    print(pode.get_posture(filtered_x, filtered_y, filtered_z, 1))
    print(pode.get_posture(filtered_x[12500:15000], filtered_y[12500:15000], filtered_z[12500:15000], 1))
    print(pode.get_posture(filtered_x[17500:18000], filtered_y[17500:18000], filtered_z[17500:18000], 1))

