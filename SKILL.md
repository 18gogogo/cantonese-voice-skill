# OpenClaw 廣東話語音系統技能包 🎤

> **適用於所有 LLM 模型（Qwen32B-Q4、Llama、Claude 等）**

## 快速開始（給 AI 模型快速參考）

### 基本流程
```
1. 檢查語音輸出狀態
2. 接收用戶輸入
3. 解析控制指令：（或）
4. 處理用戶請求
5. 生成回應
6. 如果語音開啟：文字 + 廣東話語音
   如果語音關閉：僅文字
```

### 最簡示例

```python
from voice_integration import VoiceConversation

# 創建對話實例
conversation = VoiceConversation()

# 檢查是否應該輸出語音
if conversation.is_voice_output_enabled():
    # 生成文字 + 廣東話語音
    result = conversation.respond_speech("你好")
    # result['output_file'] 是音頻文件
else:
    # 只輸出文字
    print("你好")
```

---

## 概述

OpenClaw 技能包，整合 CosyVoice (語音合成 TTS) 和 Whisper (語音識別 ASR)，支持廣東話語音輸入輸出。

## 功能特色

✅ **語音識別 (ASR)** - Whisper Turbo 支持廣東话
✅ **語音合成 (TTS)** - CosyVoice3 支持廣東話
✅ **語音輸出開關** - 可控制語音輸出的開啟/關閉
✅ **手動確認模式** - 識別結果用戶確認後才確認後才執行
✅ **100% 本地運行** - 無需雲端 API

## 安裝位置

`/home/ubuntu/.openclaw/workspace/skills/cantonese-voice/`

## 文件結構

```
cantonese-voice/
├── SKILL.md                      # 技能使用說明 (本文件)
├── README.md                     # 項目概覽
├── VOICE_CONFIG.md               # 詳細配置說明
├── voice_tts.py                  # 語音合成模組
├── voice_asr.py                  # 語音識別模組
├── voice_integration.py          # 對話集成模組
├── voice_output_manager.py       # 語音輸出控制
└── voice_output_state.json       # 語音輸出狀態
```

---

## 給 AI 模型的 API 參考

### VoiceConversation 類

```python
from voice_integration import VoiceConversation

# 初始化
conversation = VoiceConversation()

# 檢查語音輸出是否開啟
if conversation.is_voice_output_enabled():
    # 語音開啟：文字 + 語音
    result = conversation.respond_speech(text="你好")
else:
    # 語音關閉：僅文字
    print("你好")
```

### 關鍵方法

| 方法 | 功能 | 返回 |
|------|------|------|
| `is_voice_output_enabled()` | 檢查語音是否開啟 | bool |
| `enable_voice_output()` | 開啟語音輸出 | bool |
| `disable_voice_output()` | 關閉語音輸出 | bool |
| `respond_speech(text)` | 發送語音回應（自動處理狀態） | dict |
| `transcribe(audio_file)` | 識別語音 | dict |

### respond_speech 返回值

```python
{
    'success': True,
    'output_file': '/path/to/audio.wav',  # 如果語音關閉則為 None
    'duration': 3.5,                      # 秒
    'message': 'control_command_executed'  # 可選
}
```

---

## 語音輸出控制

### 默認行為
- **默認關閉**語音輸出
- 只顯示文字回應，不生成音頻

### 控制指令

| 指令 | 功能 | 使用方式 |
|------|------|----------|
| `（` | 開啟語音輸出 | 獨立輸入（不是句子的一部分） |
| `）` | 關閉語音輸出 | 獨立輸入（不是句子的一部分） |

### 行為說明

| 語音狀態 | 回應類型 | 示例 |
|---------|---------|------|
| **開啟** | 文字 + 廣東話語音 | 文字："你好" + 音頻："你好.wav" |
| **關閉** | 僅文字 | 文字："你好" |

### 程式化控制

```python
# 開啟語音輸出
conversation.enable_voice_output()

# 關閉語音輸出
conversation.disable_voice_output()

# 切換語音輸出
conversation.toggle_voice_output()

# 檢查狀態
if conversation.is_voice_output_enabled():
    print("語音輸出已開啟")

# 獲取狀態
print(conversation.get_voice_output_status())
```

