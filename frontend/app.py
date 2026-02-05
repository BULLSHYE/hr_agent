# import streamlit as st
# import requests
# from concurrent.futures import ThreadPoolExecutor

# API_BASE = "http://localhost:8000"

# def fetch_dashboard_data():
#     def fetch_jd_count():
#         try:
#             res = requests.get(f"{API_BASE}/jd/count")
#             return res.json().get("count", 0) if res.status_code == 200 else "Error"
#         except:
#             return "Error"

#     def fetch_candidate_count():
#         try:
#             res = requests.get(f"{API_BASE}/candidates/count")
#             return res.json().get("count", 0) if res.status_code == 200 else "Error"
#         except:
#             return "Error"

#     def fetch_current_model():
#         try:
#             res = requests.get(f"{API_BASE}/model/current-model")
#             return res.json() if res.status_code == 200 else {"provider": "Unknown", "model": "Unknown"}
#         except:
#             return {"provider": "Unknown", "model": "Unknown"}

#     with ThreadPoolExecutor(max_workers=3) as executor:
#         jd_future = executor.submit(fetch_jd_count)
#         candidate_future = executor.submit(fetch_candidate_count)
#         model_future = executor.submit(fetch_current_model)

#         jd_count = jd_future.result()
#         candidate_count = candidate_future.result()
#         current_model = model_future.result()

#     return jd_count, candidate_count, current_model

# def fetch_available_models():
#     try:
#         res = requests.get(f"{API_BASE}/model/available-models")
#         if res.status_code == 200:
#             providers = res.json().get("providers", {})
#             models = []
#             for provider, model_list in providers.items():
#                 for model in model_list:
#                     models.append(f"{model} ({provider})")
#             return models
#         return ["gpt-4o-mini (openai)", "claude-3-5-sonnet-20241022 (anthropic)", "gemini-1.5-pro (gemini)"]
#     except:
#         return ["gpt-4o-mini (openai)"]
# def fetch_jd_titles():
#     try:
#         res = requests.get(f"{API_BASE}/jd/titles")
#         if res.status_code == 200:
#             return res.json().get("titles", [])
#         return []
#     except:
#         return []

# st.set_page_config(page_title="AI HR Agent", layout="wide")

# st.title("🤖 AI-Powered HR Recruitment Agent")

# menu = st.sidebar.selectbox(
#     "Navigation",
#     [
#         "Login",
#         "Dashboard",
#         "Model Selection",
#         "Job Description",
#         "Candidates",
#         "Search Candidates",
#         "Match & Score",
#         "Send Email"
#     ]
# )

# # Global state for auth
# if "token" not in st.session_state:
#     st.session_state.token = None
# if "user" not in st.session_state:
#     st.session_state.user = None

# # ----------------------------
# # LOGIN
# # ----------------------------
# if menu == "Login":
#     st.header("🔐 Login")

#     if st.session_state.token:
#         st.success(f"Logged in as {st.session_state.user['username']} ({st.session_state.user['role']})")
#         if st.button("Logout"):
#             st.session_state.token = None
#             st.session_state.user = None
#             st.rerun()
#     else:
#         tab1, tab2 = st.tabs(["Login", "Register"])

#         with tab1:
#             username = st.text_input("Username")
#             password = st.text_input("Password", type="password")
#             if st.button("Login"):
#                 res = requests.post(f"{API_BASE}/auth/login", json={"username": username, "password": password})
#                 if res.status_code == 200:
#                     data = res.json()
#                     st.session_state.token = data["access_token"]
#                     # Get user info
#                     headers = {"Authorization": f"Bearer {st.session_state.token}"}
#                     user_res = requests.get(f"{API_BASE}/auth/me", headers=headers)
#                     if user_res.status_code == 200:
#                         st.session_state.user = user_res.json()
#                         st.success("Login successful!")
#                         st.rerun()
#                     else:
#                         st.error("Failed to get user info")
#                 else:
#                     st.error("Login failed")

#         with tab2:
#             reg_username = st.text_input("Username", key="reg_user")
#             reg_email = st.text_input("Email", key="reg_email")
#             reg_password = st.text_input("Password", type="password", key="reg_pass")
#             reg_role = st.selectbox("Role", ["hr", "admin"], key="reg_role")
#             if st.button("Register"):
#                 res = requests.post(f"{API_BASE}/auth/register", json={
#                     "username": reg_username,
#                     "email": reg_email,
#                     "password": reg_password,
#                     "role": reg_role
#                 })
#                 if res.status_code == 200:
#                     st.success("Registration successful! Please login.")
#                 else:
#                     st.error("Registration failed")

