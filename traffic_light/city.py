import multiprocessing
import pygame
import random
import time
from intersection import Intersection
# Defines the city class
class City:
    def __init__(self, city_config):
        self.city_config = city_config
        self.num_rows = len(city_config)
        self.num_cols = len(city_config[0])
        self.intersections = {}
        self.create_intersections()
        self.connect_intersections()

    def create_intersections(self):
        num_rows = len(self.city_config)
        num_cols = len(self.city_config[0])

        for row in range(num_rows):
            for col in range(num_cols):
                if self.city_config[row][col] == 1:
                    self.intersections[(row, col)] = Intersection()

    def connect_intersections(self):
        for (row, col), intersection in self.intersections.items():
            # Check and connect neighboring intersections
            north_row = (row - 1) % self.num_rows
            south_row = (row + 1) % self.num_rows
            west_col = (col - 1) % self.num_cols
            east_col = (col + 1) % self.num_cols

            if self.city_config[north_row][col] == 1:
                intersection.set_neighbors(north_n=self.intersections[(north_row, col)])
            if self.city_config[south_row][col] == 1:
                intersection.set_neighbors(south_n=self.intersections[(south_row, col)])
            if self.city_config[row][west_col] == 1:
                intersection.set_neighbors(west_n=self.intersections[(row, west_col)])
            if self.city_config[row][east_col] == 1:
                intersection.set_neighbors(east_n=self.intersections[(row, east_col)])

    def get_intersection(self, row, col):
        return self.intersections.get((row, col))

    def get_all_intersections(self):
        return list(self.intersections.values())
    
    def flow_traffic(self, iteration: 'int'):
        for intersection in self.intersections.values():
            intersection.flow_traffic(iteration)
        # processes = []
        # for intersection in self.intersections.values():
        #     process = multiprocessing.Process(target=intersection.flow_traffic)
        #     processes.append(process)
        #     process.start()

        # for process in processes:
        #     process.join()

    def visualize_traffic(self, iterations):
        pygame.init()
        screen_width = 1600
        screen_height = 1200
        screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption("Traffic Simulation")

        # Define colors
        BLACK = (0, 0, 0)
        BLUE = (0, 0, 255)
        WHITE = (255, 255, 255)
        RED = (255, 0, 0)
        GREEN = (0, 255, 0)
        YELLOW = (255, 255, 0)
        GRAY = (128, 128, 128)
        ROAD_COLOR = (200, 200, 200)

        # Calculate cell size based on screen size and grid dimensions
        cell_width = (screen_width - 20) // (self.num_cols + (self.num_cols - 1) // 2)
        cell_height = (screen_height - 20) // (self.num_rows + (self.num_rows - 1) // 2)
        road_width = cell_width // 2
        road_height = cell_height // 2

        # Create font for displaying text
        font = pygame.font.Font(None, 24)

        for iteration in range(iterations):
            # Clear the screen
            screen.fill(WHITE)

            # Draw roads
            for row in range(self.num_rows):
                for col in range(self.num_cols):
                    x = 10 + col * (cell_width + road_width)
                    y = 10 + row * (cell_height + road_height)
                    if col < self.num_cols - 1:
                        pygame.draw.rect(screen, ROAD_COLOR, (x + cell_width, y, road_width, cell_height))
                    if row < self.num_rows - 1:
                        pygame.draw.rect(screen, ROAD_COLOR, (x, y + cell_height, cell_width, road_height))

            # Draw intersections
            for row in range(self.num_rows):
                for col in range(self.num_cols):
                    if (row, col) not in self.intersections:
                        continue
                    intersection = self.intersections[(row, col)]
                    print("----------Before traffic flow-----------")
                    print(intersection)
                    # Update the traffic lights and vehicle positions
                    self.flow_traffic(iteration)
                    print("++++++++++After traffic flow++++++++++")
                    print(intersection)
                    x = 10 + col * (cell_width + road_width)
                    y = 10 + row * (cell_height + road_height)

                    # Draw intersection
                    pygame.draw.rect(screen, BLACK, (x, y, cell_width, cell_height), 2)

                    # Draw traffic lights
                    light_radius = 10
                    light_spacing = 5
                    if intersection.north_light:
                        color = GREEN if intersection.north_light.is_forward_light_green.value else RED
                        pygame.draw.circle(screen, color, (x + cell_width // 2, y + light_spacing), light_radius)
                    if intersection.south_light:
                        color = GREEN if intersection.south_light.is_forward_light_green.value else RED
                        pygame.draw.circle(screen, color, (x + cell_width // 2, y + cell_height - light_spacing), light_radius)
                    if intersection.east_light:
                        color = GREEN if intersection.east_light.is_forward_light_green.value else RED
                        pygame.draw.circle(screen, color, (x + cell_width - light_spacing, y + cell_height // 2), light_radius)
                    if intersection.west_light:
                        color = GREEN if intersection.west_light.is_forward_light_green.value else RED
                        pygame.draw.circle(screen, color, (x + light_spacing, y + cell_height // 2), light_radius)

                    # Draw vehicles
                    vehicle_radius = 5
                    vehicle_spacing = 10
                    for direction in ['north', 'south', 'east', 'west']:
                        num_vehicles_forward = getattr(intersection, f"cars_waiting_{direction}_forward", 0).value
                        num_vehicles_turning = getattr(intersection, f"cars_waiting_{direction}_turning", 0).value
                        for i in range(num_vehicles_forward):
                            if direction == 'north':
                                pygame.draw.circle(screen, BLUE, (x + cell_width // 2, y + light_spacing + vehicle_spacing * (i + 1)), vehicle_radius)
                            elif direction == 'south':
                                pygame.draw.circle(screen, BLUE, (x + cell_width // 2, y + cell_height - light_spacing - vehicle_spacing * (i + 1)), vehicle_radius)
                            elif direction == 'east':
                                pygame.draw.circle(screen, BLUE, (x + cell_width - light_spacing - vehicle_spacing * (i + 1), y + cell_height // 2), vehicle_radius)
                            elif direction == 'west':
                                pygame.draw.circle(screen, BLUE, (x + light_spacing + vehicle_spacing * (i + 1), y + cell_height // 2), vehicle_radius)
                        for i in range(num_vehicles_turning):
                            if direction == 'north':
                                pygame.draw.circle(screen, YELLOW, (x + cell_width // 2 - vehicle_spacing, y + light_spacing + vehicle_spacing * (i + 1)), vehicle_radius)
                            elif direction == 'south':
                                pygame.draw.circle(screen, YELLOW, (x + cell_width // 2 + vehicle_spacing, y + cell_height - light_spacing - vehicle_spacing * (i + 1)), vehicle_radius)
                            elif direction == 'east':
                                pygame.draw.circle(screen, YELLOW, (x + cell_width - light_spacing - vehicle_spacing * (i + 1), y + cell_height // 2 + vehicle_spacing), vehicle_radius)
                            elif direction == 'west':
                                pygame.draw.circle(screen, YELLOW, (x + light_spacing + vehicle_spacing * (i + 1), y + cell_height // 2 - vehicle_spacing), vehicle_radius)

                    # Display number of vehicles waiting
                    text_color = BLACK
                    text_bg_color = WHITE
                    text_padding = 5
                    for direction in ['north', 'south', 'east', 'west']:
                        num_vehicles_forward = getattr(intersection, f"cars_waiting_{direction}_forward", 0).value
                        num_vehicles_turning = getattr(intersection, f"cars_waiting_{direction}_turning", 0).value
                        total_vehicles = num_vehicles_forward + num_vehicles_turning
                        if total_vehicles > 0:
                            text = font.render(str(total_vehicles), True, text_color, text_bg_color)
                            text_rect = text.get_rect()
                            if direction == 'north':
                                text_rect.center = (x + cell_width // 2, y + text_padding)
                            elif direction == 'south':
                                text_rect.center = (x + cell_width // 2, y + cell_height - text_padding)
                            elif direction == 'east':
                                text_rect.center = (x + cell_width - text_padding, y + cell_height // 2)
                            elif direction == 'west':
                                text_rect.center = (x + text_padding, y + cell_height // 2)
                            screen.blit(text, text_rect)

            # Update the traffic lights and vehicle positions
            # self.flow_traffic()

            # Update the display
            pygame.display.flip()

            # Delay to control the animation speed
            time.sleep(1)

        pygame.quit()
    
    def print_city(self):
        num_rows = len(self.city_config)
        num_cols = len(self.city_config[0])

        print("City Configuration:")
        for row in range(num_rows):
            for col in range(num_cols):
                if self.city_config[row][col] == 1:
                    print("I", end="")
                else:
                    print(".", end="")
            print()

        print("\nIntersections:")
        for (row, col), intersection in self.intersections.items():
            print(f"Intersection at ({row}, {col}):")
            if intersection.north_neighbor:
                print(f"  North: Intersection at ({row - 1}, {col})")
            if intersection.south_neighbor:
                print(f"  South: Intersection at ({row + 1}, {col})")
            if intersection.east_neighbor:
                print(f"  East: Intersection at ({row}, {col + 1})")
            if intersection.west_neighbor:
                print(f"  West: Intersection at ({row}, {col - 1})")
            print()

        print("Roads:")
        for (row, col), intersection in self.intersections.items():
            if intersection.north_neighbor:
                print(f"  Road: ({row}, {col}) <-> ({row - 1}, {col})")
            if intersection.south_neighbor:
                print(f"  Road: ({row}, {col}) <-> ({row + 1}, {col})")
            if intersection.east_neighbor:
                print(f"  Road: ({row}, {col}) <-> ({row}, {col + 1})")
            if intersection.west_neighbor:
                print(f"  Road: ({row}, {col}) <-> ({row}, {col - 1})")
    
    def print_city_ascii(self):
        num_rows = len(self.city_config)
        num_cols = len(self.city_config[0])

        # Create a 2D grid to store the ASCII representation
        grid = [[' ' for _ in range(num_cols * 2 + 1)] for _ in range(num_rows * 2 + 1)]

        # Fill the grid with roads and intersections
        for row in range(num_rows):
            for col in range(num_cols):
                if self.city_config[row][col] == 1:
                    intersection = self.get_intersection(row, col)
                    grid[row * 2 + 1][col * 2 + 1] = '+'

                    if intersection.north_neighbor:
                        grid[row * 2][col * 2 + 1] = '|'
                    if intersection.south_neighbor:
                        grid[row * 2 + 2][col * 2 + 1] = '|'
                    if intersection.west_neighbor:
                        grid[row * 2 + 1][col * 2] = '-'
                    if intersection.east_neighbor:
                        grid[row * 2 + 1][col * 2 + 2] = '-'

        # Print the ASCII representation
        print("ASCII Representation of the City:")
        for row in grid:
            print(''.join(row))
    
def generate_city_configuration(seed, num_rows, num_cols, complexity):
    random.seed(seed)

    # Initialize the city configuration with all zeros
    city_config = [[0] * num_cols for _ in range(num_rows)]

    # Set the central intersection as a starting point
    center_row, center_col = num_rows // 2, num_cols // 2
    city_config[center_row][center_col] = 1

    # Helper function to check if a cell is within the city bounds
    def is_valid_cell(row, col):
        return 0 <= row < num_rows and 0 <= col < num_cols

    # Helper function to get the neighboring cells of a given cell
    def get_neighbors(row, col):
        neighbors = []
        for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            new_row, new_col = (row + dr) % num_rows, (col + dc) % num_cols
            neighbors.append((new_row, new_col))
        return neighbors

    # Iteratively expand the city configuration
    for _ in range(complexity):
        # Choose a random existing intersection
        intersections = [(row, col) for row in range(num_rows) for col in range(num_cols) if city_config[row][col] == 1]
        if not intersections:
            break
        row, col = random.choice(intersections)

        # Get the neighboring cells of the chosen intersection
        neighbors = get_neighbors(row, col)

        # Filter out the neighboring cells that are already intersections
        available_neighbors = [(r, c) for r, c in neighbors if city_config[r][c] == 0]

        # If there are available neighbors, choose one randomly and make it an intersection
        if available_neighbors:
            new_row, new_col = random.choice(available_neighbors)
            city_config[new_row][new_col] = 1

            # Create a closed loop by connecting the new intersection to an existing one
            loop_row, loop_col = random.choice([(r, c) for r, c in neighbors if city_config[r][c] == 1])
            city_config[loop_row][loop_col] = 1

    return city_config