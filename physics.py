import math

class PullBackCarPhysics:
    def __init__(self, name, mass, max_energy, base_force, charge_rate, depletion_rate, friction_coeff=0.02):
        self.name = name
        self.mass = mass           # kg
        
        self.max_energy = max_energy       # Max stored energy units
        self.base_force = base_force       # Base engine force when energy is max
        self.charge_rate = charge_rate     # How fast energy builds up per second when pulled back
        self.depletion_rate = depletion_rate # How much energy unwinds per meter of motion
        self.friction_coeff = friction_coeff
        
        self.stored_energy = 0.0
        self.velocity = 0.0        # m/s
        self.distance = 0.0        # m
        
        self.engine_force = 0.0
        self.acceleration = 0.0
        
        self.pulling_back = False
        
    def update(self, dt):
        if self.pulling_back:
            # We are holding the mouse to wind up the car
            self.distance = 0.0
            self.velocity = 0.0
            self.stored_energy += self.charge_rate * dt
            if self.stored_energy > self.max_energy:
                self.stored_energy = self.max_energy
            self.engine_force = 0.0
            self.acceleration = 0.0
        else:
            # Car is freely moving
            if self.stored_energy > 0:
                # Force scales linearly with remaining energy, giving a strong initial thrust that tapers off
                force_ratio = self.stored_energy / self.max_energy
                self.engine_force = self.base_force * force_ratio
                
                # Energy depletes by moving forward (spring unwinding)
                # Ensure we only deplete if moving forward
                if self.velocity > 0:
                    distance_moved = self.velocity * dt
                    self.stored_energy -= self.depletion_rate * distance_moved
                
                if self.stored_energy < 0:
                    self.stored_energy = 0.0
            else:
                self.engine_force = 0.0

            # Friction (Rolling Resistance)
            friction_force = self.mass * 9.81 * self.friction_coeff
            
            # When a pull-back car runs out of stored energy, the wheels stop freely spinning and provide massive resistance (gears lock up)
            if self.stored_energy <= 0:
                friction_force *= 50.0
            
            # Apply friction only if the car is moving or if engine force is attempting to move it
            if self.velocity > 0.1:
                net_force = self.engine_force - friction_force
            elif self.engine_force > friction_force:
                net_force = self.engine_force - friction_force
            else:
                net_force = 0.0
                self.velocity = 0.0 # Snap to zero and stop
            
            if self.velocity > 0 or net_force > 0:
                self.acceleration = net_force / self.mass
                self.velocity += self.acceleration * dt
            
            # Coast to a halt, no reverse driving
            if self.velocity < 0.1 and net_force <= 0:
                self.velocity = 0.0
                self.acceleration = 0.0
            
            self.distance += self.velocity * dt

def create_basic():
    # The Basic Car (Yellow) - Travels max 5 meters
    return PullBackCarPhysics("Basic Car", mass=1500, max_energy=100.0, base_force=6000.0, charge_rate=40.0, depletion_rate=20.0, friction_coeff=0.03)

def create_intermediate():
    # The Intermediate (White) - Travels max 6 meters
    return PullBackCarPhysics("Intermediate Car", mass=1300, max_energy=150.0, base_force=7500.0, charge_rate=50.0, depletion_rate=25.0, friction_coeff=0.02)

def create_formula_one():
    # The Formula One (Red) - Travels max 7 meters
    return PullBackCarPhysics("Formula One", mass=800, max_energy=200.0, base_force=10000.0, charge_rate=80.0, depletion_rate=28.5, friction_coeff=0.015)
