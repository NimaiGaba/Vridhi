from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
import os
import time
import httpx
from dotenv import load_dotenv
from after_login.runall import start_services

# Load environment variables
load_dotenv()

app = FastAPI()

SECRET = os.getenv("SESSION_SECRET", "a-very-secret-key-that-you-should-change")
app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET,
    same_site="lax",
    https_only=False
)

# Mount static directories
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/login_page", StaticFiles(directory="login_page"), name="login_page")
app.mount("/after_login", StaticFiles(directory="after_login"), name="after_login")

@app.on_event("startup")
async def startup_event():
    # 🚀 Auto-start chatbot & forecasting on app launch
    print("🚀 Auto-starting chatbot & forecasting services...")
    start_services()

@app.get("/", response_class=HTMLResponse)
def get_home():
    return FileResponse("index.html")

@app.get("/login", response_class=HTMLResponse)
def get_login_page():
    return FileResponse("login_page/page.html")

@app.get("/dashboard", response_class=HTMLResponse)
def get_dashboard(request: Request):
    if not request.session.get("firebase_user"):
        return RedirectResponse(url="/login", status_code=302)
    return FileResponse("after_login/frontend/UI.html")

def wait_for_service(url, timeout=15):
    start = time.time()
    while time.time() - start < timeout:
        try:
            r = httpx.get(url)
            if r.status_code in [200, 404]:  # service is running
                return True
        except:
            time.sleep(1)
    return False

@app.post("/session-login")
async def create_session(request: Request):
    body = await request.json()
    email = body.get("email")
    if not email:
        return {"status": "error", "message": "Email not provided"}, 400

    request.session["firebase_user"] = email

    # Wait for chatbot and forecasting (if needed)
    if not wait_for_service("http://127.0.0.1:8002/"):
        return {"status": "error", "message": "Chatbot failed to start"}
    if not wait_for_service("http://127.0.0.1:8001/"):
        return {"status": "error", "message": "Forecasting failed to start"}

    return {"status": "success", "message": "Session created"}

@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=302)
