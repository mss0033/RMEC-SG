from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from traffic_light_ec import evolutionary_algorithm, identify_specification_gaming_individuals

app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('run_ec')
def run_ec(data):
    population_size = data['population_size']
    num_generations = data['num_generations']
    
    population = evolutionary_algorithm(int(population_size), int(num_generations))
    potential_gaming_individuals = identify_specification_gaming_individuals(population)
    
    for individual in potential_gaming_individuals:
        # Emit the individual data to the UI
        emit('potential_gaming_individual', {'individual': str(individual)})

if __name__ == '__main__':
    socketio.run(app, debug=True)