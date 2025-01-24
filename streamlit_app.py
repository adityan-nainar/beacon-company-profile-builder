import streamlit as st
import requests

# Set up the API key
api_key = st.secrets['PER_API_KEY']

# App title
st.title("🎈 Company Profile Generator")

# User input for company name
company_name = st.text_input("Enter the company name:", placeholder="e.g., D.S Electrical Works Nagpur")

# Button to trigger the API call
if st.button("Get Company Profile"):
    if company_name.strip():
        # Define the API payload
        url = "https://api.perplexity.ai/chat/completions"
        payload = {
            "model": "sonar-pro",
            "messages": [
                {
                    "role": "system",
                    "content": "You are an AI assistant that builds detailed company profiles using online information. Use the exact company name for the search. Gather and summarize the following: Basic Information (Company Name, Founded Year, Headquarters, Company Size, Website, Industry Vertical, Location), Business Overview (Description, Mission Statement, Products/Services, Target Market, Major Competitors), Google Search Results (industry, services, notable news, GST number), LinkedIn Profile (company size, industry, key details), Company Website (services, mission, contact info), Key Professionals (important people and their roles), and Additional Sources (reviews, ratings, service offerings from Glassdoor, Indiamart, Justdial, etc.). Present the output in this format: Basic Information: Company Name: [Name] Founded Year: [Year] Headquarters: [Address] Company Size: [Size] Website: [URL] Industry Vertical: [Industry] Location: [City, State, Country] Business Overview: Description: [Description] Mission Statement: [Mission] Products and Services Offered: [List of products/services] Target Market: [Target industries] Google Search Summary: [Summarized findings with citations] Sources: [Source names and links] Key Personnel: [List of names, roles, and details]. Ensure the information is accurate, concise, and properly cited"
                },
                {
                    "role": "user",
                    "content": f"Give me an online company profile of the company \"{company_name}\"."
                }
            ],
            "temperature": 0.2,
            "top_p": 0.9,
            "stream": False,
        }
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        # Make the API request
        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()

            # Parse the response JSON
            response_data = response.json()
            content = response_data.get("choices", [{}])[0].get("message", {}).get("content", "No content available.")
            citations = response_data.get("citations", [])

            # Display the results
            st.subheader("Response Content")
            st.markdown(content.replace('\n', '\n\n'))  # Format content with line breaks

            if citations:
                st.subheader("Citations")
                for i, citation in enumerate(citations, 1):
                    st.write(f"{i}: {citation}")
            else:
                st.write("No citations available.")

        except requests.exceptions.RequestException as e:
            st.error(f"An error occurred: {e}")
    else:
        st.warning("Please enter a valid company name.")
