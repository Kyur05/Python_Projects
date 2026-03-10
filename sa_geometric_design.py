import csv
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
#2. The Function
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
#3. TESTING THE FUNCTION
print("\n--- Running TRH17 Standard Checks ---")
test_segments = [
    {"name": "Segment 1", "topography": "Flat", "speed": 120, "gradient": 3.5},
    {"name": "Segment 2", "topography": "Rolling", "speed": 100, "gradient": 6.5},
    {"name": "Segment 3", "topography": "Mountainous", "speed": 80, "gradient": 9.0},
    {"name": "Segment 4", "topography": "Flat", "speed": 80, "gradient": 7.0},
    {"name": "Segment 5", "topography": "Rolling", "speed": 120, "gradient": -5.0}
]
for seg in test_segments:
    result = check_sa_gradient(seg["name"], seg["topography"], seg["speed"], seg["gradient"])
    print(result)

#4. TRH17 Minimum K-Values for Vertical Curves Check
# Structure: {Design_Speed: {"Crest": Min_}}
trh17_min_k_values = {
    120: {"Crest": 113, "Sag": 57},
    100: {"Crest": 94, "Sag": 37},
    80: {"Crest": 11, "Sag": 15}    
}
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
#6. Testing K-Value Function
print("\n--- Running TRH17 K-Value Checks ---")
print(check_k_value("Curve 1", 120, "Crest", 100))
print(check_k_value("Curve 2", 100, "Sag", 40))
print(check_k_value("Curve 3", 80, "Crest", 15))

# --- THE BATCH PROCESSOR ---
def process_survey_data(file_name):
    print(f"\n📂 Reading {file_name}...")
    output_filename = "TRH17_Design_Report.csv"

    # We open BOTH files on a single line to prevent indentation nightmares
    with open(file_name, mode="r") as infile, open(output_filename, mode="w", newline="") as outfile:
        
        reader = csv.DictReader(infile)
        
        # This dynamically grabs the exact headers from your CSV and adds our two new columns!
        fieldnames = reader.fieldnames + ["Gradient_Report", "K_Value_Report"]
        
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for row in reader:
            # Extract data using the exact CSV headers (with underscores)
            seg_name = row["Chainage"]
            topo = row["Topography"]
            curve = row["Curve_Type"]
            speed = int(row["Design_Speed"])
            grad = float(row["Gradient"])
            k_val = float(row["K_Value"])
            
            # Feed the data into your existing TRH17 machines
            grad_result = check_sa_gradient(seg_name, topo, speed, grad)
            k_result = check_k_value(seg_name, speed, curve, k_val)
            
            # Add the new reports directly into the row dictionary
            row["Gradient_Report"] = grad_result
            row["K_Value_Report"] = k_result
            
            # Write the updated row
            writer.writerow(row)
            
    print(f"✅ Batch complete! Saved as: {output_filename}")
print("\n=== TRH17 Master Evaluator (Interactive) ===")
while True:
    seg_name = input("\nEnter Segment or Curve Name(or type 'exit' to quit):")
    if seg_name.lower() == 'exit':
        print("Exiting TRH17 Evaluator. Goodbye!")
        break
    topography = input("Enter Topography (Flat, Rolling, Mountainous): ")
    curve = input("Enter Curve Type (Crest or Sag): ")
    try:
        speed = int(input("Enter Design Speed in km/h (120, 100, 80, 60): "))
        grad = float(input("Enter actual gradient percentage (e.g., -5.0 or 7.5): "))
        k_val = float(input("Enter actual K-Value (e.g., 150.5): "))
        gradient_result = check_sa_gradient(seg_name, topography, speed, grad)
        k_value_result = check_k_value(seg_name, speed, curve, k_val)
        print("\n--- TRH17 Evaluation Results ---")
        print(gradient_result)
        print(k_value_result)
    except ValueError:
        print("Invalid input. Please enter numeric values for speed, gradient, and K-value.") 
process_survey_data("survey_export.csv")  