# # import streamlit as st
# # from langchain_google_genai import ChatGoogleGenerativeAI
# # from langchain.prompts import PromptTemplate
# # from googleapiclient.discovery import build
# # from google.oauth2.service_account import Credentials
# # import pandas as pd
# # import os
# # from dotenv import load_dotenv
# # import datetime
# # st.set_page_config(page_title="ChatBot", page_icon=":hotel:", layout="wide", initial_sidebar_state="expanded")

# # # Load environment variables
# # load_dotenv(override=True)

# # # Google Generative AI Configuration
# # genai_api_key = os.getenv("GOOGLE_API_KEY") or st.secrets["GOOGLE_API_KEY"]
# # SPREADSHEET_ID = os.getenv("SPREADSHEET_ID") or st.secrets["SPREADSHEET_ID"]
# # MENULIST_SPREADSHEET_ID = os.getenv("MENULIST_SPREADSHEET_ID") or st.secrets["MENULIST_SPREADSHEET_ID"]

# # # Google Sheets Credentials
# # credentials_info = st.secrets["credentials"] if "credentials" in st.secrets else None
# # if credentials_info:
# #     credentials = Credentials.from_service_account_info(credentials_info, scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"])
# # else:
# #     service_account_file = os.getenv("SERVICE_ACCOUNT_FILE")
# #     credentials = Credentials.from_service_account_file(service_account_file, scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"])

# # SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']


# # def get_all_sheets_data(spreadsheet_id):
# #     """Fetch data from all sheets in the spreadsheet."""
# #     service = build('sheets', 'v4', credentials=credentials)
# #     sheet_metadata = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
# #     sheets = sheet_metadata.get('sheets', [])
# #     all_data = {}

# #     for sheet in sheets:
# #         sheet_name = sheet['properties']['title']
# #         range_name = f"{sheet_name}!A1:Z1000"  # Fetch entire sheet data

# #         try:
# #             result = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()
# #             values = result.get('values', [])

# #             if not values:
# #                 continue  # Skip empty sheets

# #             df = pd.DataFrame(values)

# #             # Ensure there are at least two rows before assigning column names
# #             if df.shape[0] > 1:
# #                 df.columns = df.iloc[0]  # Assign first row as header
# #                 df = df[1:]  # Remove the header row from data
# #             else:
# #                 continue  # Skip sheets with only headers

# #             df = df.rename(columns=lambda x: x if x else f"Unnamed_{df.columns.get_loc(x)}")  # Handle empty column names
# #             df = df.loc[:, ~df.columns.duplicated()]  # Remove duplicate columns

# #             all_data[sheet_name] = df.reset_index(drop=True)  # Store DataFrame by sheet name

# #         except Exception as e:
# #             st.error(f"Error fetching data from {sheet_name}: {e}")

# #     return all_data


# # def format_all_data_for_context(all_data):
# #     """Format all sheets data into a readable string for AI model."""
# #     formatted_data = ""

# #     for sheet_name, df in all_data.items():
# #         formatted_data += f"\nSheet: {sheet_name}\n" + "-"*30 + "\n"
        
# #         # Formatting based on known columns
# #         if "Menu" in df.columns and "Price" in df.columns:
# #             formatted_data += "\n".join([f"{row['Menu']}: ₹{row['Price']}" for _, row in df.iterrows()])
# #         elif "Order Date" in df.columns and "Menu Name" in df.columns and "Quantity Sold" in df.columns:
# #             formatted_data += "\n".join([f"{row['Order Date']} | {row['Section']} | {row['Menu Name']} | {row['Quantity Sold']} | {row['Menu Price']} | {row['Menu Rate']}" for _, row in df.iterrows()])
# #         else:
# #             formatted_data += df.to_string(index=False)  # Fallback: Show entire sheet content
        
# #         formatted_data += "\n\n"

# #     return formatted_data if formatted_data else "No valid data found in any sheets."

# # def generate_answer(question, context):
# #     """Generate an answer using Google Generative AI."""
    
# #     current_date = datetime.date.today().strftime("%d-%m-%Y")  # Format as "DD-MM-YYYY"

# #     prompt_template = """
# #     You are an expert in managing and assisting at a high-end restaurant, capable of performing dual roles as both the best restaurant manager and the best waiter at Niwant. Your responsibilities include:

