import requests
import json

FIREBASE_API_KEY = "AIzaSyDD-C88x64BsaTbG6o9YZILJKiR0UrCa0s"
FIREBASE_AUTH_URL = "https://identitytoolkit.googleapis.com/v1/accounts"

def signup(email, password):
    url = f"{FIREBASE_AUTH_URL}:signUp?key={FIREBASE_API_KEY}"
    payload = {"email": email, "password": password, "returnSecureToken": True}
    
    r = requests.post(url, json=payload)

    # 🔍 Debugging Info - Add this to see what Firebase is telling you
    print("🔥 Firebase Signup Response:", r.text)

    if r.status_code == 200:
        return r.json()["idToken"]
    else:
        print("❌ Signup Error:", r.text)  # 👈 This will show the root cause
        return None

def login(email, password):
    url = f"{FIREBASE_AUTH_URL}:signInWithPassword?key={FIREBASE_API_KEY}"
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }
    r = requests.post(url, json=payload)
    if r.status_code == 200:
        return r.json()["idToken"]
    else:
        print("Login Error:", r.text)
        return None

def get_user(id_token):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:lookup?key={FIREBASE_API_KEY}"
    payload = {"idToken": id_token}
    r = requests.post(url, json=payload)  # ✅ Consistent and clean
    if r.status_code == 200:
        return r.json()["users"][0]["email"]
    else:
        return "User"
