import streamlit as st
import requests

# Set up the API key
api_key = st.secrets['PER_API_KEY']

st.title("🎈 Company Profile Generator")

# Input
company_name = st.text_input("Enter the company name:", placeholder="e.g., D.S Electrical Works Nagpur")

# Section parser function
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

# On button click
if st.button("Get Company Profile"):
    if company_name.strip():
        citations = []  # Safe default

        prompt = f"""
You are an AI assistant tasked with creating a comprehensive company profile using web resources.

Priority 1: Accurately extract basic company details for "{company_name}", including:
- Name, Year of Establishment, Business Type, Addresses, GST, Website, Contact Info, Key People, Products/Services, Turnover, Size, Industries, Certifications, Clients, Overview, Google summary, and Online Listings.

Priority 2: **Thoroughly search for and list at least 3 to 5 competitors** of this company. Competitors should be in the **same product or service domain**, within India. Include:
- Competitor Name
- Location/City
- Specialization or Key Products/Services
- Online Source or Reference

Search on platforms like: Google, Indiamart, Justdial, LinkedIn, Glassdoor, company directories, business listing portals, etc.

If limited data is found, return partial results and note "Not Available" where applicable. Format clearly under headers like:
- Company Name
- Address
- GST
- Website
- ...
- Competitor List
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

        try:
            response = requests.post("https://api.perplexity.ai/chat/completions", json=payload, headers=headers)
            response.raise_for_status()
            response_data = response.json()

            # Safely extract content
            choices = response_data.get("choices", [{}])[0]
            content = (
                choices.get("message", {}).get("content")
                or choices.get("text")
                or "No content available."
            ).strip()

            citations = response_data.get("citations", [])

        except requests.exceptions.RequestException as e:
            st.error(f"An error occurred: {e}")
            content = "Error fetching content."

        # Display Profile Section
        if content and content != "No content available.":
            st.subheader("📄 Company Profile")
            sections = parse_profile_sections(content)

            if sections:
                for header, section_content in sections.items():
                    clean = section_content.strip()
                    if "competitor" in header.lower():
                        st.subheader("🏁 Competitor List")
                        st.success(clean if clean else "No competitors found.")
                    elif "summary" in header.lower():
                        st.subheader(f"🔍 {header}")
                        st.code(clean)
                    else:
                        st.subheader(header)
                        st.markdown(clean if clean else "Not Available")
            else:
                st.warning("Could not detect structured sections.")
                st.markdown(content)  # fallback raw display
        else:
            st.warning("No profile content received.")

        # Citations
        if citations:
            st.subheader("🔗 Citations")
            for i, citation in enumerate(citations, 1):
                st.markdown(f"{i}. {citation}")
        else:
            st.caption("No citations were returned.")
    else:
        st.warning("Please enter a valid company name.")
