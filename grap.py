def get_grap_stage(aqi: int) -> str:
    if aqi > 450:
        return "Stage IV (Emergency)"
    elif aqi > 400:
        return "Stage III (Severe)"
    elif aqi > 300:
        return "Stage II (Very Poor)"
    elif aqi > 200:
        return "Stage I (Poor)"
    else:
        return "No Action Needed"