# # Only show other menus if logged in
# if not st.session_state.token:
#     st.stop()

# # Add token to headers for all requests
# headers = {"Authorization": f"Bearer {st.session_state.token}"}

# # ----------------------------
# # DASHBOARD
# # ----------------------------
# if menu == "Dashboard":
#     st.header("📊 Dashboard")

#     # Fetch all data in parallel
#     jd_count, candidate_count, current_model = fetch_dashboard_data()

#     col1, col2 = st.columns(2)

#     with col1:
#         st.subheader("Job Descriptions")
#         st.metric("Total JDs", jd_count)

#         if st.button("Peek JDs"):
#             try:
#                 res = requests.get(f"{API_BASE}/jd/peek", params={"n": 5}, headers=headers)
#                 st.json(res.json())
#             except:
#                 st.error("Failed to fetch JD data")

#     with col2:
#         st.subheader("Candidates")
#         st.metric("Total Candidates", candidate_count)

#         if st.button("Peek Candidates"):
#             try:
#                 res = requests.get(f"{API_BASE}/candidates/peek", params={"n": 5}, headers=headers)
#                 st.json(res.json())
#             except:
#                 st.error("Failed to fetch candidate data")

#     st.subheader("Current Model")
#     try:
#         res = requests.get(f"{API_BASE}/model/current-model", headers=headers)
#         st.json(res.json())
#     except:
#         st.error("Failed to fetch current model")

# # ----------------------------
# # MODEL SELECTION
# # ----------------------------
# if menu == "Model Selection":
#     st.header("🔀 Select LLM Model")

#     available_models = fetch_available_models()
#     selected_model = st.selectbox("Model Name", available_models, index=0 if available_models else 0)
#     model_name = selected_model.split(" (")[0] if " (" in selected_model else selected_model
#     api_key = st.text_input("API Key (optional)", type="password")

#     if st.button("Select Model"):
#         # Extract provider from selected_model string
#         if " (" in selected_model and selected_model.endswith(")"):
#             provider = selected_model.split(" (")[-1].rstrip(")")
#         else:
#             provider = "openai"  # fallback
        
#         payload = {"provider": provider, "model": model_name}
#         if api_key:
#             payload["api_key"] = api_key
#         res = requests.post(f"{API_BASE}/model/set-model", json=payload)
#         if res.status_code == 200:
#             st.success(res.json())
#         else:
#             st.error(res.json())

# # ----------------------------
# # JD HANDLING
# # ----------------------------
# elif menu == "Job Description":
#     st.header("📄 Job Description")

#     tab1, tab2 = st.tabs(["Upload JD", "Generate JD"])

#     with tab1:
#         file = st.file_uploader("Upload JD (PDF, DOCX, TXT)")
#         if st.button("Upload"):
#             files = {"file": file}
#             res = requests.post(f"{API_BASE}/jd/upload", files=files)
#             st.json(res.json())

#     with tab2:
#         company_name = st.text_input("Company Name")
#         company_url = st.text_input("Company URL")
#         job_role = st.text_input("Job Role")
#         location = st.text_input("Location")
#         experience_range = st.text_input("Experience Range")
#         required_skills = st.text_input("Required Skills")
#         job_description = st.text_area("Job Description (optional)", height=100)

#         if st.button("Generate Preview"):
#             payload = {
#                 "company_name": company_name,
#                 "company_url": company_url,
#                 "job_role": job_role,
#                 "location": location,
#                 "experience_range": experience_range,
#                 "required_skills": required_skills,
#                 "job_description": job_description if job_description else None
#             }
#             res = requests.post(f"{API_BASE}/jd/generate", json=payload)
#             if res.status_code == 200:
#                 st.session_state["preview_jd"] = res.json()
#                 st.success("AI-generated JD preview ready for editing!")
#             else:
#                 st.error("Failed to generate preview")

#         if "preview_jd" in st.session_state:
#             st.subheader("Edit Generated JD")
#             edited_jd = st.text_area("Job Description", st.session_state["preview_jd"]["job_description"], height=300)
            
#             if st.button("Finalize & Save JD"):
#                 structured_jd = st.session_state["preview_jd"]
#                 structured_jd["job_description"] = edited_jd
#                 res = requests.post(f"{API_BASE}/jd/finalize", json=structured_jd)
#                 if res.status_code == 200:
#                     st.success("JD finalized and saved successfully!")
#                     del st.session_state["preview_jd"]
#                 else:
#                     st.error("Failed to save JD")

