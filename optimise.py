import matplotlib.pyplot as plt
import numpy as np
import main

def coefficient_variation():
    number_array = [[41, 42, 43, 44, 45, 46, 47, 48, 49, 50],
                    [3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 4000]]
    CoVar = float('inf')
    for s in range(len(number_array[0])):
        for w in range(len(number_array[1])):
            monthly_data = main.statistics(number_array[0][s], number_array[1][w])
            total_monthly_generation = np.array(monthly_data[0]) + np.array(monthly_data[1])
            Temp_CoVar = np.std(total_monthly_generation) / np.mean(total_monthly_generation)
            print(f"s: {number_array[0][s]}, w: {number_array[1][w]}, Temp_CoVar: {Temp_CoVar}\n"
                  f"CoVar: {CoVar}, Solar / wind = {number_array[0][s] / number_array[1][w]}\n")
            if Temp_CoVar < CoVar:
                CoVar = Temp_CoVar
                solar_nr = number_array[0][s]
                wind_nr = number_array[1][w]
                print(f"New CoVar: {CoVar}")

    plt.plot(total_monthly_generation)
    plt.plot(monthly_data[0])
    plt.plot(monthly_data[1])
    plt.xlabel("Months")
    plt.ylabel("kWh")

    print(f"Minimum CoVar: {CoVar}\n"
          f"Solar Area per house, number of wind turbines: {solar_nr}, {wind_nr}\n")
    plt.show()


coefficient_variation()