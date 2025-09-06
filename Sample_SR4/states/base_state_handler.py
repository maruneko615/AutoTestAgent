"""
基礎狀態處理器
所有狀態處理器的基礎類別
"""

import sys
import os
from abc import ABC, abstractmethod
from typing import Optional, Any

# 添加父目錄到路徑
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from input.random_input import RandomInputGenerator
from input.targeted_input import TargetedInputGenerator

class BaseStateHandler(ABC):
    """狀態處理器基礎類別"""
    
    def __init__(self, state_name: str, state_value: int):
        self.state_name = state_name
        self.state_value = state_value
        self.targets = {}
        
        # 輸入生成器
        self.random_generator = RandomInputGenerator()
        self.targeted_generator = TargetedInputGenerator()
        
        print(f"🎮 {state_name} state handler initialized")
        
    @abstractmethod
    def can_handle(self, state: int) -> bool:
        """檢查是否可以處理此狀態"""
        return state == self.state_value
        
    @abstractmethod
    def handle_state(self, state: int, game_data: Any) -> Optional[bytes]:
        """處理狀態並生成輸入"""
        pass
        
    def set_targets(self, targets: dict):
        """設定目標"""
        self.targets = targets
        if targets:
            print(f"🎯 {self.state_name} targets set: {targets}")
            
    def get_state_name(self) -> str:
        """獲取狀態名稱"""
        return self.state_name
        
    def get_supported_state(self) -> int:
        """獲取支援的狀態值"""
        return self.state_value
        
    def reset_state(self):
        """重置狀態"""
        print(f"🔄 {self.state_name} state reset")
        
    def get_state_progress(self) -> dict:
        """獲取狀態進度"""
        return {
            "state": self.state_name,
            "state_value": self.state_value,
            "has_targets": bool(self.targets)
        }
        
    def handle_random_input(self, game_data: Any) -> bytes:
        """處理隨機輸入（預設實作）"""
        print(f"🎲 {self.state_name} random input")
        import random
        if random.random() < 0.3:  # 30%機率按確認
            return self.random_generator.generate_start_input()
        else:
            return self.random_generator.generate_basic_input()
            
    def handle_basic_input(self, game_data: Any) -> bytes:
        """處理基本輸入（預設實作）"""
        print(f"🔧 {self.state_name} basic input")
        return self.random_generator.generate_basic_input()
