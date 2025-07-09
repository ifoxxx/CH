import streamlit as st
from compynieshouse import CompaniesHouseClient

st.title("🔍 Companies House Search")

# Input for company name
company_name = st.text_input("Enter a company name to search:")

if company_name:
    client = CompaniesHouseClient(st.secrets["companies_house"]["api_key"])
    try:
        results = client.search_companies(company_name)
        for item in results.get("items", []):
            st.subheader(item["title"])
            st.write(f"Company Number: {item['company_number']}")
            st.write(f"Status: {item.get('company_status', 'N/A')}")
            st.write("---")
    except Exception as e:
        st.error(f"Error: {e}")
