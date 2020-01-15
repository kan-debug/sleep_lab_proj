import numpy.fft as fft
import numpy as np
import matplotlib.pyplot as plt
import itertools
from statistics import mean, median
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn import svm
from sklearn import metrics
import pickle

class REM:
    def __init__(self):
        self.frequency = 'none'

    def load_data(self, filename):
        data_list = list()
        with open(filename, 'r') as file:
            content = file.read()

        i = 0
        for line in content.split():
            i += 1
            if i > 1:
                data_list.append(float(line.split(',')[1]))
        return data_list

    def grouper(self, n, iterable, fillvalue=None):
        "grouper(3, 'ABCDEFG', 'x') --> ABC DEF Gxx"
        args = [iter(iterable)] * n
        return itertools.zip_longest(fillvalue=fillvalue, *args)

    def feature_extraction(self, data_list, label):
        # extract maxi-min distance in a interval of 2 senconds = 205*2 = 500 point
        # file:///C:/Users/Luwan%20Wang/Downloads/entropy-18-00272.pdf
        sub_lists = self.grouper(500, data_list, mean(data_list))
        features = dict()
        features['MMD'] = []
        features['mean'] = []
        features['label'] = []
        for list in sub_lists:
            features['MMD'].append(max(list) - min(list))
            features['mean'].append(mean(list))
            features['label'].append(label)
        return features

    def train_model(self, dataset1, dataset2, filename):
        df2 = pd.DataFrame.from_dict(dataset2)
        df1 = pd.DataFrame.from_dict(dataset1)
        df = pd.concat([df1, df2])
        X_train, X_test, y_train, y_test = train_test_split(df[['MMD','mean']], df['label'], test_size=0.1,
                                                            random_state=109)  # 70% training and 30% test
        clf = svm.SVC(kernel='linear')
        clf.fit(X_train, y_train)
        y_pred = clf.predict(X_test)
        print("Accuracy:", metrics.accuracy_score(y_test, y_pred))
        print("Precision:", metrics.precision_score(y_test, y_pred))
        print("Recall:", metrics.recall_score(y_test, y_pred))
        pickle.dump(clf, open(filename, 'wb'))


    def classify(self, data,filename):
        if len(data != 500):
            print("prefer list size is 500(2 seconds data)")
        features = dict()
        features['MMD'].append(max(list) - min(list))
        features['mean'].append(mean(list))
        df = pd.DataFrame.from_dict(features)
        loaded_model = pickle.load(open(filename, 'rb'))
        prediction = loaded_model.predict(pd)
        return prediction


if __name__ == "__main__":
    R = REM()
    # f1 = "D:\program files\Lithic\data\REM_no_movement\REM_no_movement_2020-01-13T10-43-42.txt"
    # f2 = "D:\program files\Lithic\data\REM_left_right\REM_left_right_2020-01-13T10-44-21.txt"
    # f3 = "D:\program files\Lithic\data\REM_around\REM_around_2020-01-13T10-46-56.txt"
    # f4 = "D:\program files\Lithic\data\REM_up_down\REM_up_down_2020-01-13T10-45-26.txt"
    f_nomove = "D:\program files\Lithic\data\\no_movement2\\no_movement2_2020-01-14T22-26-15.txt"
    f_move = "D:\program files\Lithic\data\with_movement2\with_movement2_2020-01-14T22-34-41.txt"
    D1 = R.load_data(f_nomove)
    D2 = R.load_data(f_move)

    # 0 = not moving, 1 = moving
    F1 = R.feature_extraction(D1, 0)
    print(F1)
    F2 = R.feature_extraction(D2, 1)
    print(F2)
    filename = 'SVM_model.sav'
    R.train_model(F1, F2,filename)


    # feature extraction: maximum minimum distance,