# #     As the Restaurant Manager:
# #     - Use the provided Google Sheet context, which contains records of the menu list and order details date-wise, to assist the owner with operational insights.
# #     - Answer questions about total sales, most sold items, previous month's sales, and other analytical queries clearly, concisely, and professionally.
# #     - The current date is {current_date}.
# #     - For all sales-related queries, refer only to the data in Sheet1, which contains the Order_Date, Menu_Name, Quantity_Sold, Menu_Price, and Menu_Rate.
# #     - The total sale for a day is calculated by summing up the Menu_Rate values for all items sold on that day , also shows the sold item.
# #     Example: On 26-01-2025, the total sale is the sum of Menu_Rate for the sold items.
# #     If the data for a query is unavailable in the context, respond with: "The result for this question is not available in my knowledge."
    
# #     As the Waiter:
# #     - Use the provided Google Sheet context, which contains the food menu list, to assist customers with their queries about the menu, prices, and order creation for lunch or dinner in detailed and friendly responses.
# #     - Respond in a friendly and detailed manner, including all necessary details such as item prices, quantities, and the total cost.
# #     - If the information is not available in the context, respond with: "The answer is not available in the provided context."
    
# #     Your goal is to seamlessly switch between these roles based on the user's queries, providing accurate, professional, and friendly assistance at all times. Always ensure clarity, precision, and a helpful tone in your responses.


# #     Context:
# #     {context}
    
# #     Question:
# #     {question}
    
# #     Answer:
# #     """
# #     prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question","current_date"]).format(context=context, question=question,current_date=current_date)
# #     model = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.7)
# #     response = model.invoke(prompt)
# #     return response.content

# # def main():
    
# #     hide_streamlit_style = """
# #         <style>
# #     #MainMenu {visibility: hidden;}
# #     footer {visibility: hidden;}
# #     header {visibility: hidden;}
# #     """
# #     st.markdown(hide_streamlit_style, unsafe_allow_html=True)
    
# #     st.header("Welcome! What can I help with?")
# #     user_question = st.text_input("Ask a question:")
    
# #     if st.button("Get Answer"):
# #         with st.spinner("Fetching Data... Please wait..."):
# #             all_sheets_data = get_all_sheets_data(MENULIST_SPREADSHEET_ID)
# #             context = format_all_data_for_context(all_sheets_data)

# #             if context == "No valid data found in any sheets.":
# #                 st.error(context)
# #             else:
# #                 answer = generate_answer(user_question, context)
# #                 st.success(answer)

    
# #     with st.sidebar:
# #         st.title("Menu")
# #         if st.button("View Google Sheet Data"):
# #              with st.spinner("Loading Google Sheets data..."):
# #                 sheet_data = get_all_sheets_data(MENULIST_SPREADSHEET_ID)
# #                 if not sheet_data:
# #                     st.error("No valid data found in the Google Sheet.")
# #                 else:
# #                     st.write("Google Sheet Data:")
# #                     for sheet_name, df in sheet_data.items():
# #                         st.subheader(f"Sheet: {sheet_name}")
# #                         st.dataframe(df)

# # if __name__ == "__main__":
# #     main()



# import streamlit as st
# import pandas as pd
# import os
# import datetime
# from dotenv import load_dotenv
# from googleapiclient.discovery import build
# from google.oauth2.service_account import Credentials
# from langchain_google_genai import ChatGoogleGenerativeAI
# from langchain.prompts import PromptTemplate

# # Streamlit Page Config
# st.set_page_config(page_title="Google Sheets AI Assistant", page_icon="📊", layout="wide")

# # Load Environment Variables
# load_dotenv(override=True)
# genai_api_key = os.getenv("GOOGLE_API_KEY") or st.secrets.get("GOOGLE_API_KEY")
# SPREADSHEET_ID = os.getenv("SPREADSHEET_ID") or st.secrets.get("SPREADSHEET_ID")

# # Google Sheets Credentials
# credentials_info = st.secrets.get("credentials", None)
# if credentials_info:
#     credentials = Credentials.from_service_account_info(credentials_info, scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"])
# else:
#     service_account_file = os.getenv("SERVICE_ACCOUNT_FILE")
#     credentials = Credentials.from_service_account_file(service_account_file, scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"])

