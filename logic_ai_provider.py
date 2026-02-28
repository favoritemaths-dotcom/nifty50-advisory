import json
import streamlit as st
from google.oauth2 import service_account
from google.cloud import aiplatform

def _load_vertex_credentials():
    try:
        if "vertex_ai" not in st.secrets:
            return False

        raw_json = st.secrets["vertex_ai"]["json"]
        creds_dict = json.loads(raw_json)

        credentials = service_account.Credentials.from_service_account_info(
            creds_dict
        )

        aiplatform.init(
            project=creds_dict["project_id"],
            location="us-central1",
            credentials=credentials,
        )

        return True
    except Exception as e:
        print("Vertex init failed:", e)
        return False