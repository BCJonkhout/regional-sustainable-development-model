import numpy as np

# ** Costs
# Carbon footprint
# Start up costs
# Operating Costs per year / KwH
# Consumption
# Production


# Constants
AMOUNT_OF_HOUSES = 600
TIME_INTERVAL = 1  # 1 hour

# Solar
SOLAR_PANEL_AREA = 1  # 1 square meter of efficiency
SOLAR_PANEL_EFFICIENCY = 0.15  # 15% efficiency
# Wind
WIND_SWEPT_AREA = 1500  # square meters
AIR_DENSITY = 1.225  # kg/m^3`
WIND_POWER_COEFFICIENT = 0.25 # Between 25% and 45% efficiency
WIND_GENERATOR_COEFFICIENT = 0.9  # Between 85% and 95% efficiency

# Blocks
storage_block = 0  # kWh

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
    return sunlight * SOLAR_PANEL_AREA * SOLAR_PANEL_EFFICIENCY * TIME_INTERVAL


# input wind velocity in (m/s) or production singular wind panel
def produce_wind(wind) -> float:  # Wh
    # E = 0.5 * WIND_SWEPT_AREA * AIR_DENSITY * WIND_POWER_COEFFICIENT * WIND_GENERATOR_COEFFICIENT * wind_speed^3 * t
    # E = CONSTANTS * wind_speed^3 * time
    wind_constants = 0.5 * WIND_SWEPT_AREA * AIR_DENSITY * WIND_POWER_COEFFICIENT * WIND_GENERATOR_COEFFICIENT
    return wind_constants * wind ** 3 * TIME_INTERVAL


def produce(sunlight: float, wind: float) -> float:
    solar_energy = produce_solar(sunlight)
    wind_energy = produce_wind(wind)
    print(f"Production, wind: {wind_energy}, solar_energy: {solar_energy}")
    return sum([solar_energy, wind_energy])


def iterate(consumption: float, sunlight: float, wind: float):
    global storage_block
    production = produce(sunlight, wind)
    consumption = consume(consumption)
    delta = production - consumption
    print(f"Production: {production} \t| Consumption: {consumption} \t| Delta: {delta} \t| Storage: {storage_block}")
    storage_block = storage_block + delta


def iterator():
    for i, weather_list_entry in enumerate(WEATHER):
        consumption_entry = 450
        weather_entry = weather_list_entry.split(',')

        sunlight_entry = float(weather_entry[10].strip()) / 3600 * 10000  # -> J/cm^2 -> J/m^2 -> J/s = W
        wind_entry = float(weather_entry[3].strip()) / 10  # -> in m/s
        # print(i, sunlight_entry, wind_entry)
        iterate(float(consumption_entry), float(sunlight_entry),
                float(wind_entry))  # TODO: Magic numbers  # Close the files after processing


def statistics():
    print(storage_block_values)
    storage_variance = np.var(storage_block_values)
    storage_mean = np.mean(storage_block_values)

    print(f"Storage variance: {storage_variance}\n"
          f"Storage mean: {storage_mean}\n")


# Call the iterator function to start processing the data
iterator()
# statistics()
