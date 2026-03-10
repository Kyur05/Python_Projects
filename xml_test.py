import xml.etree.ElementTree as ET

def extract_vertical_geometry(file_name):
    print(f"\n📐 Extracting Vertical Geometry from {file_name}...")
    
    try:
        tree = ET.parse(file_name)
        root = tree.getroot()
        
        found_data = False
        
        # Brute-force search through EVERY element in the entire file
        for element in root.iter():
            
            # Strip away the messy Autodesk "{http://www.landxml.org...}" namespace link
            clean_tag = element.tag.split('}')[-1]
            
            if clean_tag in ['PVI', 'ParaCurve']:
                found_data = True
                
                # Check if there is actual text inside the tag to prevent crashes
                if element.text and element.text.strip():
                    # Split the space between the chainage and elevation
                    data = element.text.strip().split()
                    chainage = float(data[0])
                    elevation = float(data[1])
                    
                    if clean_tag == 'ParaCurve':
                        # Grab the curve length attribute
                        curve_len = float(element.get('length', 0))
                        print(f"Curve | Chainage: {chainage:8.2f} | Elev: {elevation:8.2f} | Length: {curve_len}")
                    else:
                        print(f"PVI   | Chainage: {chainage:8.2f} | Elev: {elevation:8.2f}")

        if not found_data:
            print("⚠️ No vertical data found. Civil 3D may have exported a flat 2D alignment.")
                            
    except FileNotFoundError:
        print(f"❌ ERROR: Could not find '{file_name}'.")

extract_vertical_geometry("road_export.xml")