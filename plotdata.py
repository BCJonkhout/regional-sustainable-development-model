import matplotlib.pyplot as plt
import numpy as np

from main import *



plt.plot(solar_generation)
plt.plot(wind_generation)
plt.plot(energy_usage)

plt.xlabel("Hours")
plt.ylabel("kWh per hour")

plt.show()