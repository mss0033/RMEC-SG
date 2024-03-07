import time
# Defines the traffic light class
class Traffic_light:
    max_light_duration = 120
    min_light_duration = 10

    is_forward_light_green = False
    is_turn_light_green = False
    is_turn_light_red = True
    is_forward_light_red = True

    last_update_time = time.time()

    def __init__(self, red_forward_duration:int, red_turn_duration:int, green_forward_duration:int, green_turn_duration:int):
        self.red_forward_light_duration = red_forward_duration
        self.red_turn_light_duration = red_turn_duration
        self.green_forward_light_duration = green_forward_duration
        self.green_turn_light_duration = green_turn_duration

    def update_light_state(self):
        current_time = time.time()
        elapsed_time = current_time - self.last_update_time

        if self.is_forward_light_red:
            if elapsed_time >= self.red_forward_light_duration:
                self.is_forward_light_red = False
                self.is_forward_light_green = True
                self.last_update_time = current_time
        elif self.is_forward_light_green:
            if elapsed_time >= self.green_forward_light_duration:
                self.is_forward_light_green = False
                self.is_forward_light_red = True
                self.last_update_time = current_time

        if self.is_turn_light_red:
            if elapsed_time >= self.red_turn_light_duration:
                self.is_turn_light_red = False
                self.is_turn_light_green = True
                self.last_update_time = current_time
        elif self.is_turn_light_green:
            if elapsed_time >= self.green_turn_light_duration:
                self.is_turn_light_green = False
                self.is_turn_light_red = True
                self.last_update_time = current_time
        print(self.__str__())
    
    def __str__(self):
        status = f"Traffic Light Status:\n"
        status += f"  Forward Light: {'Green' if self.is_forward_light_green else 'Red'}\n"
        status += f"  Turn Light: {'Green' if self.is_turn_light_green else 'Red'}\n"
        status += f"  Red Forward Duration: {self.red_forward_light_duration} seconds\n"
        status += f"  Red Turn Duration: {self.red_turn_light_duration} seconds\n"
        status += f"  Green Forward Duration: {self.green_forward_light_duration} seconds\n"
        status += f"  Green Turn Duration: {self.green_turn_light_duration} seconds\n"
        return status