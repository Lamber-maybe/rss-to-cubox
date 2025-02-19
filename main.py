import time
import sqlite3
import feedparser
import argparse
import requests
import os
from datetime import datetime

DB_FILE = os.path.join(os.path.dirname(__file__), 'rss_entries.db')
RSS_CONFIG_FILE = os.path.join(os.path.dirname(__file__), "rss_list.txt")
BLACKLIST_FILE = os.path.join(os.path.dirname(__file__), "black_author_list.txt")

def init_db():
    """初始化SQLite数据库"""
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute(
            '''CREATE TABLE IF NOT EXISTS entries
               (id TEXT PRIMARY KEY, author TEXT, timestamp TEXT)'''
        )

def load_file(file_path):
    """通用文件加载函数"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return [line.strip() for line in file if line.strip()]
    except IOError as e:
        print(f"从本地文件获取数据失败: {e}")
        return []

def load_rss_config():
    """从本地文件加载RSS配置"""
    lines = load_file(RSS_CONFIG_FILE)
    return [
        {"url": line.split(',')[0].strip(), "folder": line.split(',')[1].strip()}
        for line in lines
    ]

def fetch_rss_feeds(rss_config):
    """获取多个RSS源的内容"""
    all_entries = []
    for config in rss_config:
        try:
            feed = feedparser.parse(config["url"])
            if feed.entries:
                for entry in feed.entries:
                    entry.source_folder = config["folder"]
                all_entries.extend(feed.entries)
        except Exception as e:
            print(f"获取RSS失败 ({config['url']}): {e}")
    return all_entries

def load_blacklist():
    """从本地文件加载黑名单列表"""
    return load_file(BLACKLIST_FILE)

def get_stored_entries():
    """获取已存储的文章标识符"""
    with sqlite3.connect(DB_FILE) as conn:
        return {row[0] for row in conn.execute("SELECT id FROM entries")}

def store_entries(entries):
    """存储新的文章标识符"""
    with sqlite3.connect(DB_FILE) as conn:
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        conn.executemany(
            "INSERT OR IGNORE INTO entries (id, author, timestamp) VALUES (?, ?, ?)",
            ((entry.get('guid', entry.link), getattr(entry, 'author', ''), current_time) for entry in entries)
        )

def remove_blacklisted_entries(blacklist):
    """从数据库中移除黑名单作者的文章"""
    with sqlite3.connect(DB_FILE) as conn:
        conn.executemany(
            "DELETE FROM entries WHERE author = ? AND author != ''",
            [(author,) for author in blacklist]
        )

def send_webhook_notification(entry, webhook_url):
    """通过Webhook发送通知"""
    message = {
        "type": "url",
        "content": entry.link,
        "title": entry.title,
        "folder": entry.source_folder
    }

    try:
        response = requests.post(webhook_url, json=message)
        response1 = requests.post("https://discord.com/api/webhooks/1341296712496578647/L05htmL-fqUW9REvCCZOCE761DroS8ORzjhGAaPH4giGJL6GWw7CxVV21cIIp8RtTZ8p", json=message)
        if response.status_code == 200:
            print(f"成功发送通知: {entry.title}")
        else:
            print(f"发送通知失败，状态码: {response.status_code}")
    except Exception as e:
        print(f"Webhook请求失败: {e}")

def main():
    """主程序"""
    parser = argparse.ArgumentParser(description='RSS to Webhook')
    parser.add_argument('--webhook', required=True, help='Cubox API URL')
    args = parser.parse_args()

    init_db()

    blacklist = load_blacklist()
    remove_blacklisted_entries(blacklist)

    rss_config = load_rss_config()
    entries = fetch_rss_feeds(rss_config)
    if entries:
        stored_entries = get_stored_entries()
        new_entries = [
            entry for entry in entries
            if entry.get('guid', entry.link) not in stored_entries
            and (getattr(entry, 'author', '') == '' or getattr(entry, 'author', '') not in blacklist)
        ]

        for entry in new_entries:
            send_webhook_notification(entry, args.webhook)
            time.sleep(3)

        store_entries(new_entries)

if __name__ == "__main__":
    main()

