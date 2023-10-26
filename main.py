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
STORAGE_SIZE = 5000  # kWh
ELECTRICITY_COST = 0.0003 # 10^3 euros per kWh

# Wind
TURBINE_CHOICE = "S"
TURBINE_NR = 2000

BATTERY_CHOICE = "Aqua"

# Solar
SOLAR_PANEL_AREA = 20  # square meter per house
SOLAR_PANEL_EFFICIENCY = 0.3  # 30% efficiency
SOLAR_COSTS_M2 = 0.14 # thousands euros / m^2

# Blocks
storage_block = 0  # kWh
grid = 0  # kWh
total_wind_produced = 0 # kWh
total_solar_produced = 0 #kWh
energy_from_grid = 0  # kWh
energy_to_grid = 0 # kWh

# Statistics
storage_block_values = []
costs_over_time = []
solar_generation = []
wind_generation = []
energy_usage = []
monthly_data = [[],[],[]] # position 0 = Solar, 1 = Wind, 2 = Consumption

# input kWh per unit
def consume(consumption) -> float:  # kWh
    return consumption * AMOUNT_OF_HOUSES

# input intensity in (Wh/m^2), output in kWh electricity generated
def produce_solar(sunlight) -> float:  # Wh
    return sunlight * solar_area * SOLAR_PANEL_EFFICIENCY * TIME_INTERVAL * AMOUNT_OF_HOUSES # kWh

# input wind velocity in (m/s) or production singular wind panel
def produce_wind(wind) -> float:  # Wh
    #print(wind)
    addition = turbines_info[TURBINE_CHOICE]["speed-addition"]
    
    return turbines_info[TURBINE_CHOICE]["production"][int(wind+addition)] * turbine_nr # kWh

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

    if storage_block > STORAGE_SIZE:
        energy_to_grid = energy_to_grid + (storage_block - STORAGE_SIZE) * factor
        storage_block = STORAGE_SIZE

    if storage_block <= 0:
        energy_from_grid = energy_from_grid - storage_block * factor
        storage_block = 0
    
    #print([int(x) for x in [delta, storage_block]])

def iterate(consumption: float, sunlight: float, wind: float, month: int):
    global storage_block
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
        # if i == 1:  # Checking to see if the numbers used are correct
        #     print(f"TEST Turbine Nr: {turbine_nr}")
        #     print(f"TEST Solar area: {solar_area}")
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
        month = month + 12 * (int(year) - 2021)

        iterate(float(consumption_entry), float(sunlight_entry),
                float(wind_entry), int(month))  # TODO: Magic numbers  # Close the files after processing

def statistics(solar_nr: int, wind_nr: int):
    global solar_area, turbine_nr
    solar_area = solar_nr
    turbine_nr = wind_nr
    print(f"solar area: {solar_area}, turbine number: {turbine_nr}")
    iterator()

    total_solar_produced = sum(solar_generation)
    total_wind_produced = sum(wind_generation)
    total_consumption = sum(energy_usage)

    storage_duration = STORAGE_SIZE / 274
    overproduction = (total_solar_produced + total_wind_produced) / total_consumption * 100
    energy_independency = 100 * (1 - energy_from_grid / (450 * 600 * len(WEATHER) / 1000))

    solar_cost = AMOUNT_OF_HOUSES * SOLAR_PANEL_AREA * SOLAR_COSTS_M2
    # 0.00012 * total_solar_produced  # LCoE of solar
    wind_cost = turbines_info[TURBINE_CHOICE]["initialcosts"] * TURBINE_NR + turbines_info[TURBINE_CHOICE]["costs-per-kWh"] * total_wind_produced # Intial and variable costs for chosen wind turbines
    # 0.00008 * total_wind_produced  # LCoE of on-shore wind
    storage_cost = storage_options[BATTERY_CHOICE]["costs-per-kwh"] * STORAGE_SIZE # Costs per kWh for chosen battery
    grid_balance = (energy_from_grid - energy_to_grid) * ELECTRICITY_COST # Cost/revenue from grid

    total_costs = 0.001 * (solar_cost + wind_cost + storage_cost + grid_balance) # 10^3 euros -> 10^6 euros
    print(
          f"Energy independency: {energy_independency}%\n"
          f"Total consumption (kWh): {total_consumption}\n"
          f"Total costs (millions): {total_costs}\n"
          f"\n"
          f"Total solar produced (kWh): {total_solar_produced}\n"
          f"Solar cost (thousands): {solar_cost}\n"
          f"\n"
          f"Total wind produced (kWh): {total_wind_produced}\n"
          f"Wind cost (thousands): {wind_cost}\n"
          f"\n"
          f"Energy from grid (kWh): {energy_from_grid}\n"
          f"Energy to grid (kWh): {energy_to_grid}\n"
          f"Grid balance (thousands): {grid_balance}\n"
          f"Storage cost (thousands): {storage_cost}\n"
          f"\n"
          f"Storage duration (hours): {storage_duration}\n"
          f"Overproduction (%): {overproduction}%\n"
          )
    return [monthly_data[0], monthly_data[1]]


# Call the statistics function to run the script.
statistics(50, 3800) # 20 m^2 solar panel ares per house and 2000 wind turbines
