import random
from copy import deepcopy
from tllogic_indiv import TLLogic
from typing import List, Tuple

class TLLogicSet:
    def __init__(self, tllogics: List['TLLogic']):
        self.tllogics = tllogics
        self.fitness = 0

    def mutate(self, phase_mutation_rate: 'float'):
        for tllogic in self.tllogics:
            tllogic.mutate(mutation_rate=phase_mutation_rate)
                
    def recombine(self, partner: 'TLLogicSet') -> Tuple['TLLogicSet', 'TLLogicSet']:
        if len(self.tllogics) != len(partner.tllogics):
            print("Warning, something is probably wrong. Trying to recombine two TLLogics Sets with differnt amounts of TLLoigcs")
            return
        for i in range(len(self.tllogics) - 1):
            self.tllogics[i].recombine(partner=partner.tllogics[i])
        return (self, partner)
    
    # Allows for easily creating deep copies of a TLLogicSet object
    def __deepcopy__(self, memo):
        # If you are already in the memo of the deepcopy, return that instance
        if self in memo:
            return memo[self]
        tllogic_set_copy = TLLogicSet(tllogics=deepcopy(self.tllogics, memo))
        tllogic_set_copy.fitness = self.fitness
        memo[self] = tllogic_set_copy
        return tllogic_set_copy
    
    # toString for the TLLogicSet object
    def __str__(self):
        tllogics_str = '\n'.join(str(tllogic) for tllogic in self.tllogics)
        return f"TLLogicSet(tllogics=[{tllogics_str}], fitness={self.fitness})"