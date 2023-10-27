import matplotlib.pyplot as plt
from mainvar import *


def hourlydata():
    fig, ax1 = plt.subplots()
    ax1.plot(solar_generation)
    ax1.plot(wind_generation)
    ax1.plot(energy_usage)
    ax1.set_ylabel('kWh per hour')

    ax2 = ax1.twinx()

    ax2.scatter(battery_level,color='tab:red', label='Battery Level')
    ax2.set_ylabel('kWh')

    # Plot the second set of data
    #ax2.set_ylabel('Y2-axis', color='tab:red')
    #ax2.tick_params(axis='y', labelcolor='tab:red')

    ax2.set_xlabel("Hours")

    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax2.legend(lines + lines2, labels + labels2, loc=0)
    
    plt.legend

def monthlydata():
    plt.plot(monthly_data[0], label='Solar')
    plt.plot(monthly_data[1], label='Wind')
    plt.plot(monthly_data[2], label='Consumption')

    plt.xlabel("Months")
    plt.ylabel("kWh")
    plt.legend(loc='upper right')

def averagemonthlydata():
    fig, var = plt.subplots()
    x = np.arange(len(monthly_average[0]))
    var.bar(x, monthly_average[0], label='Solar')
    var.bar(x, monthly_average[1], bottom=monthly_average[0], label='Wind')
    var.set_xlabel("Months")
    var.set_ylabel("kWh")
    var.legend()


#hourlydata()
#monthlydata()
averagemonthlydata()

plt.show()