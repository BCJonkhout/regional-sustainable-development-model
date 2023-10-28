import matplotlib.pyplot as plt
import numpy as np

def coefficient_variation(): # Needs a range of solar panel areas and wind turbines, returns the lowest variability per month.
    import mainvar
    number_array = [[41],
                    [3100, 3200]]
    CoVar = float('inf')
    for s in range(len(number_array[0])):
        for w in range(len(number_array[1])):
            monthly_data = mainvar.statistics(number_array[0][s], number_array[1][w])
            total_monthly_generation = np.array(monthly_data[0]) + np.array(monthly_data[1])
            Temp_CoVar = np.std(total_monthly_generation) / np.mean(total_monthly_generation)
            if Temp_CoVar < CoVar:
                CoVar = Temp_CoVar
                solar_nr = number_array[0][s]
                wind_nr = number_array[1][w]

    fig, var = plt.subplots()
    x = np.arange(len(monthly_data[0]))
    var.bar(x, monthly_data[0], label='Solar')
    var.bar(x, monthly_data[1], bottom=monthly_data[0], label='Wind')
    var.set_xlabel("Months")
    var.set_ylabel("kWh generated per month")
    var.legend()
    plt.show()

    monthly_average = mainvar.monthaverage() 
    # x = np.arange(len(monthly_average[0]))
    x = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    plt.bar(x, monthly_average[0], label='Solar')
    plt.bar(x, monthly_average[1], bottom=monthly_average[0], label='Wind')
    plt.xticks(rotation=-45)
    plt.ylabel("kWh generated per month")
    plt.legend()
    plt.show()

    print(f"Minimum CoVar: {CoVar}\n"
         f"Solar Area per house, number of wind turbines: {solar_nr}, {wind_nr}\n")

def storage_costs(storage_entry: float, overproduction: float):
    import main
    # thousands of euros
    while main.statistics(storage_entry, overproduction)[3] < 99.98:
        storage_entry = storage_entry + 250
    else:
        storage_cost = storage_entry
    results = main.statistics(storage_cost, overproduction)
    solar_cost = results[0]
    wind_cost = results[1]
    total_cost = results[2]
    energy_reliability = results[3]
    storage_duration = results[4]
    
    print(f"Solar cost: {solar_cost}\n"
          f"Wind cost: {wind_cost}\n"
          f"Storage cost: {storage_cost}\n"
          f"Total cost: {total_cost}\n"
          f"Energy reliability: {energy_reliability}\n"
          f"Storage duration: {storage_duration}\n"
          "----------------------------------------------------------------------------\n")
    return(solar_cost, wind_cost, storage_cost, total_cost, storage_duration)

def Solar_Wind_Storage():
    overproductions = [6, 5, 4.5, 4, 3.5, 3, 2.5, 1.75, 1.5, 1.25]
    solar_array = []
    wind_array = []
    storage_array = []
    total_array = []
    duration_array = []

    for i in range(len(overproductions)):
        if i == 0:
            results = storage_costs(0, overproductions[i])
        else:
            results = storage_costs(storage_entry, overproductions[i])
        solar_array.insert(0, results[0]/1000)
        wind_array.insert(0, results[1]/1000)
        storage_array.insert(0, results[2]/1000)
        storage_entry = results[2]
        total_array.insert(0, results[3])
        duration_array.insert(0, results[4])

    fig, wss = plt.subplots()
    x = overproductions[::-1]
    x_positions = range(len(x))
    wss.bar(x_positions, storage_array, label='Storage cost', color='tab:gray')
    wss.bar(x_positions, solar_array,bottom=storage_array, label='Solar cost', color='tab:olive')
    wss.bar(x_positions, wind_array, bottom=np.array(solar_array)+np.array(storage_array), label='Wind cost', color='tab:cyan')
    wss.set_xlabel("Energy overproduction, %. more than total consumption")
    wss.set_ylabel("CAPEX for Aadorp case, in million €")

    wss2 = wss.twinx()
    wss2.plot(x_positions, duration_array, color='tab:red', label='Storage duration (hours)', linewidth=3)
    wss2.set_ylabel("Storage duration for 99.98%. reliability")

    plt.xticks(x_positions, ['{:.0%}'.format(val-1) for val in x])
    wss.legend(loc='upper center', bbox_to_anchor=(0.25, -0.15), fancybox=True, shadow=True, ncol=2)
    wss2.legend(loc='upper center', bbox_to_anchor=(0.8, -0.15), fancybox=True, shadow=True)
    plt.show()

    plt.bar(x_positions, total_array, label='Total costs since 2018')
    plt.xticks(x_positions, ['{:.0%}'.format(val-1) for val in x])
    plt.legend()

    plt.show()

    

# coefficient_variation()
Solar_Wind_Storage()
