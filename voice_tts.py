#!/usr/bin/env python3
"""
CosyVoice TTS - 語音合成模組
支援廣東話文本語音合成

使用方法:
    from voice_tts import synthesize_speech

    result = synthesize_speech(
        text='你好，今日天氣很好。',
        output_file='output.wav'
    )

    print(result['output_file'])
    print(result['duration'])
"""

import os
import sys
import soundfile as sf
import numpy as np
import threading
import time

# 添加必要的路徑
COSYVOICE_DIR = '/home/ubuntu/CosyVoice'
sys.path.insert(0, f'{COSYVOICE_DIR}/third_party/Matcha-TTS')
sys.path.insert(0, COSYVOICE_DIR)

from cosyvoice.cli.cosyvoice import CosyVoice3


# 超時設定（秒）
DEFAULT_TIMEOUT = 50  # 默認超時 50 秒


def synthesize_speech(
    text: str,
    output_file: str = None,
    model_dir: str = None,
    reference_audio: str = None,
    reference_text: str = "This is a reference sentence for speech synthesis.",
    speed: float = 1.0,
    use_cantonese: bool = True,
    timeout: float = DEFAULT_TIMEOUT
) -> dict:
    """
    使用 CosyVoice3 合成語音（帶超時保護）

    Args:
        text: 要合成的文本
        output_file: 輸出音頻文件路徑 (默認: /home/ubuntu/桌面/ok/cosyvoice_output.wav)
        model_dir: CosyVoice 模型目錄 (默認: /home/ubuntu/CosyVoice/pretrained_models/Fun-CosyVoice3-0.5B)
        reference_audio: 參考音頻文件 (默認: 使用內置音頻)
        reference_text: 參考文本 (默認: 英文句子)
        speed: 語音速度 (默認: 1.0)
        use_cantonese: 是否使用廣東話模式 (默認: True, 使用 instruct 模式)
        timeout: 超時時間（秒）

    Returns:
        dict: {
            'output_file': str,  # 輸出文件路徑
            'duration': float,   # 音頻長度 (秒)
            'sample_rate': int,  # 采樣率
            'success': bool,     # 是否成功
            'error': str,        # 錯誤訊息 (如果失敗)
            'timed_out': bool    # 是否超時
        }
    """
    # 設定默認值
    if model_dir is None:
        model_dir = f'{COSYVOICE_DIR}/pretrained_models/Fun-CosyVoice3-0.5B'

    if output_file is None:
        output_file = f'{COSYVOICE_DIR}/output.wav'

    if reference_audio is None:
        reference_audio = os.path.join(model_dir, 'reference_audio.wav')

    # 確保參考音頻存在
    if not os.path.exists(reference_audio):
        # 創建默認參考音頻
        os.makedirs(os.path.dirname(reference_audio), exist_ok=True)
        sample_rate = 24000
        duration_seconds = 1.0
        audio_data = np.zeros(int(sample_rate * duration_seconds), dtype=np.float32)
        sf.write(reference_audio, audio_data, sample_rate)

    result = {
        'output_file': output_file,
        'duration': 0,
        'sample_rate': 24000,
        'success': False,
        'error': None,
        'timed_out': False
    }

    # 使用線程實現超時保護
    def _synthesize():
        try:
            print(f"[TTS] 開始合成: \"{text[:30]}{'...' if len(text) > 30 else ''}\"")
            start_time = time.time()

            # 初始化 CosyVoice3
            cosyvoice = CosyVoice3(model_dir)

            # 合成語音
            if use_cantonese:
                # 使用 instruct 模式生成廣東話
                instruct_text = 'You are a helpful assistant. 请用广东话表达。<|endofprompt|>'
                output = cosyvoice.inference_instruct2(
                    tts_text=text,
                    instruct_text=instruct_text,
                    prompt_wav=reference_audio,
                    zero_shot_spk_id='',
                    stream=False,
                    speed=speed,
                    text_frontend=True
                )
            else:
                # 使用 zero-shot 模式
                output = cosyvoice.inference_zero_shot(
                    tts_text=text,
                    prompt_text=reference_text,
                    prompt_wav=reference_audio,
                    zero_shot_spk_id='',
                    stream=False,
                    speed=speed,
                    text_frontend=True
                )

            # 提取音頻數據
            audio_data = None
            for chunk in output:
                if 'tts_speech' in chunk:
                    audio_data = chunk['tts_speech'][0]  # numpy array
                    break

            if audio_data is None:
                raise RuntimeError("語音合成失敗：無音頻輸出")

            # 保存音頻文件
            sf.write(output_file, audio_data, 24000)

            # 計算音頻長度
            duration = len(audio_data) / 24000

            elapsed_time = time.time() - start_time
            print(f"[TTS] 合成完成: {duration:.2f}s (耗時: {elapsed_time:.2f}s)")

            result['duration'] = duration
            result['success'] = True

        except Exception as e:
            elapsed_time = time.time() - start_time
            print(f"[TTS] 合成失敗: {e} (耗時: {elapsed_time:.2f}s)")
            result['error'] = str(e)
            result['success'] = False

    try:
        # 使用線程並設置超時
        thread = threading.Thread(target=_synthesize)
        thread.daemon = True  # 設為守護線程
        thread.start()

        start_time = time.time()
        thread.join(timeout=timeout)
        elapsed_time = time.time() - start_time

        if thread.is_alive():
            # 超時
            print(f"[TTS] ⚠️ 超時: {elapsed_time:.2f}s > {timeout}s")
            result['success'] = False
            result['error'] = f'Synthesis timeout after {timeout:.1f}s'
            result['timed_out'] = True
        elif result['success']:
            # 成功
            pass
        else:
            # 失敗（錯誤）
            pass

    except Exception as e:
        result['error'] = str(e)
        result['success'] = False

    return result


def main():
    """
    測試 CosyVoice TTS
    """
    import argparse

    parser = argparse.ArgumentParser(description='CosyVoice 廣東話 TTS 測試')
    parser.add_argument('--text', type=str, default='你好，我係 CosyVoice，今日天氣很好，適合去行山。',
                       help='要合成的文本')
    parser.add_argument('--output', type=str, default='/home/ubuntu/桌面/ok/cosyvoice_output.wav',
                       help='輸出音頻文件')
    parser.add_argument('--model', type=str, default=None,
                       help='CosyVoice3 模型目錄')
    parser.add_argument('--speed', type=float, default=1.0,
                       help='語音速度 (默認: 1.0)')
    parser.add_argument('--no-cantonese', action='store_true',
                       help='不使用廣東話模式 (默認: 使用廣東話)')

    args = parser.parse_args()

    # 合成語音
    print("=" * 60)
    print("CosyVoice3 廣東話 TTS")
    print("=" * 60)
    print()
    print(f"文本: {args.text}")
    print(f"輸出文件: {args.output}")
    print(f"速度: {args.speed}")
    print()

    result = synthesize_speech(
        text=args.text,
        output_file=args.output,
        model_dir=args.model,
        speed=args.speed,
        use_cantonese=not args.no_cantonese
    )

    if result['success']:
        print("✅ 合成成功！")
        print(f"📁 文件: {result['output_file']}")
        print(f"📏 長度: {result['duration']:.2f} 秒")
        print(f"📊 采樣率: {result['sample_rate']} Hz")
        print()
        print("=" * 60)
    else:
        print("❌ 合成失敗！")
        print(f"错误: {result['error']}")
        print()
        print("=" * 60)


if __name__ == '__main__':
    main()
