#!/usr/bin/env python3
"""
語音對話集成模組
整合 CosyVoice (TTS) 和 Whisper (ASR)

使用方法:
    from voice_integration import VoiceConversation

    conversation = VoiceConversation()

    # 識別用戶語音
    result = conversation.transcribe('/path/to/user_voice.ogg')

    # 等待用戶確認
    if result['success']:
        print(f"識別結果: {result['text']}")

        # 發送語音回應
        conversation.respond_speech("收到！我正在處理您的請求。")
"""

import os
import sys

# 添加路徑
COSYVOICE_DIR = '/home/ubuntu/CosyVoice'
sys.path.insert(0, f'{COSYVOICE_DIR}/third_party/Matcha-TTS')
sys.path.insert(0, COSYVOICE_DIR)

from voice_asr import transcribe_audio
from voice_tts import synthesize_speech
from voice_output_manager import VoiceOutputManager


class VoiceConversation:
    """
    語音對話類
    整合 ASR 和 TTS 功能
    """

    def __init__(
        self,
        model_dir: str = None,
        whisper_model: str = 'turbo',
        default_language: str = 'yue',
        output_dir: str = '/home/ubuntu/桌面/ok',
        voice_output_manager: VoiceOutputManager = None
    ):
        """
        初始化語音對話

        Args:
            model_dir: CosyVoice 模型目錄
            whisper_model: Whisper 模型名稱
            default_language: 默認語言 (yue - 廣東話)
            output_dir: 輸出目錄
            voice_output_manager: 語音輸出管理器
        """
        self.model_dir = model_dir or f'{COSYVOICE_DIR}/pretrained_models/Fun-CosyVoice3-0.5B'
        self.whisper_model = whisper_model
        self.default_language = default_language
        self.output_dir = output_dir
        self.voice_output = voice_output_manager or VoiceOutputManager()

        # 確保輸出目錄存在
        os.makedirs(output_dir, exist_ok=True)

    def transcribe(
        self,
        audio_file: str,
        language: str = None
    ) -> dict:
        """
        識別語音輸入

        Args:
            audio_file: 音頻文件路徑
            language: 語言代碼 (默認: default_language)

        Returns:
            dict: 識別結果
        """
        if language is None:
            language = self.default_language

        result = transcribe_audio(
            audio_file=audio_file,
            language=language,
            model_name=self.whisper_model
        )

        # 處理語音輸出控制命令
        if result['success']:
            parse_result = self.voice_output.parse_command(result['text'])
            result['text'] = parse_result['text']
            result['voice_enabled'] = parse_result['voice_enabled']
            result['control_action'] = parse_result['action']

        return result

    def synthesize(
        self,
        text: str,
        output_file: str = None,
        speed: float = 1.0,
        force: bool = False,
        timeout: float = 50  # 超時時間（秒）
    ) -> dict:
        """
        合成語音輸出

        Args:
            text: 要合成的文本
            output_file: 輸出文件路徑 (默認: 自動生成)
            speed: 語音速度
            force: 強制合成（忽略語音輸出狀態）
            timeout: 超時時間（秒）

        Returns:
            dict: 合成結果
        """
        # 檢查語音輸出是否啟用
        if not force and not self.voice_output.is_enabled():
            return {
                'success': False,
                'output_file': None,
                'duration': 0,
                'error': 'voice_output_disabled',
                'message': '語音輸出已關閉'
            }

        # 生成輸出文件路徑
        if output_file is None:
            import time
            timestamp = int(time.time())
            output_file = f'{self.output_dir}/voice_response_{timestamp}.wav'

        return synthesize_speech(
            text=text,
            output_file=output_file,
            model_dir=self.model_dir,
            speed=speed,
            timeout=timeout
        )

    def respond_speech(
        self,
        text: str,
        display_text: bool = True,
        speed: float = 1.0,
        force: bool = False,
        timeout: float = 50  # 超時時間（秒）
    ) -> dict:
        """
        發送語音回應 (帶顯示文字)

        Args:
            text: 回應文本
            display_text: 是否顯示文字
            speed: 語音速度
            force: 強制合成（忽略語音輸出狀態）

        Returns:
            dict: 合成結果
                - success: 是否成功
                - output_file: 音頻文件路徑（如果語音開啟且不是純控制指令）
                - duration: 音頻長度
                - action: 控制指令類型（'enable', 'disable', 或 None）
                - message: 信息
                - voice_enabled: 語音輸出是否啟用
        """
        # 檢查並處理語音輸出控制命令
        parse_result = self.voice_output.parse_command(text)
        processed_text = parse_result['text']
        action = parse_result['action']
        voice_enabled = parse_result['voice_enabled']

        # 構建結果
        result = {
            'success': True,
            'output_file': None,
            'duration': 0,
            'action': action,
            'message': None,
            'voice_enabled': voice_enabled
        }

        # 如果不是純控制指令，生成語音
        if processed_text.strip():
            # 計算預計合成時間（每字約 1.5 秒）
            estimated_seconds = len(processed_text) * 1.5
            max_safe_seconds = 50  # 最大安全時間（秒）
            max_safe_chars = int(max_safe_seconds / 1.5)  # 最多 33 字

            original_text = processed_text
            text_truncated = False

            # 檢查是否需要截斷
            if len(processed_text) > max_safe_chars:
                processed_text = processed_text[:max_safe_chars] + "..."
                text_truncated = True
                print(f"⚠️ 文本過長（{len(original_text)} 字，預計 {estimated_seconds:.1f} 秒 > 50 秒）")
                print(f"✂️  自動截斷為 {max_safe_chars} 字以保證在 50 秒內完成")
            else:
                # 正常文本，顯示進度提示
                print(f"⏳ 語音合成中...（預計 {estimated_seconds:.1f} 秒）")

            synthesis_result = self.synthesize(processed_text, speed=speed, force=force, timeout=timeout)

            # 檢查是否超時
            if synthesis_result.get('timed_out'):
                print("⚠️ 語音合成超時！僅返回文字回應")
                result['timed_out'] = True
                result['message'] = 'synthesis_timeout'

            result['output_file'] = synthesis_result.get('output_file')
            result['duration'] = synthesis_result.get('duration', 0)
            result['success'] = synthesis_result['success']
            result['original_text'] = original_text  # 保存原始文本
            result['text_truncated'] = text_truncated  # 記錄是否截斷
        else:
            # 純控制指令，設置消息
            if action == 'enable':
                result['message'] = 'voice_output_enabled'
            elif action == 'disable':
                result['message'] = 'voice_output_disabled'

        # 顯示文字
        if display_text:
            print("=" * 60)
            if processed_text.strip():
                if result.get('timed_out'):
                    # 超時情況
                    print("⚠️ 語音合成超時")
                    print("=" * 60)
                    print(f"📝 文字: {original_text}")
                    print(f"⏱️  說明: 合成時間超過 {timeout} 秒，僅返回文字")
                elif result['success'] and result.get('output_file'):
                    # 成功生成語音
                    if result.get('text_truncated'):
                        print("✂️  文本已自動截斷")
                        print("=" * 60)
                        print(f"📝 原始文本: {original_text}")
                        print(f"📝 合成文本: {processed_text}")
                        print(f"📁 音頻: {result['output_file']}")
                        print(f"📏 長度: {result['duration']:.2f} 秒")
                        print(f"💡 說明: 文本過長已截斷以保證在 50 秒內完成")
                    else:
                        print("🔊 語音回應")
                        print("=" * 60)
                        print(f"📝 文字: {processed_text}")
                        print(f"📁 音頻: {result['output_file']}")
                        print(f"📏 長度: {result['duration']:.2f} 秒")
                else:
                    # 語音輸出關閉或失敗
                    print("📝 文字回應")
                    print("=" * 60)
                    original_full = result.get('original_text', original_text)
                    print(f"📝 文字: {original_full}")
                    if result.get('message'):
                        print(f"ℹ️  狀態: {result['message']}")
            elif action:
                # 控制指令
                status_text = "開啟" if action == 'enable' else "關閉"
                print("🎛️ 控制指令已執行")
                print("=" * 60)
                print(f"📊 語音輸出狀態: {status_text}")
                print(f"📝 建議回應: 語音輸出已{status_text}")
            print("=" * 60)

        return result

    def conversation_flow(
        self,
        user_audio: str,
        ai_response: str
    ) -> dict:
        """
        完整對話流程 (手動確認模式)

        Args:
            user_audio: 用戶語音文件
            ai_response: AI 回應文本

        Returns:
            dict: 完整對話結果
        """
        result = {
            'transcription': None,
            'confirmation': False,
            'response': None,
            'success': False
        }

        # 1. 識別用戶語音
        print("=" * 60)
        print("🎤 語音識別中...")
        print("=" * 60)
        transcription_result = self.transcribe(user_audio)

        if not transcription_result['success']:
            print(f"❌ 識別失敗: {transcription_result['error']}")
            return result

        # 顯示識別結果
        print("\n識別結果:")
        print(f"  {transcription_result['text']}")
        print(f"  (时長: {transcription_result['duration']:.2f} 秒)")
        print()

        # 2. 等待用戶確認
        print("=" * 60)
        print("❓ 請確認識別結果")
        print("=" * 60)
        print("[1] ✓ 確認")
        print("[2] 修改文字")
        print("[3] 取消")
        print()

        # 注意：這裡需要實際的用戶輸入邏輯
        # 在 Telegram Bot 中會通過按鈕實現
        result['transcription'] = transcription_result
        result['confirmation'] = True  # 默認確認

        # 3. 發送語音回應
        if result['confirmation']:
            response_result = self.respond_speech(ai_response)
            result['response'] = response_result
            result['success'] = response_result['success']
        else:
            print("⚠️ 用戶取消對話")

        return result

    def enable_voice_output(self) -> bool:
        """
        開啟語音輸出

        Returns:
            bool: 是否成功
        """
        return self.voice_output.enable()

    def disable_voice_output(self) -> bool:
        """
        關閉語音輸出

        Returns:
            bool: 是否成功
        """
        return self.voice_output.disable()

    def toggle_voice_output(self) -> bool:
        """
        切換語音輸出狀態

        Returns:
            bool: 切換後的狀態（True = 開啟）
        """
        return self.voice_output.toggle()

    def is_voice_output_enabled(self) -> bool:
        """
        檢查語音輸出是否啟用

        Returns:
            bool: 是否啟用
        """
        return self.voice_output.is_enabled()

    def get_voice_output_status(self) -> str:
        """
        獲取語音輸出狀態信息

        Returns:
            str: 狀態信息
        """
        return self.voice_output.get_status_info()


