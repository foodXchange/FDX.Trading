import pandas as pd

# Load the supplier data
file_path = r'C:\Users\foodz\Desktop\FoodXchange\Suppliers 24_7_2025.csv'
df = pd.read_csv(file_path)

# Prepare output
output = []
output.append('First 5 rows:')
output.append(df.head().to_string())
output.append('\nColumn names:')
output.append(str(df.columns.tolist()))

# Write to a text file
with open('view_suppliers_output.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(output)) 