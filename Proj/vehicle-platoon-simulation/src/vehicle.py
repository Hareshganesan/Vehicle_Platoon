class Vehicle:
    def __init__(self, id):
        self.id = id
        self.velocity = 0

    def set_target_velocity(self, velocity):
        self.velocity = velocity
        print(f"Vehicle {self.id} target velocity set to {self.velocity}")

    def destroy(self):
        print(f"Vehicle {self.id} destroyed")