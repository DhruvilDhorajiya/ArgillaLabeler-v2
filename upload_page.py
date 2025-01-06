import streamlit as st
import pandas as pd
import json

def display_upload_page():

    # Initialize session state variables
    if 'selected_columns' not in st.session_state:
        st.session_state.selected_columns = []  # Store selected columns
    if 'dataset' not in st.session_state:
        st.session_state.dataset = None  # Store the dataset
    if 'renamed_columns' not in st.session_state:
        st.session_state.renamed_columns = {}  # Map original column names to new names

    # File uploader widget for JSON file
    st.title("ArgillaLabeler")
    uploaded_file = st.file_uploader("Choose a JSON file", type=["json"])

    if uploaded_file is not None:
        try:
            # Load JSON data from uploaded file
            data = json.load(uploaded_file)

            # Flatten nested JSON (if needed) and create DataFrame
            df = pd.json_normalize(data, sep='_')
            st.session_state.dataset = df  # Save the dataset in session state

            # Display the DataFrame
            st.markdown("**Here is the dataset you uploaded:**")
            st.dataframe(df.head(3))  # Display first 3 rows as a preview

            # Generate checkboxes and edit buttons for each column
            st.session_state.selected_columns = []
            st.markdown("**Please select at least one column to display and rename columns if needed.**")

            for column in df.columns:
                # Get the renamed column name (if exists) or the original column name
                display_name = st.session_state.renamed_columns.get(column, column)

                # Display a checkbox for selecting the column
                col_checkbox, col_edit = st.columns([3, 1])
                with col_checkbox:
                    if st.checkbox(display_name, key=column):
                        # Use the renamed column name in the selected columns list
                        st.session_state.selected_columns.append(display_name)

                # Display an edit button for renaming the column
                with col_edit:
                    if st.button("Edit", key=f"edit_{column}"):
                        st.session_state[f"editing_{column}"] = True

                # If the edit button is clicked, display a text input for renaming
                if st.session_state.get(f"editing_{column}", False):
                    new_name = st.text_input(
                        f"Rename '{column}' to:",
                        value=display_name,
                        key=f"rename_input_{column}"
                    )
                    if st.button(f"Save", key=f"save_{column}"):
                        # Update the renamed_columns mapping
                        st.session_state.renamed_columns[column] = new_name

                        # Update the DataFrame column name
                        # st.session_state.dataset.rename(
                        #     columns={column: new_name}, inplace=True
                        # )
                        st.session_state.dataset.rename(columns={column: new_name},inplace=True)

                        # Update the display name for the checkbox
                        st.session_state[f"editing_{column}"] = False

                        # Ensure the updated DataFrame is saved back to the session state
                        st.session_state.dataset = st.session_state.dataset.copy()

                        # Display updated DataFrame immediately after renaming
                        st.success(f"Column '{column}' renamed to '{new_name}'")
                        st.rerun()

                        
            # Show "Next" button to navigate to the next page
            if st.button("Next"):
                if st.session_state.selected_columns:
                    st.session_state.page = 2  # Move to the next page
                    st.rerun()
                else:
                    st.warning("Please select at least one column before proceeding.")

        except json.JSONDecodeError:
            st.error("The file is not a valid JSON file.")
        except Exception as e:
            st.error(f"An error occurred: {e}")

# Run the function to display the page
display_upload_page()
