from dotenv import load_dotenv
import streamlit as st
import os
import shutil
import json
from miner_u_parser.cli.client import PDFConverter
from main import MarkdownProcessor

load_dotenv()

# Configuration
INPUT_FOLDER = "temp_input"
OUTPUT_FOLDER = "output"


def save_uploaded_file(uploaded_file):
    if not os.path.exists(INPUT_FOLDER):
        os.makedirs(INPUT_FOLDER)

    file_path = os.path.join(INPUT_FOLDER, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path


def main():
    st.set_page_config(page_title="PDF Legislative Parser", layout="wide")

    st.title("📄 Legislative PDF Parser & Analyzer")
    st.markdown(
        "Upload a PDF to convert it to Markdown, summarize it, and extract legislative data using Gemini AI."
    )

    if "processed_data" not in st.session_state:
        st.session_state.processed_data = None

    with st.sidebar:
        st.header("Settings")
        api_key = st.text_input("Google Gemini API Key", type="password")
        st.caption("Get your key from Google AI Studio.")

    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

    if uploaded_file and api_key:
        if st.button("Process PDF"):
            with st.spinner("Processing... Please wait."):
                try:
                    if os.path.exists(INPUT_FOLDER):
                        shutil.rmtree(INPUT_FOLDER)
                    if os.path.exists(OUTPUT_FOLDER):
                        shutil.rmtree(OUTPUT_FOLDER)

                    input_path = save_uploaded_file(uploaded_file)

                    st.info("Initializing PDF Converter...")
                    converter = PDFConverter()
                    converter.convert(input_path, OUTPUT_FOLDER)

                    file_name_no_ext = os.path.splitext(uploaded_file.name)[0]
                    md_file_path = os.path.join(
                        OUTPUT_FOLDER,
                        file_name_no_ext,
                        "auto",
                        f"{file_name_no_ext}.md",
                    )

                    if os.path.exists(md_file_path):
                        st.success(f"Conversion Successful! Markdown saved.")

                        st.info("Initializing AI Processor...")
                        processor = MarkdownProcessor(api_key=api_key)

                        summary, leg_data, leg_check = processor.main(md_file_path)

                        with open(md_file_path, "r", encoding="utf-8") as f:
                            raw_md = f.read()

                        st.session_state.processed_data = {
                            "summary": summary,
                            "leg_data": leg_data,
                            "leg_check": leg_check,
                            "file_name": file_name_no_ext,
                            "raw_md": raw_md,
                        }
                    else:
                        st.error(
                            f"Error: Expected markdown file not found at {md_file_path}"
                        )

                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
                    st.exception(e)

    elif uploaded_file and not api_key:
        st.warning("Please enter your Google Gemini API Key in the sidebar to proceed.")

    if st.session_state.processed_data:
        data = st.session_state.processed_data

        st.divider()

        leg_data_json = json.dumps(data["leg_data"], indent=4)
        leg_check_json = json.dumps(data["leg_check"], indent=4)
        file_name = data["file_name"]

        col1, col2 = st.columns([1, 1])

        with col1:
            st.subheader("📝 Summary")
            st.write(data["summary"])

            st.download_button(
                label="📥 Download Summary (.md)",
                data=data["summary"],
                file_name=f"{file_name}_summary.md",
                mime="text/markdown",
            )

            with st.expander("View Raw Markdown Content"):
                st.markdown(data["raw_md"])

        with col2:
            st.subheader("🔍 Legislative Data Extraction")
            st.json(data["leg_data"])

            st.download_button(
                label="📥 Download Leg Data (.json)",
                data=leg_data_json,
                file_name=f"{file_name}_leg_data.json",
                mime="application/json",
            )

            st.subheader("✅ Compliance Check")
            st.json(data["leg_check"])

            st.download_button(
                label="📥 Download Compliance Check (.json)",
                data=leg_check_json,
                file_name=f"{file_name}_leg_check.json",
                mime="application/json",
            )


if __name__ == "__main__":
    main()
