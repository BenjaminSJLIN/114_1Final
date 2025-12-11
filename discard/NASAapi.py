import requests
import json

API_KEY = "evozkJTWmI8gVyxbGev7XFSsZ1Lwv9UGs02Imu9r"

def get_nasa_apod():
    url = f"https://api.nasa.gov/planetary/apod?api_key={API_KEY}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        result = {
            "title": data.get("title", "Unknown Title"),
            "date": data.get("date", ""),
            "description": data.get("explanation", ""),
            "image_url": data.get("hdurl", data.get("url")), # 優先用高畫質
            "media_type": data.get("media_type") # 可能是 'image' 或 'video'
        }
        
        return result

    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    nasa_data = get_nasa_apod()
    
    if nasa_data:
        print("--- data get ---")
        print(f"title: {nasa_data['title']}")
        print(f"img url: {nasa_data['image_url']}")
        print("-" * 30)
