"""
目標導向輸入生成器 - 通用版本
負責生成針對特定目標的遊戲輸入指令
"""

import time
from typing import List, Optional, Dict, Any
from .input_generator import InputGenerator

class TargetedInputGenerator(InputGenerator):
    """目標導向輸入生成器"""
    
    def __init__(self, input_generator: InputGenerator):
        super().__init__()
        self.target_keys = []
        self.input_frequency = 60.0  # 60 FPS
        self.last_input_time = 0
        self.analog_inputs = {}
        
        print("🎯 目標導向輸入生成器已初始化")
    
    def set_target_keys(self, keys: List[int]):
        """設定目標按鍵"""
        self.target_keys = keys.copy()
    
    def set_analog_inputs(self, analog: Dict[str, float]):
        """設定類比輸入值"""
        self.analog_inputs = analog.copy()
    
    def generate(self) -> Optional[bytes]:
        """生成目標導向輸入"""
        current_time = time.time()
        
        # 檢查輸入頻率
        if (current_time - self.last_input_time) < (1.0 / self.input_frequency):
            return None
        
        self.last_input_time = current_time
        
        # 生成目標輸入
        return self._create_targeted_input()
    
    # TODO: 🔧 來源: InputCommand.proto - 實現抽象方法
    def generate_input(self) -> Optional[bytes]:
        """生成目標導向輸入（基本實作）"""
        # TODO: 🔧 來源: InputCommand.proto - 調用基礎輸入生成方法
        return self.generate_basic_input()
    
    # TODO: 🔧 來源: InputCommand.proto - 生成方向輸入
    def generate_directional_input(self, direction: str) -> bytes:
        """生成方向輸入"""
        # TODO: 🔧 來源: InputCommand.proto - 方向按鍵映射
        direction_keys = {
            'up': None,    # TODO: 替換為 InputKeyType.INPUT_KEY_UP
            'down': None,  # TODO: 替換為 InputKeyType.INPUT_KEY_DOWN
            'left': None,  # TODO: 替換為 InputKeyType.INPUT_KEY_LEFT
            'right': None  # TODO: 替換為 InputKeyType.INPUT_KEY_RIGHT
        }
        key = direction_keys.get(direction)
        return self.generate_key_input([key], True)
    
    def generate_navigation_input(self, direction: str) -> bytes:
        """生成導航輸入"""
        return self.input_generator.generate_navigation_input(direction)
    
    def generate_confirm_input(self) -> bytes:
        """生成確認輸入"""
        return self.input_generator.generate_confirm_input()
    
    def _create_targeted_input(self) -> bytes:
        """創建目標導向輸入"""
        if self.target_keys:
            return self.input_generator.generate_basic_input(self.target_keys, True)
        else:
            # 如果沒有設定目標按鍵，生成確認輸入
            return self.generate_confirm_input()
