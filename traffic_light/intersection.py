import multiprocessing
import random
from traffic_light_indiv import Traffic_light
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
    cars_waiting_north_forward = random.randint(0, 3)
    cars_waiting_north_turning = random.randint(0, 3)
    cars_waiting_south_forward = random.randint(0, 3)
    cars_waiting_south_turning = random.randint(0, 3)
    cars_waiting_east_forward = random.randint(0, 3)
    cars_waiting_east_turning = random.randint(0, 3)
    cars_waiting_west_forward = random.randint(0, 3)
    cars_waiting_west_turning = random.randint(0, 3)
    # Boolean signal if a crash was detected
    collision_occured = False

    def __init__(self):
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
                    self.north_light = Traffic_light(red_forward_duration=3, red_turn_duration=2,
                                                    green_forward_duration=6, green_turn_duration=4)
            elif direction == 'south_n':
                self.south_neighbor = neighbor
                if not self.south_light:
                    self.south_light = Traffic_light(red_forward_duration=3, red_turn_duration=2,
                                                    green_forward_duration=6, green_turn_duration=4)
            elif direction == 'east_n':
                self.east_neighbor = neighbor
                if not self.east_light:
                    self.east_light = Traffic_light(red_forward_duration=3, red_turn_duration=2,
                                                    green_forward_duration=6, green_turn_duration=4)
            elif direction == 'west_n':
                self.west_neighbor = neighbor
                if not self.west_light:
                    self.west_light = Traffic_light(red_forward_duration=3, red_turn_duration=2,
                                                    green_forward_duration=6, green_turn_duration=4)
            
    def flow_traffic(self):
        processes = []
        processes.append(multiprocessing.Process(target=self.flow_north_to_south_traffic))
        processes.append(multiprocessing.Process(target=self.flow_south_to_north_traffic))
        processes.append(multiprocessing.Process(target=self.flow_east_to_west_traffic))
        processes.append(multiprocessing.Process(target=self.flow_west_to_east_traffic))
        processes.append(multiprocessing.Process(target=self.flow_north_turning_east_traffic))
        processes.append(multiprocessing.Process(target=self.flow_south_turning_west_traffic))
        processes.append(multiprocessing.Process(target=self.flow_east_turning_south_traffic))
        processes.append(multiprocessing.Process(target=self.flow_west_turning_north_traffic))
        print(self.__str__())

        for process in processes:
            process.start()

        for process in processes:
            process.join()

    def flow_north_to_south_traffic(self):
        # If there is no north light, return
        if not self.north_light:
            return
        # Update the light state
        self.north_light.update_light_state()
        # If the north forward light is green
        if self.north_light.is_forward_light_green:
            if self.east_light and self.east_light.is_forward_light_green or self.west_light and self.west_light.is_forward_light_green:
                self.collision_occured = True
                # return

            # Move cars waiting at the north light to the south neighbor
            self.cars_waiting_north_forward -= 1
            if self.south_neighbor:
                if random.choice([0, 1]) == 1:
                   self.south_neighbor.cars_waiting_north_forward += 1
                else:
                    self.south_neighbor.cars_waiting_north_turning += 1
    
    def flow_south_to_north_traffic(self):
        # If there is no south light, return
        if not self.south_light:
            return
        # Update the light state
        self.south_light.update_light_state()
        # If the south forward light is green
        if self.south_light.is_forward_light_green:
            if self.east_light and self.east_light.is_forward_light_green or self.west_light and self.west_light.is_forward_light_green:
                self.collision_occured = True
                # return

            # Move cars waiting at the south light to the north neighbor
            self.cars_waiting_south_forward -= 1
            if self.north_neighbor:
                if random.choice([0, 1]) == 1:
                   self.north_neighbor.cars_waiting_south_forward += 1
                else:
                    self.north_neighbor.cars_waiting_south_turning += 1
                

    def flow_east_to_west_traffic(self):
        # If there is no east light, return
        if not self.east_light:
            return
        # Update the light state
        self.east_light.update_light_state()
        # If the east forward light is green
        if self.east_light.is_forward_light_green:
            if self.north_light and self.north_light.is_forward_light_green or self.south_light and self.south_light.is_forward_light_green:
                self.collision_occured = True
                # return

            # Move cars waiting at the east light to the west neighbor
            self.cars_waiting_east_forward -= 1
            if self.west_neighbor:
                if random.choice([0, 1]) == 1:
                   self.west_neighbor.cars_waiting_east_forward += 1
                else:
                    self.west_neighbor.cars_waiting_east_turning += 1

    def flow_west_to_east_traffic(self):
        # If there is no west light, return
        if not self.west_light:
            return
        # Update the light state
        self.west_light.update_light_state()
        # If the west forward light is green
        if self.west_light.is_forward_light_green:
            if self.north_light and self.north_light.is_forward_light_green or self.south_light and self.south_light.is_forward_light_green:
                self.collision_occured = True
                # return

            # Move cars waiting at the east light to the west neighbor
            self.cars_waiting_west_forward -= 1
            if self.east_neighbor:
                if random.choice([0, 1]) == 1:
                   self.east_neighbor.cars_waiting_west_forward += 1
                else:
                    self.east_neighbor.cars_waiting_west_turning += 1

    def flow_north_turning_east_traffic(self):
        # If there is no north light, return
        if not self.north_light:
            return
        # Update the light state
        self.north_light.update_light_state()
        # If the north turning light is green
        if self.north_light.is_turn_light_green:
            if (self.south_light and self.south_light.is_forward_light_green 
                or self.east_light and self.east_light.is_forward_light_green 
                or self.east_light and self.east_light.is_turn_light_green 
                or self.west_light and self.west_light.is_forward_light_green 
                or self.west_light and self.west_light.is_turn_light_green):
                self.collision_occured = True
                # return

            # Move cars waiting at the south turning lane to the east or west neighbor
            self.cars_waiting_north_turning -= 1
            if self.east_neighbor:
                if random.choice([0, 1]) == 1:
                   self.east_neighbor.cars_waiting_west_forward += 1
                else:
                    self.east_neighbor.cars_waiting_west_turning += 1

    def flow_south_turning_west_traffic(self):
        # If there is no south light, return
        if not self.south_light:
            return
        # Update the light state
        self.south_light.update_light_state()
        # If the south turning light is green
        if self.south_light.is_turn_light_green:
            if (self.north_light and self.north_light.is_forward_light_green 
                or self.east_light and self.east_light.is_forward_light_green 
                or self.east_light and self.east_light.is_turn_light_green 
                or self.west_light and self.west_light.is_forward_light_green 
                or self.west_light and self.west_light.is_turn_light_green):
                self.collision_occured = True
                # return

            # Move cars waiting at the south turning lane to the east or west neighbor
            self.cars_waiting_south_turning -= 1
            if self.west_neighbor:
                if random.choice([0, 1]) == 1:
                   self.west_neighbor.cars_waiting_east_forward += 1
                else:
                    self.west_neighbor.cars_waiting_east_turning += 1


    def flow_east_turning_south_traffic(self):
        # If there is no east light, return
        if not self.east_light:
            return
        # Update the light state
        self.east_light.update_light_state()
        # If the east turning light is green
        if self.east_light.is_turn_light_green:
            if (self.north_light and self.north_light.is_forward_light_green 
                or self.north_light and self.north_light.is_turn_light_green 
                or self.south_light and self.south_light.is_forward_light_green 
                or self.south_light and self.south_light.is_turn_light_green 
                or self.west_light and self.west_light.is_forward_light_green):
                self.collision_occured = True
                # return

            # Move cars waiting at the south turning lane to the east or west neighbor
            self.cars_waiting_east_turning -= 1
            if self.south_neighbor:
                if random.choice([0, 1]) == 1:
                   self.south_neighbor.cars_waiting_north_forward += 1
                else:
                    self.south_neighbor.cars_waiting_north_turning += 1

    def flow_west_turning_north_traffic(self):
        # If there is no west light, return
        if not self.west_light:
            return
        # Update the light state
        self.west_light.update_light_state()
        # If the north turning light is green
        if self.west_light.is_turn_light_green:
            if (self.north_light and self.north_light.is_forward_light_green 
                or self.north_light and self.north_light.is_turn_light_green 
                or self.south_light and self.south_light.is_forward_light_green 
                or self.south_light and self.south_light.is_turn_light_green 
                or self.east_light and self.west_light.is_forward_light_green):
                self.collision_occured = True
                # return

            # Move cars waiting at the south turning lane to the east or west neighbor
            self.cars_waiting_west_turning -= 1
            if self.north_neighbor:
                if random.choice([0, 1]) == 1:
                   self.north_neighbor.cars_waiting_south_forward += 1
                else:
                    self.north_neighbor.cars_waiting_south_turning += 1
    
    def __str__(self):
        status = f"Intersection Status:\n"
        status += f"  North Light: {'Green' if self.north_light and self.north_light.is_forward_light_green else 'Red'}\n"
        status += f"  South Light: {'Green' if self.south_light and self.south_light.is_forward_light_green else 'Red'}\n"
        status += f"  East Light: {'Green' if self.east_light and self.east_light.is_forward_light_green else 'Red'}\n"
        status += f"  West Light: {'Green' if self.west_light and self.west_light.is_forward_light_green else 'Red'}\n"
        status += f"  Cars Waiting:\n"
        status += f"    North: {self.cars_waiting_north_forward} forward, {self.cars_waiting_north_turning} turning\n"
        status += f"    South: {self.cars_waiting_south_forward} forward, {self.cars_waiting_south_turning} turning\n"
        status += f"    East: {self.cars_waiting_east_forward} forward, {self.cars_waiting_east_turning} turning\n"
        status += f"    West: {self.cars_waiting_west_forward} forward, {self.cars_waiting_west_turning} turning\n"
        status += f"  Cars per Minute: {self.cars_per_minute}\n"
        status += f"  Collision Occurred: {self.collision_occured}\n"
        return status