import random
import time
from multiprocessing import Value, Lock
# Defines the traffic light class
class Traffic_light:
    lock = Lock()

    def __init__(self, 
                red_forward_duration:int, 
                red_turn_duration:int, 
                green_forward_duration:int, 
                green_turn_duration:int):
        # Initialize the traffic light
        self.red_forward_light_duration = Value('i', red_forward_duration)  # 'b' for boolean
        self.red_turn_light_duration = Value('i', red_turn_duration) 
        self.green_forward_light_duration = Value('i', green_forward_duration) 
        self.green_turn_light_duration = Value('i', green_turn_duration) 
        self.is_forward_light_green = Value('b', False)  # 'b' for boolean
        self.is_turn_light_green = Value('b', False)  # 'b' for boolea
        self.is_turn_light_red = Value('b', True)  # 'b' for boolean
        self.is_forward_light_red = Value('b', True)  # 'b' for boolean

    def update_light_state(self, iteration: 'int'):
        # Grab the lock
        self.lock.acquire()
        # If the forward light is red
        if self.is_forward_light_red.value:
            if iteration % self.red_forward_light_duration.value == 0:
                self.is_forward_light_red.value = False
                self.is_forward_light_green.value = True
        # If the forward light is green
        elif self.is_forward_light_green.value:
            if iteration % self.green_forward_light_duration.value == 0:
                self.is_forward_light_green.value = False
                self.is_forward_light_red.value = True
        # If the turning light is red
        if self.is_turn_light_red.value:
            if iteration % self.red_turn_light_duration.value == 0:
                self.is_turn_light_red.value = False
                self.is_turn_light_green.value = True
        # If the turning light is green
        elif self.is_turn_light_green.value:
            if iteration % self.green_turn_light_duration.value == 0:
                self.is_turn_light_green.value = False
                self.is_turn_light_red.value = True
        # Print yourself
        # print(self.__str__())
        # Release the lock
        self.lock.release()
    
    def __str__(self):
        status = f"Traffic Light Status:\n"
        status += f"  Forward Light: {'Green' if self.is_forward_light_green.value else 'Red'}\n"
        status += f"  Turn Light: {'Green' if self.is_turn_light_green.value else 'Red'}\n"
        status += f"  Red Forward Duration: {self.red_forward_light_duration.value} seconds\n"
        status += f"  Red Turn Duration: {self.red_turn_light_duration.value} seconds\n"
        status += f"  Green Forward Duration: {self.green_forward_light_duration.value} seconds\n"
        status += f"  Green Turn Duration: {self.green_turn_light_duration.value} seconds\n"
        return status
    
def generate_new_traffic_light() -> Traffic_light:
    return Traffic_light(red_forward_duration=random.randint(6, 12), 
                        red_turn_duration=random.randint(6, 12), 
                        green_forward_duration=random.randint(6, 12), 
                        green_turn_duration=random.randint(6, 12))