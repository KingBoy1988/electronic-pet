"""
Singing module - plays music and shows singing animation
Supports:
1. Direct deep-link to music player apps (NetEase, QQ Music, Spotify, etc.)
2. Command-line player streaming (mpv, ffplay, vlc)
3. Browser playback fallback
4. Local MP3 file
5. System music player app launch
6. Fallback beep melody
"""

import os
import re
import random
import threading
import time
import subprocess
import platform
import webbrowser
from src.config import CONFIG


class SingingManager:
    """唱歌管理器 - 直接链接播放器 + 唱歌动画"""

    def __init__(self):
        self.is_singing = False
        self._audio = None
        self._thread = None
        self._player_proc = None

    def start_singing(self, duration=27.5):
        """开始唱歌"""
        if self.is_singing:
            return
        self.is_singing = True
        self._play_music_async(duration)

    def stop_singing(self):
        """停止唱歌"""
        self.is_singing = False
        self._stop_music()

    def _play_music_async(self, duration):
        """异步播放音乐"""
        def _play():
            self._play_music(duration)
            self.is_singing = False
        self._thread = threading.Thread(target=_play, daemon=True)
        self._thread.start()

    def _play_music(self, duration):
        """按优先级尝试播放音乐"""
        url = self._get_song_url()
        if url:
            self._play_url(url, duration)
            return
        song_path = os.path.join(CONFIG.sounds_dir, "song.mp3")
        if os.path.exists(song_path):
            try:
                self._play_local_file(song_path, duration)
                return
            except Exception as e:
                print(f"[Singing] Local file playback failed: {e}")
        if self._try_launch_player(duration):
            return
        self._play_beep_melody(duration)

    def _get_song_url(self):
        """从 song_url.txt 读取音乐链接，支持多首随机选择"""
        url_file = os.path.join(CONFIG.sounds_dir, "song_url.txt")
        if not os.path.exists(url_file):
            return None
        try:
            urls = []
            with open(url_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and \
                       (line.startswith('http://') or line.startswith('https://') or
                        line.startswith('orpheus://') or line.startswith('qqmusic://') or
                        line.startswith('tencent3://') or line.startswith('spotify:') or
                        line.startswith('bilibili://') or line.startswith('kugou://') or
                        line.startswith('kuwo://') or line.startswith('itmss://')):
                        urls.append(line)
            if urls:
                return random.choice(urls) if len(urls) > 1 else urls[0]
        except Exception:
            pass
        return None

    def _convert_to_deep_link(self, url):
        m = re.search(r'music\.163\.com/song\?id=(\d+)', url)
        if m:
            return (f"orpheus://song/{m.group(1)}", "网易云音乐")
        m = re.search(r'music\.163\.com/playlist\?id=(\d+)', url)
        if m:
            return (f"orpheus://playlist/{m.group(1)}", "网易云音乐")
        m = re.search(r'music\.163\.com/album\?id=(\d+)', url)
        if m:
            return (f"orpheus://album/{m.group(1)}", "网易云音乐")
        m = re.search(r'y\.qq\.com/n/ryqq/songDetail/(\w+)', url)
        if m:
            return (f"qqmusic://qq.com/ui/0#!/7A/song_id=0&song_mid={m.group(1)}", "QQ音乐")
        m = re.search(r'y\.qq\.com/n/ryqq/playlist/(\w+)', url)
        if m:
            return (f"tencent3://qq.com/ui/0#!/7A/playlist_id={m.group(1)}", "QQ音乐")
        m = re.search(r'open\.spotify\.com/track/(\w+)', url)
        if m:
            return (f"spotify:track:{m.group(1)}", "Spotify")
        m = re.search(r'open\.spotify\.com/playlist/(\w+)', url)
        if m:
            return (f"spotify:playlist:{m.group(1)}", "Spotify")
        m = re.search(r'bilibili\.com/video/(BV\w+)', url)
        if m:
            return (f"bilibili://video/{m.group(1)}", "哔哩哔哩")
        m = re.search(r'kugou\.com/song/.*hash=(\w+)', url)
        if m:
            return (f"kugou://hash={m.group(1)}", "酷狗音乐")
        for proto_prefix, name in [
            ("orpheus://", "网易云音乐"), ("qqmusic://", "QQ音乐"),
            ("tencent3://", "QQ音乐"), ("spotify:", "Spotify"),
            ("bilibili://", "哔哩哔哩"), ("kugou://", "酷狗音乐"),
            ("kuwo://", "酷我音乐"),
        ]:
            if url.startswith(proto_prefix):
                return (url, name)
        return None

    def _open_deep_link(self, protocol_url, player_name):
        system = platform.system()
        print(f"[Singing] Deep-linking to {player_name}: {protocol_url}")
        try:
            if system == "Windows":
                subprocess.Popen(["cmd", "/c", "start", "", protocol_url],
                    shell=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return True
            elif system == "Darwin":
                subprocess.Popen(["open", protocol_url],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return True
            else:
                subprocess.Popen(["xdg-open", protocol_url],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return True
        except Exception as e:
            print(f"[Singing] Deep link failed: {e}")
            return False

    def _is_player_installed(self, player_name):
        system = platform.system()
        if system == "Windows":
            player_paths = {
                "网易云音乐": [r"C:\Program Files\CloudMusic\cloudmusic.exe", r"C:\Program Files (x86)\CloudMusic\cloudmusic.exe"],
                "QQ音乐": [r"C:\Program Files\Tencent\QQMusic\QQMusic.exe", r"C:\Program Files (x86)\Tencent\QQMusic\QQMusic.exe"],
                "Spotify": [os.path.expandvars(r"%APPDATA%\Spotify\Spotify.exe"), r"C:\Program Files\Spotify\Spotify.exe"],
                "酷狗音乐": [r"C:\Program Files\KuGou\KuGou.exe", r"C:\Program Files (x86)\KuGou\KuGou.exe"],
            }
            return any(os.path.exists(p) for p in player_paths.get(player_name, []))
        elif system == "Darwin":
            mac_apps = {"网易云音乐": "NeteaseMusic", "QQ音乐": "QQMusic", "Spotify": "Spotify", "酷狗音乐": "KugouMusic", "Apple Music": "Music", "哔哩哔哩": "哔哩哔哩"}
            app = mac_apps.get(player_name, "")
            return os.path.exists(f"/Applications/{app}.app")
        return False

    def _play_url(self, url, duration):
        system = platform.system()
        deep = self._convert_to_deep_link(url)
        if deep:
            protocol_url, player_name = deep
            installed = self._is_player_installed(player_name)
            if installed or system != "Windows":
                if self._open_deep_link(protocol_url, player_name):
                    print(f"[Singing] Opened in {player_name}, singing for {duration}s")
                    time.sleep(duration)
                    return
            print(f"[Singing] {player_name} not installed, trying other methods...")
        for player in ["mpv", "ffplay", "vlc", "mpg123"]:
            try:
                cmd = [player]
                if player == "mpv":
                    cmd += ["--no-video", "--quiet"]
                elif player == "vlc":
                    cmd += ["--no-video", "--quiet", "--intf", "dummy"]
                cmd.append(url)
                proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                self._player_proc = proc
                proc.wait(timeout=duration + 5)
                return
            except FileNotFoundError:
                continue
            except subprocess.TimeoutExpired:
                if self._player_proc:
                    self._player_proc.terminate()
                continue
        print("[Singing] No deep-link or CLI player, opening browser...")
        webbrowser.open(url)
        time.sleep(duration)

    def _play_local_file(self, song_path, duration):
        system = platform.system()
        if system == "Windows":
            for player in ["mpv", "ffplay", "vlc"]:
                try:
                    proc = subprocess.Popen([player, "--no-video", "--quiet", song_path],
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    self._player_proc = proc
                    proc.wait(timeout=duration + 5)
                    return
                except (FileNotFoundError, subprocess.TimeoutExpired):
                    if self._player_proc:
                        self._player_proc.terminate()
                    continue
            try:
                os.startfile(song_path)
                time.sleep(duration)
            except Exception:
                raise
        elif system == "Darwin":
            for player in ["afplay", "mpv", "ffplay"]:
                try:
                    proc = subprocess.Popen([player, song_path],
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    self._player_proc = proc
                    proc.wait(timeout=duration + 5)
                    return
                except (FileNotFoundError, subprocess.TimeoutExpired):
                    if self._player_proc:
                        self._player_proc.terminate()
                    continue
            raise RuntimeError("No audio player found on macOS")
        else:
            for player in ["mpg123", "mpv", "ffplay", "cvlc"]:
                try:
                    cmd = [player]
                    if player == "mpv":
                        cmd += ["--no-video", "--quiet"]
                    cmd.append(song_path)
                    proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    self._player_proc = proc
                    proc.wait(timeout=duration + 5)
                    return
                except (FileNotFoundError, subprocess.TimeoutExpired):
                    if self._player_proc:
                        self._player_proc.terminate()
                    continue
            raise RuntimeError("No audio player found on Linux")

    def _try_launch_player(self, duration):
        system = platform.system()
        if system == "Windows":
            players = [
                (r"C:\Program Files\Tencent\QQMusic\QQMusic.exe", "QQMusic"),
                (r"C:\Program Files (x86)\Tencent\QQMusic\QQMusic.exe", "QQMusic"),
                (r"C:\Program Files\CloudMusic\cloudmusic.exe", "NetEase"),
                (r"C:\Program Files (x86)\CloudMusic\cloudmusic.exe", "NetEase"),
                (r"C:\Program Files\KuGou\KuGou.exe", "KuGou"),
                (r"C:\Program Files (x86)\KuGou\KuGou.exe", "KuGou"),
                (r"C:\Program Files\Windows Media Player\wmplayer.exe", "WMP"),
            ]
            for path, name in players:
                if os.path.exists(path):
                    print(f"[Singing] Launching {name}...")
                    subprocess.Popen([path], shell=False)
                    time.sleep(duration)
                    return True
        elif system == "Darwin":
            players = ["QQMusic", "NeteaseMusic", "KugouMusic", "Spotify", "Music"]
            for app in players:
                app_path = f"/Applications/{app}.app"
                if os.path.exists(app_path):
                    print(f"[Singing] Launching {app}...")
                    subprocess.Popen(["open", app_path])
                    time.sleep(duration)
                    return True
        return False

    def _play_beep_melody(self, duration):
        melody = [
            (523, 0.3), (523, 0.3), (587, 0.3), (659, 0.6),
            (659, 0.3), (587, 0.3), (523, 0.3), (440, 0.6),
            (440, 0.3), (392, 0.3), (440, 0.3), (523, 0.6),
            (523, 0.3), (523, 0.15), (587, 0.15), (659, 0.3), (523, 0.6),
            (659, 0.3), (698, 0.3), (784, 0.6), (698, 0.3),
            (659, 0.3), (587, 0.6), (523, 0.3),
            (523, 0.15), (587, 0.15), (659, 0.3), (659, 0.15), (698, 0.15),
            (784, 0.6), (698, 0.3), (659, 0.3), (587, 0.3),
            (523, 0.6), (392, 0.3), (440, 0.6),
            (523, 0.3), (659, 0.3), (784, 0.9),
        ]
        total = 0
        for freq, beat in melody:
            if not self.is_singing or total >= duration:
                break
            self._beep(freq, beat)
            total += beat

    def _beep(self, freq, duration):
        system = platform.system()
        if system == "Windows":
            import winsound
            try:
                winsound.Beep(int(freq), int(duration * 1000))
            except Exception:
                pass
        else:
            try:
                subprocess.run(["play", "-nq", "-t", "alsa", "synth", str(duration), "sine", str(freq)],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=duration + 1)
            except Exception:
                try:
                    subprocess.run(["beep", "-f", str(int(freq)), "-l", str(int(duration * 1000))],
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=duration + 1)
                except Exception:
                    time.sleep(duration)

    def _stop_music(self):
        if self._player_proc:
            try:
                self._player_proc.terminate()
                self._player_proc.wait(timeout=3)
            except Exception:
                try:
                    self._player_proc.kill()
                except Exception:
                    pass
            self._player_proc = None


singing_manager = SingingManager()
