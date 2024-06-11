
# Function to get organization name from organization number
def get_org_name(orgnr):
    url = f'https://data.brreg.no/enhetsregisteret/api/enheter/{orgnr}'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data.get('navn', 'Unknown')
    else:
        return 'Not Found'

# Check if all three ID columns are non-empty before making the API call
def fetch_name_if_valid(row):
    if pd.notna(row['ID1']) and pd.notna(row['ID2']) and pd.notna(row['ID3']):
        return get_org_name(row['Organization Number'])
    else:
        return 'N/A'

# Apply the function to get organization names for valid rows
df['Organization Name'] = df.apply(fetch_name_if_valid, axis=1)

# Display the updated dataframe
print(df)

# Save the updated dataframe to a new CSV file
df.to_csv('suspects_with_names_filtered.csv', index=False)
