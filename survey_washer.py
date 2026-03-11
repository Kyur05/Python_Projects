import pandas as pd
import sys

def wash_survey_data(input_csv):
    print(f"\n>> Washing raw surveyor data: {input_csv}...")
    df = pd.read_csv(input_csv, header=None)
    clean_df = pd.DataFrame()
    clean_df['Point'] = df[13].fillna(pd.Series(df.index)).astype(int)

    clean_df['Northing'] = df[2] * -1
    clean_df['Easting'] = df[1] * -1
    clean_df['Elevation'] = df[3]
    clean_df['Description'] = df[14]

    output_name = input_csv.replace(".csv", "_Cleaned_PNEZD.csv")
    clean_df.to_csv(output_name, index=False, header=False)
    print(f"Cleaned data saved to: {output_name}")

if __name__ == "__main__":
    # If the engineer drops a file on the script, use that. Otherwise, test the hardcoded one.
    if len(sys.argv) > 1:
        wash_survey_data(sys.argv[1])
    else:
        wash_survey_data("08_ PS1830 DTM Points.csv")