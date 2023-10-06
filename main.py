import numpy as np
import json
# ** Costs
# Carbon footprint
# Start up costs
# Operating Costs per year / KwH
# Consumption
# Production


# Constants
AMOUNT_OF_HOUSES = 600
TIME_INTERVAL = 1  # 1 hour
STORAGE_SIZE = 45000  # kWh

# Solar
SOLAR_PANEL_AREA = 20  # square meter per house
SOLAR_PANEL_EFFICIENCY = 0.2  # 20% efficiency
SOLAR_COSTS_M2 = 0.14 # thousands euros
# Wind
TURBINE_CHOICE = "XL"
TURBINE_NR = 1

with open('turbines.json', 'r') as json_file:
    turbines_info = json.load(json_file)

#print(turbines_info["XL"]["production"][4])

# Blocks
storage_block = 0  # kWh
electricity_sold = 0  # kWh
hours_without_energy = 0  #

# Statistics
storage_block_values = []

# Input Data
with open('input_data_weather.txt', 'r') as weather_file, open('consumption.csv', 'r') as consumption_file:
    WEATHER = weather_file.readlines()
    CONSUMPTION = consumption_file.readlines()  # Read all lines into a list


# input kWh per unit
def consume(consumption) -> float:  # kWh
    return consumption * AMOUNT_OF_HOUSES


# input intensity in (W/m^2) (J/cm^2) or kwH output for a single panel of M^2.
def produce_solar(sunlight) -> float:  # Wh
    # E = INTENSITY(W/m^2) * A * efficiency * time
    return sunlight * SOLAR_PANEL_AREA * SOLAR_PANEL_EFFICIENCY * TIME_INTERVAL * AMOUNT_OF_HOUSES


# input wind velocity in (m/s) or production singular wind panel
def produce_wind(wind) -> float:  # Wh
    #print(wind)
    return turbines_info[TURBINE_CHOICE]["production"][int(wind)] * TURBINE_NR * 1000 # kWh -> wH



def produce(sunlight: float, wind: float) -> float:
    solar_energy = produce_solar(sunlight)
    wind_energy = produce_wind(wind)
    #print(f"Production, wind: {wind_energy}, solar_energy: {solar_energy}")
    return sum([solar_energy, wind_energy])


def iterate(consumption: float, sunlight: float, wind: float):
    global storage_block, hours_without_energy, electricity_sold, STORAGE_SIZE
    production = produce(sunlight, wind)
    consumption = consume(consumption)
    delta = (production - consumption) / 1000 # wH -> kWh
    storage_block = storage_block + delta

    if storage_block > STORAGE_SIZE:
        electricity_sold = electricity_sold + (storage_block - STORAGE_SIZE)
        storage_block = STORAGE_SIZE
    elif storage_block <= 0:
        hours_without_energy = hours_without_energy + 1
        storage_block = 0

    #print(f"Delta: {delta} \t| Storage: {storage_block} \t| Electricity sold: {electricity_sold} \t| Hours without energy: {hours_without_energy}")


def iterator():
    for i, weather_list_entry in enumerate(WEATHER):
        consumption_entry = 450
        weather_entry = weather_list_entry.split(',')
        if weather_entry[11].strip() == "":
            sunlight_entry = 0
        else:
            sunlight_entry = float(weather_entry[11].strip()) / 10000 * 3600  # -> J/cm^2/h -> J/m^2/h -> J/m^2/s = W/m^2

        if weather_entry[4].strip() == "":
            wind_entry = 0
        else:
            wind_entry = float(weather_entry[4].strip()) / 10  # from 0.1m/s -> in m/s
        # print(i, sunlight_entry, wind_entry)
        iterate(float(consumption_entry), float(sunlight_entry),
                float(wind_entry))  # TODO: Magic numbers  # Close the files after processing


def statistics():
    global Energy_reliability, Total_costs
    #print(storage_block_values)
    #storage_variance = np.var(storage_block_values)
    #storage_mean = np.mean(storage_block_values)
    Energy_reliability = 100 * (1 - hours_without_energy / len(WEATHER))
    Total_costs = AMOUNT_OF_HOUSES * SOLAR_PANEL_AREA * SOLAR_COSTS_M2 + turbines_info[TURBINE_CHOICE]["costs"] * TURBINE_NR
    print(#f"Storage variance: {storage_variance}\n"
          #f"Storage mean: {storage_mean}\n"
          f"Energy reliability: {Energy_reliability}%\n"
          f"Total costs (thousands): {Total_costs}\n")


# Call the iterator function to start processing the data
iterator()
statistics()
