import requests
import streamlit as st

BACKEND_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="AI Attendance System", page_icon="🔒", layout="centered")

if "token" not in st.session_state:
    st.session_state.token = None
    st.session_state.role = None
    st.session_state.username = None


def auth_headers():
    return {"Authorization": f"Bearer {st.session_state.token}"}


with st.sidebar:
    st.header("Admin / HR login")
    if st.session_state.token is None:
        login_username = st.text_input("Username")
        login_password = st.text_input("Password", type="password")
        if st.button("Log in"):
            resp = requests.post(
                f"{BACKEND_URL}/auth/login",
                data={"username": login_username, "password": login_password},
            )
            if resp.status_code == 200:
                data = resp.json()
                st.session_state.token = data["access_token"]
                st.session_state.role = data["role"]
                st.session_state.username = login_username
                st.rerun()
            else:
                st.error(resp.json().get("detail", "Login failed"))
    else:
        st.success(f"Logged in as {st.session_state.username} ({st.session_state.role})")
        if st.button("Log out"):
            st.session_state.token = None
            st.session_state.role = None
            st.session_state.username = None
            st.rerun()

st.title("🔒 AI Attendance System")

st.subheader("Mark attendance")
recognize_photo = st.camera_input("Look at the camera and take a photo", key="recognize_cam")

if recognize_photo is not None:
    files = {"file": (recognize_photo.name, recognize_photo.getvalue(), "image/jpeg")}
    resp = requests.post(f"{BACKEND_URL}/recognize", files=files)

    if resp.status_code == 200:
        result = resp.json()
        if result["recognized"]:
            if result["attendance_marked"]:
                st.success(
                    f"Recognized **{result['name']}** (similarity {result['similarity']:.0%}) "
                    f"— attendance marked at {result['check_in_time']}."
                )
            else:
                st.info(
                    f"Recognized **{result['name']}** — already marked present today "
                    f"at {result['check_in_time']}."
                )
        else:
            st.warning("Face not recognized. Ask an admin/HR to enroll you.")
    else:
        detail = resp.json().get("detail", resp.text)
        st.error(detail if isinstance(detail, str) else detail.get("message", str(detail)))

if st.session_state.token is not None:
    st.divider()
    st.subheader("Enroll a new person (admin/HR only)")

    employee_code = st.text_input("Employee code")
    name = st.text_input("Full name")
    department = st.text_input("Department")
    label = st.text_input("Label for this photo (e.g. front, left, right, smile)", value="front")
    enroll_photo = st.camera_input("Take an enrollment photo", key="enroll_cam")

    if st.button("Enroll", disabled=enroll_photo is None or not employee_code or not name):
        files = {"file": (enroll_photo.name, enroll_photo.getvalue(), "image/jpeg")}
        data = {
            "employee_code": employee_code,
            "name": name,
            "department": department,
            "label": label,
        }
        resp = requests.post(f"{BACKEND_URL}/enroll", files=files, data=data, headers=auth_headers())

        if resp.status_code == 200:
            st.success(f"Enrolled {name} successfully.")
        else:
            detail = resp.json().get("detail", resp.text)
            st.error(detail if isinstance(detail, str) else detail.get("message", str(detail)))

    st.divider()
    st.subheader("Today's attendance")
    resp = requests.get(f"{BACKEND_URL}/attendance/today")
    if resp.status_code == 200:
        records = resp.json()
        if records:
            st.dataframe(records, hide_index=True)
        else:
            st.write("_No one has been marked present today yet._")