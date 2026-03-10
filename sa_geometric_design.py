import csv
import openpyxl
from openpyxl.styles import Font
import physics_engine
print("=== South African TRH17 Geometric Design Tool ===")
#1. NESTED DICTIONARY: TRH17 Max Gradients
#Structure: {Topography: {Design_Speed: Max Gradient}}
trh17_max_grades = {
    "Flat": {
        120: 4.0,
        100: 5.0,
        80: 6.0
    },
    "Rolling":{
        120: 5.0,
        100: 6.0,
        80:7.0
    },
        "Mountainous":{
            100: 7.0,
            80:8.0,
            60:10.0
          }
    }
#3. NESTED DICTIONARY: TRH17 Min K-Values
#Structure: {Design_Speed: {Curve_Type: Min K-Value}}
trh17_min_k_values = {
    120: {
        "Crest": 80,
        "Sag": 50
    },
    100: {
        "Crest": 50,
        "Sag": 40
    },
    80: {
        "Crest": 30,
        "Sag": 25
    },
    60: {
        "Crest": 20,
        "Sag": 15
    }
}
#4. The Function
def check_sa_gradient(segment_name, topography, design_speed, actual_gradient):
    if topography not in trh17_max_grades:
        return f"ERROR: '{topography}' is not a valid topography type."
    if design_speed not in trh17_max_grades[topography]:
        return f"ERROR: Design speed '{design_speed} km/h' is not valid for {topography} terrain."
    allowed_limit = trh17_max_grades[topography][design_speed]
    actual_slope = abs(actual_gradient)
    if actual_slope > allowed_limit:
        return f"Critical[{segment_name}]: {actual_slope}% exceeds TRH17 limit of {allowed_limit}% for {topography} terrain at {design_speed} km/h."
    else:
        return f"PASS[{segment_name}]: {actual_slope}% is within TRH17 limit of {allowed_limit}% for {topography} terrain at {design_speed} km/h."
  
#5. The Function for K-Values
def check_k_value(curve_name, design_speed, curve_type, actual_k):
    if design_speed not in trh17_min_k_values:
        return f"ERROR: Design speed '{design_speed} km/h' is not valid for K-value checks."
    if curve_type not in trh17_min_k_values[design_speed]:
        return f"ERROR: Curve type '{curve_type}' is not valid. Must be 'Crest' or 'Sag'."
    min_k = trh17_min_k_values[design_speed][curve_type]
    if actual_k < min_k:
        return f"Critical[{curve_name}]: K-value of {actual_k} is below TRH17 minimum of {min_k} for {curve_type} curve at {design_speed} km/h."
    else:
        return f"PASS[{curve_name}]: K-value of {actual_k} meets TRH17 minimum of {min_k} for {curve_type} curve at {design_speed} km/h."

import xml.etree.ElementTree as ET
import openpyxl
from openpyxl.styles import Font

