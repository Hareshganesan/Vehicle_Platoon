import carla
import random
import time
import math

class VehiclePlatoon:
    def __init__(self, num_vehicles=4):
        # Connect to Carla server
        self.client = carla.Client('localhost', 2000)
        self.client.set_timeout(10.0)
        
        # Get the world and map
        self.world = self.client.get_world()
        self.map = self.world.get_map()
        
        # Get blueprint library
        self.blueprint_library = self.world.get_blueprint_library()
        
        # Vehicles and waypoints
        self.vehicles = []
        self.num_vehicles = num_vehicles

    def find_safe_spawn_points(self, num_points):
        """
        Find safe spawn points with no collisions
        """
        # Get all spawn points
        all_spawn_points = self.map.get_spawn_points()
        safe_spawn_points = []

        # Check each spawn point for safety
        for spawn_point in all_spawn_points:
            # Check for collisions at spawn point
            try:
                # Perform overlap check
                nearby_actors = self.world.get_actors().filter('*')
                is_safe = True

                for actor in nearby_actors:
                    # Check distance from spawn point
                    if actor.type_id.startswith('vehicle.'):
                        distance = spawn_point.location.distance(actor.get_location())
                        if distance < 5.0:  # Minimum safe distance
                            is_safe = False
                            break

                if is_safe:
                    safe_spawn_points.append(spawn_point)

                # Stop if we have enough safe points
                if len(safe_spawn_points) >= num_points:
                    break

            except Exception as e:
                print(f"Error checking spawn point: {e}")

        return safe_spawn_points[:num_points]

    def spawn_vehicles(self):
        # Use Tesla Model 3 blueprint
        vehicle_blueprints = self.blueprint_library.filter('vehicle.tesla.model3')
        blueprint = vehicle_blueprints[0]
        
        # Find safe spawn points
        spawn_points = self.find_safe_spawn_points(self.num_vehicles)
        
        # Check if we have enough spawn points
        if len(spawn_points) < self.num_vehicles:
            print(f"Not enough safe spawn points. Found {len(spawn_points)}, need {self.num_vehicles}")
            return False

        # Spawn vehicles
        for i in range(self.num_vehicles):
            try:
                # Spawn at safe point
                spawn_point = spawn_points[i]
                
                # Spawn vehicle
                vehicle = self.world.try_spawn_actor(blueprint, spawn_point)
                
                if vehicle is None:
                    print(f"Failed to spawn vehicle {i}")
                    continue
                
                # Configure vehicle
                vehicle.set_autopilot(True)
                
                self.vehicles.append(vehicle)
            
            except Exception as e:
                print(f"Error spawning vehicle {i}: {e}")

        return len(self.vehicles) > 0

    def follow_leader(self):
        """
        Advanced following mechanism
        """
        if not self.vehicles:
            return

        # Leader is the first vehicle
        leader = self.vehicles[0]

        try:
            while True:
                # Get leader's current transform
                leader_transform = leader.get_transform()
                
                # Position followers relative to leader
                for follower_index in range(1, len(self.vehicles)):
                    # Calculate offset for each follower
                    offset_distance = follower_index * 10.0
                    
                    # Calculate follower position behind leader
                    follower_location = carla.Location(
                        x=leader_transform.location.x - offset_distance * math.cos(math.radians(leader_transform.rotation.yaw)),
                        y=leader_transform.location.y - offset_distance * math.sin(math.radians(leader_transform.rotation.yaw)),
                        z=leader_transform.location.z
                    )
                    
                    # Create follower transform
                    follower_transform = carla.Transform(
                        follower_location,
                        leader_transform.rotation
                    )
                    
                    # Move follower
                    follower = self.vehicles[follower_index]
                    follower.set_transform(follower_transform)
                    
                    # Match leader's velocity
                    leader_velocity = leader.get_velocity()
                    follower.set_target_velocity(leader_velocity)
                
                # Small delay to prevent overwhelming
                time.sleep(0.1)
        
        except Exception as e:
            print(f"Platoon following error: {e}")

    def run(self):
        try:
            # Spawn vehicles
            if not self.spawn_vehicles():
                return
            
            print(f"{len(self.vehicles)} vehicles spawned. Starting platoon following...")
            
            # Start following mechanism
            self.follow_leader()
        
        except Exception as e:
            print(f"Error in platoon: {e}")
        
        finally:
            # Cleanup
            for vehicle in self.vehicles:
                vehicle.destroy()
            print("Vehicles destroyed.")

def main():
    # Create platoon with 4 vehicles
    platoon = VehiclePlatoon(num_vehicles=4)
    platoon.run()

if __name__ == "__main__":
    main()