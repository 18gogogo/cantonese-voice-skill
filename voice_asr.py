#!/usr/bin/env python3
"""
Whisper ASR - 語音識別模組
支援廣東話語音識別

使用方法:
    from voice_asr import transcribe_audio

    result = transcribe_audio(
        audio_file='user_voice.ogg',
        language='yue'  # 廣東話
    )

    print(result['text'])
    print(result['language'])
"""

import whisper
import os


def transcribe_audio(
    audio_file: str,
    language: str = 'yue',
    model_name: str = 'turbo',
    initial_prompt: str = None
) -> dict:
    """
    使用 Whisper 識別語音

    Args:
        audio_file: 音頻文件路徑
        language: 語言代碼 (默認: yue - 廣東話)
        model_name: Whisper 模型名稱 (默認: turbo)
        initial_prompt: 初始提示詞 (可提高識別準確度)

    Returns:
        dict: {
            'text': str,              # 識別文字
            'language': str,          # 語言代碼
            'duration': float,        # 音頻長度 (秒)
            'segments': list,         # 識別段落
            'model': str,             # 使用的模型
            'success': bool,          # 是否成功
            'error': str              # 錯誤訊息 (如果失敗)
        }
    """
    # 檢查文件是否存在
    if not os.path.exists(audio_file):
        return {
            'text': '',
            'language': '',
            'duration': 0,
            'segments': [],
            'model': model_name,
            'success': False,
            'error': f'文件不存在: {audio_file}'
        }

    result = {
        'text': '',
        'language': '',
        'duration': 0,
        'segments': [],
        'model': model_name,
        'success': False,
        'error': None
    }

    try:
        # 初始提示詞 (廣東話)
        if initial_prompt is None:
            initial_prompt = "這段錄音是講廣東話的，"

        # 加載 Whisper 模型
        model = whisper.load_model(model_name)

        # 識別語音
        result_data = model.transcribe(
            audio_file,
            language=language,
            initial_prompt=initial_prompt,
            word_timestamps=False
        )

        # 提取結果
        result['text'] = result_data['text'].strip()
        result['language'] = result_data['language']
        result['duration'] = result_data.get('duration', 0)

        # 提取段落
        if 'segments' in result_data:
            result['segments'] = [
                {
                    'start': seg['start'],
                    'end': seg['end'],
                    'text': seg['text'].strip()
                }
                for seg in result_data['segments']
            ]

        result['success'] = True

    except Exception as e:
        result['error'] = str(e)
        result['success'] = False

    return result


def main():
    """
    測試 Whisper ASR
    """
    import argparse

    parser = argparse.ArgumentParser(description='Whisper 廣東話 ASR 測試')
    parser.add_argument('--audio', type=str, required=True,
                       help='音頻文件路徑')
    parser.add_argument('--language', type=str, default='yue',
                       help='語言代碼 (默認: yue - 廣東話)')
    parser.add_argument('--model', type=str, default='turbo',
                       help='Whisper 模型 (默認: turbo)')

    args = parser.parse_args()

    # 識別語音
    print("=" * 60)
    print("Whisper Turbo 廣東話 ASR")
    print("=" * 60)
    print()
    print(f"音頻文件: {args.audio}")
    print(f"語言: {args.language}")
    print(f"模型: {args.model}")
    print()

    result = transcribe_audio(
        audio_file=args.audio,
        language=args.language,
        model_name=args.model
    )

    if result['success']:
        print("✅ 識別成功！")
        print()
        print("📝 識別文字:")
        print(f"  {result['text']}")
        print()
        print("📊 識別細節:")
        print(f"  語言: {result['language']}")
        print(f"  時長: {result['duration']:.2f}s")
        print(f"  段落: {len(result['segments'])}")

        for i, seg in enumerate(result['segments'], 1):
            print(f"    段 {i}: [{seg['start']:.2f}s - {seg['end']:.2f}s]")
            print(f"      文字: {seg['text']}")

        print()
        print("=" * 60)
    else:
        print("❌ 識別失敗！")
        print(f"錯誤: {result['error']}")
        print()
        print("=" * 60)


if __name__ == '__main__':
    main()