# --- THE ADVANCED LANDXML TO EXCEL AUTOMATION ENGINE ---
def process_landxml_to_excel(xml_file, speed, topo):
    print(f"\n🚀 Processing {xml_file} with advanced TRH17 Physics Engine...")
    output_filename = "N2_Master_Geometric_Report.xlsx"

    # 1. Setup the Multi-Sheet Excel Workbook
    wb = openpyxl.Workbook()
    
    # --- SHEET 1: VERTICAL DESIGN & DRAINAGE ---
    ws_vert = wb.active
    ws_vert.title = "Vertical Checks"
    vert_headers = ["PVI CH", "PVI Elev", "G1 (%)", "G2 (%)", "Length", "Curve Type", "K-Value", "BVC CH", "EVC CH", "Turn CH (Drain)", "Turn Elev", "Req SSD (m)"]
    ws_vert.append(vert_headers)
    for cell in ws_vert[1]: cell.font = Font(bold=True)

    # --- SHEET 2: HORIZONTAL DESIGN & CHORDS ---
    ws_horiz = wb.create_sheet(title="Horizontal Checks")
    horiz_headers = ["Element", "Radius (m)", "Length", "TRH17 Min R", "Req Superelev (%)", "Status", "20m Survey Chords"]
    ws_horiz.append(horiz_headers)
    for cell in ws_horiz[1]: cell.font = Font(bold=True)

    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        vert_points = []
        curve_count = 1

        # 2. Extract Raw Coordinates
        for element in root.iter():
            clean_tag = element.tag.split('}')[-1]
            
            # --- HORIZONTAL PROCESSING ---
            if clean_tag == 'Curve':
                radius_str = element.get('radius')
                length_str = element.get('length')
                
                if radius_str and length_str:
                    radius = abs(float(radius_str))
                    length = float(length_str)
                    
                    # Call the Physics Engine!
                    horiz_data = physics_engine.calculate_horizontal_parameters(speed, radius)
                    chords = physics_engine.calculate_setting_out_chords(radius, length)
                    
                    # Join the surveyor chords into a readable string (e.g., "30.1, 30.1, 15.2")
                    chord_string = ", ".join(map(str, chords))
                    
                    ws_horiz.append([
                        f"Curve {curve_count}", f"{radius:.2f}", f"{length:.2f}", 
                        horiz_data['R_min_required'], horiz_data['e_required_percent'], 
                        horiz_data['status'], chord_string
                    ])
                    curve_count += 1

            # --- VERTICAL EXTRACTION ---
            elif clean_tag in ['PVI', 'ParaCurve']:
                if element.text and element.text.strip():
                    data = element.text.strip().split()
                    chainage = float(data[0])
                    elev = float(data[1])
                    length = float(element.get('length', 0)) if clean_tag == 'ParaCurve' else 0
                    vert_points.append({'chainage': chainage, 'elev': elev, 'length': length, 'tag': clean_tag})
        
        # --- VERTICAL PROCESSING ---
        for i in range(1, len(vert_points) - 1):
            prev_pt = vert_points[i-1]
            curr_pt = vert_points[i]
            next_pt = vert_points[i+1]

            dx1 = curr_pt['chainage'] - prev_pt['chainage']
            dy1 = curr_pt['elev'] - prev_pt['elev']
            g1 = (dy1 / dx1 * 100) if dx1 != 0 else 0

            dx2 = next_pt['chainage'] - curr_pt['chainage']
            dy2 = next_pt['elev'] - curr_pt['elev']
            g2 = (dy2 / dx2 * 100) if dx2 != 0 else 0

            # Calculate Stopping Sight Distance for the approaching gradient
            ssd = physics_engine.calculate_ssd(speed, g1)

            if curr_pt['tag'] == 'ParaCurve':
                # Call the Physics Engine for Vertical Geometry!
                v_data = physics_engine.calculate_vertical_geometry(curr_pt['chainage'], curr_pt['elev'], g1, g2, curr_pt['length'])
                
                ws_vert.append([
                    f"{curr_pt['chainage']:.2f}", f"{curr_pt['elev']:.2f}", f"{g1:.2f}", f"{g2:.2f}", 
                    curr_pt['length'], v_data['Curve_Type'], v_data['K_Value'], 
                    v_data['BVC_CH'], v_data['EVC_CH'], v_data['Turn_CH'], v_data['Turn_Elev'], ssd
                ])
            else:
                ws_vert.append([
                    f"{curr_pt['chainage']:.2f}", f"{curr_pt['elev']:.2f}", f"{g1:.2f}", f"{g2:.2f}", 
                    "-", "Tangent", "-", "-", "-", "-", "-", ssd
                ])

        # 3. Save the Master Report
        wb.save(output_filename)
        print(f"✅ Advanced Master Report Successfully Generated: {output_filename}")

    except FileNotFoundError:
        print(f"❌ ERROR: Could not find '{xml_file}'.")

if __name__ == "__main__":
    # Process the N2 LandXML file at 120 km/h in Rolling terrain
    process_landxml_to_excel("road_export.xml", 120, "Rolling")