---

## 語音合成（TTS）

### 基本使用

```python
from voice_tts import synthesize_speech

result = synthesize_speech(
    text='你好，今日天氣很好。',
    output_file='output.wav',
    use_cantonese=True  # 關鍵：使用廣東話模式
)

print(f"輸出文件: {result['output_file']}")
print(f"長度: {result['duration']} 秒")
```

### 廣東話配置

- **模式**: `use_cantonese=True`
- **指令**: `'You are a helpful assistant. 请用广东话表达。<|endofprompt|>'`
- **語言**: 廣東話（Cantonese）

---

## 語音識別（ASR）

### 基本使用

```python
from voice_asr import transcribe_audio

result = transcribe_audio(
    audio_file='user_voice.ogg',
    language='yue'  # 廣東話
)

print(f"識別結果: {result['text']}")
```

### 支持的語言代碼

| 代碼 | 語言 |
|------|------|
| `yue` | 廣東話 |
| `zh` | 普通話 |
| `en` | 英語 |

---

## 使用流程（Telegram Bot）

### 完整流程

1. **用戶發送語音消息**
2. **Whisper 識別語音** → 顯示文字給用戶
3. **用戶確認識別結果** → 確認後繼續
4. **處理用戶請求** → 生成 AI 回應
5. **檢查語音輸出狀態**
   - 如果開啟：合成廣東話語音
   - 如果關閉：只顯示文字
6. **發送回應** → 文字 + （可選）語音

### 語音控制

- 用戶說「請開幫我查天氣**（**」→ **開啟語音輸出**
- 用戶說「請閉嘴**）**」→ **關閉語音輸出**

---

## 狀態文件

`voice_output_state.json`：

```json
{
  "enabled": false,
  "last_updated": "2026-02-11T09:00:00"
}
```

- `enabled`: `true` = 開啟, `false` = 關閉
- `last_updated`: 最後更新時間

---

## 配置修改

### 修改默認語言

```python
conversation = VoiceConversation(
    default_language='zh'  # 改為普通話
)
```

### 修改輸出目錄

```python
conversation = VoiceConversation(
    output_dir='/path/to/output'
)
```

### 修改模型

```python
conversation = VoiceConversation(
    model_dir='/path/to/model',
    whisper_model='base'  # 使用 Whisper Base
)
```

---

## 命令行測試

### 測試語音合成

```bash
cd /home/ubuntu/.openclaw/workspace/skills/cantonese-voice
source /home/ubuntu/CosyVoice/cosyvoice-env/bin/activate

# 廣東話模式（默認）
python voice_tts.py --text "你好，今日天氣很好。" --output output.wav

# 普通話模式
python voice_tts.py --text "你好，今天天气很好。" --output output.wav --no-cantonese
```

### 測試語音識別

```bash
python voice_asr.py --audio user_voice.ogg --language yue
```

### 測試對話流程

```bash
python voice_integration.py --mode test
```

### 測試語音輸出控制

```bash
python voice_output_manager.py
```

---

## 故障排除

### 語音輸出沒有音頻

檢查語音輸出狀態：
```python
print(conversation.get_voice_output_status())
```

### 語音是國語不是廣東話

確保使用 `use_cantonese=True`：
```python
synthesize_speech(text="你好", use_cantonese=True)
```

### 識別結果準確度低

- 確保使用正確的語言代碼 (`yue`)
- 檢查音頻質量
- 考慮使用更好的 Whisper 模型

---

## 相關記憶文件

- `/home/ubuntu/.openclaw/memory/VOICE_OUTPUT_CONTROL.md` - 語音輸出設定
- `/home/ubuntu/.openclaw/memory/CANTONESE_VOICE_DEVELOPMENT_LOG.md` - 開發經驗

---

## 支持

如有問題或建議，請参考記憶文件中的錯誤記錄和經驗。

---

**最後更新**: 2026-02-11 09:35
**版本**: 1.0
**適用模型**: Qwen32B-Q4, Llama, Claude, OpenAI 等
