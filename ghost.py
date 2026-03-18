# ghost.py — Ghost race recording & playback
import json, os, time

def _data_file():
    """Return writable path for ghost_save.json (works on Android + desktop)."""
    try:
        from kivy.app import App
        app = App.get_running_app()
        if app and hasattr(app, 'user_data_dir'):
            d = app.user_data_dir
            os.makedirs(d, exist_ok=True)
            return os.path.join(d, "ghost_save.json")
    except Exception:
        pass
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "ghost_save.json")

class GhostRecorder:
    def __init__(self):
        self.events = []
        self._start = None

    def start(self):
        self._start = time.time()
        self.events = []

    def record(self, word, correct):
        if self._start is None:
            return
        self.events.append({
            "t":  round(time.time() - self._start, 3),
            "w":  word,
            "ok": correct,
        })

    def save(self, wpm, mode):
        data = {"wpm": wpm, "mode": mode, "events": self.events}
        try:
            with open(_data_file(), "w") as f:
                json.dump(data, f)
        except Exception as e:
            print(f"[ghost] save failed: {e}")

    @staticmethod
    def exists():
        return os.path.exists(_data_file())

    @staticmethod
    def load():
        path = _data_file()
        if not os.path.exists(path):
            return None
        try:
            with open(path) as f:
                return json.load(f)
        except Exception:
            return None


class GhostPlayer:
    def __init__(self, data):
        self.events      = data.get("events", [])
        self.saved_wpm   = data.get("wpm", 0)
        self.mode        = data.get("mode", "")
        self._ptr        = 0
        self._start      = None
        self.words_done  = 0
        self.current_wpm = 0.0

    def start(self):
        self._start     = time.time()
        self._ptr       = 0
        self.words_done = 0

    def update(self):
        if self._start is None:
            return
        elapsed = time.time() - self._start
        while self._ptr < len(self.events):
            ev = self.events[self._ptr]
            if ev["t"] > elapsed:
                break
            if ev["ok"]:
                self.words_done += 1
            self._ptr += 1
        if elapsed > 0:
            self.current_wpm = (self.words_done / elapsed) * 60

    @property
    def progress(self):
        if not self.events:
            return 0.0
        return min(self._ptr / len(self.events), 1.0)
