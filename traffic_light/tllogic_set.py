import random
from copy import deepcopy
from tllogic_indiv import TLLogic
from typing import List, Tuple

class TLLogicSet:
    def __init__(self, tllogics: List['TLLogic'] = None):
        self.tllogics = tllogics
        self.fitness = 0
        self.stairstep_fitness_normalized = 0
        self.random_fitness_normalized = 0
        self.stairstep_cars_teleported = 0
        self.random_cars_teleported = 0
        self.penalty = 0

    def mutate(self, phase_mutation_rate: 'float'):
        for tllogic in self.tllogics:
            tllogic.mutate(mutation_rate=phase_mutation_rate)
                
    # def recombine(self, partner: 'TLLogicSet') -> Tuple['TLLogicSet', 'TLLogicSet']:
    #     if len(self.tllogics) != len(partner.tllogics):
    #         print("Warning, something is probably wrong. Trying to recombine two TLLogics Sets with differnt amounts of TLLoigcs")
    #         return
    #     for i in range(len(self.tllogics) - 1):
    #         self.tllogics[i].recombine(partner=partner.tllogics[i])
    #     return (self, partner)

    def recombine(self, partner: 'TLLogicSet') -> Tuple['TLLogicSet', 'TLLogicSet']:
        # Create copies to manipulate
        self_copy = deepcopy(self)
        partner_copy = deepcopy(partner)
        # Create dictionaries to store the TLLogics for each TLLogicSet
        self_tllogics_dict = {tllogic.id: tllogic for tllogic in self_copy.tllogics}
        partner_tllogics_dict = {tllogic.id: tllogic for tllogic in partner_copy.tllogics}

        # Find the common junctions between self and partner
        common_junctions = list(set(tllogic.id[0] for tllogic in self_copy.tllogics) & set(tllogic.id[0] for tllogic in partner_copy.tllogics))

        # Randomly select junctions to swap
        num_swaps = random.randint(1, len(common_junctions))
        junctions_to_swap = random.sample(common_junctions, num_swaps)

        # Swap the TLLogics for the selected junctions
        for junction in junctions_to_swap:
            self_junction_tllogics = [tllogic.id for tllogic in self_copy.tllogics if tllogic.id.startswith(junction)]
            partner_junction_tllogics = [tllogic.id for tllogic in partner_copy.tllogics if tllogic.id.startswith(junction)]

            for self_tllogic_id, partner_tllogic_id in zip(self_junction_tllogics, partner_junction_tllogics):
                self_tllogics_dict[self_tllogic_id], partner_tllogics_dict[partner_tllogic_id] = (
                    partner_tllogics_dict[partner_tllogic_id], self_tllogics_dict[self_tllogic_id]
                )

        # Update the TLLogics in each TLLogicSet
        self_copy.tllogics = list(self_tllogics_dict.values())
        partner_copy.tllogics = list(partner_tllogics_dict.values())

        return self_copy, partner_copy
    
    # Allows for easily creating deep copies of a TLLogicSet object
    def __deepcopy__(self, memo):
        # If you are already in the memo of the deepcopy, return that instance
        if id(self) in memo:
            return memo[id(self)]
        # Get the desired class
        cls = self.__class__
        # Initialize a new instance
        tllogic_set_copy = cls.__new__(cls)
        # Copy the attributes
        for k, v in self.__dict__.items():
            setattr(tllogic_set_copy, k, deepcopy(v, memo))
        # Populate memo to help prevent over-copying
        memo[id(self)] = tllogic_set_copy
        # Return the fresh deep copy
        return tllogic_set_copy
    
    # toString for the TLLogicSet object
    def __str__(self):
        tllogics_str = '\n'.join(str(tllogic) for tllogic in self.tllogics)
        return f"TLLogicSet(tllogics=[{tllogics_str}], fitness={self.fitness})"