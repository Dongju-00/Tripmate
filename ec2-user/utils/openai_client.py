from openai import OpenAI
from dotenv import load_dotenv
from fastapi.responses import JSONResponse
import os
import json
import re

load_dotenv()
client = OpenAI()

def openai_management(prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful travel planner. Respond in JSON format."},
                {"role": "user", "content": prompt}
            ],
            stream=True
        )

        openai_response = ""
        for chunk in response:
            if chunk.choices[0].delta.content:
                openai_response += chunk.choices[0].delta.content

        # 🔍 JSON 형식만 추출
        json_match = re.search(r"\{.*\}", openai_response, re.DOTALL)
        if not json_match:
            print("❌ JSON 형식이 아닙니다:", openai_response)
            return JSONResponse(content={"error": "Invalid OpenAI response"}, status_code=500)

        cleaned_json = json_match.group()

        # 📦 JSON 파싱
        try:
            parsed_data = json.loads(cleaned_json)
            return JSONResponse(content=parsed_data)
        except json.JSONDecodeError as e:
            print("❌ JSON 파싱 실패:", e)
            return JSONResponse(content={"error": "JSON parsing error"}, status_code=500)

    except Exception as e:
        print(f"❌ OpenAI 오류 발생: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)
