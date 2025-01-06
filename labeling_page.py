import streamlit as st
import pandas as pd

def display_labeling_page():
    st.set_page_config(layout="wide")
    st.title("Playground for Labelling before uploading to Argilla")

    # Ensure required session state variables are initialized
    if "current_index" not in st.session_state:
        st.session_state.current_index = 0
    if "labels_selected" not in st.session_state:
        st.session_state.labels_selected = {}
    if "labeling_complete" not in st.session_state:
        st.session_state.labeling_complete = False

    col1, col2 = st.columns([2, 1])

    # Left column: Display one dataset record at a time
    with col1:
        dataset = st.session_state.get("dataset")
        selected_columns = st.session_state.get("selected_columns")
        renamed_columns = st.session_state.get("renamed_columns")
        #st.session_state.dataset.rename(columns={column: new_name},inplace=True)

        # If renamed columns exist, apply the renaming to the dataset
        if renamed_columns:
            dataset.rename(columns=renamed_columns, inplace=True)
            st.session_state["dataset"] = dataset  # Ensure dataset in session state is updated

        col1_nav, col2_nav = st.columns([1, 1])
        with col1_nav:
            if st.button("Previous") and st.session_state.current_index > 0:
                st.session_state.current_index -= 1

        with col2_nav:
            if st.button("Next") and st.session_state.current_index < len(dataset) - 1:
                st.session_state.current_index += 1

        if dataset is not None and selected_columns:
            # Validate that selected_columns exist in the dataset
            valid_columns = [col for col in selected_columns if col in dataset.columns]
            if not valid_columns:
                st.error("Selected columns are not found in the dataset. Please check the column names.")
                st.markdown(selected_columns)
                st.markdown(dataset.head(3))
                print(renamed_columns)
            st.markdown("#### Dataset Records")

            if 0 <= st.session_state.current_index < len(dataset):
                record = dataset[valid_columns].iloc[st.session_state.current_index]

                for column in valid_columns:
                    st.markdown(f"**{column}:**")
                    st.markdown(f"{record[column]}")

            

    with col2:
        st.markdown("#### User Questions")
        questions = st.session_state.get("questions", [])

        user_responses = {}
        if questions:
            for idx, question in enumerate(questions, start=1):
                st.markdown(f"**{idx}. {question['question_title']}**")

                if question['question_type'] == "Label":
                    selected_label = st.radio(
                        f"{question['label_description']}",
                        question['labels'],
                        key=f"label_{idx}_{st.session_state.current_index}",
                        horizontal=True
                    )
                    user_responses[question['question_title']] = selected_label

                elif question['question_type'] == "Multi-label":
                    selected_labels = []
                    for label in question['labels']:
                        if st.checkbox(label, key=f"multi_label_{label}_{st.session_state.current_index}"):
                            selected_labels.append(label)
                    user_responses[question['question_title']] = ", ".join(selected_labels)

                elif question['question_type'] == "Rating":
                    user_responses[question['question_title']] = st.radio(
                        f"{question['label_description']}",
                        [1, 2, 3, 4, 5],
                        key=f"rating_{idx}_{st.session_state.current_index}",
                        horizontal=True
                    )

        if st.button("Submit"):
            for question_title, response in user_responses.items():
                st.session_state.dataset.loc[
                    st.session_state.current_index, question_title
                ] = response

            if st.session_state.current_index >= len(dataset) - 1:
                st.success("🎉 All examples have been labeled!")
                st.session_state.labeling_complete = True  # Mark labeling as complete
            else:
                st.session_state.current_index += 1
                
        if st.button("➡️ Upload to Argilla"):
            st.session_state.page = 4  # Redirect to the upload page
            st.rerun()

    # Save labeled data as CSV
    if st.session_state.get("labeling_complete"):
        if st.button("Save labeled data"):
            labeled_df = pd.DataFrame(st.session_state.dataset)
            labeled_df.to_csv("labeled_data.csv", index=False)
            st.success("Labeled data saved as 'labeled_data.csv'!")
            st.rerun()
