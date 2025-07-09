import streamlit as st
import requests
from requests.auth import HTTPBasicAuth

st.set_page_config(page_title="Companies House Explorer", layout="wide")

# --- Hard-coded API Key (keep this secret!) ---
API_KEY = "ZWMwNjhjMGYtNWE4OS00ZDM2LWJlYjctM2VhM2YzNmRmZTQw"
auth = HTTPBasicAuth(API_KEY, "")

BASE = "https://api.company-information.service.gov.uk"

def get_json(url):
    resp = requests.get(url, auth=auth)
    if resp.status_code == 200:
        return resp.json()
    else:
        st.warning(f"API Error {resp.status_code}: {resp.text}")
        return {}

def get_company_profile(company_number):
    url = f"{BASE}/company/{company_number}"
    return get_json(url)

def get_filing_dates(company_number):
    url = f"{BASE}/company/{company_number}/filing-history"
    return get_json(url)

def get_officers(company_number):
    url = f"{BASE}/company/{company_number}/officers"
    return get_json(url)

def get_pscs(company_number):
    url = f"{BASE}/company/{company_number}/persons-with-significant-control"
    return get_json(url)

def get_charges(company_number):
    url = f"{BASE}/company/{company_number}/charges"
    return get_json(url)

def search_officer_by_name(name):
    url = f"{BASE}/search/officers?q={requests.utils.quote(name)}"
    return get_json(url)

def get_insolvency(company_number):
    url = f"{BASE}/company/{company_number}/insolvency"
    return get_json(url)

st.title("🔎 UK Companies House Explorer")

company_number = st.text_input("Enter a UK Company Number (e.g., 00000006):", "")
search_clicked = st.button("Search")

if company_number and search_clicked:
    with st.spinner("Fetching data..."):
        profile = get_company_profile(company_number)
        filings = get_filing_dates(company_number)
        officers = get_officers(company_number)
        pscs = get_pscs(company_number)
        charges = get_charges(company_number)
    
    st.header("Company Profile")
    if profile:
        st.write({
            "Name": profile.get("company_name", ""),
            "Status": profile.get("company_status", ""),
            "Type": profile.get("type", ""),
            "Incorporated On": profile.get("date_of_creation", ""),
            "Dissolved On": profile.get("date_of_cessation", ""),
            "SIC Codes": profile.get("sic_codes", []),
            "Registered Address": profile.get("registered_office_address", {}),
        })
    else:
        st.warning("No company profile found.")

    st.header("Filing History (Confirmation Statement & Accounts)")
    if filings and "items" in filings:
        for item in filings["items"]:
            typ = item.get("type", "")
            if typ in ("CS01", "AA"):
                st.write({
                    "Type": typ,
                    "Date": item.get("date"),
                    "Description": item.get("description", "")
                })
    else:
        st.warning("No filings found.")

    st.header("Officers")
    if officers and "items" in officers:
        for off in officers["items"]:
            st.write({
                "Name": off.get("name", ""),
                "Role": off.get("officer_role", ""),
                "Status": "Active" if not off.get("resigned_on") else "Resigned",
                "Appointed On": off.get("appointed_on", ""),
                "Resigned On": off.get("resigned_on", "")
            })
    else:
        st.warning("No officers found.")

    st.header("Persons with Significant Control (PSC)")
    if pscs and "items" in pscs:
        for p in pscs["items"]:
            name = p.get("name") or (p.get("name_elements") and " ".join(p["name_elements"].values())) or ""
            st.write({
                "Name": name,
                "Nature of Control": p.get("nature_of_control", []),
                "Active": "No" if p.get("ceased_on") else "Yes"
            })
    else:
        st.warning("No PSCs found.")

    st.header("Company Charges")
    if charges and "items" in charges:
        for ch in charges["items"]:
            st.write({
                "Charge Code": ch.get("charge_code", ""),
                "Status": ch.get("status", ""),
                "Created On": ch.get("created_on", ""),
                "Secured": ch.get("secured_details", [{}])[0].get("description", "") if ch.get("secured_details") else ""
            })
    else:
        st.warning("No charges found.")

    st.header("Officer Cross-Check (Other Directorships & Insolvency)")
    if officers and "items" in officers:
        for off in officers["items"]:
            if not off.get("resigned_on"):
                st.subheader(f"Other directorships for {off.get('name')}:")
                search_result = search_officer_by_name(off.get("name"))
                found = False
                if "items" in search_result:
                    for item in search_result["items"]:
                        appts = item.get("appointments", 0)
                        if appts == 0:
                            continue
                        for link in item.get("links", {}).get("officer", {}).get("appointments", []):
                            cnum = link.get("company_number")
                            if not cnum or cnum == company_number:
                                continue
                            comp = get_company_profile(cnum)
                            status = comp.get("company_status", "")
                            insolvency_info = get_insolvency(cnum)
                            insolvent = "Yes" if insolvency_info.get("cases") else "No"
                            st.write({
                                "Company Number": cnum,
                                "Company Name": comp.get("company_name", ""),
                                "Status": status,
                                "Insolvency": insolvent
                            })
                            found = True
                if not found:
                    st.info("No other directorships found or no insolvency history.")

st.sidebar.info("💡 Tip: The API key is hard-coded in this app. For security, do not share this file publicly.")
