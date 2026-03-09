import csv

# 1. The Setup: Our dictionary and testing machine
max_gradients = {"Class A": 6.0, "Class B": 8.0, "Class C": 10.0}

def evaluate_segment(segment_name, road_class, gradient):
    allowed_limit = max_gradients[road_class]
    actual_slope = abs(gradient)
    
    if actual_slope > allowed_limit:
        return f"❌ FAIL [{segment_name}]: {actual_slope}% exceeds {allowed_limit}% limit."
    return f"✅ PASS [{segment_name}]: {actual_slope}% is acceptable."

print("--- Running Automated Batch Processing ---")

# Variables to keep track of our final report
pass_count = 0
fail_count = 0

# 2. Opening the file in "Read" mode
try:
    with open("survey_data.csv", mode="r") as file:
        
        # 3. The Smart Reader
        csv_reader = csv.DictReader(file)
        
        # 4. The Automation Loop
        for row in csv_reader:
            # Extract data using the exact column headers from the CSV
            name = row["Segment"]
            r_class = row["Class"]
            
            # Convert the CSV text into a decimal number
            grad = float(row["Gradient"])
            
            # Run the machine and print the result
            result = evaluate_segment(name, r_class, grad)
            print(result)
            
            # Tally up the final scores
            if "FAIL" in result:
                fail_count += 1
            else:
                pass_count += 1
                
    print(f"\n📊 FINAL SUMMARY: {pass_count} Passed | {fail_count} Failed")

except FileNotFoundError:
    print("❌ Error: Could not find 'survey_data.csv'. Make sure it is in the same folder!")