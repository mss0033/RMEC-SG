import random
from traffic_light_indiv import Traffic_light
from traffic_light_indiv import generate_new_traffic_light
# Defines the intersection class
class Intersection:
    # All intersections are 4 way
    # North and South roads are assumed parallel, and perpandicular to East and West roads
    north_light = None
    south_light = None
    # East and West roads are assumed parallel, and perpandicular to North and South roads
    east_light = None
    west_light = None
    # An intersection can be connected up to 4 neighboring intersections
    north_neighbor = None
    south_neighbor = None
    east_neighbor = None
    west_neighbor = None
    # Total throughput of the intersection in terms of number of cars passing through per minute
    cars_per_minute = 0
    # Number of cars waiting at all lights during at the intersection
    cars_waiting_north_forward = []
    cars_waiting_north_turning = []
    cars_waiting_south_forward = []
    cars_waiting_south_turning = []
    cars_waiting_east_forward = []
    cars_waiting_east_turning = []
    cars_waiting_west_forward = []
    cars_waiting_west_turning = []
    # Boolean signal if a crash was detected
    collision_occured = False

    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.north_light = None
        self.south_light = None
        self.east_light = None
        self.west_light = None
        self.north_neighbor = None
        self.south_neighbor = None
        self.east_neighbor = None
        self.west_neighbor = None

    def set_lights(self, north_l: 'Traffic_light' = None, south_l: 'Traffic_light' = None, east_l: 'Traffic_light' = None, west_l: 'Traffic_light' = None):
        self.north_light = north_l
        self.south_light = south_l
        self.east_light = east_l
        self.west_light = west_l
        
    def set_neighbors(self, **kwargs):
        for direction, neighbor in kwargs.items():
            if direction == 'north_n':
                self.north_neighbor = neighbor
                if not self.north_light:
                    self.north_light = generate_new_traffic_light()
            elif direction == 'south_n':
                self.south_neighbor = neighbor
                if not self.south_light:
                    self.south_light = generate_new_traffic_light()
            elif direction == 'east_n':
                self.east_neighbor = neighbor
                if not self.east_light:
                    self.east_light = generate_new_traffic_light()
            elif direction == 'west_n':
                self.west_neighbor = neighbor
                if not self.west_light:
                    self.west_light = generate_new_traffic_light()

    def add_cars(self, min_num_cars: 'int', max_num_cars: 'int'):
        for i in range(random.randint(min_num_cars, max_num_cars)):
            self.add_car(direction=random.choice(['north', 'south', 'east', 'west']), turning=random.choice([True, False]))

    def add_car(self, direction: str, turning: bool):
        x = 0
        y = 0
        if direction == 'north':
            x = self.x + self.width // 2
            y = self.y
        elif direction == 'south':
            x = self.x + self.width // 2
            y = self.y + self.height
        elif direction == 'east':
            x = self.x + self.width
            y = self.y + self.height // 2
        elif direction == 'west':
            x = self.x
            y = self.y + self.height // 2

        car = {'position': (x, y), 'new_position': (x, y)}
        if turning:
            getattr(self, f"cars_waiting_{direction}_turning").append(car)
        else:
            getattr(self, f"cars_waiting_{direction}_forward").append(car)

    def update_car_positions(self):
        for direction in ['north', 'south', 'east', 'west']:
            for car in getattr(self, f"cars_waiting_{direction}_forward"):
                car['position'] = car['new_position']
            for car in getattr(self, f"cars_waiting_{direction}_turning"):
                car['position'] = car['new_position']
            
    def flow_traffic(self, iteration: 'int'):
        # Update the light states before moving cars
        if self.north_light:
            self.north_light.update_light_state(iteration)
        if self.south_light:
            self.south_light.update_light_state(iteration)
        if self.east_light:
            self.east_light.update_light_state(iteration)
        if self.west_light:
            self.west_light.update_light_state(iteration)
        # Flow the traffic at the lights
        flow_north_to_south_traffic(self)
        flow_south_to_north_traffic(self)
        flow_east_to_west_traffic(self)
        flow_west_to_east_traffic(self)
        flow_north_turning_east_traffic(self)
        flow_south_turning_west_traffic(self)
        flow_east_turning_south_traffic(self)
        flow_west_turning_north_traffic(self)
        # print(self.__str__())
    
    def __str__(self):
        status = f"Intersection Status:\n"
        # North Light
        if self.north_light:
            status += f"  North Light: Forward: {'Green' if self.north_light.is_forward_light_green else 'Red'}, Turning: {'Green' if self.north_light.is_turn_light_green else 'Red'}\n"
        else:
            status += f"  Noth light: NA\n"
        # South Light
        if self.south_light:
            status += f"  South Light: Forward: {'Green' if self.south_light.is_forward_light_green else 'Red'}, Turning: {'Green' if self.south_light.is_turn_light_green else 'Red'}\n"
        else:
            status += f"  South light: NA\n"
        # East Light
        if self.east_light:
            status += f"  East Light: Forward: {'Green' if self.east_light.is_forward_light_green else 'Red'}, Turning: {'Green' if self.east_light.is_turn_light_green else 'Red'}\n"
        else:
            status += f"  East light: NA\n"
        # West Light
        if self.west_light:
            status += f"  West Light: Forward: {'Green' if self.west_light.is_forward_light_green else 'Red'}, Turning: {'Green' if self.west_light.is_turn_light_green else 'Red'}\n"
        else:
            status += f"  West light: NA\n"
        status += f"  Cars Waiting:\n"
        status += f"    North: {self.cars_waiting_north_forward} forward, {self.cars_waiting_north_turning} turning\n"
        status += f"    South: {self.cars_waiting_south_forward} forward, {self.cars_waiting_south_turning} turning\n"
        status += f"    East: {self.cars_waiting_east_forward} forward, {self.cars_waiting_east_turning} turning\n"
        status += f"    West: {self.cars_waiting_west_forward} forward, {self.cars_waiting_west_turning} turning\n"
        status += f"  Cars per Minute: {self.cars_per_minute}\n"
        status += f"  Collision Occurred: {self.collision_occured}\n"
        return status
    
