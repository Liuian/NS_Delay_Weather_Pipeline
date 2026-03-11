import requests
import json

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

# ==========================================
# 程式執行起點 (Main)
# ==========================================
if __name__ == "__main__":
    # 這裡先暫時把 API Key 寫死測試，之後我們會教你怎麼隱藏它
    MY_NS_API_KEY = "e5b885d550aa480e88630b10b78e03ba" 
    STATION = "UT" # Utrecht Centraal 的代碼
    
    # 呼叫我們寫好的 Function
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