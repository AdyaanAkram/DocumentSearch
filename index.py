import streamlit as st
import os
import openai

# Set up your API key
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Initialize OpenAI client
st.title("Worldox Boolean Search Generator")
st.write("Enter your search criteria in natural language, and this tool will convert it to Worldox-compatible Boolean logic.")

# Input field
user_input = st.text_area("Enter your search criteria:")

# Function to process the input using OpenAI
def generate_boolean_query(input_text):
    # Define the messages for OpenAI chat completion
    messages = [
        {
            "role": "system",
            "content": """
            Convert the following search criteria into a Boolean query for a document search. Use AND, OR, NOT, and quotation marks for phrases. Ensure it follows this pattern:

            Example 1:
            Input: "Find documents with contract information from 2023 or 2024, but exclude drafts."
            Output: "(contract AND (2023 OR 2024)) AND NOT draft"

            Example 2:
            Input: "Show reports that mention 'financial projections' and 'market analysis'."
            Output: "(\"financial projections\" AND \"market analysis\")"

            Now, convert this:
            """
        },
        {
            "role": "user",
            "content": input_text,
        },
    ]

    # Send the messages to OpenAI and retrieve the response
    chat_completion = client.ChatCompletion.create(
        messages=messages,
        model="gpt-4",
    )

    # Correctly access the content of the first choice message
    return chat_completion.choices[0].message["content"].strip()

# Display the output when the user clicks the button
if st.button("Generate Boolean Query"):
    if user_input:
        boolean_query = generate_boolean_query(user_input)
        st.write("Generated Boolean Query:")
        st.code(boolean_query)
    else:
        st.write("Please enter a search query.")
