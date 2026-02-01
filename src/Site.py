# Site Class
from Weather_Manager import Weather_Manager

class Site:
    
    def __init__(self, name, coordinates):
        self.name = name
        self.coordinates = coordinates
        self.stand_list = []
        self.ranked_list = []

    def print_stand_list(self):
        for stand in self.stand_list:
            print("Stand: ", stand.name, "||| Degree: ", stand.degree)

