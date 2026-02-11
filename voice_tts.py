#!/usr/bin/env python3
"""
CosyVoice TTS - 語音合成模組（修復版）
支援廣東話文本語音合成

修復項目：
1. 使用單例模式緩存 CosyVoice3 實例，避免重複初始化
2. 添加重試機制（最多 3 次）
3. 設置環境變量禁用 Triton 優化（避免鎖競爭）
4. 改進錯誤處理和日誌

使用方法:
    from voice_tts_fixed import synthesize_speech_fixed

    result = synthesize_speech_fixed(
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
import gc

# 添加必要的路徑
COSYVOICE_DIR = '/home/ubuntu/CosyVoice'
sys.path.insert(0, f'{COSYVOICE_DIR}/third_party/Matcha-TTS')
sys.path.insert(0, COSYVOICE_DIR)

# 禁用 Triton 優化（避免 CPU 模式下的問題）
os.environ.setdefault('TRITON_DISABLE_TORTOISE', '1')
os.environ.setdefault('TRITON_CACHE_DIR', '/tmp/triton_cache')

from cosyvoice.cli.cosyvoice import CosyVoice3


# 超時設定（秒）
DEFAULT_TIMEOUT = 50
DEFAULT_MODEL_DIR = f'{COSYVOICE_DIR}/pretrained_models/Fun-CosyVoice3-0.5B'


# 全局單例緩存
_cosyvoice_instance = None
_model_dir = None
_instance_lock = threading.Lock()


def _get_cosyvoice_instance(model_dir: str = None):
    """
    獲取 CosyVoice3 單例實例（緩存）

    Args:
        model_dir: 模型目錄

    Returns:
        CosyVoice3 實例
    """
    global _cosyvoice_instance, _model_dir

    if model_dir is None:
        model_dir = DEFAULT_MODEL_DIR

    with _instance_lock:
        # 如果實例已存在且模型目錄相同，直接返回
        if _cosyvoice_instance is not None and _model_dir == model_dir:
            return _cosyvoice_instance

        # 否則重新創建
        print(f"[TTS] 初始化 CosyVoice3 模型... ({model_dir})")
        start_time = time.time()

        try:
            _cosyvoice_instance = CosyVoice3(model_dir)
            _model_dir = model_dir

            init_time = time.time() - start_time
            print(f"[TTS] CosyVoice3 初始化完成 ({init_time:.2f}s)")

            return _cosyvoice_instance
        except Exception as e:
            print(f"[TTS ERROR] CosyVoice3 初始化失敗: {e}")
            raise


def synthesize_speech_fixed(
    text: str,
    output_file: str = None,
    model_dir: str = None,
    reference_audio: str = None,
    reference_text: str = "This is a reference sentence for speech synthesis.",
    speed: float = 1.0,
    use_cantonese: bool = True,
    max_retries: int = 3,
    timeout: float = DEFAULT_TIMEOUT
) -> dict:
    """
    使用 CosyVoice3 合成語音（修復版，帶重試和超時保護）

    Args:
        text: 要合成的文本
        output_file: 輸出音頻文件路徑
        model_dir: CosyVoice 模型目錄
        reference_audio: 參考音頻文件
        reference_text: 參考文本
        speed: 語音速度
        use_cantonese: 是否使用廣東話模式
        max_retries: 最大重試次數（默認 3）
        timeout: 超時時間（秒）

    Returns:
        dict: {
            'output_file': str,
            'duration': float,
            'sample_rate': int,
            'success': bool,
            'error': str,
            'timed_out': bool,
            'retry_count': int  # 重試次數
        }
    """
    # 設定默認值
    if model_dir is None:
        model_dir = DEFAULT_MODEL_DIR

    if output_file is None:
        output_file = f'/home/ubuntu/桌面/ok/cosyvoice_output_{int(time.time())}.wav'

    if reference_audio is None:
        reference_audio = os.path.join(model_dir, 'reference_audio.wav')

    # 確保參考音頻存在
    if not os.path.exists(reference_audio):
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
        'timed_out': False,
        'retry_count': 0
    }

    # 重試機制
    for retry in range(max_retries):
        result['retry_count'] = retry

        # 使用線程實現超時保護
        def _synthesize():
            try:
                print(f"[TTS] 嘗試 {retry + 1}/{max_retries}: 合成 \"{text[:30]}{'...' if len(text) > 30 else ''}\"")
                synthesis_start = time.time()

                # 獲取緩存的 CosyVoice3 實例
                cosyvoice = _get_cosyvoice_instance(model_dir)

                # 合成語音
                if use_cantonese:
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
                        audio_data = chunk['tts_speech'][0]
                        break

                if audio_data is None:
                    raise ValueError("未生成音頻數據（output['tts_speech'] 為空）")

                # 增加音量（增益）
                # CosyVoice3 默認輸出較小，需要增加增益以提升音量
                audio_gain = 6.0  # 增益倍数（可根据调整：4.0, 6.0, 8.0）
                audio_data = audio_data * audio_gain

                # 简单限制防止削波
                audio_data = np.clip(audio_data, -1.0, 1.0)

                # 保存音頻文件
                sf.write(output_file, audio_data, 24000)

                duration = time.time() - synthesis_start
                print(f"[TTS] 合成成功 ({duration:.2f}s，重試 {retry + 1}/{max_retries})")

                # 更新結果
                result['duration'] = len(audio_data) / 24000
                result['success'] = True
                result['output_file'] = output_file
                result['timed_out'] = False

            except Exception as e:
                print(f"[TTS ERROR] 嘗試 {retry + 1}/{max_retries} 失敗: {e}")
                error_msg = str(e)
                if 'terminate called without an active exception' in error_msg:
                    error_msg = "Triton 優化內核崩潰（已設置環境變量禁用優化）"
                result['error'] = error_msg
                result['success'] = False
                raise

        try:
            # 創建並啟動線程
            thread = threading.Thread(target=_synthesize)
            thread.daemon = True
            thread.start()
            thread.join(timeout=timeout)

            # 檢查線程是否還在運行
            if thread.is_alive():
                result['timed_out'] = True
                result['error'] = f'Synthesis timeout after {timeout}s'
                print(f"[TTS WARNING] 超時 ({timeout}s)，重試 {retry + 1}/{max_retries}")

                # 如果是最後一次重試，直接返回（已超時）
                if retry >= max_retries - 1:
                    print(f"[TTS ERROR] 所有重試均超時，放棄")
                    return result
                else:
                    # 否則繼續重試
                    print(f"[TTS] 繼續重試...")
                    time.sleep(1)  # 等待 1 秒後重試
                    continue

            # 檢查是否成功
            if result['success'] or (not thread.is_alive() and not result.get('error')):
                # 成功或線程正常結束
                if result['success']:
                    print(f"[TTS] ✅ 合成成功（重試 {retry + 1}/{max_retries}）")
                    break  # 退出重試循環
                else:
                    # 線程結束但未成功，檢查是否有錯誤
                    if retry >= max_retries - 1:
                        break  # 最後一次重試，退出
                    else:
                        print(f"[TTS] 線程結束但未成功，繼續重試...")
                        time.sleep(1)
                        continue

        except Exception as e:
            print(f"[TTS ERROR] 嘗試 {retry + 1}/{max_retries} 異常: {e}")
            if retry >= max_retries - 1:
                result['error'] = str(e)
                break
            else:
                print(f"[TTS] 繼續重試...")
                time.sleep(1)
                continue

    return result


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='CosyVoice TTS 修復版')
    parser.add_argument('--text', type=str, required=True, help='要合成的文本')
    parser.add_argument('--output', type=str, default=None, help='輸出文件路徑')
    parser.add_argument('--model-dir', type=str, default=None, help='模型目錄')
    parser.add_argument('--timeout', type=int, default=DEFAULT_TIMEOUT)

    args = parser.parse_args()

    result = synthesize_speech_fixed(
        text=args.text,
        output_file=args.output,
        model_dir=args.model_dir,
        timeout=args.timeout
    )

    print("=" * 60)
    if result['success']:
        print("✅ 合成成功")
        print(f"輸出文件: {result['output_file']}")
        print(f"音頻長度: {result['duration']:.2f} 秒")
        print(f"重試次數: {result['retry_count']}")
    else:
        print("❌ 合成失敗")
        print(f"錯誤: {result.get('error')}")
        print(f"超時: {result['timed_out']}")
        print(f"重試次數: {result['retry_count']}")
    print("=" * 60)
# 導出別名（兼容性）
synthesize_speech = synthesize_speech_fixed

