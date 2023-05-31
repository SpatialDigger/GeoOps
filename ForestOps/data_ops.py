import pandas as pd
import json


def add_data(organisation, key, url, year):
    file_path = "ForestOps/data.json"
    # Load existing data from the JSON file
    with open(file_path, 'r') as f:
        data = json.load(f)

    # Check if the organization already exists in the data
    if organisation in data['api']:
        # Check if the key already exists in the organization
        if key in data['api'][organisation]:
            # Check if the year is different from the existing key
            if str(year) in data['api'][organisation][key]:
                print(f"The key '{key}' already exists in the organization '{organisation}' for the year {year}.")
                return

            # Add the new year and URL to the existing key
            data['api'][organisation][key][str(year)] = url
        else:
            # Add the new key, URL, and year to the organization
            data['api'][organisation][key] = {
                str(year): url
            }
    else:
        # Create a new organization and add the key, URL, and year
        data['api'][organisation] = {
            key: {
                str(year): url
            }
        }

    # Write the updated data back to the JSON file
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)

    print("Data added successfully!")


# # Usage example
# file_path = "ForestOps/data.json"
# add_data(file_path, "Natural England", "Ancient Woodland England", "https://example.com/ancient-woodland-2023", 2023)
#
# # Usage example
# add_data("Natural England", "Another Key", "https://example.com/another-key", 2023)


def flatten_json(data, prefix='', rows=None, level=0):
    if rows is None:
        rows = []

    if isinstance(data, dict):
        for key, value in data.items():
            new_prefix = prefix + '_' + key if prefix else key

            if isinstance(value, dict):
                flatten_json(value, prefix=new_prefix, rows=rows, level=level + 1)
            else:
                rows.append([level, new_prefix, value])
    elif isinstance(data, list):
        for i, value in enumerate(data):
            new_prefix = prefix + '_' + str(i) if prefix else str(i)

            if isinstance(value, (dict, list)):
                flatten_json(value, prefix=new_prefix, rows=rows, level=level + 1)
            else:
                rows.append([level, new_prefix, value])

    return rows

def data_sources():
    file_path = "ForestOps/data.json"
    # Load the JSON data
    with open(file_path) as f:
        data = json.load(f)

    # Flatten the nested JSON
    rows = flatten_json(data)

    # Create a DataFrame from the rows
    df = pd.DataFrame(rows, columns=['Level', 'Key', 'Source'])

    # Split the Key column into separate columns
    df[['Source_type', 'Organisation', 'Layer', 'Year']] = df['Key'].str.split('_', expand=True)

    # Reorder the DataFrame columns
    df = df[['Source_type', 'Organisation', 'Layer', 'Year', 'Source']]

    # Sort the DataFrame by organisation, layer, and year
    df = df.sort_values(['Organisation', 'Layer', 'Year'], ascending=[True, True, True])

    # Reset the index of the DataFrame
    df = df.reset_index(drop=True)

    # Return the DataFrame
    return df


# Usage example
# file_path = "ForestOps/data.json"
# df = display_data_as_dataframe(file_path)
# print(df)


# Usage example
# df = display_data_as_dataframe()
# print(df)
