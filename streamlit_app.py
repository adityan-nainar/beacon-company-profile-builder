import streamlit as st
import requests
import re

# Set up the API key
api_key = st.secrets['PER_API_KEY']

# App title
st.title("🎈 Company Profile Generator")

# User input for company name
company_name = st.text_input("Enter the company name:", placeholder="e.g., D.S Electrical Works Nagpur")

# Function to split content into sections by headers
def parse_profile_sections(content):
    sections = {}
    current_header = None
    lines = content.split('\n')
    for line in lines:
        if line.strip().endswith(':') and len(line.strip()) < 80:
            current_header = line.strip().rstrip(':')
            sections[current_header] = ""
        elif current_header:
            sections[current_header] += line.strip() + '\n'
    return sections

# Button to trigger the API call
if st.button("Get Company Profile"):
    if company_name.strip():
        # API request setup
        url = "https://api.perplexity.ai/chat/completions"
        prompt = f"""
You are an AI assistant tasked with creating a comprehensive company profile using web resources.

Your goal is to extract and summarize as much of the following information as possible based on the company name: "{company_name}". Use only publicly available online sources.

Prioritize these fields: [Company Name, Establishment Year, Business Type, Addresses, GST, Website, Contact, Key People, Services, Turnover, Size, Industries, Certifications, Clients, Overview, Competitors, Google/LinkedIn/Justdial info, and Other Details].

If a field isn't found, write “Not Available”.
Return clearly under headers like:
Company Name:
Year of Establishment:
GST Number:
...
        """

        payload = {
            "model": "sonar-pro",
            "messages": [
                {"role": "system", "content": prompt},
                {"role": "user", "content": f"Build a company profile for: {company_name}"}
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

            # Process and Display Profile
            st.subheader("📄 Company Profile")
            sections = parse_profile_sections(content)

            for header, section_content in sections.items():
                if header.lower().startswith("google search") or "summary" in header.lower():
                    st.subheader(f"🔍 {header}")
                    st.code(section_content.strip())
                elif header.lower() in ["contact", "certifications", "key personnel"]:
                    st.subheader(f"📌 {header}")
                    st.info(section_content.strip())
                else:
                    st.subheader(header)
                    st.markdown(section_content.strip())

            # Show citations if available
            if citations:
                st.subheader("🔗 Citations")
                for i, citation in enumerate(citations, 1):
                    st.markdown(f"{i}. {citation}")
            else:
                st.caption("No citations provided by the API.")

        except requests.exceptions.RequestException as e:
            st.error(f"An error occurred: {e}")
    else:
        st.warning("Please enter a valid company name.")
