








# from fastapi import FastAPI, Request
# from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
# from fastapi.staticfiles import StaticFiles
# from starlette.middleware.sessions import SessionMiddleware
# from fastapi.responses import JSONResponse
# import os
# import subprocess
# from dotenv import load_dotenv
# import threading
# import sys
# import time
# import httpx
# from after_login.frontend.bakend.main import initialize_agent, llm, get_sentiment



# # Load environment variables
# load_dotenv()

# app = FastAPI()

# def run_services():
#     try:
#         base_dir = os.path.dirname(os.path.abspath(__file__))
#         frontend_dir = os.path.join(base_dir, "after_login", "frontend")
        
#         # Set up environment
#         env = os.environ.copy()
#         env["PYTHONPATH"] = f"{frontend_dir}{os.pathsep}{env.get('PYTHONPATH', '')}"
        
#         # Start Chatbot Service with detailed logging
#     # Start root-level chatbot (main.py) service
#         chatbot_log2 = open(os.path.join(base_dir, "chatbot2.log"), "w")
#         chatbot_proc2 = subprocess.Popen(
#             [sys.executable, "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9000", "--reload"],
#             cwd=frontend_dir,
#             env=env,
#             stdout=chatbot_log2,
#             stderr=subprocess.STDOUT
#         )
#         chatbot_log = open(os.path.join(base_dir, "chatbot.log"), "w")
#         chatbot_proc = subprocess.Popen(
#             [sys.executable, "-m", "uvicorn", "bakend.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"],
#             cwd=os.path.join(base_dir, "after_login", "frontend"),
#             env=env,
#             stdout=chatbot_log,
#             stderr=subprocess.STDOUT
#         )        
#         # Start Forecasting Service (working)
#         forecast_proc = subprocess.Popen(
#             [sys.executable, "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8001"],
#             cwd=frontend_dir,
#             env=env
#         )
        
#         # Verify services
#         time.sleep(3)
#         if chatbot_proc.poll() is not None:
#             chatbot_log.close()
#             with open(os.path.join(base_dir, "chatbot.log"), "r") as f:
#                 print("CHATBOT ERROR LOG:\n" + f.read())
#             raise RuntimeError("Chatbot failed to start - see chatbot.log")
            
#         return (chatbot_proc, forecast_proc, chatbot_proc2)
        
#     except Exception as e:
#         print(f"Service startup failed: {str(e)}", file=sys.stderr)
#         sys.exit(1)
        
# # Start services in a separate thread
# services_thread = threading.Thread(target=run_services, daemon=True)
# services_thread.start()

# # ... [rest of your existing connect.py code remains exactly the same]# Rest of your original code remains exactly the same...

# # Rest of your existing connect.py code...
# SECRET = os.getenv("SESSION_SECRET", "a-very-secret-key-that-you-should-change")
# app.add_middleware(
#     SessionMiddleware,
#     secret_key=SECRET,
#     same_site="lax",
#     https_only=False
# )

# # ... (keep all your existing mount points and routes)
# # Mount static directories
# app.mount("/static", StaticFiles(directory="static"), name="static")
# app.mount("/login_page", StaticFiles(directory="login_page"), name="login_page")
# app.mount("/after_login", StaticFiles(directory="after_login"), name="after_login")

# @app.get("/", response_class=HTMLResponse)
# def get_home():
#     return FileResponse("index.html")

# @app.get("/login", response_class=HTMLResponse)
# def get_login_page():
#     return FileResponse("login_page/page.html")

# @app.get("/dashboard", response_class=HTMLResponse)
# def get_dashboard(request: Request):
#     if not request.session.get("firebase_user"):
#         return RedirectResponse(url="/login", status_code=302)
#     return FileResponse("after_login/frontend/UI.html")

# @app.post("/session-login")
# async def create_session(request: Request):
#     try:
#         body = await request.json()
#         email = body.get("email")
#         if email:
#             request.session["firebase_user"] = email
#             return {"status": "success", "message": "Session created"}
#         return {"status": "error", "message": "Email not provided"}, 400
#     except Exception as e:
#         return {"status": "error", "message": str(e)}, 500
# import httpx

# import httpx

# @app.post("/chat")
# async def chat_endpoint(request: Request):
#     data = await request.json()
#     user_message = data.get("message", "")
#     async with httpx.AsyncClient() as client:
#         try:
#             resp = await client.post(
#                 "http://localhost:8000/chat",
#                 json={"message": user_message},
#                 timeout=10
#             )
#             resp.raise_for_status()
#             chatbot_response = resp.json().get("response")
#             return JSONResponse({"response": chatbot_response})
#         except Exception as e:
#             return JSONResponse({"response": f"Error contacting chatbot: {e}"})
# @app.get("/logout")
# def logout(request: Request):
#     request.session.clear()
#     return RedirectResponse(url="/login", status_code=302)