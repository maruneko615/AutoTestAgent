"""
目標導向輸入生成器
根據目標生成特定的輸入指令
"""

import sys
import os
from typing import List, Optional, Any

# 添加Proto路徑
proto_path = os.path.join(os.path.dirname(__file__), '..', '..', 'ProtoSchema')
sys.path.append(proto_path)

try:
    import InputCommand_pb2 as InputCommand
except ImportError as e:
    print(f"✗ Failed to import InputCommand_pb2 in targeted_input: {e}")

from .input_generator import InputGenerator
from config.game_config import InputKeyType, GameFlowState

class TargetedInputGenerator(InputGenerator):
    """目標導向輸入生成器"""
    
    def __init__(self):
        super().__init__()
        
        # 方向按鍵映射
        self.direction_keys = {
            'up': InputKeyType.INPUT_KEY_UP,
            'down': InputKeyType.INPUT_KEY_DOWN,
            'left': InputKeyType.INPUT_KEY_LEFT,
            'right': InputKeyType.INPUT_KEY_RIGHT
        }
        
    def generate_input(self) -> Optional[bytes]:
        """生成目標導向輸入（基本實作）"""
        return self.generate_basic_input()
        
    def generate_directional_input(self, direction: str) -> bytes:
        """生成方向輸入"""
        key = self.direction_keys.get(direction, InputKeyType.INPUT_KEY_RIGHT)
        self.log_input_generation([key], f"方向-{direction}")
        return self.generate_key_input([key], True)
        
    def generate_confirm_input(self) -> bytes:
        """生成確認輸入"""
        start_key = [InputKeyType.INPUT_KEY_START]
        self.log_input_generation(start_key, "確認")
        return self.generate_key_input(start_key, True)
        
    def generate_navigation_input(self, current_value: Any, target_value: Any, 
                                state: int, search_direction: str) -> bytes:
        """生成導航輸入"""
        # 根據狀態和搜尋方向生成輸入
        if state == GameFlowState.GAME_FLOW_SELECT_SCENE:
            # 場景選擇使用上下
            if search_direction == 'up':
                key = InputKeyType.INPUT_KEY_UP
            else:
                key = InputKeyType.INPUT_KEY_DOWN
        else:
            # 其他選擇使用左右
            if search_direction == 'right':
                key = InputKeyType.INPUT_KEY_RIGHT
            else:
                key = InputKeyType.INPUT_KEY_LEFT
                
        self.log_input_generation([key], f"導航-{search_direction}")
        return self.generate_key_input([key], True)
        
    def generate_selection_sequence(self, target_state: int, steps: int) -> List[bytes]:
        """生成選擇序列"""
        sequence = []
        
        # 根據目標狀態決定按鍵序列
        if target_state == GameFlowState.GAME_FLOW_SELECT_BIKE:
            # 車輛選擇主要使用左右
            for _ in range(steps):
                direction = 'right'  # 預設向右搜尋
                sequence.append(self.generate_directional_input(direction))
        elif target_state == GameFlowState.GAME_FLOW_SELECT_SCENE:
            # 場景選擇主要使用上下
            for _ in range(steps):
                direction = 'up'  # 預設向上搜尋
                sequence.append(self.generate_directional_input(direction))
        else:
            # 其他狀態使用右鍵
            for _ in range(steps):
                sequence.append(self.generate_directional_input('right'))
                
        return sequence
        
    def generate_basic_input(self) -> bytes:
        """生成基本輸入"""
        # 預設生成右鍵輸入
        return self.generate_directional_input('right')
        
    def generate_search_input(self, search_state: dict) -> bytes:
        """根據搜尋狀態生成輸入"""
        direction = search_state.get('direction', 'right')
        return self.generate_directional_input(direction)
        
    def generate_target_reached_input(self) -> bytes:
        """生成目標達成時的輸入（確認）"""
        return self.generate_confirm_input()
        
    def generate_left_input(self) -> bytes:
        """生成左鍵輸入"""
        return self.generate_directional_input('left')
        
    def generate_right_input(self) -> bytes:
        """生成右鍵輸入"""
        return self.generate_directional_input('right')
        
    def generate_start_input(self) -> bytes:
        """生成 START 鍵輸入"""
        return self.generate_confirm_input()
        
    def should_confirm_selection(self, current_value: Any, target_value: Any) -> bool:
        """判斷是否應該確認選擇"""
        return current_value == target_value
        
    def calculate_search_direction(self, current_value: Any, target_value: Any, 
                                 state: int, last_direction: str) -> str:
        """計算搜尋方向"""
        # 簡單的搜尋邏輯：如果當前方向無效，則切換方向
        if state == GameFlowState.GAME_FLOW_SELECT_SCENE:
            # 場景選擇使用上下切換
            return 'down' if last_direction == 'up' else 'up'
        else:
            # 其他選擇使用左右切換
            return 'left' if last_direction == 'right' else 'right'
            
    def get_default_direction(self, state: int) -> str:
        """獲取預設搜尋方向"""
        if state == GameFlowState.GAME_FLOW_SELECT_SCENE:
            return 'up'  # 場景選擇預設向上
        else:
            return 'right'  # 其他選擇預設向右
