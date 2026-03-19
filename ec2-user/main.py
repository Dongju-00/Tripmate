from fastapi import FastAPI, Form, Query
from fastapi.responses import HTMLResponse
from fastapi.responses import JSONResponse
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
import json
import logging

from googlemaps import Client as GoogleMapsClient

import openai

from utils.openai_client import openai_management
from prompt_generator import create_prompt_generator
from prompt_recommendation import create_recommendation

import os
from dotenv import load_dotenv
from pydantic import BaseModel

from starlette.staticfiles import StaticFiles


logging.basicConfig(level=logging.DEBUG)


# 환경 변수 로드
load_dotenv()

# OpenAI 및 Google Maps API 키 설정
openai_api_key = os.getenv("OPENAI_API_KEY")
google_maps_api_key = os.getenv("GOOGLE_MAPS_API_KEY")

# OpenAI 클라이언트 설정
openai.api_key = openai_api_key

# Google Maps 클라이언트 설정
gmaps = GoogleMapsClient(key=google_maps_api_key)

# FastAPI 앱 생성
app = FastAPI()

# # ✅ 정적 파일 연결
# app.mount("/static", StaticFiles(directory="resources/static"), name="static")
#
# # ✅ HTML 템플릿 연결
# templates = Jinja2Templates(directory="resources/templates")
#
# @app.get("/", response_class=HTMLResponse)
# async def home(request: Request):
#     return templates.TemplateResponse("index.html", {"request": request})
# 공유할 일정 데이터를 저장하는 변수
shared_schedule_data = {}

# main.py
shared_schedule = {}  # 글로벌 변수로 일정 보관

@app.post("/share_schedule")
def share_schedule(data: dict):
    global shared_schedule
    shared_schedule = data.get("selected_schedule", {})
    print("📌 사용자 선택 일정 저장됨:", shared_schedule)
    return {"message": "선택한 일정이 성공적으로 공유되었습니다."}

@app.get("/share_schedule")
def get_shared_schedule():
    if not shared_schedule:
        return {"error": "No selected schedule shared yet"}
    return shared_schedule

@app.post("/share_aiplaces")
def share_schedule(data: dict):
    global shared_schedule
    shared_schedule = data.get("recommendationPlace", {})
    print("📌 사용자 선택 일정 저장됨:", shared_schedule)
    return {"message": "추천 장소가 성공적으로 공유되었습니다."}

@app.get("/share_aiplaces")
def get_shared_schedule():
    if not shared_schedule:
        return {"error": "No recommendation Place shared yet"}
    return shared_schedule

# 정적 파일 경로 추가
# app.mount("/tripmate_copy/tripmate/src/main/resources", StaticFiles(directory="resources"), name="resources")

class PromptRequest(BaseModel):
    selectedCity: str
    days: int
    selectedTheme: list[str]  # 선택된 테마 (리스트)
    selectedGowith: str  # 동행자
    addedPlaces: list[str] #

# CORS 설정 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 도메인 허용 (보안이 필요한 경우 특정 도메인만 허용)
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메서드 허용
    allow_headers=["*"],  # 모든 헤더 허용
)

@app.get("/", response_class=HTMLResponse)
async def serve_schedule_management():
    # ScheduleManagement.html 파일 읽기
    with open("static/html/ScheduleManagement.html", "r", encoding="utf-8") as file:
        html_content = file.read()
        # API 키를 삽입
        html_content = html_content.replace("YOUR_GOOGLE_MAPS_API_KEY", google_maps_api_key)
        return HTMLResponse(content=html_content)

@app.get("/static/html/Who.html", response_class=HTMLResponse)
async def serve_Who():
    with open("static/html/Who.html", "r", encoding="utf-8") as file:
        return file.read()

@app.get("/static/html/addplace.html", response_class=HTMLResponse)
async def serve_addplce():
    with open("static/html/addplace.html", "r", encoding="utf-8") as file:
        return file.read()

@app.get("static/html/SelectSchedule.html", response_class=HTMLResponse)
async def serve_selectschedule():
    with open("static/html/SelectSchedule.html", "r", encoding="utf-8") as file:
        return file.read()

