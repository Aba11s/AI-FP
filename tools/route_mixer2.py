#!/usr/bin/env python3
import re
import os

def convert_route():
    print("Route File Mixer")
    print(f"Current directory: {os.getcwd()}")
    print("-" * 40)
    
    # Show available .rou.xml files in current directory
    route_files = [f for f in os.listdir() if f.endswith('.rou.xml')]
    if route_files:
        print("Available .rou.xml files:")
        for f in route_files:
            print(f"  {f}")
        print()
    
    input_file = input("Input route file (e.g., data/6l_4w_4p.rou.xml): ").strip()
    
    try:
        with open(input_file, 'r') as f:
            content = f.read()
    except:
        print(f"Error: Cannot read {input_file}")
        print(f"Make sure to include the 'data/' directory if file is there.")
        return
    
    moto_ratio = float(input("Motorcycle ratio (0-1): ") or "0.75")
    car_ratio = 1 - moto_ratio
    
    # Suggest a default output in data/ directory
    basename = os.path.basename(input_file)
    default_output = f"data/{basename.replace('.rou.xml', '_mixed.rou.xml')}"
    output_file = input(f"Output file name (default: {default_output}): ").strip()
    if not output_file:
        output_file = default_output
    
    # Build XML
    xml = '''<?xml version="1.0" encoding="UTF-8"?>
<routes xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/routes_file.xsd">
    
    <vTypeDistribution id="mixedTraffic">
        <vType id="moto" vClass="motorcycle" probability="''' + str(moto_ratio) + '''" lcSublane="10" maxSpeedLat="1" latAlignment="arbitrary"/>
        <vType id="car" vClass="passenger" probability="''' + str(car_ratio) + '''" lcSublane="10" maxSpeedLat="0.6" minGap="1" latAlignment="center"/>
    </vTypeDistribution>
    
'''
    
    # Find all flow elements
    for flow_match in re.finditer(r'<flow\s+([^>]*)/>', content):
        flow_text = flow_match.group(1)
        attrs = dict(re.findall(r'(\w+)="([^"]*)"', flow_text))
        
        # Check if it's the new format with perHour
        if 'perHour' in attrs and 'id' in attrs and 'from' in attrs and 'to' in attrs:
            per_hour = float(attrs['perHour'])
            
            # Keep all attributes except perHour (we'll use vehsPerHour instead)
            flow_id = attrs['id']
            begin = attrs.get('begin', '0')
            end = attrs.get('end', '3600')
            depart_lane = attrs.get('departLane', 'random')
            from_edge = attrs['from']
            to_edge = attrs['to']
            
            xml += f'''    <flow id="{flow_id}" begin="{begin}" end="{end}" vehsPerHour="{per_hour}" departLane="{depart_lane}" type="mixedTraffic">
        <route edges="{from_edge} {to_edge}"/>
    </flow>
'''
        # Fallback for old format (with number and probability)
        elif 'number' in attrs and 'probability' in attrs and 'id' in attrs and 'from' in attrs and 'to' in attrs:
            number = float(attrs.get('number', '0'))
            prob = float(attrs.get('probability', '0'))
            per_hour = number * prob
            
            if per_hour > 0:
                xml += f'''    <flow id="{attrs['id']}" begin="{attrs.get('begin','0')}" end="3600" vehsPerHour="{per_hour}" departLane="{attrs.get('departLane','random')}" type="mixedTraffic">
        <route edges="{attrs['from']} {attrs['to']}"/>
    </flow>
'''
    
    xml += '</routes>'
    
    with open(output_file, 'w') as f:
        f.write(xml)
    
    print(f"Created: {output_file}")
    #print(f"Total flows processed: {len(re.findall(r'<flow\s+([^>]*)/>', content))}")

if __name__ == "__main__":
    convert_route()