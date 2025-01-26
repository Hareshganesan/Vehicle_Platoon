import time
import math
import carla

class Vehicle:
    def __init__(self, id, carla_vehicle):
        self.id = id
        self.carla_vehicle = carla_vehicle

    def set_target_velocity(self, velocity):
        self.carla_vehicle.set_target_velocity(velocity)

    def get_transform(self):
        return self.carla_vehicle.get_transform()

    def get_velocity(self):
        return self.carla_vehicle.get_velocity()

    def set_transform(self, transform):
        self.carla_vehicle.set_transform(transform)

    def destroy(self):
        self.carla_vehicle.destroy()
        print(f"Vehicle {self.id} destroyed.")

class VehiclePlatoon:
    def __init__(self, num_vehicles):
        self.num_vehicles = num_vehicles
        self.vehicles = []
        self.client = carla.Client('localhost', 2000)
        self.client.set_timeout(10.0)
        self.world = self.client.get_world()

    def spawn_vehicles(self):
        try:
            blueprint_library = self.world.get_blueprint_library()
            vehicle_bp = blueprint_library.filter('vehicle.*')[0]
            spawn_points = self.world.get_map().get_spawn_points()

            for i in range(self.num_vehicles):
                spawn_point = spawn_points[i % len(spawn_points)]
                carla_vehicle = self.world.spawn_actor(vehicle_bp, spawn_point)
                vehicle = Vehicle(i, carla_vehicle)
                self.vehicles.append(vehicle)
            return True
        except Exception as e:
            print(f"Error spawning vehicles: {e}")
            return False

    def follow_leader(self):
        if not self.vehicles:
            return

        leader = self.vehicles[0]
        leader.set_target_velocity(carla.Vector3D(10, 0, 0))  # Set initial velocity for the leader to start moving

        try:
            while True:
                leader_transform = leader.get_transform()
                leader_velocity = leader.get_velocity()

                # Check traffic light state
                traffic_light = leader.carla_vehicle.get_traffic_light()
                if traffic_light is not None:
                    if traffic_light.get_state() == carla.TrafficLightState.Red:
                        leader.set_target_velocity(carla.Vector3D(0, 0, 0))  # Stop at red light
                    elif traffic_light.get_state() == carla.TrafficLightState.Green:
                        leader.set_target_velocity(carla.Vector3D(10, 0, 0))  # Move at green light

                for i in range(1, len(self.vehicles)):
                    follower = self.vehicles[i]

                    # Calculate the desired position for the follower
                    offset_distance = i * 10.0
                    follower_location = carla.Location(
                        x=leader_transform.location.x - offset_distance * math.cos(math.radians(leader_transform.rotation.yaw)),
                        y=leader_transform.location.y - offset_distance * math.sin(math.radians(leader_transform.rotation.yaw)),
                        z=leader_transform.location.z
                    )

                    follower_transform = carla.Transform(
                        follower_location,
                        leader_transform.rotation
                    )

                    follower.set_transform(follower_transform)

                    # Adjust velocity based on distance to leader
                    distance_to_leader = leader_transform.location.distance(follower_transform.location)
                    if distance_to_leader > 15.0:
                        follower.set_target_velocity(carla.Vector3D(leader_velocity.x + 1, leader_velocity.y, leader_velocity.z))
                    elif distance_to_leader < 5.0:
                        follower.set_target_velocity(carla.Vector3D(leader_velocity.x - 1, leader_velocity.y, leader_velocity.z))
                    else:
                        follower.set_target_velocity(leader_velocity)

                time.sleep(0.1)
        except Exception as e:
            print(f"Platoon following error: {e}")

    def run(self):
        try:
            if not self.spawn_vehicles():
                return
            print(f"{len(self.vehicles)} vehicles spawned. Starting platoon following...")
            self.follow_leader()
        except Exception as e:
            print(f"Error in platoon: {e}")
        finally:
            for vehicle in self.vehicles:
                vehicle.destroy()
            print("Vehicles destroyed.")

def main():
    platoon = VehiclePlatoon(num_vehicles=4)
    platoon.run()

if __name__ == "__main__":
    main()