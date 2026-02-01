#Stand Evaluation
from Stand import Stand

class stand_evaluator:
    def __init__(self, stand):
        self.grade = 0
        self.stand = stand

    def get_degree_dif(self, wind_deg, stand_deg):
        difference = 180 - abs(abs(wind_deg - stand_deg) - 180)
        return difference

    def get_stand_grade(self, wind_angle):
        return 100 - ((wind_angle / 180) * 100)
    
    def evaluator(self, stand_list, windage)

            
