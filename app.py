# # chatbot for Owner
# import streamlit as st
# from langchain_google_genai import ChatGoogleGenerativeAI
# from langchain.prompts import PromptTemplate
# from googleapiclient.discovery import build
# from google.oauth2.service_account import Credentials
# import pandas as pd  # Import pandas for tabular data handling
# import os
# from dotenv import load_dotenv

# # Load environment variables
# load_dotenv()

# # Google Generative AI Configuration
# genai_api_key = os.getenv("GOOGLE_API_KEY") or st.secrets("GOOGLE_API_KEY")
# SPREADSHEET_ID = os.getenv("SPREADSHEET_ID") or st.secrets("SPREADSHEET_ID")


# if st.secrets:
#     credentials_info = dict(st.secrets["credentials"])  # Use Streamlit secrets
#     credentials = Credentials.from_service_account_info(credentials_info, scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"])
# else:
#     # Use local JSON file path for development
#     service_account_file = os.getenv("SERVICE_ACCOUNT_FILE")
#     credentials = Credentials.from_service_account_file(service_account_file, scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"])

# SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
# RANGE_NAME = "Sheet1!A1:Z1000"  # Adjust range as needed

# def get_sheet_data():
#     """Fetch and clean all rows from Google Sheets."""
#     service = build('sheets', 'v4', credentials=credentials)
#     sheet = service.spreadsheets()
    
#     try:
#         # Fetch the raw data from the specified range
#         result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
#         values = result.get('values', [])
        
#         # Check if data exists
#         if not values:
#             return []

#         # Convert the raw data into a pandas DataFrame for better handling
#         df = pd.DataFrame(values)
#         df.columns = df.iloc[0]  # Set the first row as column headers
#         df = df[1:]  # Remove the header row from the data
#         return df.reset_index(drop=True)

#     except Exception as e:
#         st.error(f"Error fetching data: {e}")
#         return None

# def format_data_for_context(df):
#     """Format cleaned data into a readable context string."""
#     return "\n".join([f"{row['Order_Date']}:{row['Menu_Name']}: {row['Quantity_Sold']} : {row['Menu_Price']} : {row['Menu_Rate']}" for _, row in df.iterrows()])

# def generate_answer(question, context):
#     """Generate an answer using the Google Generative AI model."""
#     prompt_template = """
#     You are the best restaurant manager at Le-meridian. Use the following context from a Google Sheet, which contains records of order datewise . Your job is to assist the owner by answering questions about today's total sales, the most sold items, previous month's sales, and other operational insights.
#     Provide answers in a full sentense,clear, concise, and professional manner with numerical details where applicable. If the answer is not available in the context, say: 'The data for this query is not available in the provided context.
#     When there is price then provide it in rupees.
    
#     Context:
#     {context}
    
#     Question:
#     {question}
    
#     Answer:
#     """
#     # Format the prompt
#     prompt = PromptTemplate(
#         template=prompt_template,
#         input_variables=["context", "question"]
#     ).format(context=context, question=question)

#     # Initialize the model
#     model = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.5)
#     response = model.invoke(prompt)
#     return response.content

# def main():
#     # st.set_page_config(page_title="Google Sheets ChatBot",layout="wide",initial_sidebar_state="expanded",page_icon=":shark:")
#     st.set_page_config(
#     page_title="ChatBot",
#     page_icon=":hotel:",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )
#     # **HIDE STREAMLIT DEFAULT UI ELEMENTS**
#     hide_streamlit_style = """
#         <style>
#         #MainMenu {visibility: hidden;}
#         footer {visibility: hidden;}
#         header {visibility: hidden;}
#         .stDeployButton {display: none !important;} /* Hides the "Manage App" button */
#         div[data-testid="stDecoration"] {display: none !important;} /* Additional hiding for Streamlit elements */
#         </style>
#     """


#     st.markdown(hide_streamlit_style, unsafe_allow_html=True)

#     st.header("Welcome ! What can I help with?")
#     user_question = st.text_input("Ask a question:")

#     if st.button("Get Answer"):
#         with st.spinner("Fetching Data ...Please wait..."):
#             # Fetch and clean Google Sheets data
#             sheet_data = get_sheet_data()

