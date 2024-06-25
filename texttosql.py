import pandas as pd
import google.generativeai as genai
from mysql import connector
import streamlit as st
from configparser import ConfigParser


config = ConfigParser()
config.read('config.conf')
user = config.get('DATABASE','user')
password = config.get('DATABASE','password')
database = config.get('DATABASE','database')
api_key = config.get('API_KEY','api_key')

genai.configure(api_key = api_key)
cnx = connector.connect(user=user, password=password,host='127.0.0.1',database=database)
def fetch_results(query):
    cursor = cnx.cursor()
    cursor.execute(query)
    df = pd.DataFrame(cursor.fetchall())
    df.columns = cursor.column_names
    cursor.close()
    cnx.close()
    return df

def create_query(query):
    prompt = '''
    You are an expert in SQL queries!

        The SQL database contains the following tables:

        Table 1: employees
        Columns: emp_no (int), birth_date (date), first_name (varchar(14)), last_name (varchar(16)),gender (enum('M','F')), hire_date (date)

        Table 2: dept_emp
        Columns: emp_no (int), dept_no(char(4)), from_date (date), to_date(date)

        Table 3: departments
        Columns: dept_no (char(4)), dept_name (varchar(40))

        generate the corresponding SQL query. Use MySQL.
        also the sql code should not have ``` in beginning or end and sql word in output
    '''
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content([prompt,query])
    return response.text 


# Creating a streamlit app
st.set_page_config(page_title="Query Databases with Gemini Pro")
st.header("Gemini App To Retrieve Data With Normal Text")

question = st.text_input("Enter your text:", key="input", placeholder="Type your text here")

submit = st.button("Ask the question")
try:
    if submit:

        if question is None or question == "":
            raise Exception("question cannot be null")

        response = create_query(question)
        st.write(response)

        response = fetch_results(response)
        
        st.subheader("The Response is")
        st.dataframe(response)
        # response.index = response['dept_name']
        # st.pyplot(response.plot.barh(stacked=True).figure)

except Exception as exception:
    st.header(exception)
