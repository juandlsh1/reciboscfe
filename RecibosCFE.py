import os
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer
import pandas as pd

data_dict = {}  # Dictionary to store data

common_key_names = {
    0: "Company Name",
    5: "Service Number",
    6: "Billing Period",
    16: "kWh base",
    17: "kWh intermedia",
    18: "kWh punta",
    19: "kW base",
    20: "kW intermedia",
    21: "kW punta"
}

# Iterate through all files in the current directory
for filename in os.listdir():
    if filename.endswith(".pdf"):
        pdf_file = filename
        whole_data = []  # List to store data from the current PDF

        for page_layout in extract_pages(pdf_file, page_numbers=None, maxpages=1, caching=True, laparams=None):
            data = {}
            i = 0  # Initialize i for each page

            for element in page_layout:
                if isinstance(element, LTTextContainer) and i in common_key_names:
                    key = common_key_names[i]
                    data[key] = element.get_text().replace("\n", ' ')
                i += 1  # Increment i for each element

            whole_data.append(data)  # Append the data from the current page to whole_data

        data_dict[pdf_file] = whole_data  # Store the data from the current PDF in data_dict

# Create an empty DataFrame
df = pd.DataFrame(columns=['PDF File', 'Billing Period', 'kWh', 'kW'])

# Iterate through the data_dict and extract 'Billing Period', 'kWh', and 'kW'
for pdf_file, data_list in data_dict.items():
    for data in data_list:
        if 'Billing Period' in data and 'kWh' in data and 'kW' in data:
            # Remove commas, split the 'kWh' and 'kW' values, and convert them to float
            kWh_values = [float(value.replace(',', '')) for value in data['kWh'].split()]
            kW_values = [float(value.replace(',', '')) for value in data['kW'].split()]

            # Create a new DataFrame for the current PDF data
            pdf_data = pd.DataFrame({'PDF File': pdf_file,
                                      'Billing Period': data['Billing Period'],
                                      'kWh': kWh_values,
                                      'kW': kW_values})

            # Concatenate the new DataFrame to the main DataFrame
            df = pd.concat([df, pdf_data], ignore_index=True)

# Group by 'Billing Period' and 'PDF File', and sum the 'kWh' and 'kW' values
df_grouped = df.groupby(['Billing Period', 'PDF File']).sum().reset_index()

# Display the DataFrame
df.to_csv("cfe.csv")



