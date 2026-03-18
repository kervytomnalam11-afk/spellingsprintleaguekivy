# leaderboard.py — JSON-backed score storage
import json, os
from config import get_league

def _data_file():
    """Return writable path for leaderboard.json (works on Android + desktop)."""
    try:
        from kivy.app import App
        app = App.get_running_app()
        if app and hasattr(app, 'user_data_dir'):
            d = app.user_data_dir
            os.makedirs(d, exist_ok=True)
            return os.path.join(d, "leaderboard.json")
    except Exception:
        pass
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "leaderboard.json")

def load():
    path = _data_file()
    if os.path.exists(path):
        try:
            with open(path) as f:
                return json.load(f)
        except Exception:
            pass
    return []

def save_score(name, wpm, accuracy, mode):
    league_name, _, _ = get_league(wpm)
    entry = {
        "name":     name[:16],
        "wpm":      round(wpm, 1),
        "accuracy": round(accuracy, 1),
        "mode":     mode,
        "league":   league_name,
    }
    data = load()
    data.append(entry)
    data.sort(key=lambda x: x["wpm"], reverse=True)
    data = data[:100]
    try:
        with open(_data_file(), "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"[leaderboard] save failed: {e}")
    return entry

def top(limit=15, mode=None):
    data = load()
    if mode:
        data = [e for e in data if e["mode"] == mode]
    return data[:limit]

def personal_best(name):
    data = load()
    mine = [e for e in data if e["name"].lower() == name.lower()]
    return mine[0] if mine else None
