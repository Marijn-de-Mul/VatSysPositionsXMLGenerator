import xml.etree.ElementTree as ET
import os
import shutil

if os.path.exists('Output'):
    shutil.rmtree('Output')
os.makedirs('Output')

root = ET.Element('Positions', {
    'xmlns:xsd': 'http://www.w3.org/2001/XMLSchema',
    'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance'
})

icao_regions = {
    'WAH': 'Java',
    'WAR': 'Java',
    'WAD': 'Bali/Nusa Tenggara',
    'WAT': 'Bali/Nusa Tenggara',
    'WAG': 'Kalimantan',
    'WAO': 'Kalimantan',
    'WAL': 'Kalimantan',
    'WAQ': 'Kalimantan',
    'WAA': 'Sulawesi/Maluku',
    'WAW': 'Sulawesi/Maluku',
    'WAF': 'Sulawesi/Maluku',
    'WAM': 'Sulawesi/Maluku',
    'WAE': 'Sulawesi/Maluku',
    'WAP': 'Sulawesi/Maluku',
    'WAK': 'Papua',
    'WAJ': 'Papua',
    'WAY': 'Papua',
    'WAV': 'Papua',
    'WAB': 'Papua',
    'WAS': 'Papua',
    'WAU': 'Papua',
    'WII': 'Java',
    'WIH': 'Java',
    'WIR': 'Java',
    'WIC': 'Java',
    'WIL': 'Java',
    'WIP': 'Sumatra',
    'WIG': 'Sumatra',
    'WIE': 'Sumatra',
    'WIM': 'Sumatra',
    'WIT': 'Sumatra',
    'WID': 'Kalimantan/Islands',
    'WIK': 'Kalimantan/Islands',
    'WIO': 'Kalimantan/Islands'
}

airport_names = {}
runway_headings = {}
runway_lengths = {}
with open('Navdata/Airports.txt', 'r') as file:
    current_icao_code = None
    for line in file:
        fields = line.split(',')
        if fields[0] == 'A':
            current_icao_code = fields[1]
            airport_names[current_icao_code] = fields[2].title()
            runway_headings[current_icao_code] = []
            runway_lengths[current_icao_code] = []
        if fields[0] == 'R' and current_icao_code:
            runway_headings[current_icao_code].append(int(fields[2]))  
            runway_lengths[current_icao_code].append(int(fields[3])) 

files = os.listdir('Input/')

icao_codes = [file[4:-4] for file in files if file.startswith('SMR_') and file.endswith('.xml')]

added_regions = {}
for code in icao_codes:
    region = icao_regions.get(code[:3])  
    if region and region not in added_regions:
        group = ET.SubElement(root, 'Group', {'Name': region})
        added_regions[region] = group

    if region:
        tree = ET.parse(f'Input/SMR_{code}.xml')
        center = tree.find('.//Map').get('Center')

        if code not in runway_headings or not runway_headings[code]:
            raise ValueError(f'Runway heading not found for ICAO code {code}')
        longest_runway_index = runway_lengths[code].index(max(runway_lengths[code])) 
        runway_heading = runway_headings[code][longest_runway_index]  
        rotation = 90 - runway_heading
        if rotation < 0:
            rotation += 360

        if code == 'WIII':
            defaultrange = '4'
        else: 
            defaultrange = '3'

        position = ET.SubElement(added_regions[region], 'Position', {
            'Name': f'{code} {airport_names.get(code, code)}', 
            'Type': 'ASMGCS',
            'ASMGCSAirport': code,
            'DefaultCenter': center,
            'DefaultRange': defaultrange,
            'MagneticVariation': '-1',
            'Rotation': str(rotation)
        })

        maps = ET.SubElement(position, 'Maps')

        map_names = ['BAK', 'HOLES', 'MOVE', 'BLD', 'RWY', 'TWY_CL', 'BAY_CL', 'SB', 'BAY', 'TWY']
        for name in map_names:
            ET.SubElement(maps, 'Map', {'Name': f'{code}/SMR_{code}_{name}'})

tree = ET.ElementTree(root)

ET.indent(tree, space="  ")

with open('Output/Positions.xml', 'wb') as file:
    tree.write(file, encoding='utf-8', xml_declaration=True)