# # ----------------------------
# # CANDIDATES
# # ----------------------------
# elif menu == "Candidates":
#     st.header("👤 Candidate Discovery")

#     if st.button("Fetch Candidates"):
#         res = requests.post(f"{API_BASE}/candidates/fetch")
#         st.session_state["candidates"] = res.json()
#         st.json(res.json())

#     if "candidates" in st.session_state:
#         if st.button("Store Candidates in Vector DB"):
#             res = requests.post(f"{API_BASE}/candidates/store-from-fetch")
#             st.success(res.json())

# # ----------------------------
# # SEARCH
# # ----------------------------
# elif menu == "Search Candidates":
#     st.header("🔍 Semantic Candidate Search")

#     query = st.text_input("Search Query (e.g., Python ML 4 years)")

#     if st.button("Search"):
#         res = requests.get(f"{API_BASE}/candidates/search", params={"query": query})
#         st.json(res.json())

# # ----------------------------
# # MATCH & SCORE
# # ----------------------------
# elif menu == "Match & Score":
#     st.header("⚖️ Match JD with Candidates")
#     if "jd_titles" not in st.session_state:
#         st.session_state["jd_titles"] = fetch_jd_titles()
#     jd_titles = st.session_state["jd_titles"]   
#     # jd_titles = fetch_jd_titles()
#     selected_title = st.selectbox("Select Job Role", jd_titles if jd_titles else ["No JDs available"], index=0)

#     if st.button("Run Matching"):
#         payload = {"title": selected_title, "n_results": 5}
#         res = requests.post(f"{API_BASE}/match/score", json=payload)
#         if res.status_code == 200:
#             matches = res.json().get("matches", [])
#             st.session_state["matches"] = matches
#             st.session_state["selected_jd"] = selected_title
#             st.success(f"Found {len(matches)} matches")
#         else:
#             error_detail = res.json().get("detail", "Unknown error")
#             st.error(f"Failed to run matching: {error_detail}")

#     if "matches" in st.session_state:
#         st.subheader("Matched Candidates")
#         for i, match in enumerate(st.session_state["matches"]):
#             with st.expander(f"👤 {match['name']} - Score: {match['score']}/100"):
#                 col1, col2 = st.columns([3, 1])
#                 with col1:
#                     st.write(f"**Skills:** {match['skills']}")
#                     st.write(f"**Experience:** {match['experience']}")
#                     st.write(f"**Reason:** {match['reason']}")
#                     st.write(f"**Email:** {match.get('email', 'N/A')}")
#                 with col2:
#                     if st.button(f"Send Email to {match['name']}", key=f"email_{i}"):
#                         payload = {
#                             "title": st.session_state["selected_jd"],
#                             "candidate_name": match["name"],
#                             "candidate_email": match.get("email", ""),
#                             "score": match["score"],
#                             "reason": match["reason"]
#                         }
#                         email_res = requests.post(f"{API_BASE}/email/send-emails", json=payload)
#                         if email_res.status_code == 200:
#                             st.success(f"Emails sent to {match['name']} and HR!")
#                         else:
#                             st.error(f"Failed to send emails: {email_res.json()}")

# # ----------------------------
# # EMAIL
# # ----------------------------
# elif menu == "Send Email":
#     st.header("✉️ Send Shortlist Emails")

#     jd_title = st.text_input("Job Description Title")
#     candidate_name = st.text_input("Candidate Name")
#     candidate_email = st.text_input("Candidate Email")
#     score = st.number_input("Score", 0, 100, 80)
#     reason = st.text_area("Reason")

#     if st.button("Send Emails"):
#         if score <= 60:
#             st.error("Candidate score must be greater than 60 to send emails")
#         else:
#             payload = {
#                 "title": jd_title,
#                 "candidate_name": candidate_name,
#                 "candidate_email": candidate_email,
#                 "score": score,
#                 "reason": reason
#             }
#             res = requests.post(f"{API_BASE}/email/send-emails", json=payload)
#             if res.status_code == 200:
#                 st.success(res.json())
#             else:
#                 st.error(res.json())

import streamlit as st
import requests
from concurrent.futures import ThreadPoolExecutor

API_BASE = "http://127.0.0.1:8000"

