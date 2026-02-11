# OpenClaw Cantonese Voice Skill 🎤

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue)](https://www.python.org)

廣東話語音輸入輸出系統，適用於 OpenClaw 和其他 LLM 框架
>
>

## ✨ 特性

- ✅ **語音識別 (ASR)** - Whisper Turbo 支持廣東話、普通話、英語
- ✅ **語音合成 (TTS)** - CosyVoice3 支持廣東話、普通話、多種語言
- ✅ **語音輸出開關** - 簡單控制語音輸出的開啟/關閉
- ✅ **100% 本地運行** - 無需雲端 API 或 API Key
- ✅ **模型兼容** - 適用於 Qwen、Llama、Claude、OpenAI 等 LLM

## 🚀 快速開始

### 安裝

```bash
# 克隆倉庫
git clone https://github.com/your-username/cantonese-voice-skill.git
cd cantonese-voice-skill
```

### 环境準備

```bash
# 創建虛擬環境
python3 -m venv venv
source venv/bin/activate

# 安裝依賴
pip install -r requirements.txt
```

### 下載模型

#### CosyVoice3 TTS
```bash
# 下載 CosyVoice3 模型
from modelscope import snapshot_download
snapshot_download('FunAudioLLM/Fun-CosyVoice3-0.5B-2512', local_dir='models/cosyvoice3')
```

#### Whisper ASR
```bash
# Whisper 模型會自動下載到 ~/.cache/whisper/
```

## 📖 使用方法

### 1. 語音識別

```python
from voice_asr import transcribe_audio

result = transcribe_audio(
    audio_file='user_voice.ogg',
    language='yue'  # 廣東話
)

print(f"識別結果: {result['text']}")
```

### 2. 語音合成

```python
from voice_tts import synthesize_speech

result = synthesize_speech(
    text='你好，今日天氣很好。',
    output_file='output.wav',
    use_cantonese=True  # 使用廣東話
)

print(f"輸出文件: {result['output_file']}")
```

### 3. 完整對話

```python
from voice_integration import VoiceConversation

conversation = VoiceConversation()

# 檢查語音輸出狀態
if conversation.is_voice_output_enabled():
    # 生成文字 + 廣東話語音
    result = conversation.respond_speech("你好")
else:
    # 只顸出文字
    print("你好")
```

### 4. 語音輸出控制

```python
from voice_integration import VoiceConversation

conversation = VoiceConversation()

# 開啟語音輸出
conversation.enable_voice_output()

# 關閉語音輸出
conversation.disable_voice_output()

# 切換語音輸出
conversation.toggle_voice_output()
```

## 🎯 給 LLM 模型的 API

### VoiceConversation 類

```python
from voice_integration import VoiceConversation

# 初始化
conversation = VoiceConversation()

# 關鍵方法
conversation.is_voice_output_enabled()  # 返回 bool
conversation.enable_voice_output()      # 開啟語音
conversation.disable_voice_output()     # 關閉語音
conversation.respond_speech(text)       # 發送回應
conversation.transcribe(audio_file)     # 識別語音
```

### respond_speech 返回值

```python
{
    'success': True,
    'output_file': '/path/to/audio.wav',  # 音頻文件（如果語音開啟）
    'duration': 3.5,                       # 秒
    'message': 'control_command_executed'  # 可選信息
}
```

## 🎛️ 語音輸出開關

### 控制指令

| 指令 | 功能 |
|------|------|
| `（` | 開啟語音開啟語音輸出（獨立指令） |
| `）` | 關閉語音輸出（獨立指令） |

### 行為說明

| 語音狀態 | 回應類型 |
|---------|---------|
| **開啟** | 文字 + 廣東話語音 |
| **關閉** | 僅文字 |

## 🌐 支持的語言

### 語音識別 (Whisper)

| 代碼 | 語言 |
|------|------|
| `yue` | 廣東話 |
| `zh` | 普通話 |
| `en` | 英語 |

### 語音合成 (CosyVoice3)

- 廣東話（Cantonese）
- 普通話（Mandarin）
- 英語（English）
- 日語（Japanese）
- 韓語（Korean）
- 德語（Deutsch）
- 西班牙語（Español）
- 法語（Français）
- 義大利語（Italiano）
- 俄語（Русский）
- 18+ 中文方言

## 📁 項目結構

```
cantone
-voice/
├── SKILL.md                      # 技能使用說明（給 LLM 模型）
├── README.md                     # 本文件
├── requirements.txt              # Python 依賴
├── voice_tts.py                  # 語音合成模組
├── voice_asr.py                  # 語音識別模組
├── voice_integration.py          # 對話集成模組
├── voice_output_manager.py       # 語音輸出控制
└── examples/                     # 使用範例
    ├── basic_usage.py            # 基本用法
    ├── telegram_bot.py           # Telegram Bot 集成
    └── voice_control.py          # 語音輸出控制
```

## 🖥️ 硬體需求

### 最低配置
- CPU: 4 cores
- RAM: 8 GB
- Disk: 15 GB（模型文件）

### 推薦配置
- CPU: 8+ cores
- RAM: 16+ GB
- GPU: NVIDIA GPU with 8GB VRAM
- Disk: 20+ GB SSD

### 測試硬體
- Intel N100 (4 cores, 11GB RAM)
- TTS RTF: 12-13 (CPU), < 1 (GPU)
- ASR RTF: 0.8 (CPU), < 0.1 (GPU)

## 🔧 配置

### 修改默認語言

```python
conversation = VoiceConversation(
    default_language='zh'
)
```

### 修改模型路徑

```python
conversation = VoiceConversation(
    model_dir='/path/to/cosyvoice3',
    whisper_model='turbo'
)
```

### 修改輸出目錄

```python
conversation = VoiceConversation(
    output_dir='/path/to/output'
)
```

## 🐛 故障排除

### 語音是國語不是廣東話
確保在 `voice_tts.py` 中使用 `use_cantonese=True`

### 語音輸出沒有音頻
檢查 `voice_output_state.json` 或調用 `conversation.is_voice_output_enabled()`

### 識別結果準確度低
- 使用正確的語言代碼（`yue` for 廣東話）
- 檢查音頻質量
- 使用更好的 Whisper 模型（base→small→medium）

### 語音合成超時問題
⚠️ **常見問題**：時常收不到「文字+語音」回應

✅ **解決方案**：系統已實現雙重保護機制
1. **超時保護**：50 秒自動超時，返回文字回應
2. **自動截斷**：>33 字自動截斷，確保可控等待時間

詳見 [SETTINGS.md](SETTINGS.md) 了解完整設定和調優方法。

## 📝 開發記錄

完整的開發記錄、報錯和解決方案請參考：
- [VOICE_OUTPUT_CONTROL.md](docs/VOICE_OUTPUT_CONTROL.md) - 語音輸出設定
- [CANTONESE_VOICE_DEVELOPMENT_LOG.md](docs/CANTONESE_VOICE_DEVELOPMENT_LOG.md) - 開發經驗

## 🤝 貢獻

歡迎提交 Issue 和 Pull Request！

## 📄 License

MIT License

## 🙏 致謝

- [CosyVoice3](https://github.com/FunAudioLLM/CosyVoice) - Alibaba FunAudioLLM Team
- [Whisper](https://github.com/openai/whisper) - OpenAI
- [OpenClaw](https://github.com/openclaw/openclaw) - OpenClaw Team

---

**最後更新**: 2026-02-11 15:55
**版本**: v1.2.1
**重要更新**: 添加超時保護和自動截斷機制