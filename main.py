from fastapi import FastAPI, HTTPException, Form
from fastapi.responses import HTMLResponse
import redis
import random
import jwt
from datetime import datetime, timedelta
from key import generate_key



private = generate_key()
public = private

app = FastAPI()
r = redis.Redis(host="localhost", port=6379, decode_responses=True)


def generate_access_token(email: str):
    payload = {"sub": email, "exp": datetime.utcnow() + timedelta(minutes=15)}
    return jwt.encode(payload, private, algorithm="HS256")


def generate_refresh_token(email: str):
    payload = {"sub": email, "exp": datetime.utcnow() + timedelta(days=7)}
    return jwt.encode(payload, private, algorithm="HS256")


def verify_token(token: str):
    try:
        payload = jwt.decode(token, public, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


@app.get("/", response_class=HTMLResponse)
def read_root():
    """
    Возвращает HTML-форму для ввода email.
    """
    return """
    <html>
        <head>
            <title>Email Verification</title>
        </head>
        <body>
            <h2>Enter your email to receive a verification code</h2>
            <form action="/send_verification_code" method="post">
                <label for="email">Email:</label>
                <input type="email" id="email" name="email" required>
                <button type="submit">Send Verification Code</button>
            </form>
        </body>
    </html>
    """


@app.post("/send_verification_code")
def send_verification_code(email: str = Form(...)):
    """
    Отправка кода подтверждения на email.
    """
    code = random.randint(1000, 9999)  # Генерация 4-значного кода
    r.set(email, code, ex=300)  # Храним код в Redis 5 минут
    print(f"Sending code {code} to email {email}")  # Имитация отправки email
    return {"message": f"Verification code sent to {email}"}


@app.post("/verify_and_register")
def verify_and_register(email: str = Form(...), code: int = Form(...), password: str = Form(...)):
    """
    Проверка кода подтверждения и регистрация пользователя.
    """
    stored_code = r.get(email)
    if stored_code and int(stored_code) == code:
        r.hset(f"user:{email}", mapping={"password": password})
        r.delete(email)
        return {"message": "User registered successfully"}
    else:
        raise HTTPException(status_code=400, detail="Invalid or expired verification code")


@app.post("/login")
def login(email: str = Form(...), password: str = Form(...)):
    """
    Логин пользователя и генерация токенов.
    """
    user_data = r.hgetall(f"user:{email}")
    if not user_data or user_data.get("password") != password:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = generate_access_token(email)
    refresh_token = generate_refresh_token(email)
    r.set(f"refresh:{email}", refresh_token, ex=7 * 24 * 60 * 60)
    return {"access_token": access_token, "refresh_token": refresh_token}


@app.post("/refresh_token")
def refresh_token(email: str = Form(...), refresh_token: str = Form(...)):
    """
    Обновление access токена по refresh токену.
    """
    stored_refresh_token = r.get(f"refresh:{email}")
    if not stored_refresh_token or stored_refresh_token != refresh_token:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    verify_token(refresh_token)
    new_access_token = generate_access_token(email)
    return {"access_token": new_access_token}


@app.get("/user_info")
def user_info(token: str = Form(...)):
    """
    Получение информации о пользователе по access токену.
    """
    payload = verify_token(token)
    email = payload["sub"]
    user_data = r.hgetall(f"user:{email}")
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")
    return {"email": email}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