# # Google Gemini AI Model
# model = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.5)

# # Hide Streamlit UI elements
# st.markdown("""
#     <style>
#         #MainMenu {visibility: hidden;}
#         footer {visibility: hidden;}
#         header {visibility: hidden;}
#     </style>
# """, unsafe_allow_html=True)

# def fetch_google_sheets_data(spreadsheet_id):
#     """Fetch all data from Google Sheets."""
#     try:
#         service = build('sheets', 'v4', credentials=credentials)
#         sheet_metadata = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
#         sheets = sheet_metadata.get('sheets', [])
#         all_data = {}

#         for sheet in sheets:
#             sheet_name = sheet['properties']['title']
#             range_name = f"{sheet_name}!A1:Z1000"  # Fetch entire sheet data

#             result = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()
#             values = result.get('values', [])

#             if not values:
#                 continue  # Skip empty sheets

#             df = pd.DataFrame(values)

#             # Ensure valid column names
#             if df.shape[0] > 1:
#                 df.columns = df.iloc[0]  # Assign first row as headers
#                 df = df[1:]  # Remove the header row from data

#             df = df.rename(columns=lambda x: x if x else f"Unnamed_{df.columns.get_loc(x)}")  # Handle empty column names
#             df = df.loc[:, ~df.columns.duplicated()]  # Remove duplicate columns
#             df.fillna("", inplace=True)  # Clean missing values

#             all_data[sheet_name] = df.reset_index(drop=True)

#         return all_data
#     except Exception as e:
#         st.error(f"Error fetching data from Google Sheets: {e}")
#         return None

# def format_data_for_ai(data_dict):
#     """Prepare Google Sheets data in a structured format for Gemini AI."""
#     formatted_text = ""

#     for sheet_name, df in data_dict.items():
#         formatted_text += f"\n📄 Sheet: {sheet_name}\n" + "-"*30 + "\n"
#         formatted_text += df.to_string(index=False)  # Convert DataFrame to text
#         formatted_text += "\n\n"

#     return formatted_text if formatted_text else "No valid data found."

# def generate_answer(question, context):
#     """Generate an AI-powered answer using Google Gemini."""
#     current_date = datetime.date.today().strftime("%d-%m-%Y")
#     prompt_template = """
#     Refined Prompt:
#     You are an advanced AI assistant with expertise in mathematics, data analysis, and interpretation of Google Sheets records. Additionally, you possess comprehensive knowledge of restaurant management and customer service, enabling you to perform dual roles seamlessly: a highly proficient restaurant manager and an exceptional waiter at Niwant. Your responsibilities include:

#     Analyzing Google Sheets Data
#     ➤ The provided Google Sheets dataset contains various structured records. Your task is to analyze and extract insights based on the available  information, delivering well-structured, concise, and professional responses.
    
#     Role 1: Restaurant Manager
#     As a restaurant manager, you are responsible for assisting the owner in operational decision-making by leveraging the data available in the Google Sheet.

#     ➤ The todays date is {current_date}.
#     ➤ The todays date is in DD-MM-YYYY.
#     ➤ Refer only to the OrderComplete sheet for all sales-related inquiries.
#     ➤ Formatting: Use bold text where necessary to emphasize key details.

#     ➤ Provide analytical insights on:
#         • Sales performance (e.g., today's sales, yesterday's sales, sales on a specific date, total sales up to a given date).
#         • Top-selling menu items: Identify the three highest-selling items (based on quantity sold) in descending order, formatted as a bullet-point list.
#         • Monthly and cumulative sales trends for performance evaluation.
#         • Give response in upto the point . concise and in details.
#     ➤ For all sales-related queries, include:
#         • To calculate Todays sale , sum of Menu Grand Total for the sold items.
#         • Itemized sales data, specifying menu items, quantity sold, and any applicable taxes.
#         • Order and table details, presenting the records in an organized manner.
#         • Refer only OrderCompleteDummy page of sheet to answer the questions related to sales.Ignore all other sheets.  
        
#         Example: Today's Sales (03-02-2025): ₹2,963.30

#         This is calculated by summing the Menu Grand Total for all orders completed today. The itemized sales data is as follows:

