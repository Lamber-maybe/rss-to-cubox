import feedparser
import requests
import time

# RSS源地址
RSS_URL = "https://wechat.doonsec.com/rss.xml"  # 替换为实际的RSS源
# Webhook地址
WEBHOOK_URL = "https://cubox.pro/c/api/save/xxxxxxxx"  # 替换为实际的Webhook地址
# GitHub黑名单文件URL
GITHUB_BLACKLIST_URL = "https://raw.githubusercontent.com/Lamber-maybe/rss-to-cubox/refs/heads/main/black_author_list.txt"  # 替换为实际的GitHub文件URL

def fetch_rss_feed():
    """获取RSS内容"""
    try:
        feed = feedparser.parse(RSS_URL)
        return feed.entries
    except Exception as e:
        print(f"获取RSS失败: {e}")
        return []

def load_blacklist():
    """从GitHub加载黑名单列表"""
    try:
        response = requests.get(GITHUB_BLACKLIST_URL)
        response.raise_for_status()  # 检查请求是否成功
        return [line.strip() for line in response.text.splitlines() if line.strip()]
    except requests.exceptions.RequestException as e:
        print(f"从GitHub获取黑名单失败: {e}")
        return []

def send_webhook_notification(entry):
    """通过Webhook发送通知"""
    message = {
        "type":"url",
        "content": entry.link,
        "title": entry.title,
        "folder": "微信公众号"
    }
    
    try:
        response = requests.post(WEBHOOK_URL, json=message)
        if response.status_code == 200:
            print(f"成功发送通知: {entry.title}")
        else:
            print(f"发送通知失败，状态码: {response.status_code}")
    except Exception as e:
        print(f"Webhook请求失败: {e}")

def is_blacklisted(entry):
    """检查作者是否在黑名单中
    
    参数:
        entry: RSS条目对象，包含文章信息
        
    返回:
        bool: 如果作者在黑名单中返回True，否则返回False
        
    功能说明:
        1. 首先检查entry对象是否包含author属性
        2. 如果包含author属性，则检查该作者是否在从GitHub获取的黑名单列表中
        3. 使用短路逻辑，先检查属性存在性，避免属性不存在时抛出异常
    """
    blacklist = load_blacklist()
    return hasattr(entry, 'author') and entry.author in blacklist

def main():
    """主程序"""
    last_checked = None
    
    while True:
        entries = fetch_rss_feed()
        if entries:
            # 如果是第一次运行，只发送最新的一条
            if last_checked is None:
                if not is_blacklisted(entries[0]):
                    send_webhook_notification(entries[0])
                last_checked = entries[0].published
            else:
                # 遍历所有条目，找出比上次检查时间新的条目
                new_entries = [entry for entry in entries 
                              if entry.published > last_checked 
                              and not is_blacklisted(entry)]
                
                # 如果有新条目，按时间顺序发送（从旧到新）
                if new_entries:
                    for entry in reversed(new_entries):
                        send_webhook_notification(entry)
                    # 更新最后检查时间为最新条目的发布时间
                    last_checked = new_entries[0].published
                
         # 每隔5分钟检查一次
        time.sleep(60)

if __name__ == "__main__":
     main()
