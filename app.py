import streamlit as st
import pandas as pd
import os
import datetime
from dotenv import load_dotenv
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate

# Streamlit Page Config
st.set_page_config(page_title="Google Sheets AI Assistant", page_icon="📊", layout="wide")

# Load Environment Variables
load_dotenv(override=True)
genai_api_key = os.getenv("GOOGLE_API_KEY") or st.secrets.get("GOOGLE_API_KEY")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID") or st.secrets.get("SPREADSHEET_ID")

# Google Sheets Credentials
credentials_info = st.secrets.get("credentials", None)
if credentials_info:
    credentials = Credentials.from_service_account_info(credentials_info, scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"])
else:
    service_account_file = os.getenv("SERVICE_ACCOUNT_FILE")
    credentials = Credentials.from_service_account_file(service_account_file, scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"])

# Google Gemini AI Model
model = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.7)

# Hide Streamlit UI elements
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

def fetch_google_sheets_data(spreadsheet_id):
    """Fetch all data from Google Sheets."""
    try:
        service = build('sheets', 'v4', credentials=credentials)
        sheet_metadata = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        sheets = sheet_metadata.get('sheets', [])
        all_data = {}

        for sheet in sheets:
            sheet_name = sheet['properties']['title']
            range_name = f"{sheet_name}!A1:Z1000"  # Fetch entire sheet data

            result = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()
            values = result.get('values', [])

            if not values:
                continue  # Skip empty sheets

            df = pd.DataFrame(values)

            # Ensure valid column names
            if df.shape[0] > 1:
                df.columns = df.iloc[0]  # Assign first row as headers
                df = df[1:]  # Remove the header row from data

            df = df.rename(columns=lambda x: x if x else f"Unnamed_{df.columns.get_loc(x)}")  # Handle empty column names
            df = df.loc[:, ~df.columns.duplicated()]  # Remove duplicate columns
            df.fillna("", inplace=True)  # Clean missing values

            all_data[sheet_name] = df.reset_index(drop=True)

        return all_data
    except Exception as e:
        st.error(f"Error fetching data from Google Sheets: {e}")
        return None

def format_data_for_ai(data_dict):
    """Prepare Google Sheets data in a structured format for Gemini AI."""
    formatted_text = ""

    for sheet_name, df in data_dict.items():
        formatted_text += f"\n📄 Sheet: {sheet_name}\n" + "-"*30 + "\n"
        formatted_text += df.to_string(index=False)  # Convert DataFrame to text
        formatted_text += "\n\n"

    return formatted_text if formatted_text else "No valid data found."

def generate_answer(question, context):
    """Generate an AI-powered answer using Google Gemini."""
    current_date = datetime.date.today().strftime("%d-%m-%Y")

    prompt_template = """
    You are an AI assistant with expertise in analyzing and understanding Google Sheets data and You are also an expert in managing and assisting at a high-end restaurant, capable of performing dual roles as both the best restaurant manager and the best waiter at Niwant. Your responsibilities include:
    - The provided Google Sheets data contains various records. Analyze and answer the question based on available information in detailed and professional responses.
    As the Restaurant Manager:
    - Use the provided Google Sheet context, which contains records of the menu list and order details date-wise, to assist the owner with operational insights.
    - Answer questions about total sales, most sold items, previous month's sales, and other analytical queries clearly, concisely, and professionally.
    - Refer only OrderComplete sheet to answer the questions based on running tables.
    - where isPrint is true in OrderComplete sheet means tables is running but its payment is not get done. Avoid table Numbers duplicate entry in OrderComplete sheet.
    - The current date is {current_date}.
    - Most selling menu means the menu that has the highest quantity sold upto {current_date}.
    - Less / Low selling menu means the menu that has the lowest quantity sold upto {current_date}.
    - When user asks for deleted Quantity Sold, respond with detailed information about the menus previous Quantity".
    - For all sales-related queries, give all menu items and there prices also.
    - The total sale for a day is calculated by summing up the Menu_Rate values for all items sold on that day , also shows the sold item.
    Example: On 26-01-2025, the total sale is the sum of Menu_Rate for the sold items.
    If the data for a query is unavailable in the context, respond with: "The result for this question is not available in my knowledge."
    
    As the Waiter:
    - Use the provided Google Sheet context, which contains the food menu list, to assist customers with their queries about the menu, prices, and order creation for lunch or dinner in detailed and friendly responses.
    - Respond in a friendly and detailed manner, including all necessary details such as item prices, quantities, and the total cost.
    - If the information is not available in the context, respond with: "The answer is not available in the provided context."
    
    Your goal is to seamlessly switch between these roles based on the user's queries, providing accurate, professional, and friendly assistance at all times. Always ensure clarity, precision, and a helpful tone in your responses.

    Data Context:
    {context}
    
    User Question:
    {question}
    
    Answer:
    """
    
    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question", "current_date"]).format(
        context=context, question=question, current_date=current_date
    )
    
    response = model.invoke(prompt)
    return response.content

def main():
    st.title("📊 Your Hotel's AI Assistant")
    st.write("Your AI-powered assistant created by S-Tech")

    # Fetch Google Sheets data
    with st.spinner("Fetching data ..."):
        sheet_data = fetch_google_sheets_data(SPREADSHEET_ID)

    # if sheet_data:
    #     st.success("Now your AI is ready to chat!")

        # Display Sheets Data
        # for sheet_name, df in sheet_data.items():
        #     st.subheader(f"📄 Sheet: {sheet_name}")
        #     st.dataframe(df)

        # Format data for AI
        formatted_context = format_data_for_ai(sheet_data)

        # User Question Input
        user_question = st.text_input("Ask a question:")

        if st.button("Get Answer"):
            with st.spinner("Analyzing data..."):
                response = generate_answer(user_question, formatted_context)
                st.success(response)
    # else:
    #     st.error("Failed to fetch data from Google Sheets.")

if __name__ == "__main__":
    main()
