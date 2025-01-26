# FILE: /vehicle-platoon-simulation/vehicle-platoon-simulation/src/main.py
from platoon import VehiclePlatoon

def main():
    platoon = VehiclePlatoon(num_vehicles=4)
    platoon.run()

if __name__ == "__main__":
    main()