# utils/traffic_generator_universal.py
import random
import xml.etree.ElementTree as ET
from pathlib import Path
import sumolib
import os

def detect_intersection_edges(network_filename):
    """Automatically detect incoming and outgoing edges for any intersection"""
    project_root = Path(__file__).parent.parent
    net_path = project_root / "data" / "networks" / network_filename
    
    # Fix: Convert to absolute path and ensure it exists
    net_path = net_path.resolve()
    
    if not net_path.exists():
        print(f"❌ Network file not found: {net_path}")
        return [], []
    
    print(f"📁 Loading network from: {net_path}")
    
    try:
        # Fix: Use the file path directly, sumolib should handle it
        net = sumolib.net.readNet(str(net_path))
        
        incoming_edges = []
        outgoing_edges = []
        
        # Find traffic light nodes (intersections)
        tls_found = 0
        for node in net.getNodes():
            if node.getType() == "traffic_light":
                tls_found += 1
                print(f"🚦 Found traffic light: {node.getID()}")
                
                # Get edges that lead INTO this intersection
                for edge in node.getIncoming():
                    if not edge.isSpecial():
                        edge_id = edge.getID()
                        if edge_id not in incoming_edges:
                            incoming_edges.append(edge_id)
                            print(f"  ↪️ Incoming: {edge_id} ({edge.getLaneNumber()} lanes)")
                
                # Get edges that lead OUT of this intersection
                for edge in node.getOutgoing():
                    if not edge.isSpecial():
                        edge_id = edge.getID()
                        if edge_id not in outgoing_edges:
                            outgoing_edges.append(edge_id)
                            print(f"  ↪️ Outgoing: {edge_id} ({edge.getLaneNumber()} lanes)")
        
        if tls_found == 0:
            print("⚠️  No traffic lights found! Looking for any connected edges...")
            # Fallback: get any edges that are connected
            for edge in net.getEdges():
                if not edge.isSpecial() and len(edge.getOutgoing()) > 0:
                    edge_id = edge.getID()
                    if edge_id not in incoming_edges:
                        incoming_edges.append(edge_id)
                    # Get outgoing edges from connections
                    for conn in edge.getOutgoing():
                        out_edge = conn.getTo()
                        if not out_edge.isSpecial():
                            out_id = out_edge.getID()
                            if out_id not in outgoing_edges:
                                outgoing_edges.append(out_id)
            
            print(f"  ↪️ Found {len(incoming_edges)} incoming, {len(outgoing_edges)} outgoing edges")
        
        return incoming_edges, outgoing_edges
        
    except Exception as e:
        print(f"❌ Error reading network: {e}")
        return [], []

def generate_universal_traffic(network_filename, output_filename="jakarta_traffic"):
    """Generate traffic that works for ANY intersection"""
    project_root = Path(__file__).parent.parent
    routes_path = project_root / "data" / "routes" / f"{output_filename}.rou.xml"
    
    # Auto-detect edges for this specific network
    print("🔍 Analyzing network structure...")
    incoming_edges, outgoing_edges = detect_intersection_edges(network_filename)
    
    if not incoming_edges or not outgoing_edges:
        print("❌ No suitable edges found for traffic generation!")
        print("💡 Try opening the network in SUMO-GUI to check if it loaded properly")
        return None
    
    print(f"✅ Found {len(incoming_edges)} incoming edges, {len(outgoing_edges)} outgoing edges")
    
    # Create routes directory if it doesn't exist
    routes_path.parent.mkdir(parents=True, exist_ok=True)
    
    root = ET.Element("routes")
    
    # Define vehicle types
    car_type = ET.SubElement(root, "vType")
    car_type.set("id", "car")
    car_type.set("accel", "2.6")
    car_type.set("decel", "4.5")
    car_type.set("sigma", "0.5")
    car_type.set("length", "4.5")
    car_type.set("maxSpeed", "13.89")
    car_type.set("color", "1,0,0")
    
    moto_type = ET.SubElement(root, "vType")
    moto_type.set("id", "motorcycle")
    moto_type.set("vClass", "motorcycle")
    moto_type.set("accel", "3.0")
    moto_type.set("decel", "7.5")
    moto_type.set("sigma", "0.8")
    moto_type.set("length", "2.0")
    moto_type.set("maxSpeed", "13.89")
    moto_type.set("lcStrategic", "1.0")
    moto_type.set("lcSpeedGain", "2.0")
    moto_type.set("maxSpeedLat", "1.5")
    moto_type.set("latAlignment", "compact")
    moto_type.set("color", "0,0,1")
    
    vehicle_id = 0
    routes_created = 0
    
    # Generate routes from any incoming edge to any outgoing edge
    for from_edge in incoming_edges:
        for to_edge in outgoing_edges:
            # Skip if it's basically the same edge (simple check)
            if from_edge != to_edge:
                # Create route
                route = ET.SubElement(root, "route")
                route.set("id", f"route_{routes_created}")
                route.set("edges", f"{from_edge} {to_edge}")
                routes_created += 1
    
    print(f"🛣️ Created {routes_created} possible routes")
    
    if routes_created == 0:
        print("❌ No valid routes could be created!")
        return None
    
    # Now generate vehicles using these routes
    vehicles_to_generate = min(50, routes_created * 3)  # Start with fewer vehicles
    
    for i in range(vehicles_to_generate):
        # Choose random route
        route_id = f"route_{random.randint(0, routes_created - 1)}"
        
        # 75% motorcycles, 25% cars (Jakarta ratio)
        vtype = "motorcycle" if random.random() < 0.75 else "car"
        
        # Create vehicle
        vehicle = ET.SubElement(root, "vehicle")
        vehicle.set("id", f"veh_{vehicle_id}")
        vehicle.set("type", vtype)
        vehicle.set("route", route_id)
        vehicle.set("depart", str(random.uniform(0, 300)))  # Stagger over 5 minutes
        
        vehicle_id += 1
    
    # Write the XML file
    tree = ET.ElementTree(root)
    ET.indent(tree, space="  ", level=0)
    
    with open(routes_path, 'wb') as f:
        tree.write(f, encoding='utf-8', xml_declaration=True)
    
    print(f"✅ Generated universal traffic: {routes_path}")
    print(f"   - Total vehicles: {vehicle_id}")
    print(f"   - Motorcycles: ~75%, Cars: ~25%")
    print(f"   - Based on {routes_created} possible routes")
    
    return routes_path

def create_simple_test_config(network_file, route_file):
    """Create a simple config file for testing"""
    project_root = Path(__file__).parent.parent
    config_path = project_root / "data" / "configs" / "test_simulation.sumocfg"
    
    config_content = f"""<configuration>
    <input>
        <net-file value="data/networks/{network_file}"/>
        <route-files value="data/routes/{route_file}"/>
    </input>
    <time>
        <begin value="0"/>
        <end value="600"/>
    </time>
    <processing>
        <lateral-resolution value="0.5"/>
    </processing>
</configuration>"""
    
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(config_path, 'w') as f:
        f.write(config_content)
    
    print(f"✅ Created test config: {config_path}")
    return config_path

if __name__ == "__main__":
    network_file = input("Enter network filename (e.g., central_jakarta.net.xml): ").strip()
    
    # Generate traffic
    route_file = generate_universal_traffic(network_file)
    
    if route_file:
        # Create config
        config_file = create_simple_test_config(network_file, route_file.name)
        
        print(f"\n🎉 Ready to test! Run:")
        print(f"sumo-gui -c {config_file}")