def fetch_dashboard_data():
    def fetch_jd_count():
        try:
            res = requests.get(f"{API_BASE}/jd/count")
            return res.json().get("count", 0) if res.status_code == 200 else "Error"
        except:
            return "Error"

    def fetch_candidate_count():
        try:
            res = requests.get(f"{API_BASE}/candidates/count")
            return res.json().get("count", 0) if res.status_code == 200 else "Error"
        except:
            return "Error"

    def fetch_current_model():
        try:
            res = requests.get(f"{API_BASE}/model/current-model")
            return res.json() if res.status_code == 200 else {"provider": "Unknown", "model": "Unknown"}
        except:
            return {"provider": "Unknown", "model": "Unknown"}

    with ThreadPoolExecutor(max_workers=3) as executor:
        jd_future = executor.submit(fetch_jd_count)
        candidate_future = executor.submit(fetch_candidate_count)
        model_future = executor.submit(fetch_current_model)

        jd_count = jd_future.result()
        candidate_count = candidate_future.result()
        current_model = model_future.result()

    return jd_count, candidate_count, current_model

def fetch_available_models():
    try:
        res = requests.get(f"{API_BASE}/model/available-models")
        if res.status_code == 200:
            providers = res.json().get("providers", {})
            models = []
            # Store mapping of display name to actual name for later use
            if "model_mapping" not in st.session_state:
                st.session_state.model_mapping = {}
            
            for provider, model_list in providers.items():
                for model in model_list:
                    # Extract name and display from model dict
                    model_name = model.get("name", model) if isinstance(model, dict) else model
                    model_display = model.get("display", model_name) if isinstance(model, dict) else model_name
                    display_with_provider = f"{model_display} ({provider})"
                    models.append(display_with_provider)
                    # Store mapping for later retrieval
                    st.session_state.model_mapping[display_with_provider] = {
                        "name": model_name,
                        "provider": provider
                    }
            return models
        return ["GPT-5.2 (Latest) (openai)", "Claude Sonnet 4.5 (anthropic)", "Gemini 2.5 Pro (gemini)"]
    except:
        return ["GPT-5.2 (Latest) (openai)"]
def fetch_jd_titles():
    try:
        res = requests.get(f"{API_BASE}/jd/titles")
        if res.status_code == 200:
            return res.json().get("titles", [])
        return []
    except:
        return []

st.set_page_config(page_title="AI HR Agent", layout="wide")

st.title("🤖 AI-Powered HR Recruitment Agent")

