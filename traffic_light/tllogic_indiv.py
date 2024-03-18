import random
from copy import deepcopy
from typing import Tuple

# Light Phases
RED_LIGHT = 'r'
YELLOW_LIGHT = 'y'
GREEN_NO_PRI_LIGHT = 'g'
GREEN_YES_PRI_LIGHT = 'G'
GREEN_TURN_ARROW_LIGHT = 's'
RED_PLUS_YELLOW_LIGHT = 'u'
OFF_BLINKING_LIGHT = 'o'
OFF_NO_SIGNAL_LIGHT = 'O'
# List of Phase options
PHASE_STATE_OPTIONS = [RED_LIGHT, YELLOW_LIGHT, GREEN_NO_PRI_LIGHT, GREEN_YES_PRI_LIGHT, RED_PLUS_YELLOW_LIGHT, OFF_BLINKING_LIGHT, OFF_NO_SIGNAL_LIGHT]
# Phase attribte keys
DURATION_ATTR = 'duration'
STATE_ATTR = 'state'
# List of Phase attributes
PHASE_ATTRIBUTES = [DURATION_ATTR, STATE_ATTR]
# Phase duration recombination stratigies
SWAP = 'swap'
TAKE_FROM_SELF = 'take_from_self'
TAKE_FROM_PARTNER = 'take_from_partner'
# List of Phase recombination stratigies
PHASE_DURATION_RECOMB_STRATS = [SWAP, TAKE_FROM_SELF, TAKE_FROM_PARTNER]
# Phase state recombination stratigies
HALF_AND_HALF = 'half_and_half'
ZIPPER = 'zipper'
# List of Phase state recombination stratigies
PHASE_STATE_RECOMB_STRATS = [HALF_AND_HALF, ZIPPER]
# Min and max duration of lights
MIN_LIGHT_DURATION = 1
MAX_LIGHT_DURATION = 120

# Represents a Phase component of a Traffic Light Logic
class Phase:
    def __init__(self, attrib):
        self.duration = attrib[DURATION_ATTR]
        self.state = attrib[STATE_ATTR]
    
    # Mutates an individual
    def mutate(self):
        # Select if the mutation is to the duration or to the state
        # If the mutation is to the state
        if random.choice(PHASE_ATTRIBUTES) == STATE_ATTR:
            # Select a random index in the state to mutate
            index_to_mutate = random.randint(0, len(self.state) - 1)
            # Mutate the state at the index to a random light state
            self.state = self.state[:index_to_mutate] + random.choice(PHASE_STATE_OPTIONS) + self.state[index_to_mutate + 1:]
        # If the mutation is to the duration
        else:
            # Randomly select a valid duration
            self.duration = random.randint(MIN_LIGHT_DURATION, MAX_LIGHT_DURATION)
    
    def recombine(self, partner: 'Phase') -> Tuple['Phase', 'Phase']:
        # Randomly select a duration recombination strategy
        duration_recombine_strat = SWAP
        # duration_recombine_strat = random.choice(PHASE_DURATION_RECOMB_STRATS)
        # If the strat is swap
        if duration_recombine_strat == SWAP:
            # Capture the origional duration for yourself
            temp = self.duration
            # Assign your partner's duration to yourself
            self.duration = partner.duration
            # Assign your origional duration to your partner
            partner.duration = temp
        # If the strat is take from self
        elif duration_recombine_strat == TAKE_FROM_SELF:
            # Selfishly assign your duration to your partner
            partner.duration = self.duration
        # If the strat is take from partner
        elif duration_recombine_strat == TAKE_FROM_PARTNER:
            # Selflessly take your duration from your partner
            self.duration = partner.duration
        # Randomly select a state recombination strategy
        # state_recombine_strat = random.choice(PHASE_STATE_RECOMB_STRATS)
        state_recombine_strat = HALF_AND_HALF
        # If the strat is half and half
        if state_recombine_strat == HALF_AND_HALF:
            # Calculate the midpoints of the states, using integer division to handle odd lengths
            self_midpoint = len(self.state) // 2
            partner_midpoint = len(partner.state) // 2
            # Create the new strings by concatenating the appropriate halves
            self.state = self.state[:self_midpoint] + partner.state[partner_midpoint:]
            partner.state = self.state[self_midpoint:] + partner.state[:partner_midpoint]
        # If the strat is zipper
        elif state_recombine_strat == ZIPPER:
            # Combine both strings into a list of characters
            combined = list(self.state + partner.state)
            # Shuffle the combined list to randomize character order
            # random.shuffle(combined)
            # Split the combined list back into two parts, preserving the original lengths
            self.state = ''.join(combined[:len(self.state)])
            partner.state = ''.join(combined[len(partner.state):])
        return (self, partner)

    # Allows for the randomization of the phase
    def apply_entropy(self):
        self.duration = random.randint(MIN_LIGHT_DURATION, MAX_LIGHT_DURATION)
        self.state = ''.join(random.choices(PHASE_STATE_OPTIONS, k=len(self.state)))

    # Allows for easily creating deep copies of a Phase object
    def __deepcopy__(self, memo):
        # If you are already in the memo of the deepcopy, return that instance
        if self in memo:
            return memo[self]
        phase_copy = Phase(attrib={DURATION_ATTR: self.duration, STATE_ATTR: self.state})
        memo[self] = phase_copy
        return phase_copy
    
    # toString for the Phase object
    def __str__(self):
        return f"Phase(duration={self.duration}, state='{self.state}')"

# Represents a Traffic Light Logic
class TLLogic:
    def __init__(self, attrib):
        self.id = attrib['id']
        self.type = attrib['type']
        self.programID = attrib['programID']
        self.offset = attrib['offset']
        self.phases = []
    
    # Add a phase to the TLLogic
    def add_phase(self, phase_element):
        phase = Phase(phase_element.attrib)
        self.phases.append(phase)

    # Mutates an individual 
    def mutate(self,  mutation_rate: 'float'):
        # Check and see if this individual is going to be mutated
        if random.random() <= mutation_rate:
            # Select a random phase to mutate
            random.choice(self.phases).mutate()    
    
    # Recombines a pair of individuals
    def recombine(self, partner: 'TLLogic') -> Tuple['TLLogic', 'TLLogic']:
        # 
        if len(self.phases) != len(partner.phases):
            print("Warning, something is probably wrong. Trying to recombine two TLLogics with differnt sized phases")
            return
        for i in range(len(self.phases) - 1):
            self.phases[i].recombine(partner.phases[i])
        return (self, partner)
    
    # Allows for easily creating deep copies of a TLLogic object
    def __deepcopy__(self, memo):
        # If you are already in the memo of the deepcopy, return that instance
        if self in memo:
            return memo[self]
        tllogic_copy = TLLogic(attrib={'id': self.id, 'type': self.type, 'programID': self.programID, 'offset': self.offset})
        tllogic_copy.phases = deepcopy(self.phases, memo)
        memo[self] = tllogic_copy
        return tllogic_copy

    # toString for the TLLogic object
    def __str__(self):
        phases_str = ', '.join(str(phase) for phase in self.phases)
        return f"TLLogic(id='{self.id}', type='{self.type}', programID='{self.programID}', offset={self.offset}, phases=[{phases_str}])"