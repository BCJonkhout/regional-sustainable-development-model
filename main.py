import json
import math
import numpy as np
import csv

# ** Costs
# Carbon footprint
# Start up costs
# Operating Costs per year / KwH
# Consumption
# Production

# Input Data
with open('input_data_weather.txt', 'r') as weather_file, open('consumption.csv', 'r') as consumption_file:
    WEATHER = weather_file.readlines()
    CONSUMPTION = consumption_file.readlines()  # Read all lines into a list

with open('turbines.json', 'r') as json_file:
    turbines_info = json.load(json_file)

with open('storage.json', 'r') as json_file:
    storage_options = json.load(json_file)

# Constants
AMOUNT_OF_HOUSES = 600
TIME_INTERVAL = 1  # in hours
ELECTRICITY_COST = 0.0003 # 10^3 euros per kWh

# Wind
TURBINE_CHOICE = "S"
#TURBINE_NR = 2000

BATTERY_CHOICE = "Aqua"

# Solar
SOLAR_PANEL_EFFICIENCY = 0.3  # 30% efficiency
SOLAR_COSTS_M2 = 0.14 # thousands euros / m^2

SOLAR_PROD_ONE = 579692.5 # kWh for one m^2 solar panel per house for the whole period
WIND_PROD_ONE = 7398.68 # kWh for one wind turbine for the whole period
TOTAL_CONSUMPTION = 7123566 # kWh total consumption of Aadorp for the whole period

# Blocks
storage_block = 0  # kWh
grid = 0  # kWh
total_wind_produced = 0 # kWh
total_solar_produced = 0 #kWh
energy_from_grid = 0  # kWh
energy_to_grid = 0 # kWh

# Statistics

# input kWh per unit
def consume(consumption) -> float:  # kWh
    return consumption * AMOUNT_OF_HOUSES

# input intensity in (Wh/m^2), output in kWh electricity generated
def produce_solar(sunlight) -> float:  # Wh
    #print(f"Solar_nr: {solar_nr}")
    return sunlight * solar_nr * SOLAR_PANEL_EFFICIENCY * TIME_INTERVAL * AMOUNT_OF_HOUSES # kWh

# input wind velocity in (m/s) or production singular wind panel
def produce_wind(wind) -> float:  # Wh
    #print(wind)
    addition = turbines_info[TURBINE_CHOICE]["speed-addition"]
    #print(f"Wind_nr: {wind_nr}")
    return turbines_info[TURBINE_CHOICE]["production"][int(wind+addition)] * wind_nr # kWh

def produce(sunlight: float, wind: float) -> float:
    global solar_energy, wind_energy
    solar_energy = produce_solar(sunlight)
    wind_energy = produce_wind(wind)
    
    solar_generation.append(solar_energy)
    wind_generation.append(wind_energy)


    #print(f"Production, wind: {wind_energy}, solar_energy: {solar_energy}")

    return sum([solar_energy, wind_energy])

def storage(delta):
    global storage_block, energy_to_grid, energy_from_grid
    efficiency = math.sqrt(storage_options[BATTERY_CHOICE]["efficiency"])
    factor = efficiency if delta > 0 else 1/efficiency

    storage_block = storage_block + delta * factor

    if storage_block > storage_size:
        energy_to_grid = energy_to_grid + (storage_block - storage_size) * factor
        storage_block = storage_size

    if storage_block <= 0:
        energy_from_grid = energy_from_grid - storage_block * factor
        storage_block = 0
    
    battery_level.append(storage_block)
    
    #print([int(x) for x in [delta, storage_block]])

def iterate(consumption: float, sunlight: float, wind: float, month: int):
    global monthly_data
    production = produce(sunlight, wind)
    consumption = consumption * AMOUNT_OF_HOUSES

    # Aggregating the data per month:
    if month <= len(monthly_data[0]):   # If the number of the month is smaller than or equal to the length of the array
        monthly_data[0][month-1] = monthly_data[0][month-1] + solar_energy  # Add the current hour value to the total for that month
        monthly_data[1][month-1] = monthly_data[1][month-1] + wind_energy
        monthly_data[2][month-1] = monthly_data[2][month-1] + consumption
    else:
        monthly_data[0].append(sunlight)    # Else start a new month
        monthly_data[1].append(wind)
        monthly_data[2].append(consumption)

    energy_usage.append(float(consumption))   
    delta = (production - consumption) # kWh

    storage(delta)

