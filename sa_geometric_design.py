import csv
import openpyxl
from openpyxl.styles import Font
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

# --- THE LANDXML TO EXCEL AUTOMATION ENGINE ---
def process_landxml_to_excel(xml_file, speed, topo):
    print(f"\n🚀 Processing {xml_file} and calculating TRH17 Compliance...")
    output_filename = "N2_TRH17_Master_Report.xlsx"

    # 1. Setup the Blank Excel Report
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Vertical Alignment Checks"
    
    headers = ["Chainage", "Element", "Length (m)", "G1 (%)", "G2 (%)", "K-Value", "Curve Type", "TRH17 Status"]
    ws.append(headers)
    for cell in ws[1]: cell.font = Font(bold=True)

    try:
        # 2. Extract Raw Coordinates from Civil 3D
        tree = ET.parse(xml_file)
        root = tree.getroot()
        points = []

        for element in root.iter():
            clean_tag = element.tag.split('}')[-1]
            if clean_tag in ['PVI', 'ParaCurve']:
                if element.text and element.text.strip():
                    data = element.text.strip().split()
                    chainage = float(data[0])
                    elev = float(data[1])
                    length = float(element.get('length', 0)) if clean_tag == 'ParaCurve' else 0
                    
                    points.append({'chainage': chainage, 'elev': elev, 'length': length, 'tag': clean_tag})

        # 3. Calculate Engineering Math & Run TRH17 Checks
        for i in range(1, len(points) - 1):
            prev_pt = points[i-1]
            curr_pt = points[i]
            next_pt = points[i+1]

            # Calculate entering (G1) and exiting (G2) gradients
            dx1 = curr_pt['chainage'] - prev_pt['chainage']
            dy1 = curr_pt['elev'] - prev_pt['elev']
            g1 = (dy1 / dx1 * 100) if dx1 != 0 else 0

            dx2 = next_pt['chainage'] - curr_pt['chainage']
            dy2 = next_pt['elev'] - curr_pt['elev']
            g2 = (dy2 / dx2 * 100) if dx2 != 0 else 0

            # 4. Evaluate Curves vs Tangents
            if curr_pt['tag'] == 'ParaCurve':
                A = abs(g2 - g1)
                k_val = curr_pt['length'] / A if A != 0 else 0
                curve_type = "Crest" if g1 > g2 else "Sag"

                # Run your TRH17 Curve Machine
                status = check_k_value(f"CH {curr_pt['chainage']:.0f}", speed, curve_type, k_val)
                ws.append([f"{curr_pt['chainage']:.2f}", "Curve", curr_pt['length'], f"{g1:.2f}", f"{g2:.2f}", f"{k_val:.2f}", curve_type, status])
            
            else:
                # Run your TRH17 Tangent Machine
                status = check_sa_gradient(f"CH {curr_pt['chainage']:.0f}", topo, speed, g1)
                ws.append([f"{curr_pt['chainage']:.2f}", "Tangent", "-", f"{g1:.2f}", "-", "-", "-", status])

        # 5. Save the finished report
        wb.save(output_filename)
        print(f"✅ Excel Report Successfully Generated: {output_filename}")

    except FileNotFoundError:
        print(f"❌ ERROR: Could not find '{xml_file}'.")

# --- THE CORRECTION ---
# Make sure this 'if' statement is pushed tight against the left wall!
if __name__ == "__main__":
    # Process the N2 LandXML file at 120 km/h in Rolling terrain
    process_landxml_to_excel("road_export.xml", 120, "Rolling")