@app.post("/api/calendar/submit")
async def submit_calendar(data: dict):
    print("📌 캘린더 데이터:", data)
    return JSONResponse(content={"message": "캘린더 데이터가 성공적으로 저장되었습니다."})


@app.get("/items/")
async def read_items(q: str = Query(default="default value", max_length=50)):
    return {"q": q}


@app.post("/get_prompt", response_class=JSONResponse)
async def generator_itinerary(request: Request):
    print("🚀 /get_prompt 엔드포인트 호출됨!", flush=True)

    try:
        data = await request.json()
        print("📌 받은 데이터:", data)

        selectedCity = data.get("selectedCity")
        days = int(data.get("days"))
        selectedTheme = data.get("selectedTheme")
        selectedGowith = data.get("selectedGowith")
        addedPlaces = data.get("addedPlaces",[])  # ✅ 사용자가 추가한 장소 리스트

        geocode_result = gmaps.geocode(selectedCity)
        if not geocode_result:
            return JSONResponse(content={"error": f"No coordinates found for {selectedCity}"}, status_code=400)

        coordinates = geocode_result[0]["geometry"]["location"]
        print(f"📌 Coordinates: {coordinates}")

        # ✅ 리스트 요소가 딕셔너리라면 문자열로 변환
        selectedTheme = [str(item) if isinstance(item, dict) else item for item in selectedTheme]
        addedPlaces = [str(item) if isinstance(item, dict) else item for item in addedPlaces]

        # ✅ 변환된 리스트를 create_prompt_generator()에 전달
        prompt = create_prompt_generator(
            selectedCity=selectedCity,
            days=days,
            selectedTheme=selectedTheme,  # 리스트 그대로 전달
            selectedGowith=selectedGowith,
            addedPlaces=addedPlaces  # 리스트 그대로 전달
        )

        openai_response = openai_management(prompt)

        if isinstance(openai_response, JSONResponse):
            openai_data = json.loads(openai_response.body.decode("utf-8"))
        else:
            return JSONResponse(content={"error": "Invalid OpenAI response"}, status_code=500)

        print("📌 OpenAI JSON 변환 후 데이터:", openai_data)

        # ✅ 일정 개수 (days + 1) 맞추기
        busy_schedule = {}
        relaxed_schedule = {}

        if "busy_schedule" in openai_data:
            for i in range(1, days + 2):  # ✅ Day 1 ~ Day N+1까지 포함
                schedule_key = f"Schedule {i}"
                busy_schedule[schedule_key] = openai_data["busy_schedule"].get(schedule_key, [])

        if "relaxed_schedule" in openai_data:
            for i in range(1, days + 2):
                schedule_key = f"Schedule {i}"
                relaxed_schedule[schedule_key] = openai_data["relaxed_schedule"].get(schedule_key, [])

        response_data = {
            "busy_schedule": busy_schedule,
            "relaxed_schedule": relaxed_schedule
        }

        print("📌 최종 반환 데이터:", response_data)
        return JSONResponse(content=response_data)

    except Exception as e:
        print(f"❌ 서버 오류 발생: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.post("/ai_place_suggestions", response_class=HTMLResponse)
async def ai_place_suggestions(request: Request):

    try:
        data = await request.json()

        selectedCity = data.get("selectedCity")
        selectedTheme = data.get("selectedTheme")
        selectedGowith = data.get("selectedGowith")
        selectedSchedules = data.get("selectedSchedules")

        selectedTheme = [str(item) if isinstance(item, dict) else item for item in selectedTheme]

        # ✅ 변환된 리스트를 create_prompt_generator()에 전달
        prompt = create_recommendation(
            selectedCity=selectedCity,
            selectedTheme=selectedTheme,  # 리스트 그대로 전달
            selectedGowith=selectedGowith,
            selectedSchedules=selectedSchedules # 리스트 그대로 전달
        )

        recommendation_ai_response = openai_management(prompt)

        if not recommendation_ai_response:
            return JSONResponse(content={"error": "AI 응답이 없습니다"}, status_code=500)

        ai_data = json.loads(recommendation_ai_response)
        return JSONResponse(content=ai_data)

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
