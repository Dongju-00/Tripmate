def create_prompt_generator(selectedCity, days, selectedTheme="general", selectedGowith="alone", addedPlaces=[]):
    import json

    theme_mapping = {
        "자연": "a nature", "엑티비티&체험": "an activity", "대표 관광지": "a famous", "SNS 핫플레이스" : "popular Instagram spots",
        "문화&역사&예술": "Cultural and Historical Activity", "쇼핑": "a shopping"
    }
    gowith_mapping = {
        "부모님이랑": "with parents", "친구들이랑": "with friends", "혼자" : "alone",
        "연인이랑": "as a couple", "배우자랑": "with your wife", "아이들이랑": "with kids"
    }

    trip_type_theme = ", ".join([theme_mapping.get(theme, "a general") for theme in selectedTheme])
    trip_type_gowith = gowith_mapping.get(selectedGowith, "alone")
    user_places_str = ", ".join([json.dumps(place) if isinstance(place, dict) else place for place in
                                 addedPlaces]) or "No specific places added"

    schedules = {
        f"Schedule {i}": [
            {"name": "Place A", "latitude": 0.0000, "longitude": 0.0000, "type": {"landmark": "명소"}},
            {"name": "Restaurant X", "latitude": 0.0000, "longitude": 0.0000, "type": {"restaurant": "식당"}},
            {"name": "Cafe Y", "latitude": 0.0000, "longitude": 0.0000, "type": {"cafe": "카페"}}
        ]
        for i in range(1, days + 2)
    }

    schedules_json = json.dumps({
        "busy_schedule": schedules,
        "relaxed_schedule": schedules
    }, indent=4, ensure_ascii=False)

    return f"""
        You are a travel itinerary planner.

        Generate 2 distinct {days}-day travel plans in {selectedCity} for a {trip_type_theme} trip {trip_type_gowith}.
        The trip should last for **{days + 1} days**, from **Day 1 to Day {days + 1}**.
        User-added places: {user_places_str}.

        Rules (❗ strictly enforce):
        1. Each day must include **at least 2 restaurants** (type: "restaurant") and **1 cafe** (type: "cafe").
        2. Include both user-added places and new suggestions.
        3. Group places geographically to reduce travel time.
        4. Recommend popular, highly rated places suitable for {trip_type_gowith} and {trip_type_theme}.
        5. Balance activity levels to avoid exhaustion.

        ⚠️ Return response in **STRICT JSON only** — no extra explanations or formatting.

        Format:
        '''
        json
        {schedules_json}
        '''
        
        🚨 **IMPORTANT:**  
        - Include plans for every single day from **schedule 1 to schedule {days + 1}**.
        - Each day must contain at least 2 restaurants and 1 cafe.  
        - The response must strictly follow the JSON format without additional text.
        - **Busy schedules**: Maximize the number of locations visited per day. At least 7 locations, including restaurants and cafes.
        - **Leisurely schedules**: Fewer locations, allowing for a more relaxed experience. At least 5, but up to 6 locations, including restaurants and cafes.


        ❗ Do not repeat the example. Generate actual recommendations based on the input above.
        ❗ Do not repeat the example. Respond ONLY with a fully populated JSON object.
        ❗ Respond ONLY with a fully populated JSON object that matches the format. 
        Do NOT include any explanation, markdown, or incomplete example.
        """