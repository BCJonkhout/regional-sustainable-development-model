import matplotlib.pyplot as plt
import numpy as np

from main import *


def hourlydata():
    plt.plot(solar_generation)
    plt.plot(wind_generation)
    plt.plot(energy_usage)

    plt.xlabel("Hours")
    plt.ylabel("kWh per hour")


def monthlydata():
    plt.plot(monthly_data[0])
    plt.plot(monthly_data[1])
    plt.plot(monthly_data[2])

    plt.xlabel("Months")
    plt.ylabel("kWh")

#hourlydata()
monthlydata()

plt.show()