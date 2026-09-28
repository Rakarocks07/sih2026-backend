"""
Merges M1 (cams_gfs_processed.json) + M3 (ml_corrected_forecast.json)
into the single target schema for the frontend / M5's API.

Run: python merge_forecast.py
Outputs: forecast_merged.json
"""
import json

M1_PATH = "cams_gfs_processed.json"
M3_PATH = "ml_corrected_forecast.json"
OUT_PATH = "forecast_merged.json"

# Indian CPCB PM2.5 -> AQI breakpoints (Clow, Chigh, Ilow, Ihigh)
PM25_BREAKPOINTS = [
    (0, 30, 0, 50),
    (31, 60, 51, 100),
    (61, 90, 101, 200),
    (91, 120, 201, 300),
    (121, 250, 301, 400),
    (251, 380, 401, 450),
    (381, 100000, 451, 500),
]

def pm25_to_aqi(pm25):
    for clow, chigh, ilow, ihigh in PM25_BREAKPOINTS:
        if clow <= pm25 <= chigh:
            return round(ilow + (ihigh - ilow) * (pm25 - clow) / (chigh - clow))
    return 500

def grap_stage(aqi):
    if aqi >= 450:
        return 4
    elif aqi >= 401:
        return 3
    elif aqi >= 301:
        return 2
    elif aqi >= 201:
        return 1
    return 0

GRAP_ACTIONS = {
    0: "No action required",
    1: "Stage I: Dust control, mechanized sweeping",
    2: "Stage II: Stop diesel gensets, intensify public transport",
    3: "Stage III: Halt non-essential construction, BS-III petrol/BS-IV diesel restrictions",
    4: "Stage IV: Stop all construction, restrict truck entry, consider school closures",
}

def load(path):
    with open(path) as f:
        return json.load(f)

def main():
    m1 = load(M1_PATH)
    m3 = load(M3_PATH)

    # M3 covers only one station currently (DL001 / Anand Vihar).
    # Map M3's station name -> M1's station_id key so we know which one has real ML data.
    m3_station_key = "Anand_Vihar"  # matches M3's "Anand Vihar, Delhi"
    m3_hours = m3["hours"]           # 72 entries, "+0h".."+71h"
    m3_uncoupled = m3["uncoupled_aqi"]
    m3_coupled = m3["coupled_aqi"]

    merged_stations = []

    for station_id, sdata in m1["stations"].items():
        hourly_out = []
        for i, hr in enumerate(sdata["hours"]):
            h = hr["h"]  # 0..72

            # --- Determine AQI source ---
            if station_id == m3_station_key and i < len(m3_uncoupled):
                aqi_uncoupled = m3_uncoupled[i]
                aqi_coupled = m3_coupled[i]
                aqi_source = "ml_real"
            else:
                # Derive placeholder AQI from M1's PM2.5 until M3 sends real data
                aqi_uncoupled = pm25_to_aqi(hr["pm25_uncoupled"])
                aqi_coupled = pm25_to_aqi(hr["pm25_coupled"])
                aqi_source = "derived_from_pm25"

            stage = grap_stage(aqi_coupled)

            hourly_out.append({
                "h": h,
                "time": hr["time"],

                "pm25_uncoupled": hr["pm25_uncoupled"],
                "pm25_coupled": hr["pm25_coupled"],

                "aqi_uncoupled": aqi_uncoupled,
                "aqi_coupled": aqi_coupled,
                "aqi_source": aqi_source,

                "o3_uncoupled": hr["o3_uncoupled"],
                "o3_coupled": hr["o3_coupled"],

                "sw_clear": hr["sw_clear"],
                "sw_dimmed": hr["sw_dimmed"],
                "dimming_pct": hr["dimming_pct"],

                "pbl_uncoupled": hr["pbl_uncoupled"],
                "pbl_coupled": hr["pbl_coupled"],

                "T2m_uncoupled": hr["T2m_uncoupled"],
                "T2m_coupled": hr["T2m_coupled"],

                "wind": hr["wind"],

                "ventilation_uncoupled": hr["ventilation_uncoupled"],
                "ventilation_coupled": hr["ventilation_coupled"],
                "stagnation_coupled": hr["stagnation_coupled"],

                "inversion_gamma": hr["inversion_gamma"],

                "grap_stage": stage,
                "grap_action": GRAP_ACTIONS[stage],
            })

        merged_stations.append({
            "station_id": station_id,
            "station_name": station_id.replace("_", " ") + ", Delhi",
            "coordinates": sdata["coordinates"],  # already [lon, lat]
            "hourly": hourly_out,
        })

    output = {
        "meta": {
            "domain": "Delhi-NCR",
            "bounding_box": m1["meta"]["domain"],
            "init_time": m1["meta"]["init_time"],
            "forecast_horizon_hours": 72,
            "coord_order": "[lon, lat]",
            "note": "aqi_source='derived_from_pm25' means placeholder AQI pending real M3 model output for this station",
        },
        "stations": merged_stations,
    }

    with open(OUT_PATH, "w") as f:
        json.dump(output, f, indent=2)

    print(f"Wrote {OUT_PATH} with {len(merged_stations)} stations.")
    for s in merged_stations:
        real = sum(1 for h in s["hourly"] if h["aqi_source"] == "ml_real")
        print(f"  {s['station_id']}: {len(s['hourly'])} hours, {real} using real ML AQI")

if __name__ == "__main__":
    main()
