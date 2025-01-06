import streamlit as st
import pandas as pd
import argilla as rg

def display_upload_to_argilla_page():
    st.title("Upload to Argilla")
    
    # Load the dataset from session state
    dataset = st.session_state.get("dataset", pd.DataFrame())
    selected_columns = st.session_state.get("selected_columns", [])
    questions = st.session_state.get("questions", [])
    
    # If no dataset or questions, display a warning
    if dataset.empty or not questions:
        st.warning("No labeled dataset or questions found. Please ensure labeling is completed before uploading.")
        return
    
    st.markdown("#### Upload the labeled dataset to the Argilla server.")
    
    # Check if selected columns are available, otherwise show a warning
    if selected_columns:
        st.write("Selected Columns Preview:")
        st.write(dataset[selected_columns].head())  # Show selected columns
    else:
        st.warning("No columns selected. Please select at least one column on the upload page.")

    st.write("Labeled Dataset Preview:")
    st.write(dataset.head())  # Show the entire dataset preview

    # Additional inputs for Argilla upload
    guidelines = st.text_area("Write labeling guidelines:", value="")
    api_url = st.text_input("Argilla Server URL", value="https://your-argilla-server.com")
    api_key = st.text_input("Argilla API Key", type="password")
    dataset_name = st.text_input("Dataset Name", value="labeled_dataset")
    workspace_name = st.text_input("Workspace Name", value="default_workspace")

    # Upload button
    if st.button("Upload to Argilla"):
        try:
            # Initialize Argilla client
            client = rg.Argilla(api_url=api_url, api_key=api_key)
            
            # Prepare records for upload to Argilla
            records = []
            for idx, row in dataset.iterrows():
                record = {}
                for column in selected_columns:
                    record[column] = row[column]  # Add each selected column's data

                annotations = {}
                # Add annotations for each question
                for question in questions:
                    question_title = question['question_title']
                    question_type = question['question_type']
                    label = row.get(question_title)  # Get the label selected during labeling

                    # Handle Label questions (single label)
                    if question_type == "Label":
                        annotations[question_title] = label  # Single label

                    # Handle Multi-label questions (multiple labels)
                    elif question_type == "Multi-label":
                        if isinstance(label, list):
                            annotations[question_title] = ", ".join(label)  # Multi-label as comma-separated
                        else:
                            annotations[question_title] = label  # Single value fallback (if any issue with multi-label)

                    # Handle Rating questions (numeric rating)
                    elif question_type == "Rating":
                        annotations[question_title] = label  # Rating value (assumed to be a number)

                record["annotations"] = annotations
                records.append(record)
            
            # Define TextFields for each selected column
            fields = []
            for column in selected_columns:
                fields.append(rg.TextField(name=column, title=column, use_markdown=False))
            
            # Define the questions (assuming labels are defined for Label or Multi-label questions)
            label_questions = []
            for question in questions:
                question_type = question["question_type"]
                if question_type == "Label":
                    label_questions.append(
                        rg.LabelQuestion(
                            name=question["question_title"],
                            labels=question["labels"],
                            description=question["label_description"]
                        )
                    )
                elif question_type == "Rating":
                    # For rating, use RatingQuestion with options 1-5
                    label_questions.append(
                        rg.RatingQuestion(
                            name=question["question_title"],
                            values=[1,2,3,4,5],
                            description=question["label_description"]  # Assuming a 1-5 rating scale
                            
                        )
                    )
                elif question_type == "Multi-label":
                    label_questions.append(
                        rg.MultiLabelQuestion(
                            name=question['question_title'],
                            labels=question['labels'],
                            description=question["label_description"]
                        )
                    )

            # Setup dataset settings with fields (TextFields for columns) and questions
            settings = rg.Settings(
                guidelines=guidelines,
                fields=fields,  # Include TextFields for all selected columns
                questions=label_questions  # Include the questions defined in the question page
            )

            # Create or get the dataset on Argilla
            dataset = rg.Dataset(name=dataset_name, workspace=workspace_name, settings=settings)
            dataset.create()
            
            # Log the records to Argilla
            dataset.records.log(records)

            # Display success message
            st.success("Data uploaded to Argilla successfully!")

        except Exception as e:
            st.error(f"Failed to upload to Argilla: {str(e)}")