st.markdown(
    """
    <style>
    section[data-testid="stSidebar"] .stButton > button {
        justify-content: flex-start;
        text-align: left;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Global state for auth
if "token" not in st.session_state:
    st.session_state.token = None
if "user" not in st.session_state:
    st.session_state.user = None

is_authenticated = st.session_state.token is not None

MENU_ITEMS = [
    "Dashboard",
    "Model Selection",
    "Job Description",
    "Candidates",
    "Search Candidates",
    "Match & Score",
    "Send Email"
]

if "menu" not in st.session_state:
    st.session_state.menu = "Dashboard"

if is_authenticated:
    st.sidebar.markdown(
        f"**Logged in as:** {st.session_state.user['username']} ({st.session_state.user['role']})"
    )
    if st.sidebar.button("Logout"):
        st.session_state.token = None
        st.session_state.user = None
        st.session_state.menu = "Dashboard"
        st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.subheader("Navigation")
    for item in MENU_ITEMS:
        label = f"➡️ {item}" if st.session_state.menu == item else item
        if st.sidebar.button(label, use_container_width=True):
            st.session_state.menu = item
            st.rerun()

    menu = st.session_state.menu
else:
    st.sidebar.markdown("**Please login to continue.**")
    menu = "Login"

# ----------------------------
# LOGIN
# ----------------------------
if menu == "Login":
    st.header("🔐 Login")

    if st.session_state.token:
        st.success(f"Logged in as {st.session_state.user['username']} ({st.session_state.user['role']})")
        if st.button("Logout"):
            st.session_state.token = None
            st.session_state.user = None
            st.rerun()
    else:
        tab1, tab2 = st.tabs(["Login", "Register"])

        with tab1:
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            if st.button("Login"):
                res = requests.post(f"{API_BASE}/auth/login", json={"username": username, "password": password})
                if res.status_code == 200:
                    data = res.json()
                    st.session_state.token = data["access_token"]
                    # Get user info
                    headers = {"Authorization": f"Bearer {st.session_state.token}"}
                    user_res = requests.get(f"{API_BASE}/auth/me", headers=headers)
                    if user_res.status_code == 200:
                        st.session_state.user = user_res.json()
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error("Failed to get user info")
                else:
                    st.error("Login failed")

        with tab2:
            reg_username = st.text_input("Username", key="reg_user")
            reg_email = st.text_input("Email", key="reg_email")
            reg_password = st.text_input("Password", type="password", key="reg_pass")
            reg_role = st.selectbox("Role", ["hr", "admin"], key="reg_role")
            if st.button("Register"):
                res = requests.post(f"{API_BASE}/auth/register", json={
                    "username": reg_username,
                    "email": reg_email,
                    "password": reg_password,
                    "role": reg_role
                })
                if res.status_code == 200:
                    st.success("Registration successful! Please login.")
                else:
                    st.error("Registration failed")

# Only show other menus if logged in
if not st.session_state.token:
    st.stop()

# Add token to headers for all requests
headers = {"Authorization": f"Bearer {st.session_state.token}"}

# ----------------------------
# DASHBOARD
# ----------------------------
if menu == "Dashboard":
    st.header("📊 Dashboard")

    # Fetch all data in parallel
    jd_count, candidate_count, current_model = fetch_dashboard_data()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Job Descriptions")
        st.metric("Total JDs", jd_count)

        if st.button("Peek JDs"):
            try:
                res = requests.get(f"{API_BASE}/jd/peek", params={"n": 5}, headers=headers)
                st.json(res.json())
            except:
                st.error("Failed to fetch JD data")

    with col2:
        st.subheader("Candidates")
        st.metric("Total Candidates", candidate_count)

        if st.button("Peek Candidates"):
            try:
                res = requests.get(f"{API_BASE}/candidates/peek", params={"n": 5}, headers=headers)
                st.json(res.json())
            except:
                st.error("Failed to fetch candidate data")

    st.subheader("Current Model")
    try:
        res = requests.get(f"{API_BASE}/model/current-model", headers=headers)
        model_info = res.json()
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Provider", model_info.get("provider", "Unknown"))
        with col2:
            display_name = model_info.get("display", model_info.get("model", "Unknown"))
            st.metric("Model", display_name)
    except:
        st.error("Failed to fetch current model")

# ----------------------------
# MODEL SELECTION
# ----------------------------
if menu == "Model Selection":
    st.header("🔀 Select LLM Model")

    available_models = fetch_available_models()
    selected_model = st.selectbox("Model Name", available_models, index=0 if available_models else 0)
    api_key = st.text_input("API Key (optional)", type="password")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Set Model", use_container_width=True):
            if not selected_model:
                st.error("Please select a model")
            else:
                # Get actual model name and provider from mapping
                model_info = st.session_state.get("model_mapping", {}).get(selected_model)
                if not model_info:
                    st.error("Model information not found")
                else:
                    model_name = model_info["name"]
                    provider = model_info["provider"]
                    
                    payload = {"provider": provider, "model": model_name}
                    if api_key:
                        payload["api_key"] = api_key
                    
                    try:
                        res = requests.post(f"{API_BASE}/model/set-model", json=payload, headers=headers)
                        if res.status_code == 200:
                            data = res.json()
                            st.success(f"✅ {data.get('message', 'Model set successfully')}")
                            st.session_state["model_changed"] = True
                            st.rerun()
                        else:
                            error_detail = res.json().get("detail", "Failed to set model")
                            st.error(f"❌ Error: {error_detail}")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
    
    with col2:
        if st.button("Refresh", use_container_width=True):
            st.rerun()

# ----------------------------
# JD HANDLING
# ----------------------------
elif menu == "Job Description":
    st.header("📄 Job Description")

    tab1, tab2 = st.tabs(["Upload JD", "Generate JD"])

    with tab1:
        file = st.file_uploader("Upload JD (PDF, DOCX, TXT)")
        if st.button("Upload"):
            files = {"file": file}
            res = requests.post(f"{API_BASE}/jd/upload", files=files)
            st.json(res.json())

    with tab2:
        company_name = st.text_input("Company Name")
        company_url = st.text_input("Company URL")
        job_role = st.text_input("Job Role")
        location = st.text_input("Location")
        experience_range = st.text_input("Experience Range")
        required_skills = st.text_input("Required Skills")
        job_description = st.text_area("Job Description (optional)", height=100)

        if st.button("Generate Preview"):
            payload = {
                "company_name": company_name,
                "company_url": company_url,
                "job_role": job_role,
                "location": location,
                "experience_range": experience_range,
                "required_skills": required_skills,
                "job_description": job_description if job_description else None
            }
            res = requests.post(f"{API_BASE}/jd/generate", json=payload)
            if res.status_code == 200:
                st.session_state["preview_jd"] = res.json()
                st.success("AI-generated JD preview ready for editing!")
            else:
                st.error("Failed to generate preview")

        if "preview_jd" in st.session_state:
            st.subheader("Edit Generated JD")
            edited_jd = st.text_area("Job Description", st.session_state["preview_jd"]["job_description"], height=300)
            
            if st.button("Finalize & Save JD"):
                structured_jd = st.session_state["preview_jd"]
                structured_jd["job_description"] = edited_jd
                res = requests.post(f"{API_BASE}/jd/finalize", json=structured_jd)
                if res.status_code == 200:
                    st.success("JD finalized and saved successfully!")
                    del st.session_state["preview_jd"]
                else:
                    st.error("Failed to save JD")

# ----------------------------
# CANDIDATES
# ----------------------------
elif menu == "Candidates":
    st.header("👤 Candidate Discovery")

    if st.button("Fetch Candidates"):
        res = requests.post(f"{API_BASE}/candidates/fetch")
        st.session_state["candidates"] = res.json()
        st.json(res.json())

    if "candidates" in st.session_state:
        if st.button("Store Candidates in Vector DB"):
            res = requests.post(f"{API_BASE}/candidates/store-from-fetch")
            st.success(res.json())

# ----------------------------
# SEARCH
# ----------------------------
elif menu == "Search Candidates":
    st.header("🔍 Semantic Candidate Search")

    query = st.text_input("Search Query (e.g., Python ML 4 years)")

    if st.button("Search"):
        res = requests.get(f"{API_BASE}/candidates/search", params={"query": query})
        st.json(res.json())

# ----------------------------
# MATCH & SCORE
# ----------------------------
elif menu == "Match & Score":
    st.header("⚖️ Match JD with Candidates")
    if "jd_titles" not in st.session_state:
        st.session_state["jd_titles"] = fetch_jd_titles()
    jd_titles = st.session_state["jd_titles"]   
    # jd_titles = fetch_jd_titles()
    selected_title = st.selectbox("Select Job Role", jd_titles if jd_titles else ["No JDs available"], index=0)

    if st.button("Run Matching"):
        payload = {"title": selected_title, "n_results": 5}
        res = requests.post(f"{API_BASE}/match/score", json=payload)
        if res.status_code == 200:
            matches = res.json().get("matches", [])
            st.session_state["matches"] = matches
            st.session_state["selected_jd"] = selected_title
            st.success(f"Found {len(matches)} matches")
        else:
            error_detail = res.json().get("detail", "Unknown error")
            st.error(f"Failed to run matching: {error_detail}")

    if "matches" in st.session_state:
        st.subheader("Matched Candidates")
        for i, match in enumerate(st.session_state["matches"]):
            with st.expander(f"👤 {match['name']} - Score: {match['score']}/100"):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**Skills:** {match['skills']}")
                    st.write(f"**Experience:** {match['experience']}")
                    st.write(f"**Reason:** {match['reason']}")
                    st.write(f"**Email:** {match.get('email', 'N/A')}")
                with col2:
                    if st.button(f"Send Email to {match['name']}", key=f"email_{i}"):
                        payload = {
                            "title": st.session_state["selected_jd"],
                            "candidate_name": match["name"],
                            "candidate_email": match.get("email", ""),
                            "score": match["score"],
                            "reason": match["reason"]
                        }
                        email_res = requests.post(f"{API_BASE}/email/send-emails", json=payload)
                        if email_res.status_code == 200:
                            st.success(f"Emails sent to {match['name']} and HR!")
                        else:
                            st.error(f"Failed to send emails: {email_res.json()}")

# ----------------------------
# EMAIL
# ----------------------------
elif menu == "Send Email":
    st.header("✉️ Send Shortlist Emails")

    jd_title = st.text_input("Job Description Title")
    candidate_name = st.text_input("Candidate Name")
    candidate_email = st.text_input("Candidate Email")
    score = st.number_input("Score", 0, 100, 80)
    reason = st.text_area("Reason")

    if st.button("Send Emails"):
        if score <= 60:
            st.error("Candidate score must be greater than 60 to send emails")
        else:
            payload = {
                "title": jd_title,
                "candidate_name": candidate_name,
                "candidate_email": candidate_email,
                "score": score,
                "reason": reason
            }
            res = requests.post(f"{API_BASE}/email/send-emails", json=payload)
            if res.status_code == 200:
                st.success(res.json())
            else:
                st.error(res.json())