# 廣東話語音系統 - 配置說明

## 安裝位置

- **技能目錄**: `/home/ubuntu/.openclaw/workspace/skills/cantonese-voice/`
- **CosyVoice**: `/home/ubuntu/CosyVoice/`
- **CosyVoice 模型**: `/home/ubuntu/CosyVoice/pretrained_models/Fun-CosyVoice3-0.5B/`
- **Whisper 模型**: `~/.cache/whisper/turbo.pt`

## 環境配置

### 必要環境變量 (可選)

```bash
# CosyVoice 模型路徑
export COSYVOICE_MODEL_DIR="/home/ubuntu/CosyVoice/pretrained_models/Fun-CosyVoice3-0.5B"

# Whisper 模型配置
export WHISPER_MODEL="turbo"
export WHISPER_LANGUAGE="yue"

# 輸出目錄
export OUTPUT_DIR="/home/ubuntu/桌面/ok"
```

### Python 虛擬環境

```bash
# 激活 CosyVoice 虛擬環境
cd /home/ubuntu/CosyVoice
source cosyvoice-env/bin/activate
```

## 模組使用

### 1. 語音識別 (ASR)

```python
from voice_asr import transcribe_audio

# 識別語音
result = transcribe_audio(
    audio_file='user_voice.ogg',
    language='yue',
    model_name='turbo'
)

if result['success']:
    print(f"識別文字: {result['text']}")
    print(f"時長: {result['duration']}秒")
```

### 2. 語音合成 (TTS)

```python
from voice_tts import synthesize_speech

# 合成語音
result = synthesize_speech(
    text='你好，今日天氣很好。',
    output_file='response.wav',
    model_dir='/home/ubuntu/CosyVoice/pretrained_models/Fun-CosyVoice3-0.5B'
)

if result['success']:
    print(f"音頻文件: {result['output_file']}")
    print(f"長度: {result['duration']}秒")
```

### 3. 完整對話流程

```python
from voice_integration import VoiceConversation

# 創建對話實例
conversation = VoiceConversation()

# 識別用戶語音
transcription_result = conversation.transcribe('user_voice.ogg')

# 顯示識別結果等待確認
if transcription_result['success']:
    print(f"識別: {transcription_result['text']}")

    # 合成並發送語音回應
    conversation.respond_speech("收到！我正在處理您的請求。")
```

## 命令行界面

### ASR 測試

```bash
# 識別語音
python voice_asr.py --audio user_voice.ogg \
    --language yue \
    --model turbo
```

### TTS 測試

```bash
# 合成語音
python voice_tts.py --text "你好，今日天氣很好。" \
    --output response.wav \
    --speed 1.0
```

### 集成測試

```bash
# 測試對話流程
python voice_integration.py --mode test

# 測試 ASR
python voice_integration.py --mode asr --audio user_voice.ogg

# 測試 TTS
python voice_integration.py --mode tts --text "測試文本"

# 測試完整對話
python voice_integration.py --mode conversation --audio user_voice.ogg
```

## 性能參數

### 處理速度 (當前 CPU 模式)

| 操作 | 模式 | RTF (實時因子) | 10 秒音頻的處理時間 |
|------|------|----------------|-------------------|
| TTS | CPU | ~12.4 | 124 秒 |
| ASR | CPU | ~0.8 | 8 秒 |

### GPU 模式 (預估，若 NVIDIA 可用)

| 操作 | 模式 | RTF (實時因子) | 10 秒音頻的處理時間 |
|------|------|----------------|-------------------|
| TTS | GPU | < 1 | < 10 秒 |
| ASR | GPU | < 0.1 | < 1 秒 |

**說明**:
- RTF = 處理時間 / 音頻時長
- RTF < 1: 實時或更快
- RTF = 1: 與音頻時長相同
- RTF > 1: 比實時慢

## 限制和注意事項

### 1. 參考音頻 (TTS)
- CosyVoice 需要 1 秒參考音頻
- 參考音頻位置: `/home/ubuntu/CosyVoice/pretrained_models/Fun-CosyVoice3-0.5B/reference_audio.wav`
- 系統會自動創建默認音頻（如果不存在）

### 2. GPU 檢測
- 當前系統使用 CPU 模式
- N100 GPU 檢測失敗，待修復
- 使用 GPU 顯著提升 TTS 速度 (從 12RTF 到 <1RTF)

### 3. 語音品質
- Whisper 對音頻品質要求較高
- 建議使用高品質錄音 (16kHz+)
- 背景噪音會影響識別準確度

### 4. 語言支持
- 主要支持廣東話 (yue)
- CosyVoice 支持多種語言和風格
- 通過文本自動識別語言

## 數據格式

### 輸入音頻格式 (ASR)
- 支持格式: WAV, MP3, OGG
- 采樣率: 16000 Hz+ (建議 24000 Hz)
- 聲道: 單聲道或立體聲

### 輸出音頻格式 (TTS)
- 格式: WAV
- 采樣率: 24000 Hz
- 聲道: 單聲道
- 位元深度: 16-bit PCM

## 測試腳本

### TTS 測試
```bash
# 使用 CosyVoice 測試腳本
cd /home/ubuntu/CosyVoice
source cosyvoice-env/bin/activate
python test_tts_final.py
```

### ASR 測試
```bash
# 使用 Whisper 測試腳本
cd /home/ubuntu/CosyVoice
source cosyvoice-env/bin/activate
python test_cantonese_asr.py
```

### 集成測試
```bash
# 使用技能包測試腳本
cd /home/ubuntu/.openclaw/workspace/skills/cantonese-voice
source /home/ubuntu/CosyVoice/cosyvoice-env/bin/activate
python voice_integration.py --mode test
```

## 故障排除

### CosyVoice 初始化失敗
```bash
# 檢查模型文件
ls /home/ubuntu/CosyVoice/pretrained_models/Fun-CosyVoice3-0.5B/

# 確認 cosyvoice3.yaml 存在
ls /home/ubuntu/CosyVoice/pretrained_models/Fun-CosyVoice3-0.5B/cosyvoice3.yaml
```

### Whisper 識別失敗
```bash
# 檢查模型
ls ~/.cache/whisper/turbo.pt

# 測試模型加載
python -c "import whisper; model = whisper.load_model('turbo'); print('OK')"
```

### 依賴問題
```bash
# 檢查 Python 版本
cd /home/ubuntu/CosyVoice
source cosyvoice-env/bin/activate
python --version  # 需要 Python 3.12+
```

## 下一步

1. **Telegram Bot 集成**: 實現語音消息的接收和發送
2. **手動確認機制**: 實現文本確認工作流
3. **性能優化**: 修復 GPU 檢測，加速處理
4. **多語言支持**: 擴展到其他語言和方言
