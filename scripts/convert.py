import pandas as pd
import os

def convert_xlsx_to_csv(xlsx_filename, csv_filename):
    
    # Construct full paths
    input_path = os.path.join('..', 'data', 'raw', xlsx_filename)
    output_path = os.path.join('..', 'data', 'raw', csv_filename)
    
    try:
        # Read the Excel file
        df = pd.read_excel(input_path)
        
        # Save it as a CSV file, without the pandas index column
        df.to_csv(output_path, index=False, encoding='utf-8')
        
        print(f"Successfully converted '{xlsx_filename}' to '{csv_filename}'")
    except FileNotFoundError:
        print(f"Error: The file '{xlsx_filename}' was not found in the 'data/raw' directory.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # Convert the O*NET files
    convert_xlsx_to_csv('Skills.xlsx', 'onet_skills.csv')
    convert_xlsx_to_csv('Occupation Data.xlsx', 'onet_occupations.csv')