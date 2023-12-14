import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Read the data
war_data = pd.read_csv('/Users/aly.milne/Library/CloudStorage/OneDrive-BrighamYoungUniversity/Fall 2023/STAT 386/ST386_Final_Project/Scraped_Data/war_translated.csv')
trade_data = pd.read_csv('/Users/aly.milne/Library/CloudStorage/OneDrive-BrighamYoungUniversity/Fall 2023/STAT 386/ST386_Final_Project/Scraped_Data/trade_translated.csv')

# Function to extract unique values from a DataFrame column
def extract_unique_values(df, column):
    materials = set()
    for items in df[column].dropna().unique():
        for item in str(items).split():
            materials.add(item)
    return materials

# Function to plot a bar chart of materials
def plot_materials_bar_chart(df):
    material_counts = df['Material_translated'].str.split().explode().value_counts()
    plt.figure(figsize=(10, 6))
    material_counts.plot(kind='bar')
    st.pyplot(plt)

# Streamlit app
def main():
    st.title('Viking Artifatcs')

    # Choose between war data and trade data
    data_choice = st.radio("Choose the dataset", ('War Data', 'Trade Data'))

    if data_choice == 'War Data':
        data_to_display = war_data
        lat_column, lon_column = 'plats_latitude', 'plats_longitude'
    else:
        data_to_display = trade_data
        lat_column, lon_column = 'latitude', 'longitude'

    # Extract unique materials and places
    unique_materials = extract_unique_values(data_to_display, 'Material_translated')
    unique_places = extract_unique_values(data_to_display, 'Plats')

    # Widgets for material and place selection
    selected_materials = st.multiselect('Select Materials', list(unique_materials))
    selected_places = st.multiselect('Select Places', list(unique_places))

    # Filter data based on the selections
    filtered_data = data_to_display[
        (data_to_display['Material'].apply(lambda x: any(material in str(x) for material in selected_materials)) if selected_materials else True) &
        (data_to_display['Plats'].isin(selected_places) if selected_places else True)
    ]

    # Displaying the map
    if not filtered_data[[lat_column, lon_column]].dropna().empty:
        st.map(filtered_data[[lat_column, lon_column]].dropna())

    # Displaying the bar chart for materials
    plot_materials_bar_chart(filtered_data)

    st.dataframe(filtered_data)

if __name__ == '__main__':
    main()