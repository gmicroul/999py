py-multi-bi-pw.py 
import requests
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway
import time
import re
import json
import logging

# 配置日志记录
logging.basicConfig(level=logging.INFO, filename='error.log', filemode='a')

PROMETHEUS_GATEWAY = 'http://localhost:9091'

def get_video_info(bvid, retries=3, delay=2):
    """
    获取视频信息

    :param bvid: 视频的 BVID
    :param retries: 重试次数
    :param delay: 重试间隔
    :return: 视频的观看数、标题、时长、AID、CID，如果获取失败则返回 None
    """
    API_URL = f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    for attempt in range(retries):
        try:
            response = requests.get(API_URL, headers=headers, timeout=10)  # 设置超时时间为 10 秒
            if response.status_code == 200:
                data = response.json()
                if data and 'code' in data and data['code'] == 0 and 'data' in data:
                    view_count = data['data']['stat']['view']
                    title = data['data']['title']
                    duration = data['data']['duration']
                    aid = data['data'].get('aid', None)
                    cid = data['data'].get('cid', None)
                    if aid is not None and cid is not None:  # 确保 aid 和 cid 都存在
                        return view_count, title, duration, aid, cid
                    else:
                        logging.warning(f"Missing 'aid' or 'cid' in data for BVID: {bvid}")
                else:
                    logging.error(f"Failed to extract data for BVID: {bvid}")
            else:
                logging.error(f"Failed to fetch data for BVID: {bvid}, status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            logging.error(f"Request exception occurred for BVID: {bvid}, error: {e}")
        time.sleep(delay)
    return None, None, None, None, None

def get_online_count(aid, cid, retries=3, delay=2):
    """
    获取在线人数

    :param aid: 视频的 AID
    :param cid: 视频的 CID
    :param retries: 重试次数
    :param delay: 重试间隔
    :return: 在线人数，如果获取失败则返回 None
    """
    API_URL = f"https://api.bilibili.com/x/player/online/total?aid={aid}&cid={cid}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    for attempt in range(retries):
        try:
            response = requests.get(API_URL, headers=headers, timeout=10)  # 设置超时时间为 10 秒
            if response.status_code == 200:
                try:
                    data = response.json()
                    if data and 'code' in data and data['code'] == 0 and 'data' in data:
                        online_count = data['data'].get('count', 0)  # 使用正确的字段
                        return int(online_count)
                    else:
                        logging.error(f"Data format error when fetching online count for AID: {aid}, CID: {cid}")
                except json.JSONDecodeError:
                    logging.error(f"Failed to decode JSON when fetching online count for AID: {aid}, CID: {cid}")
            else:
                logging.error(f"Failed to fetch online count for AID: {aid}, CID: {cid}, status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            logging.error(f"Request exception occurred for AID: {aid}, CID: {cid}, error: {e}")
        time.sleep(delay)
    return None

def push_to_prometheus(video_data):
    """
    将视频数据推送到 Prometheus

    :param video_data: 包含视频信息的字典
    """
    registry = CollectorRegistry()
    metric = Gauge('bilibili_video_info', 'Bilibili video information', ['bvid', 'title', 'duration', 'aid', 'cid'], registry=registry)
    online_metric = Gauge('bilibili_video_online_count', 'Bilibili video online count', ['title'], registry=registry)

    for bvid, info in video_data.items():
        view_count, title, duration, aid, cid = info
        if aid is not None and cid is not None:  # 确保aid和cid存在
            metric.labels(bvid=bvid, title=title, duration=duration, aid=aid, cid=cid).set(view_count)
            online_count = get_online_count(aid, cid)
            if online_count is not None:
                online_metric.labels(title=title).set(online_count)
            else:
                logging.error(f"Failed to get online count for {title} (bvid: {bvid})")
        else:
            logging.error(f"Missing 'aid' or 'cid' for {title} (bvid: {bvid})")

    push_to_gateway(PROMETHEUS_GATEWAY, job='bilibili_monitoring', registry=registry)

def extract_bvid_from_url(url):
    """
    从 URL 中提取 BVID

    :param url: 包含 BVID 的 URL
    :return: BVID，如果提取失败则返回 None
    """
    match = re.search(r"bvid=([^&]+)", url)
    if match:
        return match.group(1)
    else:
        return None

if __name__ == "__main__":
    # 从文件中读取 Bilibili 视频 URL 和对应的 BVID
    update_interval = 15
    urls = {}
    
    while True:
        with open('urls.txt', 'r') as file:
            urls = {line.strip().split()[1]: line.strip().split()[0] for line in file if line.strip()}

        video_data = {}
        for bvid, url in urls.items():
            view_count, title, duration, aid, cid = get_video_info(bvid)
            if view_count is not None:
                video_data[bvid] = (view_count, title, duration, aid, cid)
                print(f"Successfully fetched info for video with bvid: {bvid}, title: {title}, duration: {duration}")
            else:
                print(f"Failed to fetch info for video with bvid: {bvid}")

        push_to_prometheus(video_data)
        print(f"Data pushed to Prometheus.")

        print(f"Waiting {update_interval} seconds before next update...")
        time.sleep(update_interval)




