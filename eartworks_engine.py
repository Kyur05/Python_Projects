import pandas as pd
# We import your working bridge from the previous step!
from report_compiler import inject_data_to_word

def process_earthworks(csv_path):
    print(f"\n>> Analyzing Mass Haul Data: {csv_path}...")
    
    # 1. Read the Civil 3D CSV
    df = pd.read_csv(csv_path)
    
    # Clean column names just in case Civil 3D added weird spaces
    df.columns = df.columns.str.strip()
    
    # 2. Grab the absolute last row to get the final cumulative volumes
    final_row = df.iloc[-1]
    
    total_cut = float(final_row['Cum Cut Vol'])
    total_fill = float(final_row['Cum Fill Vol'])
    
    # 3. The Engineering Logic Engine
    net_volume = total_cut - total_fill
    
    if net_volume > 0:
        balance_type = "surplus"
        action = "spoiled at a designated site as per the environmental management plan"
    else:
        balance_type = "shortfall"
        action = "sourced from approved commercial borrow pits"
        
    # 4. Package the data for Word (formatting numbers with commas and 0 decimals)
    project_data = {
        "<<PROJECT_NAME>>": "N2 Section 7 Upgrade: Die Vleie to Swartvlei",
        "<<TOTAL_CUT>>": f"{total_cut:,.0f}",
        "<<TOTAL_FILL>>": f"{total_fill:,.0f}",
        "<<NET_VOLUME>>": f"{abs(net_volume):,.0f}",
        "<<BALANCE_TYPE>>": balance_type,
        "<<ACTION>>": action
    }
    
    print(f"[SUCCESS] Calculated {balance_type} of {abs(net_volume):,.0f} m3.")
    return project_data

if __name__ == "__main__":
    # 1. Crunch the numbers
    earthworks_data = process_earthworks("earthworks_report.csv")
    
    # 2. Fire the Word Compiler
    inject_data_to_word("Report_Template.docx", "N2_Earthworks_Report_Rev1.docx", earthworks_data)