"""
Singing module - plays music and shows singing animation
Supports custom MP3 files in assets/sounds/
"""

import os
import threading
import time
from src.config import CONFIG


class SingingManager:
    """唱歌管理器 - 播放音乐 + 唱歌动画"""

    def __init__(self):
        self.is_singing = False
        self._audio = None
        self._thread = None

    def start_singing(self, duration=27.5):
        """开始唱歌"""
        if self.is_singing:
            return

        self.is_singing = True

        # 尝试加载并播放 MP3
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
        """播放音乐文件"""
        song_path = os.path.join(CONFIG.sounds_dir, "song.mp3")

        # 尝试用 PySide6 播放
        try:
            self._play_with_qt(song_path, duration)
            return
        except Exception as e:
            print(f"[Singing] Qt playback failed: {e}")

        # 尝试用系统命令播放
        try:
            self._play_with_system(song_path, duration)
            return
        except Exception as e:
            print(f"[Singing] System playback failed: {e}")

        # 没有音乐文件 -> 用蜂鸣声模拟旋律
        self._play_beep_melody(duration)

    def _play_with_qt(self, song_path, duration):
        """用 PySide6 QMediaPlayer 播放"""
        if not os.path.exists(song_path):
            raise FileNotFoundError("No song.mp3 found")

        from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
        from PySide6.QtCore import QUrl

        # QMediaPlayer 必须在主线程创建
        # 所以我们用信号通知主线程
        raise NotImplementedError("Qt media needs main thread")

    def _play_with_system(self, song_path, duration):
        """用系统命令播放 MP3"""
        import subprocess
        import platform

        if not os.path.exists(song_path):
            raise FileNotFoundError("No song.mp3 found")

        system = platform.system()

        if system == "Windows":
            # Windows: 使用 playsound 或 mci
            try:
                from playsound import playsound
                playsound(song_path)
            except ImportError:
                # 使用 Windows Media Player CLI
                cmd = ["cmd", "/c", "start", "/min", "wmplayer", song_path]
                subprocess.Popen(cmd, shell=False)
                time.sleep(duration)
                subprocess.Popen(["taskkill", "/f", "/im", "wmplayer.exe"],
                                  shell=False, stdout=subprocess.DEVNULL,
                                  stderr=subprocess.DEVNULL)

        elif system == "Darwin":  # macOS
            cmd = ["afplay", song_path]
            proc = subprocess.Popen(cmd)
            time.sleep(duration)
            proc.terminate()

        else:  # Linux
            for player in ["mpg123", "mpv", "ffplay"]:
                try:
                    cmd = [player, "--quiet", song_path]
                    proc = subprocess.Popen(cmd,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL)
                    time.sleep(duration)
                    proc.terminate()
                    return
                except FileNotFoundError:
                    continue
            raise RuntimeError("No audio player found")

    def _play_beep_melody(self, duration):
        """没有 MP3 时用蜂鸣声播放一段欢快旋律"""
        import platform

        # 简单的欢快旋律 (频率, 持续秒)
        # 类似一首歌的旋律
        melody = [
            # 第一段
            (523, 0.3), (523, 0.3), (587, 0.3), (659, 0.6),
            (659, 0.3), (587, 0.3), (523, 0.3), (440, 0.6),
            (440, 0.3), (392, 0.3), (440, 0.3), (523, 0.6),
            (523, 0.3), (523, 0.15), (587, 0.15), (659, 0.3), (523, 0.6),
            # 第二段
            (659, 0.3), (698, 0.3), (784, 0.6), (698, 0.3),
            (659, 0.3), (587, 0.6), (523, 0.3),
            # 第三段
            (523, 0.15), (587, 0.15), (659, 0.3), (659, 0.15), (698, 0.15),
            (784, 0.6), (698, 0.3), (659, 0.3), (587, 0.3),
            (523, 0.6), (392, 0.3), (440, 0.6),
            # 收尾
            (523, 0.3), (659, 0.3), (784, 0.9),
        ]

        total = 0
        for freq, beat in melody:
            if not self.is_singing or total >= duration:
                break
            self._beep(freq, beat)
            total += beat

    def _beep(self, freq, duration):
        """发出蜂鸣音"""
        import platform
        system = platform.system()

        if system == "Windows":
            import winsound
            try:
                winsound.Beep(int(freq), int(duration * 1000))
            except Exception:
                pass
        else:
            # Linux/macOS: 用 osc 或 aplay
            import subprocess
            try:
                subprocess.run(
                    ["play", "-nq", "-t", "alsa", "synth", str(duration),
                     "sine", str(freq)],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    timeout=duration + 1
                )
            except Exception:
                try:
                    subprocess.run(
                        ["beep", "-f", str(int(freq)), "-l", str(int(duration * 1000))],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        timeout=duration + 1
                    )
                except Exception:
                    time.sleep(duration)

    def _stop_music(self):
        """停止音乐播放"""
        # 蜂鸣模式通过 is_singing 标志自动停止
        # MP3 模式会在 stop_singing 后由超时退出
        pass


# 全局实例
singing_manager = SingingManager()
