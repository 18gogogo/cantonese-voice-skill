# Telegram 集成文檔

## 概述

本文檔說明如何將 Cantonese Voice Skill 集成到 Telegram Bot 中，特別關注語音合成后的音頻發送流程。

---

## 核心要求 ⚠️

### 合成語音後必須傳送到 Telegram 及用戶

**關鍵規則**：
- ✅ 合成完成 → 立即發送到 Telegram
- ✅ 同時顯示文字回應
- ✅ 格式：「文字 + 語音音頻文件」
- ❌ 不能只合成不發送

---

## 集成流程

### 完整流程

```
1. 用戶發送請求 (Telegram)
          ↓
2. 解析控制指令 (（或））
          ↓
3. 檢查語音輸出狀態
          ↓
4. 生成 AI 回應 (OpenClaw LLM)
          ↓
5. 檢查文本長度 (>33字？)
    ├─ 是 → 截斷為33字 → 合成短文本語音
    └─ 否 → 直接合成語音
          ↓
6. 合成完成 (output_file.wav)
    ↓
7. ⚠️ 必須發送到 Telegram
    ├─ 發送文字回應
    └─ 發送音頻文件 (作為語音消息或附件)
```

---

## Python-Telegram-Bot 實現示例

### 基本用法

```python
from telegram import Update
from telegram.ext import ContextTypes
from voice_integration import VoiceConversation

# 初始化
voice = VoiceConversation()

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """處理 Telegram 用戶消息"""
    user_id = update.effective_user.id
    user_text = update.message.text

    # 1. 檢查語音輸出狀態
    if voice.is_voice_output_enabled():
        # 2. 合成語音
        result = voice.respond_speech(
            text=user_text,
            display_text=False  # 不在控制台顯示，直接發送到 Telegram
        )

        # 3. ⚠️ 必須發送到 Telegram
        if result.get('output_file') and result['success']:
            audio_file = result['output_file']

            # 發送文字回應
            await update.message.reply_text(
                text=user_text,
                reply_markup=None
            )

            # 發送語音音頻 (方法 1: 作為語音消息)
            with open(audio_file, 'rb') as audio:
                await update.message.reply_voice(
                    voice=audio,
                    caption=None
                )

            # 或 (方法 2: 作為音頻文件)
            # with open(audio_file, 'rb') as audio:
            #     await update.message.reply_audio(
            #         audio=audio,
            #         title="AI 回應",
            #         performer="CosyVoice3"
            #     )

        else:
            # 語音合成失敗或超時，只發送文字
            await update.message.reply_text(
                text=user_text,
                reply_markup=None
            )

            if result.get('timed_out'):
                await update.message.reply_text(
                    text="⚠️ 語音合成超時，已返回文字回應"
                )
    else:
        # 語音輸出關閉，只發送文字
        await update.message.reply_text(
            text=user_text,
            reply_markup=None
        )
```

---

## 發送方法對比

### 方法 1: 語音消息 (Voice Message)
```python
async def send_voice(update, audio_file):
    """發送為語音消息（推薦）"""
    await update.message.reply_voice(voice=open(audio_file, 'rb'))
```

**優點**：
- ✅ Telegram 自動顯示時間長度
- ✅ 可以調整播放速度
- ✅ 語音消息更自然

**缺點**：
- ⚠️ 只支持 OGG/WAV
- ⚠️ 需要轉換為 ogg 格式（WAV 需轉換）

---

### 方法 2: 音頻文件 (Audio File)
```python
async def send_audio(update, audio_file):
    """發送為音頻文件"""
    await update.message.reply_audio(
        audio=open(audio_file, 'rb'),
        title="AI 回應",
        caption="廣東話語音"
    )
```

**優點**：
- ✅ 支持多種格式（WAV/MP3/OGG）
- ✅ 可以顯示標題和描述
- ✅ 可以加封面圖

**缺點**：
- ⚠️ 沒有播放速度控制
- ⚠️ 不能轉發為語音消息

---

### 方法 3: 文檔附件 (Document)
```python
async def send_document(update, audio_file):
    """發送為文檔附件"""
    await update.message.reply_document(
        document=open(audio_file, 'rb'),
        filename="ai_response.wav",
        caption="AI 回應音頻"
    )
```

**優點**：
- ✅ 任何格式都可發送
- ✅ 文件大小可更大

**缺點**：
- ❌ 不能直接播放
- ❌ 用戶需要下載后播放

---

## 推薦設置

### 格式轉換（WAV → OGG）

CosyVoice 默認輸出 WAV，Telegram 語音消息需要 OGG：

```python
import pydub
import tempfile
import os

def convert_wav_to_ogg(wav_file: str) -> str:
    """轉換 WAV 為 OGG"""
    ogg_file = tempfile.mktemp(suffix='.ogg')

    # 使用 pydub 轉換
    audio = pydub.AudioSegment.from_wav(wav_file)
    audio.export(ogg_file, format='ogg', codec='libopus')

    return ogg_file

# 使用
async def send_voice_converted(update, wav_file):
    """轉換後發送語音消息"""
    ogg_file = convert_wav_to_ogg(wav_file)

    try:
        await update.message.reply_voice(voice=open(ogg_file, 'rb'))
    finally:
        # 清理臨時文件
        if os.path.exists(ogg_file):
            os.remove(ogg_file)
```

---

## respond_speech 返回值使用

