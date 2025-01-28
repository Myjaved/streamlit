# chatbot for Owner
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
import pandas as pd  # Import pandas for tabular data handling
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Google Generative AI Configuration
genai_api_key = os.getenv("GOOGLE_API_KEY") or st.secrets("GOOGLE_API_KEY")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID") or st.secrets("SPREADSHEET_ID")


if st.secrets:
    credentials_info = dict(st.secrets["credentials"])  # Use Streamlit secrets
    credentials = Credentials.from_service_account_info(credentials_info, scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"])
else:
    # Use local JSON file path for development
    service_account_file = os.getenv("SERVICE_ACCOUNT_FILE")
    credentials = Credentials.from_service_account_file(service_account_file, scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"])

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
RANGE_NAME = "Sheet1!A1:Z1000"  # Adjust range as needed

def get_sheet_data():
    """Fetch and clean all rows from Google Sheets."""
    service = build('sheets', 'v4', credentials=credentials)
    sheet = service.spreadsheets()
    
    try:
        # Fetch the raw data from the specified range
        result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
        values = result.get('values', [])
        
        # Check if data exists
        if not values:
            return []

        # Convert the raw data into a pandas DataFrame for better handling
        df = pd.DataFrame(values)
        df.columns = df.iloc[0]  # Set the first row as column headers
        df = df[1:]  # Remove the header row from the data
        return df.reset_index(drop=True)

    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None

def format_data_for_context(df):
    """Format cleaned data into a readable context string."""
    return "\n".join([f"{row['Order_Date']}:{row['Menu_Name']}: {row['Quantity_Sold']} : {row['Menu_Price']} : {row['Menu_Rate']}" for _, row in df.iterrows()])

def generate_answer(question, context):
    """Generate an answer using the Google Generative AI model."""
    prompt_template = """
    You are the best restaurant manager at Le-meridian. Use the following context from a Google Sheet, which contains records of order datewise . Your job is to assist the owner by answering questions about today's total sales, the most sold items, previous month's sales, and other operational insights.
    Provide answers in a full sentense,clear, concise, and professional manner with numerical details where applicable. If the answer is not available in the context, say: 'The data for this query is not available in the provided context.
    When there is price then provide it in rupees.
    
    Context:
    {context}
    
    Question:
    {question}
    
    Answer:
    """
    # Format the prompt
    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["context", "question"]
    ).format(context=context, question=question)

    # Initialize the model
    model = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.5)
    response = model.invoke(prompt)
    return response.content

def main():
    st.set_page_config(page_title="Google Sheets ChatBot",layout="wide")

    st.header("Welcome ! What can I help with?")
    user_question = st.text_input("Ask a question:")

    if st.button("Get Answer"):
        with st.spinner("Fetching Data ...Please wait..."):
            # Fetch and clean Google Sheets data
            sheet_data = get_sheet_data()

            if sheet_data is None or sheet_data.empty:
                st.error("No valid data found in the Google Sheet.")
            else:
                # Format data for context
                context = format_data_for_context(sheet_data)
                # Generate a response
                answer = generate_answer(user_question, context)
                st.success(answer)

    with st.sidebar:
        st.title("Menu")
        if st.button("View Google Sheet Data"):
            with st.spinner("Loading Google Sheets data..."):
                sheet_data = get_sheet_data()
                if sheet_data is None or sheet_data.empty:
                    st.error("No valid data found in the Google Sheet.")
                else:
                    st.write("Google Sheet Data:")
                    st.dataframe(sheet_data)  # Display the data as a table in Streamlit

if __name__ == "__main__":
    main()