import requests
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway
import time
import re

# Prometheus Pushgateway URL
PROMETHEUS_GATEWAY = 'http://localhost:9091'

def get_video_info(bvid, retries=3, delay=2):
    API_URL = f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    for attempt in range(retries):
        response = requests.get(API_URL, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data and 'data' in data and 'stat' in data['data']:
                view_count = data['data']['stat']['view']
                title = data['data']['title']
                duration = data['data']['duration']
                return view_count, title, duration
            else:
                print("Failed to extract data, retrying...")
        else:
            print(f"Failed to fetch data, status code: {response.status_code}, retrying...")
        time.sleep(delay)
    return None, None, None

def push_to_prometheus(video_data):
    registry = CollectorRegistry()
    metric = Gauge('bilibili_video_info', 'Bilibili video information', ['bvid', 'title', 'duration'], registry=registry)
    
    for bvid, info in video_data.items():
        view_count, title, duration = info
        metric.labels(bvid=bvid, title=title, duration=duration).set(view_count)
    
    push_to_gateway(PROMETHEUS_GATEWAY, job='bilibili_monitoring', registry=registry)

def extract_bvid_from_url(url):
    match = re.search(r"bvid=([^&]+)", url)
    if match:
        return match.group(1)
    else:
        return None

if __name__ == "__main__":
    update_interval = 15  # Update every 15 seconds
    urls = {
        "BV1oN4y1Y7uZ": "https://api.bilibili.com/x/web-interface/view?bvid=BV1oN4y1Y7uZ",
        "BV1H5411v7ws": "https://api.bilibili.com/x/web-interface/view?bvid=BV1H5411v7ws",
        "BV1yr42187Qq": "https://api.bilibili.com/x/web-interface/view?bvid=BV1yr42187Qq",
        "BV1fr421t7cW": "https://api.bilibili.com/x/web-interface/view?bvid=BV1fr421t7cW",
        "BV1vJ4m177aR": "https://api.bilibili.com/x/web-interface/view?bvid=BV1vJ4m177aR",
        "BV1ne4y1f72P": "https://api.bilibili.com/x/web-interface/view?bvid=BV1ne4y1f72P",
        "BV1tD4y167PL": "https://api.bilibili.com/x/web-interface/view?bvid=BV1tD4y167PL",
        "BV14F411z7gv": "https://api.bilibili.com/x/web-interface/view?bvid=BV14F411z7gv",
        "BV1TL4y1p7G1": "https://api.bilibili.com/x/web-interface/view?bvid=BV1TL4y1p7G1",
        "BV14D42157Jh": "https://api.bilibili.com/x/web-interface/view?bvid=BV14D42157Jh"
        # Add more bvids and URLs here
    }
    
    while True:
        video_data = {}
        for bvid, url in urls.items():
            view_count, title, duration = get_video_info(bvid)
            if view_count is not None:
                video_data[bvid] = (view_count, title, duration)
                print(f"Successfully fetched info for video with bvid: {bvid}, title: {title}, duration: {duration}")
            else:
                print(f"Failed to fetch info for video with bvid: {bvid}")
        
        push_to_prometheus(video_data)
        print(f"Data pushed to Prometheus.")
        
        print(f"Waiting {update_interval} seconds before next update...")
        time.sleep(update_interval)

