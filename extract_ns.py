import requests
import json
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def fetch_ns_departures(station_code, api_key):
    """
    從 NS API 獲取指定車站的即時出發班次。
    """
    # NS 官方提供的 API 端點 (以 v2 departures 為例)
    url = f"https://gateway.apiportal.ns.nl/reisinformatie-api/api/v2/departures?station={station_code}"
    
    # API 認證：NS API 要求將 Key 放在 Header 中的 'Ocp-Apim-Subscription-Key'
    headers = {
        'Ocp-Apim-Subscription-Key': api_key
    }
    
    try:
        # 發送 GET 請求
        print(f"正在連線至 NS API 獲取 {station_code} 車站資料...")
        response = requests.get(url, headers=headers)
        
        # 檢查 HTTP 狀態碼，如果不是 200 (OK)，會直接觸發例外錯誤
        response.raise_for_status()
        
        # 將回傳的 JSON 字串解析成 Python 字典 (Dictionary)
        data = response.json()
        print("成功獲取資料！\n")
        return data

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP 錯誤發生: {http_err}")
    except requests.exceptions.ConnectionError as conn_err:
        print(f"連線錯誤: 請檢查網路狀態。詳細資訊: {conn_err}")
    except Exception as err:
        print(f"發生未預期的錯誤: {err}")
        
    # 如果發生錯誤，回傳 None
    return None

def fetch_weather_by_coords(lat, lon, api_key):
    """
    使用精準的經緯度，從 OpenWeatherMap 獲取當下天氣。
    """
    # 使用免費版的 /weather 端點，但改用 lat 和 lon
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"
    
    try:
        print(f"正在獲取座標 ({lat}, {lon}) 的天氣資料...")
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        # 特別處理 401 (Unauthorized) 錯誤，提供更明確的指引
        if response.status_code == 401:
            print(f"天氣 API 錯誤: 401 Unauthorized. 請檢查你的 OpenWeather API Key 是否正確或已啟用。")
        else:
            print(f"天氣 API 發生 HTTP 錯誤: {http_err}")
    except requests.exceptions.ConnectionError as conn_err:
        print(f"連線錯誤: 請檢查網路狀態。詳細資訊: {conn_err}")
    except Exception as err:
        print(f"天氣 API 發生未預期的錯誤: {err}")
        
    return None

def save_data_to_local(data, data_type, location_id):
    """
    將資料存成帶有時間戳記的 JSON 檔案。
    data_type: 'departures' 或 'weather'
    location_id: 車站代碼(UT) 或 城市名稱(Utrecht)
    """
    if not data:
        print("沒有資料可以儲存。")
        return
    
    # 產生當下時間的字串，例如：20260312_224200
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 組合檔案名稱，例如：departures_UT_20260312_224200.json
    filename = f"{data_type}_{location_id}_{current_time}.json"
    
    # 建立一個名為 'raw_data' 的資料夾來放這些檔案 (如果資料夾不存在的話)
    os.makedirs('raw_data', exist_ok=True)
    file_path = os.path.join('raw_data', filename)
    
    # 將資料寫入 JSON 檔案
    with open(file_path, 'w', encoding='utf-8') as f:
        # ensure_ascii=False 可以確保中文字或特殊符號正常顯示
        # indent=4 會自動幫你排版，讓 JSON 看起來整齊易讀
        json.dump(data, f, ensure_ascii=False, indent=4)
        
    print(f"📁 成功！資料已儲存至: {file_path}")
    return file_path

# ==========================================
# 程式執行起點 (Main)
# ==========================================
if __name__ == "__main__":
    # Fetch API key
    MY_NS_API_KEY = os.getenv("NS_API_KEY")
    WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

    if not MY_NS_API_KEY or not WEATHER_API_KEY:
        print("❌ 找不到 API Key！請檢查 .env 檔案。")
        exit()
    
    STATION = "UT" # Utrecht Centraal 的代碼
    CITY = "Utrecht"
    COUNTRY = "NL"
    
    # 1. Extract and Save NS data
    departures_data = fetch_ns_departures(STATION, MY_NS_API_KEY)
    
    if departures_data:
        # 為了不要讓螢幕被幾千行資料淹沒，我們只印出「前 3 筆」班次來檢查
        # NS 的班次資料通常包在 'payload' -> 'departures' 裡面
        first_3_trains = departures_data.get('payload', {}).get('departures', [])[:3]
        
        print("--- 最新 3 筆出發班次 ---")
        for train in first_3_trains:
            direction = train.get('direction', '未知目的地')
            planned_time = train.get('plannedDateTime', '未知時間')
            train_category = train.get('trainCategory', '未知車種')
            
            print(f"🚆 車種: {train_category} | 開往: {direction} | 預計時間: {planned_time}")
            
        print("\n(你可以印出 print(departures_data) 來查看完整結構)")

    if departures_data:
        save_data_to_local(departures_data, "departures", STATION)

    # 2. Extract and Save Weather data
    weather_data = fetch_weather_by_coords(52.0907, 5.1214, WEATHER_API_KEY)   

    if weather_data:
        temp = weather_data.get('main', {}).get('temp', '未知')
        desc = weather_data.get('weather', [{}])[0].get('description', '未知')
        print(f"\n Location:{CITY} Weather:{desc} Temperature:{temp}°C")

    save_data_to_local(weather_data, "weather", CITY)