def test_voice_conversation():
    """
    測試語音對話流程
    """
    # 創建對話實例
    conversation = VoiceConversation()

    print("=" * 60)
    print("📊 語音對話測試")
    print("=" * 60)
    print()

    # 測試文本輸入 (不需要實際音頻)
    test_text = "你好，今日天氣很好，我想去行山。"
    print(f"測場景: 用戶說「{test_text}」")
    print()

    # 模擬 AI 回應
    ai_response = "收到！今日天氣很好，去行山是一個很好的主意。要帶足水和注意安全哦！"
    print(f"AI 回應: {ai_response}")
    print()

    # 合成語音
    result = conversation.respond_speech(ai_response)

    if result['success']:
        print("\n✅ 語音對話測試完成！")
    else:
        print(f"\n❌ 測試失敗: {result['error']}")


def main():
    """
    主程序
    """
    import argparse

    parser = argparse.ArgumentParser(description='語音對話集成測試')
    parser.add_argument('--mode', type=str, default='test',
                       choices=['test', 'asr', 'tts', 'conversation'],
                       help='測試模式')
    parser.add_argument('--audio', type=str,
                       help='音頻文件 (用於 asr 或 conversation 模式)')
    parser.add_argument('--text', type=str,
                       help='文本 (用於 tts 模式)')
    parser.add_argument('--output', type=str,
                       help='輸出文件 (用於 tts 模式)')

    args = parser.parse_args()

    conversation = VoiceConversation()

    if args.mode == 'test':
        test_voice_conversation()

    elif args.mode == 'asr':
        if not args.audio:
            print("錯誤：asr 模式需要 --audio 參數")
            return

        result = conversation.transcribe(args.audio)
        if result['success']:
            print(f"識別結果: {result['text']}")
        else:
            print(f"識別失敗: {result['error']}")

    elif args.mode == 'tts':
        if not args.text:
            print("錯誤：tts 模式需要 --text 參數")
            return

        result = conversation.synthesize(
            text=args.text,
            output_file=args.output
        )
        if result['success']:
            print(f"合成成功: {result['output_file']} ({result['duration']:.2f}s)")
        else:
            print(f"合成失敗: {result['error']}")

    elif args.mode == 'conversation':
        if not args.audio:
            print("錯誤：conversation 模式需要 --audio 參數")
            return

        # 模擬對話 (不需要 AI 實際回應)
        result = conversation.conversation_flow(
            user_audio=args.audio,
            ai_response="收到！我正在處理您的請求。"
        )

        print(f"\n對話結果: {'成功' if result['success'] else '失敗'}")


if __name__ == '__main__':
    main()
