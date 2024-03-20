import xml.etree.ElementTree as ET
from tllogic_indiv import TLLogic
from typing import List

def parse_tl_logic(xml_string):
    root = ET.fromstring(xml_string)
    tl_logics = []

    for tl_logic_element in root.findall('.//tlLogic'):
        tl_logic = TLLogic(tl_logic_element.attrib)
        for phase_element in tl_logic_element.findall('phase'):
            tl_logic.add_phase(phase_element)
        tl_logics.append(tl_logic)

    return tl_logics

def write_tl_logic(xml_string, tl_logics: List[TLLogic]):
    root = ET.fromstring(xml_string)

    for tl_logic in tl_logics:
        tl_logic_element = root.find(f".//tlLogic[@id='{tl_logic.id}']")

        # If the tl_logic_element is found
        if tl_logic_element is not None:
            # Create a new tl_logic_element
            new_tl_logic_element = ET.Element('tlLogic', {
                'id': tl_logic.id,
                'type': tl_logic.type,
                'programID': tl_logic.programID,
                'offset': str(tl_logic.offset)
            })
            # For each phase
            for phase in tl_logic.phases:
                # Create and add a phase element
                ET.SubElement(new_tl_logic_element, 'phase', {
                    'duration': str(phase.duration),
                    'state': phase.state
                })
            # Get the index of the origional tl_logic_element
            index = list(root).index(tl_logic_element)
            # Remove the outgoing tl_logic_element
            root.remove(tl_logic_element)
            # Insert the new_tl_logic_element at the index of the old one
            root.insert(index, new_tl_logic_element)

    return ET.tostring(root, encoding='unicode')

# # Example usage
# xml_file = 'traffic_light/network_configs/grid_network_original.net.xml'
# with open(xml_file, 'r') as file:
#     xml_string = file.read()

# tl_logics = parse_tl_logic(xml_string)

# for tl_logic in tl_logics:
#     print(f"TLLogic ID: {tl_logic.id}")
#     print(f"Type: {tl_logic.type}")
#     print(f"Program ID: {tl_logic.programID}")
#     print(f"Offset: {tl_logic.offset}")
#     print("Phases:")
#     for phase in tl_logic.phases:
#         print(f"  Duration: {phase.duration}, State: {phase.state}")
#     print()

# # Modify the TLLogic objects
# tl_logics[0].offset = '10'
# tl_logics[0].phases[0].duration = '50'

# # Write the modified TLLogic objects back to the XML file
# updated_xml_string = write_tl_logic(xml_string, tl_logics)
# with open('traffic_light/network_configs/grid_network_999_modified.net.xml', 'w') as file:
#     file.write(updated_xml_string)