```python
result = voice.respond_speech("你好")

# 返回值結構
{
    'success': True,           # 是否成功
    'output_file': '/path/to/audio.wav',  # 音頻文件路徑（如果合成成功）
    'duration': 3.5,          # 音頻長度（秒）
    'action': None,           # 控制指令類型 ('enable', 'disable', None)
    'message': None,          # 附加信息
    'voice_enabled': True,     # 語音輸出是否啟用
    'timed_out': False,       # 是否超時
    'text_truncated': False,  # 文本是否被截斷
    'original_text': '...'    # 原始文本（如果被截斷）
}

# 檢查是否應該發送語音
if result.get('success') and result.get('output_file'):
    # ✅ 有音頻文件 → 發送到 Telegram
    audio_file = result['output_file']
    await send_to_telegram(audio_file)
elif result.get('timed_out'):
    # ⚠️ 超時 → 只發送文字
    await send_text_only()
else:
    # ❌ 語音輸出關閉 → 只發送文字
    await send_text_only()
```

---

## 錯誤處理

### 音頻文件不存在

```python
if result.get('output_file'):
    audio_file = result['output_file']

    if os.path.exists(audio_file):
        # 發送音頻
        await update.message.reply_voice(voice=open(audio_file, 'rb'))
    else:
        # 文件生成失敗
        await update.message.reply_text(
            "⚠️ 音頻文件生成失敗，僅返回文字回應"
        )
```

---

### 發送失敗處理

```python
try:
    await update.message.reply_voice(voice=open(audio_file, 'rb'))
except Exception as e:
    # 發送失敗，回退到文字
    print(f"語音發送失敗: {e}")
    await update.message.reply_text(
        "文字回應（語音發送失敗）"
    )
```

---

## 性能優化

### 合成后立即發送

```python
# ✅ 好做法：合成后立即發送
result = voice.respond_speech(text)
if result.get('output_file'):
    await send_voice(result['output_file'])

# ❌ 壞做法：等待多個請求后批量發送
results = []
for text in texts:
    results.append(voice.respond_speech(text))
# 批量發送可能導致用戶等待時間過長
```

---

## 長文本處理示例（重要！）

### 正確處理方式

```python
async def handle_long_text(update, text):
    """正確處理長文本（> 33 字）"""
    # 1. 合成語音（自動截斷為 33 字）
    result = voice.respond_speech(text, display_text=False)

    # 2. ⚠️ 發送原始完整長文本（不截斷）
    await update.message.reply_text(text)  # 完整的 80 字

    # 3. ⚠️ 發送截斷后的短語音
    if result.get('output_file'):
        with open(result['output_file'], 'rb') as audio:
            await update.message.reply_voice(voice=audio)
        # 音頻內容：33 字短文本（非完整 80 字）
```

### 示例對比

| 項目 | 內容 |
|------|------|
| 用戶輸入 | 「這是一個非常長的句子，可能超過33字限制，需要確保用戶能看到完整內容...」（80 字）|
| 發送文字 | 「這是一個非常長的句子，可能超過33字限制，需要確保用戶能看到完整內容...」（80 字，完整）✅|
| 語音內容 | 「這是一個非常長的句子，可能超過33...」（33 字，截斷）✅|
| 用戶看到 | 完整文字 + 短語音（都能收到）✅|

### 常見錯誤

```python
# ❌ 錯誤做法：發送截斷后的文字
await update.message.reply_text(processed_text)  # 只發送 33 字
# 用戶看不到完整內容！

# ❌ 錯誤做法：截斷 user 輸入再發送
short_text = text[:33] + "..."
await update.message.reply_text(short_text)  # 只發送 33 字
# 用戶看不到完整內容！

# ✅ 正確做法：發送原始完整文本
await update.message.reply_text(text)  # 發送完整 80 字
# 用戶能看到完整內容！
```

**關鍵規則**：
- 📝 **文字必須完整**：發送原始長文本（不截斷）
- 🎤 **語音可以短**：使用截斷后的短文本合成的音頻
- 🎯 **目的**：用戶既能聽到短語音，又能看到完整文字

---

## 完整示例

```python
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes
from voice_integration import VoiceConversation

# 初始化
voice = VoiceConversation()

async def voice_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """開啟語音輸出"""
    voice.enable_voice_output()
    result = voice.respond_speech('語音輸出已開啟', display_text=False)

    if result.get('output_file'):
        # ⚠️ 必須發送音頻
        with open(result['output_file'], 'rb') as audio:
            await update.message.reply_voice(voice=audio)
    else:
        await update.message.reply_text('語音輸出已開啟')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """處理普通消息"""
    text = update.message.text

    if voice.is_voice_output_enabled():
        # 合成語音
        result = voice.respond_speech(text, display_text=False)

        # 發送文字（使用原始完整長文本）
        # ⚠️ 重要：發送原始長文本，不是截斷后的文本
        await update.message.reply_text(text)

        # ⚠️ 必須發送音頻（使用截斷后的短文本合成的音頻）
        if result.get('output_file') and os.path.exists(result['output_file']):
            with open(result['output_file'], 'rb') as audio:
                await update.message.reply_voice(voice=audio)
        elif result.get('timed_out'):
            await update.message.reply_text('⏱️ 語音合成超時，僅返回文字')
    else:
        # 只發送文字
        await update.message.reply_text(text)

# 應用設置
application = Application.builder().token("YOUR_BOT_TOKEN").build()

application.add_handler(CommandHandler("voice", voice_command))
application.add_handler(MessageHandler(None, handle_message))

application.run_polling()
```

---

## 檢查清單

發送音頻前必須確認：
- [ ] 音頻文件路徑正確
- [ ] 音頻文件存在
- [ ] 音頻文件可讀
- [ ] 文件大小 < Telegram 限制（50MB）
- [ ] 格式正確（WAV/OGG/MP3）
- [ ] 同時發送文字回應
- [ ] 錯誤處理（發送失敗時回退到文字）

---

**最後更新**: 2026-02-11 16:35
**重要性**: ⚠️ 關鍵要求（長文本處理规则已明确）
