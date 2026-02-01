#main

from Hunter import Hunter
from Site import Site
from Stand import Stand
from Weather_Manager import Weather_Manager

def get_degree_dif(wind_deg, stand_deg):
    difference = 180 - abs(abs(wind_deg - stand_deg) - 180)
    return difference

def get_stand_grade(wind_angle):
    return 100 - ((wind_angle / 180) * 100)

def main():
    
    
    testWeather = Weather_Manager()
    windage = testWeather.get_weather()
    print(windage)

    testHunter = Hunter("Andrew")

    testStand1 = Stand("Hog Parlor", 90)
    testStand2 = Stand("Cash", 37)
    testStand3 = Stand("Big Log Deck", 122)
    testStand4 = Stand("Hot Blooded", 301)

    orangeburg = Site("orange", 12234)

    orangeburg.stand_list.append(testStand1)
    orangeburg.stand_list.append(testStand2)
    orangeburg.stand_list.append(testStand3)
    orangeburg.stand_list.append(testStand4)

    testHunter.site_list.append(orangeburg)

    # print()
    # for stand in orangeburg.stand_list:
    #     print("Stand: ", stand.name, "||| Degree: ", stand.degree)
    orangeburg.print_stand_list()

    # print()

    # for stand in orangeburg.stand_list:
    #     print("Name: ", stand.name, "||| Grade: ", get_stand_grade(get_degree_dif(windage, stand.degree)))









    

if __name__ == "__main__":
     main()

