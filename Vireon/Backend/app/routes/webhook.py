# app/routes/oauth.py

from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
import os, requests
from app.database import supabase
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

@router.get("/oauth/callback")
async def oauth_callback(request: Request):
    code = request.query_params.get("code")

    # Intercambiás el code por tokens
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "code": code,
        "client_id": os.getenv("GMAIL_CLIENT_ID"),
        "client_secret": os.getenv("GMAIL_CLIENT_SECRET"),
        "redirect_uri": os.getenv("GMAIL_REDIRECT_URI"),
        "grant_type": "authorization_code"
    }

    response = requests.post(token_url, data=data)
    tokens = response.json()
    access_token = tokens["access_token"]
    refresh_token = tokens["refresh_token"]
    id_token = tokens.get("id_token")
    
    # Ahora obtenés el email con el token
    headers = {"Authorization": f"Bearer {access_token}"}
    profile = requests.get("https://www.googleapis.com/oauth2/v2/userinfo", headers=headers).json()
    email = profile["email"]

    # Guardás en Supabase
    supabase.table("users").insert({
        "email": email,
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_expiry": tokens.get("expires_in")
    }).execute()

    # Redirigir a alguna página de confirmación
    return RedirectResponse(url="https://dmpbjeckkodecclfcnlcmpaifjnagmh.chromiumapp.org/oauth2callback.html")


@router.post("/register")
async def register_user(request: Request):
    data = await request.json()
    email = data.get("email")
    access_token = data.get("access_token")

    if not email or not access_token:
        return {"status": "error", "message": "Email o token faltante"}

    # Insertar en Supabase
    try:
        supabase.table("users").insert({
            "email": email,
            "access_token": access_token
        }).execute()
        return {"status": "ok", "message": "Usuario registrado"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
