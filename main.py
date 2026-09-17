import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from google import genai

app = FastAPI()

# НАСТРОЙКА CORS: разрешаем вашему сайту (фронтенду) обращаться к этому серверу
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешаем запросы с любых доменов
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Инициализация клиента Gemini
try:
    client = genai.Client()
except Exception as e:
    print(f"Ошибка инициализации Gemini client: {e}")

class ChatRequest(BaseModel):
    prompt: str

@app.post("/api/chat")
async def chat_with_ai(request: ChatRequest):
    try:
        # Используем потоковый метод генерации
        response_stream = client.models.generate_content_stream(
            model="gemini-3.5-flash",
            contents=request.prompt,
        )
        
        # Генератор для отправки кусочков текста клиенту по мере поступления
        def generate():
            for chunk in response_stream:
                if chunk.text:
                    yield chunk.text

        return StreamingResponse(generate(), media_type="text/plain; charset=utf-8")
        
    except Exception as e:
        print(f"Ошибка при генерации контента: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Простая проверка работоспособности сервера
@app.get("/")
def read_index():
    return {"status": "Сервер MOROF со стримингом успешно работает на Railway!"}

