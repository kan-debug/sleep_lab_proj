class HeartInfo:
    def __init__(self):
        self.measures = {}

    def set_measures(self,new_measure):
        self.measures = new_measure

    def get_measures(self):
        return self.measures