#         Order 1:
#         Anda Bhurji: 1 x ₹100.00
#         Veg Manchow Soup: 1 x ₹99.00
#         Subtotal: ₹199.00
#         Taxes: ₹19.90
#         Grand Total: ₹238.80

#         Order 2:
#         Chiken Chilly Dry: 1 x ₹249.00
#         Chiken Manchurian Dry: 1 x ₹269.00
#         Veg Manchow Soup: 1 x ₹99.00
#         Subtotal: ₹617.00
#         Taxes: ₹61.70
#         Grand Total: ₹740.40

#         Order 3:
#         Anda Bhurji: 1 x ₹100.00
#         Subtotal: ₹100.00
#         Taxes: ₹10.00
#         Grand Total: ₹120.00

#         Order 4:
#         Green Salad: 1 x ₹79.00
#         Chiken Chilly Dry: 2 x ₹249.00 = ₹498.00
#         Subtotal: ₹577.00
#         Taxes: ₹0.00
#         Grand Total: ₹1182.50

#         Order 5:
#         Chiken Spring Roll: 1 x ₹299.00
#         Chiken Manchurian Dry: 1 x ₹269.00
#         Subtotal: ₹568.00
#         Taxes: ₹56.80
#         Grand Total: ₹681.60
#         Total: ₹238.80 + ₹740.40 + ₹120.00 + ₹1182.50 + ₹681.60 = ₹2,963.30
        
#     ➤ Avoid referencing the sheet names in your responses.
#     ➤ If the requested information is not available in the provided data, respond with:
#     "The result for this question is not available in my knowledge."
    
#     Role 2: Waiter
#     As a waiter, you serve as an expert in the restaurant’s menu, assisting customers with their inquiries regarding food options, pricing, and order details in a friendly and informative manner.

#     ➤ Use the provided Google Sheet, which contains the menu list, to accurately respond to customer queries.
#     ➤ Your responses should be engaging, detailed, and customer-friendly, covering:
#         • Menu item descriptions, prices, and portion sizes.
#         • Order recommendations for lunch or dinner.
#         • Comprehensive cost breakdowns, including itemized totals.
#     ➤ If the requested information is not available, respond with:
#     "The result for this question is not available in my knowledge."
    
#     General Guidelines:
#     Your goal is to seamlessly transition between these roles based on the user’s query, ensuring that your responses remain:
#     ✔ Accurate and data-driven
#     ✔ Ensure all responses are in English. If menu items appear in another language,translate them into English.
#     ✔ Professional and concise (for management inquiries)
#     ✔ Engaging and customer-friendly (for service-related queries)
#     ✔ Clear, structured, and easy to comprehend

#     Maintain a helpful, precise, and insightful tone at all times to provide the best possible assistance.

#     Data Context:
#     {context}
    
#     User Question:
#     {question}
    
#     Answer:
#     """
    
#     prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question", "current_date"]).format(
#         context=context, question=question, current_date=current_date
#     )
    
#     response = model.invoke(prompt)
#     return response.content

# import streamlit as st

# def main():
#     # Reduce top margin using markdown CSS
#     st.markdown("""
#         <style>
#             .block-container { padding-top: 5px; }
#             h1 { font-size: 20px !important; }
#         </style>
#     """, unsafe_allow_html=True)
    
#     st.title("📊 Niwant's AI Assistant")
#     st.write("Your AI-powered assistant ")
#     st.write("FAQ's :")

#     # Default Questions
#     default_questions = [
#         "What are today's total sales?",
#         "Which menu items are the best-selling?",
#         "What were yesterday's total sales?",
#         "What is the total cash amount for today?",
#     ]
    
#     # Fetch Google Sheets data
#     with st.spinner("Fetching data ..."):
#         sheet_data = fetch_google_sheets_data(SPREADSHEET_ID)

#     # Format data for AI
#     formatted_context = format_data_for_ai(sheet_data)
    
#     # Initialize an empty list to store responses
#     responses = []
    
#     for question in default_questions:
#         if st.button(question):
#             with st.spinner("Analyzing data..."):
#                 response = generate_answer(question, formatted_context)
#                 responses.append((question, response))
    
#     # User Question Input
#     user_question = st.text_input("Ask a question:")

