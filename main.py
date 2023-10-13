import json
import math
import numpy as np

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
TIME_INTERVAL = 1  # 1 hour
STORAGE_SIZE = 45000  # kWh
ELECTRICITY_COST = 0.0004 # 10^3 euros per kWh

# Wind
TURBINE_CHOICE = "XL"
TURBINE_NR = 1

BATTERY_CHOICE = "Aqua"

# Solar
SOLAR_PANEL_AREA = 20  # square meter per house
SOLAR_PANEL_EFFICIENCY = 0.3  # 30% efficiency
SOLAR_COSTS_M2 = 0.14 # thousands euros

# Blocks
storage_block = 0  # kWh
grid = 0  # kWh
total_wind_produced = 0 # kWh
energy_from_grid = 0  # kWh
energy_to_grid = 0 # kWh

# Statistics
storage_block_values = []



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
    return turbines_info[TURBINE_CHOICE]["production"][int(wind)] * TURBINE_NR * 1000 # kWh -> Wh


def produce(sunlight: float, wind: float) -> float:
    global total_wind_produced
    solar_energy = produce_solar(sunlight)
    wind_energy = produce_wind(wind)
    total_wind_produced =  total_wind_produced + wind_energy / 1000
    #print(f"Production, wind: {wind_energy}, solar_energy: {solar_energy}")

    return sum([solar_energy, wind_energy])


def iterate(consumption: float, sunlight: float, wind: float):
    global storage_block
    production = produce(sunlight, wind)
    consumption = consume(consumption)
    delta = (production - consumption) / 1000 # Wh -> kWh
    
    storage(delta)


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
    global energy_independency, total_costs, energy_from_grid

    energy_independency = 100 * (1 - energy_from_grid / (450 * 600 * len(WEATHER) / 1000))
    total_costs = 0.001 * (AMOUNT_OF_HOUSES * SOLAR_PANEL_AREA * SOLAR_COSTS_M2 # 10^3 euros -> 10^6 euros
                   + turbines_info[TURBINE_CHOICE]["initialcosts"] * TURBINE_NR
                   + turbines_info[TURBINE_CHOICE]["costs-per-kWh"] * total_wind_produced 
                   + storage_options[BATTERY_CHOICE]["costs-per-kwh"] * STORAGE_SIZE
                   + (energy_from_grid - energy_to_grid) * ELECTRICITY_COST
                   )
    print(
          f"Energy independency: {energy_independency}%\n"
          f"Total costs (million): {total_costs}\n"
          f"Total wind produced (kWh): {total_wind_produced}\n"
          f"Energy from grid (kWh): {energy_from_grid}\n"
          f"Energy to grid (kWh): {energy_to_grid}\n"
          )


# Call the iterator function to start processing the data
iterator()
statistics()
