import csv
print("=== Highway Alignment Design Tool ===")
#1. Dictionary: Storing our Design Standards
# Syntax; {"Key": Value}
max_gradients = {
    "Class A": 6.0,
    "Class B": 8.0,
    "Class C": 10.0
}
#2. Function: A resuable tool that takes 3 specific inputs
def evaluate_segment(segment_name, road_class, gradient):
    #We look up the max allowed gradient using the road_class input
    allowed_limit = max_gradients[road_class]
    #We use abs() to handle steep downhill segments
    actual_slope = abs(gradient)
    #3. Logic: COMPARE ACTUAL VS ALLOWED
    if actual_slope > allowed_limit:
        return f"FAIL[{segment_name}]: {actual_slope}% exceeds the {allowed_limit}% limit for {road_class}"
    else:
        return f"PASS[{segment_name}]: {actual_slope}% is within the {allowed_limit}% limit for {road_class}"

#4. LIST OF DICTIONARIES: Organising complex survey data
# Each dictionary represents one specific road segment
project_segments = [
    {"name":"N2 Northbound", "class": "Class A", "gradient":4.5},
    {"name": "M4 uMhlanga Offramp", "class": "Class C", "gradient": -11.2},
    {"name": "Coastal Access Rd", "class": "Class B", "gradient": 8.5}
]
print("\n--- Generating Alignment Report ---")
#5. THE AUTOMATION LOOP
for segment in project_segments:
    # We pull the specific data points out of each dictionary
    s_name = segment["name"]
    s_class = segment["class"]
    s_gradient = segment["gradient"]
    #6. THE EXECUTION: We feed those points into our custom function
    report_line = evaluate_segment(s_name, s_class, s_gradient)
    print(report_line)
    
print("\n--- Interactive Design Check ---")
print("Type 'exit' as the segment name to close the tool.")
#1. The Loop
while True:
    custom_name = input("\nEnter segment name (or 'exit'):")
    if custom_name.lower() == "exit":
        print("Exiting the tool. Goodbye!")
        break
    custom_class = input("Enter road class (Class A, Class B, Class C):")
    custom_gradient_test = input("Enter gradient percentage (e.g., -5.0 or 7.5):")
    try:
        custom_gradient = float(custom_gradient_test)
        custom_result = evaluate_segment(custom_name, custom_class, custom_gradient)
        print("--- Custom Report---")
        print(custom_result)
        with open("design_checks.csv", mode="a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([custom_name, custom_class, custom_gradient, custom_result])
    except ValueError:
        print("Invalid input for gradient. Please enter a numeric value.")