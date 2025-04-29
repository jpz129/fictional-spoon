import streamlit as st
import requests

API_URL = "http://localhost:8000"

st.markdown("# 📄 Contract Task Similarity Explorer\nWelcome! Upload a contract or search by phrase.")

input_mode = st.radio("Choose input method:", ["Text Query", "Upload .docx File"])

query = ""
if input_mode == "Text Query":
    query = st.text_input("Enter a task or phrase to search for similar tasks:")
elif input_mode == "Upload .docx File":
    uploaded_file = st.file_uploader("Upload a contract (.docx)", type=["docx"])
    if uploaded_file:
        import docx
        try:
            doc = docx.Document(uploaded_file)
            query = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
            st.success("Contract uploaded and parsed successfully.")
        except Exception as e:
            st.error(f"Error parsing .docx file: {e}")

if st.button("Search"):
    if query:
        with st.spinner("Searching for similar contracts..."):
            response = requests.get(f"{API_URL}/search_task", params={"query": query})
        if response.status_code == 200:
            response_json = response.json()
            results = response_json["contracts"]
            final_summary = response_json["final_summary"]

            for result in results:
                with st.expander(f"📄 Contract ID: {result['contract_id']} (Similarity: {result['similarity']:.4f})"):
                    st.markdown(f"**Explanation:** {result['explanation']}")
                    st.markdown("**Tasks:**")
                    for task in result['tasks']:
                        st.markdown(f"- {task}")
            if results:
                st.markdown("---")
                st.markdown("### 🔎 Summary of Contract Group")
                st.markdown(final_summary)
        else:
            st.error("Error retrieving results.")