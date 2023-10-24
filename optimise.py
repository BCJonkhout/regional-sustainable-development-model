import matplotlib.pyplot as plt
import numpy as np
import main

def coefficient_variation():
    number_array = [[0, 5,      10,     15,     20,     25,     30,     35,     40],
                    [0, 300,    600,    900,    1200,   1500,   1800,   2100,   2400]]
    CoVar = 1
    for s in range(len(number_array[0])):
        for w in range(len(number_array[0])):
            monthly_data = main.statistics(number_array[0][s], number_array[1][w])

            total_monthly_generation = np.array(monthly_data[0]) + np.array(monthly_data[1])
            Temp_CoVar = np.std(total_monthly_generation) / np.mean(total_monthly_generation)

            if Temp_CoVar < CoVar:
                CoVar = Temp_CoVar
                solar_nr = number_array[0][s]
                wind_nr = number_array[1][w]

    plt.plot(total_monthly_generation)
    plt.xlabel("Months")
    plt.ylabel("kWh")

    print(f"Minimum CoVar: {CoVar}\n"
          f"Solar Area per house, number of wind turbines: {solar_nr}, {wind_nr}\n")
    plt.show()


coefficient_variation()