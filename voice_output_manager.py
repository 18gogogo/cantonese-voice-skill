#!/usr/bin/env python3
"""
語音輸出管理器
控制語音輸出的開啟/關閉狀態
"""

import os
import json
from pathlib import Path
from datetime import datetime


class VoiceOutputManager:
    """
    語音輸出管理器
    管理語音輸出的開啟/關閉狀態
    """

    def __init__(self, config_file: str = None):
        """
        初始化語音輸出管理器

        Args:
            config_file: 配置文件路徑
        """
        if config_file is None:
            # 使用 skills 目錄下的配置文件
            skills_dir = Path(__file__).parent
            config_file = skills_dir / 'voice_output_state.json'

        self.config_file = Path(config_file)
        self.state = self._load_state()

    def _load_state(self) -> dict:
        """
        載入狀態

        Returns:
            dict: 狀態字典
        """
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ 載入狀態失敗，使用默認值: {e}")

        # 默認狀態：關閉語音輸出
        return {
            'enabled': False,
            'last_updated': None
        }

    def _save_state(self) -> bool:
        """
        保存狀態

        Returns:
            bool: 是否成功
        """
        try:
            self.state['last_updated'] = str(datetime.now())

            # 確保目錄存在
            self.config_file.parent.mkdir(parents=True, exist_ok=True)

            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.state, f, ensure_ascii=False, indent=2)

            return True
        except Exception as e:
            print(f"⚠️ 保存狀態失敗: {e}")
            return False

    def is_enabled(self) -> bool:
        """
        檢查語音輸出是否啟用

        Returns:
            bool: 是否啟用
        """
        return self.state.get('enabled', False)

    def enable(self) -> bool:
        """
        開啟語音輸出

        Returns:
            bool: 是否成功
        """
        if not self.is_enabled():
            self.state['enabled'] = True
            success = self._save_state()
            if success:
                print("✅ 語音輸出已開啟")
            return success
        return True

    def disable(self) -> bool:
        """
        關閉語音輸出

        Returns:
            bool: 是否成功
        """
        if self.is_enabled():
            self.state['enabled'] = False
            success = self._save_state()
            if success:
                print("✅ 語音輸出已關閉")
            return success
        return True

    def toggle(self) -> bool:
        """
        切換語音輸出狀態

        Returns:
            bool: 切換後的狀態（True = 開啟）
        """
        current = self.is_enabled()
        new_state = not current

        self.state['enabled'] = new_state
        success = self._save_state()

        if success:
            status = "開啟" if new_state else "關閉"
            print(f"✅ 語音輸出已{status}")

        return new_state

    def parse_command(self, text: str) -> str:
        """
        解析用戶輸入中的語音輸出控制命令

        Args:
            text: 用戶輸入文本

        Returns:
            str: 處理後的文本（如果是純控制指令，返回空串）
        """
        import re

        original_text = text.strip()

        # 檢測純開啟命令：（、[、(
        if re.match(r'^[（[(\(]*$', original_text):
            self.enable()
            print(f"🎛️ 語音輸出控制: 開啟")
            return ""  # 空串表示是純控制指令，無需處理

        # 檢測純關閉命令：）、]、)
        elif re.match(r'^[）)\)]*$', original_text):
            self.disable()
            print(f"🎛️ 語音輸出控制: 關閉")
            return ""  # 空串表示是純控制指令，無需處理

        # 其他情況，不作為控制指令處理
        return original_text

    def get_status_info(self) -> str:
        """
        獲取狀態信息

        Returns:
            str: 狀態信息字符串
        """
        status = "開啟" if self.is_enabled() else "關閉"
        return f"語音輸出: {status}"


# 全局實例
_manager = None


def get_voice_output_manager() -> VoiceOutputManager:
    """
    獲取語音輸出管理器實例（單例模式）

    Returns:
        VoiceOutputManager: 管理器實例
    """
    global _manager
    if _manager is None:
        _manager = VoiceOutputManager()
    return _manager


def main():
    """
    測試程序
    """
    print("=" * 60)
    print("🎛️ 語音輸出管理器測試")
    print("=" * 60)
    print()

    manager = VoiceOutputManager()

    print(f"初始狀態: {manager.get_status_info()}")
    print()

    # 測試開啟
    print("測試: 用戶輸入「請開幫我查天氣（」")
    text = manager.parse_command("請開幫我查天氣（")
    print(f"處理後: {text}")
    print(f"狀態: {manager.get_status_info()}")
    print()

    # 測試關閉
    print("測試: 用戶輸入「停止語音輸出）」")
    text = manager.parse_command("停止語音輸出）")
    print(f"處理後: {text}")
    print(f"狀態: {manager.get_status_info()}")
    print()

    print("=" * 60)
    print("✅ 測試完成")
    print("=" * 60)


if __name__ == '__main__':
    from datetime import datetime
    main()
