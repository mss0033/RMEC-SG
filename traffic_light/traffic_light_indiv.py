import random
# Defines the traffic light class
class Traffic_light:
    def __init__(self, 
                red_forward_duration:int, 
                red_turn_duration:int, 
                green_forward_duration:int, 
                green_turn_duration:int):
        # Initialize the traffic light
        self.red_forward_light_duration = red_forward_duration 
        self.red_turn_light_duration = red_turn_duration
        self.green_forward_light_duration = green_forward_duration
        self.green_turn_light_duration = green_turn_duration
        self.is_forward_light_green = True
        self.is_turn_light_green = True
        self.is_turn_light_red = False
        self.is_forward_light_red = False

    def update_light_state(self, iteration: 'int'):
        # Grab the lock
        # If the forward light is red
        if self.is_forward_light_red:
            if iteration % self.red_forward_light_duration == 0:
                self.is_forward_light_red = False
                self.is_forward_light_green = True
        # If the forward light is green
        elif self.is_forward_light_green:
            if iteration % self.green_forward_light_duration == 0:
                self.is_forward_light_green = False
                self.is_forward_light_red = True
        # If the turning light is red
        if self.is_turn_light_red:
            if iteration % self.red_turn_light_duration == 0:
                self.is_turn_light_red = False
                self.is_turn_light_green = True
        # If the turning light is green
        elif self.is_turn_light_green:
            if iteration % self.green_turn_light_duration == 0:
                self.is_turn_light_green = False
                self.is_turn_light_red = True
        # Print yourself
        # print(self.__str__())
    
    def __str__(self):
        status = f"Traffic Light Status:\n"
        status += f"  Forward Light: {'Green' if self.is_forward_light_green else 'Red'}\n"
        status += f"  Turn Light: {'Green' if self.is_turn_light_green else 'Red'}\n"
        status += f"  Red Forward Duration: {self.red_forward_light_duration} seconds\n"
        status += f"  Red Turn Duration: {self.red_turn_light_duration} seconds\n"
        status += f"  Green Forward Duration: {self.green_forward_light_duration} seconds\n"
        status += f"  Green Turn Duration: {self.green_turn_light_duration} seconds\n"
        return status
    
def generate_new_traffic_light() -> Traffic_light:
    return Traffic_light(red_forward_duration=random.randint(6, 12), 
                        red_turn_duration=random.randint(6, 12), 
                        green_forward_duration=random.randint(6, 12), 
                        green_turn_duration=random.randint(6, 12))