#             if sheet_data is None or sheet_data.empty:
#                 st.error("No valid data found in the Google Sheet.")
#             else:
#                 # Format data for context
#                 context = format_data_for_context(sheet_data)
#                 # Generate a response
#                 answer = generate_answer(user_question, context)
#                 st.success(answer)

#     with st.sidebar:
#         st.title("Menu")
#         if st.button("View Google Sheet Data"):
#             with st.spinner("Loading Google Sheets data..."):
#                 sheet_data = get_sheet_data()
#                 if sheet_data is None or sheet_data.empty:
#                     st.error("No valid data found in the Google Sheet.")
#                 else:
#                     st.write("Google Sheet Data:")
#                     st.dataframe(sheet_data)  # Display the data as a table in Streamlit

# if __name__ == "__main__":
#     main()


import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
import pandas as pd
import os
from dotenv import load_dotenv
import datetime

# Load environment variables
load_dotenv()

# Google Generative AI Configuration
genai_api_key = os.getenv("GOOGLE_API_KEY") or st.secrets["GOOGLE_API_KEY"]
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID") or st.secrets["SPREADSHEET_ID"]
MENULIST_SPREADSHEET_ID = os.getenv("MENULIST_SPREADSHEET_ID") or st.secrets["MENULIST_SPREADSHEET_ID"]