#     if st.button("Get Answer"):
#         with st.spinner("Analyzing data..."):
#             response = generate_answer(user_question, formatted_context)
#             responses.append((user_question, response))
    
#     # Display all responses below the input field
#     for question, answer in responses:
#         st.write(f"**Q:** {question}")
#         st.success(answer)

# if __name__ == "__main__":
#     main()




import streamlit as st
import pandas as pd
import os
import datetime
import plotly.express as px
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
model = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.5)

# Hide Streamlit UI elements
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=60)
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


def extract_sales_data(sheet_data):
    """Extract and process sales data from Google Sheets."""
    sales_df = sheet_data.get("OrderCompleteDummy")  # Ensure correct sheet name
    
    if sales_df is None:
        st.error("Sales data not found in the provided Google Sheets.")
        return None

    # Print column names to debug
    # st.write("Available columns:", sales_df.columns.tolist())  # ✅ Show all columns in Streamlit
    # st.write("🔍 First few rows of sales data:", sales_df.head())

    # Rename columns to remove spaces and lowercase them for consistency
    sales_df.columns = sales_df.columns.str.strip().str.lower()

    # Ensure 'Order Date' exists after renaming
    if "order date" not in sales_df.columns:
        st.error("Column 'Order Date' not found! Check Google Sheets structure.")
        return None

    # Convert date column to datetime
    sales_df['order date'] = pd.to_datetime(sales_df['order date'], errors='coerce', dayfirst=True)

    # Convert sales column to numeric values
    if "menu grand total" in sales_df.columns:
        sales_df['menu grand total'] = pd.to_numeric(sales_df['menu grand total'], errors='coerce')

    return sales_df



def plot_sales_trend(sales_df, start_date=None, end_date=None):
    """Generate a sales trend graph for a given date range."""
    if start_date and end_date:
        # Convert start_date and end_date to datetime
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)

        # Apply mask for date range filtering
        mask = (sales_df['order date'] >= start_date) & (sales_df['order date'] <= end_date)
        filtered_sales = sales_df.loc[mask]
    else:
        filtered_sales = sales_df

    if filtered_sales.empty:
        st.warning("No sales data available for the selected date range.")
        return

    # Group sales by date
    sales_summary = filtered_sales.groupby('order date')['menu grand total'].sum().reset_index()

    # Plot using Plotly
    fig = px.bar(sales_summary, x='order date', y='menu grand total', title="Sales Trend Over Time",
                  labels={'menu grand total': "Total Sales (₹)", 'order date': "Date"},
                  text_auto=True)
    
    st.plotly_chart(fig, use_container_width=True)
    
    
    

