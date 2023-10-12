import json
import math

# ** Costs
# Carbon footprint
# Start up costs
# Operating Costs per year / KwH
# Consumption
# Production


# Constants
AMOUNT_OF_HOUSES = 600
TIME_INTERVAL = 1  # 1 hour
STORAGE_SIZE = 5000  # kWh

# Solar
SOLAR_PANEL_AREA = 20  # square meter per house
SOLAR_PANEL_EFFICIENCY = 0.2  # 20% efficiency
SOLAR_COSTS_M2 = 0.14 # thousands euros
# Wind
TURBINE_CHOICE = "XL" # XL, L, M, S
AMOUNT_OF_TURBINES = 1

with open('turbines.json', 'r') as json_file:
    turbines_info = json.load(json_file)

# Storage
STORAGE_METHOD = 'home' #'aqua', 'home', 'hydrogen', 'salt'
AQUA_BATTERY_EFFICIENCY = 0.7
HOME_BATTERY_EFFICIENCY = 0.9
HYDROGEN_BROMINE = 0.7
SALT_BATTERY_EFFICIENCY = 0.8

# Blocks
storage_block = STORAGE_SIZE  # kWh
electricity_sold = 0  # kWh
grid = 0 # kWh
hours_without_energy = 0  # h

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
    return turbines_info[TURBINE_CHOICE]["production"][int(wind)] * AMOUNT_OF_TURBINES * 1000 # kWh -> wH


def produce(sunlight: float, wind: float) -> float:
    solar_energy = produce_solar(sunlight)
    wind_energy = produce_wind(wind)
    # print(f"Production, wind: {wind_energy}, solar_energy: {solar_energy}")
    return sum([solar_energy, wind_energy])


def iterate(consumption: float, sunlight: float, wind: float):
    production = produce(sunlight, wind)
    consumption = consume(consumption)
    delta = (production - consumption) / 1000 # wH -> kWh
    storage(delta)


def storage(delta):
    global storage_block, grid
    efficiency = {
        'aqua':AQUA_BATTERY_EFFICIENCY,
        'home':HOME_BATTERY_EFFICIENCY,
        'hydrogen-bromine':HYDROGEN_BROMINE,
        'salt':SALT_BATTERY_EFFICIENCY
    }[STORAGE_METHOD]

    factor = efficiency if delta > 0 else 1/efficiency
    factor = math.sqrt(factor)
    storage_block = storage_block + delta * factor
    if storage_block > STORAGE_SIZE:
        grid = grid + (storage_block - STORAGE_SIZE)*factor
        storage_block = STORAGE_SIZE

    if storage_block <= 0:
        grid = grid + factor*storage_block
        storage_block = 0

    print([int(x) for x in [delta, storage_block, grid]])


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
    Total_costs = AMOUNT_OF_HOUSES * SOLAR_PANEL_AREA * SOLAR_COSTS_M2 + turbines_info[TURBINE_CHOICE]["costs"] * AMOUNT_OF_TURBINES
    print(#f"Storage variance: {storage_variance}\n"
          #f"Storage mean: {storage_mean}\n"
          f"Energy reliability: {Energy_reliability}%\n"
          f"Total costs (thousands): {Total_costs}\n")


# Call the iterator function to start processing the data
iterator()
statistics()