def flow_north_to_south_traffic(self: 'Intersection'):
    # If the intersection is None or whatever is passed in is not an Intersection, return
    if not self or type(self) is not Intersection:
            return
    # If there is no north light, return
    if not self.north_light:
        return
    # If the north forward light is green
    if self.north_light.is_forward_light_green and len(self.cars_waiting_north_forward) > 0:
        if self.east_light and self.east_light.is_forward_light_green or self.west_light and self.west_light.is_forward_light_green:
            # Indicate collision
            self.collision_occured = True
            # return

        # Move cars waiting at the north light to the south neighbor
        car = self.cars_waiting_north_forward.pop(0)
        if self.south_neighbor:
            if random.choice([0, 1]) == 1:
                self.south_neighbor.cars_waiting_north_forward.append(car)
            else:
                self.south_neighbor.cars_waiting_north_turning.append(car)

def flow_south_to_north_traffic(self: 'Intersection'):
    # If the intersection is None or whatever is passed in is not an Intersection, return
    if not self or type(self) is not Intersection:
        return
    # If there is no south light, return
    if not self.south_light:
        return
    # If the south forward light is green
    if self.south_light.is_forward_light_green and len(self.cars_waiting_south_forward) > 0:
        if self.east_light and self.east_light.is_forward_light_green or self.west_light and self.west_light.is_forward_light_green:
            # Indicate collision
            self.collision_occured = True
            # return

        # Move cars waiting at the south light to the north neighbor
        car = self.cars_waiting_south_forward.pop(0)
        if self.north_neighbor:
            if random.choice([0, 1]) == 1:
                self.north_neighbor.cars_waiting_south_forward.append(car)
            else:
                self.north_neighbor.cars_waiting_south_turning.append(car)

def flow_east_to_west_traffic(self: 'Intersection'):
    # If the intersection is None or whatever is passed in is not an Intersection, return
    if not self or type(self) is not Intersection:
        return
    # If there is no east light, return
    if not self.east_light:
        return
    # If the east forward light is green
    if self.east_light.is_forward_light_green and len(self.cars_waiting_east_forward) > 0:
        if self.north_light and self.north_light.is_forward_light_green or self.south_light and self.south_light.is_forward_light_green:
            # Indicate collision
            self.collision_occured = True
            # return

        # Move cars waiting at the east light to the west neighbor
        car = self.cars_waiting_east_forward.pop(0)
        if self.west_neighbor:
            if random.choice([0, 1]) == 1:
                self.west_neighbor.cars_waiting_east_forward.append(car)
            else:
                self.west_neighbor.cars_waiting_east_turning.append(car)

def flow_west_to_east_traffic(self: 'Intersection'):
    # If the intersection is None or whatever is passed in is not an Intersection, return
    if not self or type(self) is not Intersection:
        return
    # If there is no west light, return
    if not self.west_light:
        return
    # If the west forward light is green
    if self.west_light.is_forward_light_green and len(self.cars_waiting_west_forward) > 0:
        if self.north_light and self.north_light.is_forward_light_green or self.south_light and self.south_light.is_forward_light_green:
            # Indicate collision
            self.collision_occured = True
            # return

        # Move cars waiting at the east light to the west neighbor
        car = self.cars_waiting_west_forward.pop(0)
        if self.east_neighbor:
            if random.choice([0, 1]) == 1:
                self.east_neighbor.cars_waiting_west_forward.append(car)
            else:
                self.east_neighbor.cars_waiting_west_turning.append(car)