# Google Sheets Credentials
credentials_info = st.secrets["credentials"] if "credentials" in st.secrets else None
if credentials_info:
    credentials = Credentials.from_service_account_info(credentials_info, scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"])
else:
    service_account_file = os.getenv("SERVICE_ACCOUNT_FILE")
    credentials = Credentials.from_service_account_file(service_account_file, scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"])

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
RANGE_NAME = "Sheet1!A1:Z1000"
MENULIST_RANGE_NAME = "Sheet2!A1:Z1000"

def get_all_sheets_data(spreadsheet_id):
    """Fetch data from all sheets in the spreadsheet."""
    service = build('sheets', 'v4', credentials=credentials)
    sheet_metadata = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    sheets = sheet_metadata.get('sheets', [])
    
    all_data = {}

    for sheet in sheets:
        sheet_name = sheet['properties']['title']
        range_name = f"{sheet_name}!A1:Z1000"  # Fetch entire sheet data

        try:
            result = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()
            values = result.get('values', [])

            if not values:
                continue  # Skip empty sheets

            df = pd.DataFrame(values)

            # Ensure there are at least two rows before assigning column names
            if df.shape[0] > 1:
                df.columns = df.iloc[0]  # Assign first row as header
                df = df[1:]  # Remove the header row from data
            else:
                continue  # Skip sheets with only headers

            df = df.rename(columns=lambda x: x if x else f"Unnamed_{df.columns.get_loc(x)}")  # Handle empty column names
            df = df.loc[:, ~df.columns.duplicated()]  # Remove duplicate columns

            all_data[sheet_name] = df.reset_index(drop=True)  # Store DataFrame by sheet name

        except Exception as e:
            st.error(f"Error fetching data from {sheet_name}: {e}")

    return all_data


def format_all_data_for_context(all_data):
    """Format all sheets data into a readable string for AI model."""
    formatted_data = ""

    for sheet_name, df in all_data.items():
        formatted_data += f"\nSheet: {sheet_name}\n" + "-"*30 + "\n"
        
        # Formatting based on known columns
        if "Menu" in df.columns and "Price" in df.columns:
            formatted_data += "\n".join([f"{row['Menu']}: ₹{row['Price']}" for _, row in df.iterrows()])
        elif "Order_Date" in df.columns and "Menu_Name" in df.columns and "Quantity_Sold" in df.columns:
            formatted_data += "\n".join([f"{row['Order_Date']} | {row['Menu_Name']} | {row['Quantity_Sold']} | {row['Menu_Price']} | {row['Menu_Rate']}" for _, row in df.iterrows()])
        else:
            formatted_data += df.to_string(index=False)  # Fallback: Show entire sheet content
        
        formatted_data += "\n\n"

    return formatted_data if formatted_data else "No valid data found in any sheets."

def generate_answer(question, context):
    """Generate an answer using Google Generative AI."""
    
    current_date = datetime.date.today().strftime("%d-%m-%Y")  # Format as "DD-MM-YYYY"

    prompt_template = """
    You are an expert in managing and assisting at a high-end restaurant, capable of performing dual roles as both the best restaurant manager and the best waiter at Niwant. Your responsibilities include:

    As the Restaurant Manager:
    - Use the provided Google Sheet context, which contains records of the menu list and order details date-wise, to assist the owner with operational insights.
    - Answer questions about total sales, most sold items, previous month's sales, and other analytical queries clearly, concisely, and professionally.
    - The current date is {current_date}.
    - For all sales-related queries, refer only to the data in Sheet1, which contains the Order_Date, Menu_Name, Quantity_Sold, Menu_Price, and Menu_Rate.
    - The total sale for a day is calculated by summing up the Menu_Rate values for all items sold on that day , also shows the sold item.
    Example: On 26-01-2025, the total sale is the sum of Menu_Rate for the sold items.
    If the data for a query is unavailable in the context, respond with: "The data for this query is not available in the provided context."
    
    As the Waiter:
    - Use the provided Google Sheet context, which contains the food menu list, to assist customers with their queries about the menu, prices, and order creation for lunch or dinner in detailed and friendly responses.
    - Respond in a friendly and detailed manner, including all necessary details such as item prices, quantities, and the total cost.
    - If the information is not available in the context, respond with: "The answer is not available in the provided context."
    
    Your goal is to seamlessly switch between these roles based on the user's queries, providing accurate, professional, and friendly assistance at all times. Always ensure clarity, precision, and a helpful tone in your responses.


    Context:
    {context}
    
    Question:
    {question}
    
    Answer:
    """
    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question","current_date"]).format(context=context, question=question,current_date=current_date)
    model = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.7)
    response = model.invoke(prompt)
    return response.content

def main():
    st.set_page_config(page_title="ChatBot", page_icon=":hotel:", layout="wide", initial_sidebar_state="collapsed", menu_items=None)
    
    hide_streamlit_style = """
        <style>
        #MainMenu, header, footer {visibility: hidden !important;}
        .stDeployButton, div[data-testid="stDecoration"] {display: none !important;}
        iframe[title="Manage app"], iframe[title="streamlit_app"] {display: none !important;}

        ._link_gzau3_10, div._link_gzau3_10 {
            display: none !important;
            visibility: hidden !important;
            opacity: 0 !important;
            height: 0px !important;
            width: 0px !important;
        }
        </style>

        <script>
        function removeUnwantedElements() {
            let elementsToRemove = [
                "._link_gzau3_10",  // GitHub Button
                "div._link_gzau3_10",  // Streamlit Branding
                "iframe[title='Manage app']", 
                "iframe[title='streamlit_app']",
                "footer", 
                "#MainMenu"
            ];

            elementsToRemove.forEach(selector => {
                document.querySelectorAll(selector).forEach(el => el.remove());
            });
        }

        removeUnwantedElements();

        var observer = new MutationObserver((mutations) => {
            removeUnwantedElements();
        });

        observer.observe(document.body, { childList: true, subtree: true });
        </script>
    """
    
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)
    
    st.header("Welcome! What can I help with?")
    user_question = st.text_input("Ask a question:")
    
    if st.button("Get Answer"):
        with st.spinner("Fetching Data... Please wait..."):
            all_sheets_data = get_all_sheets_data(MENULIST_SPREADSHEET_ID)
            context = format_all_data_for_context(all_sheets_data)

            if context == "No valid data found in any sheets.":
                st.error(context)
            else:
                answer = generate_answer(user_question, context)
                st.success(answer)

    
    # with st.sidebar:
    #     st.title("Menu")
    #     if st.button("View Google Sheet Data"):
    #          with st.spinner("Loading Google Sheets data..."):
    #             sheet_data = get_all_sheets_data(MENULIST_SPREADSHEET_ID)
    #             if not sheet_data:
    #                 st.error("No valid data found in the Google Sheet.")
    #             else:
    #                 st.write("Google Sheet Data:")
    #                 for sheet_name, df in sheet_data.items():
    #                     st.subheader(f"Sheet: {sheet_name}")
    #                     st.dataframe(df)

if __name__ == "__main__":
    main()