def iterator():
    for i, weather_list_entry in enumerate(WEATHER):

        consumption_list_entry = CONSUMPTION[i].split('\t') #kWh
        consumption_entry = consumption_list_entry[2]

        weather_entry = weather_list_entry.split(',')
        if weather_entry[11].strip() == "":
            sunlight_entry = 0
        else:
            sunlight_entry = float(weather_entry[11].strip()) * 10000 / 3600 / 1000  # -> J/h/cm^2 -> J/h/m^2 -> Wh/m^2 -> kWh/m^2

        if weather_entry[4].strip() == "":
            wind_entry = 0
        else:
            wind_entry = float(weather_entry[4].strip()) / 10  # from 0.1m/s -> in m/s

        month = int(weather_entry[1].strip()[4:][:-2])
        year = int(weather_entry[1].strip()[:-4])
        month = month + 12 * (int(year) - 2018)

        iterate(float(consumption_entry), float(sunlight_entry),
                float(wind_entry), int(month))  # TODO: Magic numbers  # Close the files after processing

def statistics(storage_cost: float, overproduction: float):
    global solar_nr, wind_nr, storage_size, battery_level, solar_generation, wind_generation, energy_usage, monthly_data, energy_from_grid, energy_to_grid

    battery_level = []
    solar_generation = []
    wind_generation = []
    energy_usage = []
    monthly_data = [[],[],[]] # position 0 = Solar, 1 = Wind, 2 = Consumption
    energy_from_grid = 0
    energy_to_grid = 0

    solar_nr = int(math.ceil(TOTAL_CONSUMPTION * overproduction / 1.96525 / SOLAR_PROD_ONE))
    wind_nr = int(math.floor(TOTAL_CONSUMPTION * overproduction / 2.036 / WIND_PROD_ONE))
    storage_size = storage_cost / storage_options[BATTERY_CHOICE]["costs-per-kwh"] # in kWh

    # print(f"Solar_nr: {solar_nr} | Wind_nr: {wind_nr}")

    iterator()

    total_solar_produced = sum(solar_generation)
    total_wind_produced = sum(wind_generation)
    total_consumption = sum(energy_usage)

    storage_duration = storage_size / 274
    overproduction = (total_solar_produced + total_wind_produced) / TOTAL_CONSUMPTION * 100
    energy_independency = 100 * (1 - energy_from_grid / (450 * 600 * len(WEATHER) / 1000))

    solar_cost = AMOUNT_OF_HOUSES * solar_nr * SOLAR_COSTS_M2
    # 0.00012 * total_solar_produced  # LCoE of solar
    wind_cost = turbines_info[TURBINE_CHOICE]["initialcosts"] * wind_nr + turbines_info[TURBINE_CHOICE]["costs-per-kWh"] * total_wind_produced # Intial and variable costs for chosen wind turbines
    # 0.00008 * total_wind_produced  # LCoE of on-shore wind
    grid_balance = (energy_from_grid - energy_to_grid) * ELECTRICITY_COST # Cost/revenue from grid

    total_costs = 0.001 * (solar_cost + wind_cost + storage_cost + grid_balance) # 10^3 euros -> 10^6 euros

    # print(
    #       f"Energy independency: {energy_independency}% | Total costs (millions): {total_costs}\n"
    #       f"Total consumption (kWh): {total_consumption}\n"
    #       f"\n"
    #       f"Total solar produced (kWh): {total_solar_produced} | Solar cost (thousands): {solar_cost}\n"
    #       f"Total wind produced (kWh): {total_wind_produced} | Wind cost (thousands): {wind_cost}\n"
    #       f"\n"
    #       f"Energy from grid (kWh): {energy_from_grid} | Energy to grid (kWh): {energy_to_grid}\n"
    #       f"Grid balance (thousands): {grid_balance} | Storage cost (thousands): {storage_cost}\n"
    #       f"\n"
    #       f"Storage duration (hours): {storage_duration} | Overproduction (%): {overproduction}%\n"
    #       )
    return [solar_cost, wind_cost, total_costs, energy_independency, storage_duration]


# Call the statistics function to run the script.
# statistics(375, 3) # 20 m^2 solar panel ares per house and 2000 wind turbines
