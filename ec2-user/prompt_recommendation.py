def create_recommendation(selectedCity, selectedTheme="general", selectedGowith="alone", selectedSchedules = []):
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

    example_json = {
        "recommended_places ": [
            {"name": "Place A", "latitude": 0.0000, "longitude": 0.0000, "type": {"landmark": "명소"}},
            {"name": "Restaurant X", "latitude": 0.0000, "longitude": 0.0000, "type": {"restaurant": "식당"}},
            {"name": "Cafe Y", "latitude": 0.0000, "longitude": 0.0000, "type": {"cafe": "카페"}}
        ]
    }

    return f"""
        You are a travel Guide
        
        Generate distinct travel place in {selectedCity} for a {trip_type_theme} trip {trip_type_gowith}.
        
        Rules (❗ strictly enforce):
        1. Suggest new places that are not in selectedSchedule
        2. Recommend popular, highly at least 4.2 rated places suitable for {trip_type_gowith} and {trip_type_theme}.
        3. Only show popular places with more than 75 reviews.
        4. Return a JSON with 10 attractions, 10 restaurants, and 10 cafes.
        
        Respond ONLY with JSON, like the format below:
        {json.dumps(example_json, ensure_ascii=False, indent=2)}

        ❗ Do not repeat the example. Respond ONLY with a fully populated JSON object.
        Do NOT include any explanation, markdown, or incomplete example.
        
    """