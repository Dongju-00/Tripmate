# google_maps_utils.py
from starlette.responses import JSONResponse


def filter_places_by_rating(places_result, min_rating=4.0):

    try:
        filtered_results = {
            "results": [
                place for place in places_result.get("results", [])
                if place.get("rating", 0) >= min_rating
            ]
        }
        return filtered_results
    except Exception as e:
        print(f"Error in filter_places_by_rating: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)



def extract_place_names(places):
    """
    places: Google Places API 결과 리스트
    return: 장소 이름 리스트
    """
    return [place["name"] for place in places]