def generate_answer(question, context, sheet_data):
    """Generate an AI-powered answer or show a sales graph based on the query."""
    current_date = datetime.date.today().strftime("%d-%m-%Y")
    
    prompt_template = """
    Refined Prompt:
    You are an advanced AI assistant with expertise in mathematics, data analysis, and interpretation of Google Sheets records. Additionally, you possess comprehensive knowledge of restaurant management and customer service, enabling you to perform dual roles seamlessly: a highly proficient restaurant manager and an exceptional waiter at Niwant. Your responsibilities include:

    Analyzing Google Sheets Data
    ➤ The provided Google Sheets dataset contains various structured records. Your task is to analyze and extract insights based on the available  information, delivering well-structured, concise, and professional responses.
    
    Role 1: Restaurant Manager
    As a restaurant manager, you are responsible for assisting the owner in operational decision-making by leveraging the data available in the Google Sheet.

    ➤ The todays date is {current_date}.
    ➤ The todays date is in DD-MM-YYYY.
    ➤ Formatting: Use bold text where necessary to emphasize key details.
    ➤ Give Sales performance report accurately (e.g., today's sales, yesterday's sales, sales on a specific date, total sales up to a given date).
    ➤ Strictly follow only OrderCompleteDummy sheet to answer the questions related to sales.Ignore all other sheets.  
    ➤ To calculate sale , strictly do the correct addition of all "menu grand total" column and consider it as correct answer.
    ➤ neglect the discrepancy in the provided data. 
    ➤ Refer Example for better understanding.Give response in upto the point , concise and in details.
    ➤ For all sales-related queries :
        • Top-selling menu items: Identify the three highest-selling items (based on quantity sold) in descending order, formatted as a bullet-point list.
        • While calulating do not consider time component of the date.            
    
    
    Example :Today's total sales (04-02-2025) based on the "Menu Grand Total" column are ₹1404.00.

    Individual Breakup:
    Order 1: ₹328.00
    Order 2: ₹322.00
    Order 3: ₹219.00
    Order 4: ₹535.00

    ➤ Avoid referencing the sheet names in your responses.
    ➤ If the requested information is not available in the provided data, respond with:
    "The result for this question is not available in my knowledge."
    
    Role 2: Waiter
    As a waiter, you serve as an expert in the restaurant’s menu, assisting customers with their inquiries regarding food options, pricing, and order details in a friendly and informative manner.

    ➤ Use the provided Google Sheet, which contains the menu list, to accurately respond to customer queries.
    ➤ When user ask plan a menu for lunch or dinner , provide the details of the menu items, prices and proper portion sizes.
    ➤ Your responses should be engaging, detailed, and customer-friendly, covering:
        • Menu item descriptions, prices, and portion sizes.
        • Order recommendations for lunch or dinner.
        • Comprehensive cost breakdowns, including itemized totals.
    ➤ If the requested information is not available, respond with:
    "The result for this question is not available in my knowledge."
    
    General Guidelines:
    Your goal is to seamlessly transition between these roles based on the user’s query, ensuring that your responses remain:
    ✔ Accurate and data-driven
    ✔ Ensure all responses are in English. If menu items appear in another language,translate them into English.
    ✔ Professional and concise (for management inquiries)
    ✔ Engaging and customer-friendly (for service-related queries)
    ✔ Clear, structured, and easy to comprehend

    Maintain a helpful, precise, and insightful tone at all times to provide the best possible assistance.

    Data Context:
    {context}
    
    User Question:
    {question}
    
    Answer:
    """
    
    if "date-wise sales" in question.lower() or "sales trend" in question.lower():
        sales_df = extract_sales_data(sheet_data)
        if sales_df is not None:
            start_date = st.date_input("Select Start Date", datetime.date.today() - datetime.timedelta(days=7))
            end_date = st.date_input("Select End Date", datetime.date.today())
            plot_sales_trend(sales_df, start_date, end_date)
        return "Here's the graphical representation of date-wise sales."

    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question", "current_date"]).format(
        context=context, question=question, current_date=current_date
    )
    
    response = model.invoke(prompt)
    return response.content


def main():
    st.markdown(
        """
        <style>
            .block-container { padding-top: 5px; }
            h1 { font-size: 20px !important; }
            
            /* Make the answer section scrollable */
            div[data-testid="stVerticalBlock"] > div:last-child {
                max-height: 400px; /* Adjust height as needed */
                overflow-y: auto;
                border: 1px solid #ddd;
                padding: 10px;
                border-radius: 5px;
                background-color: #f9f9f9;
            }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    st.title("📊 Restaurants AI Assistant")
    # st.write("Your AI-powered assistant ")
    # st.write("FAQ's :")

    # Default Questions
    default_questions = [
        "today's sales?",
        "date-wise sales trend"  # ✅ New Graph-Based Question
    ]

        
    # Fetch Google Sheets data
    with st.spinner("Fetching data ..."):
        sheet_data = fetch_google_sheets_data(SPREADSHEET_ID)

    # Format data for AI
    # formatted_context = "Formatted sales data from Google Sheets."
    # Format data for AI
    formatted_context = format_data_for_ai(sheet_data)

    # Initialize an empty list to store responses
    responses = []
    
    for question in default_questions:
        if st.button(question):
            with st.spinner("Analyzing data..."):
                response = generate_answer(question, formatted_context, sheet_data)
                responses.append((question, response))
    
    # User Question Input
    user_question = st.text_input("Ask a question:")

    if st.button("Get Answer"):
        with st.spinner("Analyzing data..."):
            response = generate_answer(user_question, formatted_context, sheet_data)
            responses.append((user_question, response))
    
    # Display all responses below the input field
    for question, answer in responses:
        st.write(f"**Q:** {question}")
        st.success(answer)

if __name__ == "__main__":
    main()
