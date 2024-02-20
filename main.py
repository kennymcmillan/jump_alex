import streamlit as st
import pandas as pd
from datetime import datetime

# function
def transform_data(df, controller_value, team_value):
    # Drop specified columns
    columns_to_drop = ['Tf+Tc', 'PPO / Total mass', 'Tf\\Tc', 'Height', 'Rsi', 'Ppo',
                       'LegStiffness', 'Impulse', 'DeviceCount', 'Total']
    df.drop(columns=columns_to_drop, inplace=True, errors='ignore')

    # Rename specified columns
    columns_to_rename = {
        'GivenName': 'Given Name',
        'FamilyName': 'Family Name',
        'JumpIndex': 'Jump index',
        'ContactTime': 'Contact time',
        'FlightTime': 'Flight time'
    }
    df.rename(columns=columns_to_rename, inplace=True)

    # Duplicate columns
    df['First Name'] = df['Given Name']
    df['Last Name'] = df['Family Name']

    # Add empty columns
    empty_columns = ['Controller', 'Team', 'Start mode', 'Mass unit', 'Height Unit',
                     'Testing Type', 'External mass', 'Drop height']
    for col in empty_columns:
        df[col] = None

    # Populate specified columns based on non-empty Date column
    date_condition = df['Date'].notna()
    df.loc[date_condition, 'Mass unit'] = "Kilogram"
    df.loc[date_condition, 'Height Unit'] = "Centimetre"
    df.loc[date_condition, 'Testing Type'] = "Testing"

    # Convert 'Time' column to datetime format and perform the same operation as before
    df['Time'] = pd.to_datetime(df['Time'], format='%I:%M %p')

    ### TIME CALC
    # Group by 'First Name' and 'Last Name', and find the minimum time for each group
    min_time_group_new = df.groupby(['First Name', 'Last Name'])['Time'].min().reset_index()

    # Merge the minimum time back to the original dataframe
    new_data_merged = pd.merge(df, min_time_group_new, on=['First Name', 'Last Name'], how='left')

    # Replace the original 'Time' column with the minimum time
    new_data_merged = new_data_merged.drop('Time_x', axis=1)
    new_data_merged = new_data_merged.rename({'Time_y': 'Time'}, axis=1)

    # Parse the full timestamp
    new_data_merged['Time'] = pd.to_datetime(new_data_merged['Time'], format='%d/%m/%Y %H:%M')  # Convert to datetime
    new_data_merged['Time'] = new_data_merged['Time'].dt.strftime('%H:%M')
    new_data_merged['Controller'] = controller_value
    new_data_merged['Team'] = team_value
    
    # Add an Index column
    new_data_merged.reset_index(inplace=True)
    new_data_merged['index'] = new_data_merged['index'] + 1
    new_data_merged.rename(columns={'index': 'Index'}, inplace=True)

    return new_data_merged

def main():
    st.title('Transform VALD data')

    # Sidebar
    # Add instructions or any other text in the sidebar
    st.sidebar.write("Here are the instructions for using this tool:")

    # You can add more instructions here
    st.sidebar.write("1. Upload your CSV file.")
    st.sidebar.write("2. Select Controller & Team from Dropdown boxes below.")
    st.sidebar.write("3. Click the 'Transform Data' button.")
    st.sidebar.write("4. Download the transformed data.")
    st.sidebar.write("5. Make any final edits (click in table to edit)")
    st.sidebar.write("6. Download the csv file ")
    st.sidebar.write("7. Go for a coffee to waste the time you saved with this automation :-) ")

    # Dropdown menu for selecting Controller
    controller_options = ['Jack Andrew', 'Alexander Johan Daalhuizen', 'Kenneth Mcmillan']
    team_options = ['Development 1', 'Development 2', 'Development 3', 'Sprints', 'Jumps', 'Throws', 'Endurance']

    selected_controller = st.sidebar.selectbox('Select Controller', controller_options)
    selected_team = st.sidebar.selectbox('Select Team', team_options)

    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)

    if st.button('Transform Data'):
        transformed_df = transform_data(df, selected_controller, selected_team)
        st.session_state['transformed_df'] = transformed_df
        st.session_state['show_final_edit'] = False

        st.write("Transformed Data")
        st.dataframe(st.session_state['transformed_df'])

    if 'transformed_df' in st.session_state:
        if st.button('Make Final Edits'):
            st.session_state['show_final_edit'] = True

    if 'show_final_edit' in st.session_state and st.session_state['show_final_edit']:
        st.session_state['edited_df'] = st.data_editor(st.session_state['transformed_df'])

        if 'edited_df' in st.session_state:
            current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_name = f"Edited_VALD_{current_time}.csv"

            st.download_button(label="Download Edited Data for Smartabase",
                               data=st.session_state['edited_df'].to_csv(index=False).encode('utf-8'),
                               file_name=file_name,
                               mime='text/csv')

if __name__ == "__main__":
    main()



