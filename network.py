# network.py — WiFi Multiplayer (TCP sockets)
"""
Protocol (newline-delimited JSON):
  host→client  {"type":"start","words":[...],"mode":"Sprint"}
  client→host  {"type":"join","name":"Alice"}
  both ways    {"type":"progress","words_done":12,"accuracy":95.2}
  both ways    {"type":"finish","wpm":48.3,"accuracy":95.2,"name":"Alice"}
  both ways    {"type":"chat","msg":"gg"}
"""

import socket, threading, json, time, queue
from config import NET_PORT, NET_TIMEOUT


def _send(sock: socket.socket, obj: dict):
    try:
        data = (json.dumps(obj) + "\n").encode()
        sock.sendall(data)
    except Exception:
        pass

def _recv_lines(sock: socket.socket, buf: list[str]) -> list[dict]:
    """Non-blocking read; returns list of parsed messages."""
    msgs = []
    try:
        chunk = sock.recv(4096).decode(errors="ignore")
        if chunk:
            buf[0] += chunk
            while "\n" in buf[0]:
                line, buf[0] = buf[0].split("\n", 1)
                if line.strip():
                    try:
                        msgs.append(json.loads(line))
                    except Exception:
                        pass
    except BlockingIOError:
        pass
    except Exception:
        pass
    return msgs


class NetHost:
    """Runs on the host machine; manages up to 3 remote players."""

    MAX_CLIENTS = 3

    def __init__(self):
        self.clients:  list[socket.socket] = []
        self.names:    list[str]           = []
        self.progress: list[dict]          = []
        self._bufs:    list[list[str]]     = []
        self._srv:     socket.socket | None = None
        self.running   = False
        self.in_queue: queue.Queue = queue.Queue()
        self._thread:  threading.Thread | None = None
        self.ip        = self._get_local_ip()

    @staticmethod
    def _get_local_ip() -> str:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"

    def start_server(self):
        self._srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._srv.bind(("", NET_PORT))
        self._srv.listen(self.MAX_CLIENTS)
        self._srv.settimeout(0.5)
        self.running = True
        self._thread = threading.Thread(target=self._accept_loop, daemon=True)
        self._thread.start()

    def _accept_loop(self):
        while self.running:
            try:
                conn, addr = self._srv.accept()
                conn.setblocking(False)
                self.clients.append(conn)
                self.names.append(f"Player{len(self.clients)+1}")
                self.progress.append({"words_done": 0, "accuracy": 100.0})
                self._bufs.append([""])
                self.in_queue.put({"type": "connected", "addr": addr[0]})
            except socket.timeout:
                pass
            except Exception:
                break
            # poll clients — iterate a snapshot to avoid mutation during loop
            for i, c in enumerate(list(self.clients)):
                if i >= len(self._bufs):
                    break
                for msg in _recv_lines(c, self._bufs[i]):
                    if msg.get("type") == "join":
                        self.names[i] = msg.get("name", self.names[i])
                    elif msg.get("type") == "progress":
                        self.progress[i].update(msg)
                    elif msg.get("type") == "finish":
                        msg["player_index"] = i
                    self.in_queue.put(msg)

    def broadcast(self, obj: dict):
        for c in self.clients:
            _send(c, obj)

    def send_start(self, words: list[str], mode: str):
        self.broadcast({"type": "start", "words": words, "mode": mode})

    def send_progress(self, words_done: int, accuracy: float):
        self.broadcast({"type": "host_progress",
                         "words_done": words_done, "accuracy": accuracy})

    def stop(self):
        self.running = False
        for c in self.clients:
            try: c.close()
            except Exception: pass
        if self._srv:
            try: self._srv.close()
            except Exception: pass
        # wait for accept thread to exit so the port is free to rebind
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.5)
        self._thread = None

    @property
    def client_count(self) -> int:
        return len(self.clients)


class NetClient:
    """Runs on each guest machine."""

    def __init__(self):
        self.sock:    socket.socket | None = None
        self._buf:    list[str]            = [""]
        self.running  = False
        self.in_queue: queue.Queue         = queue.Queue()
        self.connected                     = False
        self.words:   list[str]            = []
        self.mode:    str                  = ""
        self.opponents: dict               = {}  # name → progress
        self._thread: threading.Thread | None = None

    def connect(self, host_ip: str, name: str) -> bool:
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(NET_TIMEOUT)
            self.sock.connect((host_ip, NET_PORT))
            self.sock.setblocking(False)
            _send(self.sock, {"type": "join", "name": name})
            self.connected = True
            self.running = True
            self._thread = threading.Thread(target=self._recv_loop, daemon=True)
            self._thread.start()
            return True
        except Exception:
            return False

    def _recv_loop(self):
        while self.running:
            for msg in _recv_lines(self.sock, self._buf):
                if msg.get("type") == "start":
                    self.words = msg.get("words", [])
                    self.mode  = msg.get("mode", "")
                elif msg.get("type") == "host_progress":
                    self.opponents["Host"] = msg
                self.in_queue.put(msg)
            time.sleep(0.05)

    def send_progress(self, words_done: int, accuracy: float):
        _send(self.sock, {"type": "progress",
                           "words_done": words_done, "accuracy": accuracy})

    def send_finish(self, name: str, wpm: float, accuracy: float):
        _send(self.sock, {"type": "finish",
                           "name": name, "wpm": wpm, "accuracy": accuracy})

    def disconnect(self):
        self.running = False
        if self.sock:
            try: self.sock.close()
            except Exception: pass
