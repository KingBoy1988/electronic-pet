# Sounds Directory - 唱歌功能配置

## 播放优先级（自动选择）

1. **深链直连播放器**（推荐） - 直接在音乐 App 中打开指定歌曲
2. **命令行播放器流式播放** - mpv/ffplay/vlc 直接播放 URL
3. **浏览器播放** - 打开浏览器播放
4. **本地 MP3 文件** - `song.mp3`
5. **本地播放器 App** - 启动已安装的音乐播放器
6. **蜂鸣旋律** - 用系统蜂鸣声播放一段旋律

## 方式一：深链直连播放器（推荐）

在 `song_url.txt` 中放入歌曲网页链接：

```
https://music.163.com/song?id=1811821591
```

保存后右键宠物 -> 唱歌，宠物会：

1. **自动识别**链接来源（网易云/QQ音乐/Spotify/B站等）
2. **转换为深链协议**（orpheus://, qqmusic://, spotify: 等）
3. **直接在播放器 App 中打开**指定歌曲，不开浏览器
4. 宠物跟着音乐摇摆唱歌 27.5 秒

### 支持的链接来源

| 来源 | 网页链接格式 | 深链协议 |
|------|-------------|---------|
| 网易云音乐 | `music.163.com/song?id=xxx` | `orpheus://song/xxx` |
| 网易云歌单 | `music.163.com/playlist?id=xxx` | `orpheus://playlist/xxx` |
| 网易云专辑 | `music.163.com/album?id=xxx` | `orpheus://album/xxx` |
| QQ音乐 | `y.qq.com/n/ryqq/songDetail/xxx` | `qqmusic://qq.com/ui/...` |
| Spotify | `open.spotify.com/track/xxx` | `spotify:track:xxx` |
| 哔哩哔哩 | `bilibili.com/video/BVxxx` | `bilibili://video/BVxxx` |
| 酷狗音乐 | `kugou.com/song/#hash=xxx` | `kugou://hash=xxx` |

也可以直接写协议链接（不需要 http）。

## 方式二：本地 MP3 文件

将 `song.mp3` 放在此目录，右键宠物 -> 唱歌时优先播放。

## 方式三：直接写协议链接

在 `song_url.txt` 中直接写协议（不以 http 开头）：

```
orpheus://song/1811821591
```

这样无需转换，直接打开播放器。

## 播放器检测

宠物会自动检测以下播放器是否已安装：
- Windows: 网易云音乐、QQ音乐、Spotify、酷狗音乐
- macOS: NeteaseMusic、QQMusic、Spotify、酷狗、Apple Music

如果对应播放器未安装，会自动降级到其他播放方式。