def flow_north_turning_east_traffic(self: 'Intersection'):
    # If the intersection is None or whatever is passed in is not an Intersection, return
    if not self or type(self) is not Intersection:
        return
    # If there is no north light, return
    if not self.north_light:
        return
    # If the north turning light is green
    if self.north_light.is_turn_light_green and len(self.cars_waiting_north_turning) > 0:
        if (self.south_light and self.south_light.is_forward_light_green 
            or self.east_light and self.east_light.is_forward_light_green 
            or self.east_light and self.east_light.is_turn_light_green 
            or self.west_light and self.west_light.is_forward_light_green 
            or self.west_light and self.west_light.is_turn_light_green):
            # Indicate collision
            self.collision_occured = True
            # return

        # Move cars waiting at the south turning lane to the east or west neighbor
        car = self.cars_waiting_north_turning.pop(0)
        if self.east_neighbor:
            if random.choice([0, 1]) == 1:
                self.east_neighbor.cars_waiting_west_forward.append(car)
            else:
                self.east_neighbor.cars_waiting_west_turning.append(car)

def flow_south_turning_west_traffic(self: 'Intersection'):
    # If the intersection is None or whatever is passed in is not an Intersection, return
    if not self or type(self) is not Intersection:
        return
    # If there is no south light, return
    if not self.south_light:
        return
    # If the south turning light is green
    if self.south_light.is_turn_light_green and len(self.cars_waiting_south_turning) > 0:
        if (self.north_light and self.north_light.is_forward_light_green 
            or self.east_light and self.east_light.is_forward_light_green 
            or self.east_light and self.east_light.is_turn_light_green 
            or self.west_light and self.west_light.is_forward_light_green 
            or self.west_light and self.west_light.is_turn_light_green):
            # Indicate collision
            self.collision_occured = True
            # return

        # Move cars waiting at the south turning lane to the east or west neighbor
        car = self.cars_waiting_south_turning.pop(0)
        if self.west_neighbor:
            if random.choice([0, 1]) == 1:
                self.west_neighbor.cars_waiting_east_forward.append(car)
            else:
                self.west_neighbor.cars_waiting_east_turning.append(car)

def flow_east_turning_south_traffic(self: 'Intersection'):
    # If the intersection is None or whatever is passed in is not an Intersection, return
    if not self or type(self) is not Intersection:
        return
    # If there is no east light, return
    if not self.east_light:
        return
    # If the east turning light is green
    if self.east_light.is_turn_light_green and len(self.cars_waiting_east_turning) > 0:
        if (self.north_light and self.north_light.is_forward_light_green 
            or self.north_light and self.north_light.is_turn_light_green 
            or self.south_light and self.south_light.is_forward_light_green 
            or self.south_light and self.south_light.is_turn_light_green 
            or self.west_light and self.west_light.is_forward_light_green):
            # Indicate collision
            self.collision_occured = True
            # return

        # Move cars waiting at the south turning lane to the east or west neighbor
        car = self.cars_waiting_east_turning.pop(0)
        if self.south_neighbor:
            if random.choice([0, 1]) == 1:
                self.south_neighbor.cars_waiting_north_forward.append(car)
            else:
                self.south_neighbor.cars_waiting_north_turning.append(car)

def flow_west_turning_north_traffic(self: 'Intersection'):
    # If the intersection is None or whatever is passed in is not an Intersection, return
    if not self or type(self) is not Intersection:
        return
    # If there is no west light, return
    if not self.west_light:
        return
    # If the north turning light is green
    if self.west_light.is_turn_light_green and len(self.cars_waiting_west_turning) > 0:
        if (self.north_light and self.north_light.is_forward_light_green 
            or self.north_light and self.north_light.is_turn_light_green 
            or self.south_light and self.south_light.is_forward_light_green 
            or self.south_light and self.south_light.is_turn_light_green 
            or self.east_light and self.west_light.is_forward_light_green):
            # Indicate collision
            self.collision_occured = True
            # return

        # Move cars waiting at the south turning lane to the east or west neighbor
        car = self.cars_waiting_west_turning.pop(0)
        if self.north_neighbor:
            if random.choice([0, 1]) == 1:
                self.north_neighbor.cars_waiting_south_forward.append(car)
            else:
                self.north_neighbor.cars_waiting_south_turning.append(car)