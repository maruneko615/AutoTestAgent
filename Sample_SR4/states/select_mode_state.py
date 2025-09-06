"""
GAME_FLOW_SELECT_MODE 狀態處理器
處理模式選擇狀態 (EGameFlowState = 14)
使用共用的選擇邏輯和參數
"""

import sys
import os
from typing import Optional, Any

# 添加父目錄到路徑
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from config.game_config import GameFlowState
from input.random_input import RandomInputGenerator
from input.targeted_input import TargetedInputGenerator
from .base_selection_state import BaseSelectionStateHandler

class SelectModeStateHandler(BaseSelectionStateHandler):
    def __init__(self):
        super().__init__()  # 呼叫基礎類別的初始化
        self.random_generator = RandomInputGenerator()
        self.targeted_generator = TargetedInputGenerator()
    
    def get_state_name(self) -> str:
        """獲取狀態名稱"""
        return "SELECT_MODE"
        
    def get_supported_state(self) -> int:
        """獲取支援的狀態"""
        return GameFlowState.GAME_FLOW_SELECT_MODE
        
    def can_handle(self, state: int) -> bool:
        """檢查是否可以處理此狀態"""
        return state == GameFlowState.GAME_FLOW_SELECT_MODE
        
    def handle_state(self, state: int, game_data: Any) -> Optional[bytes]:
        """處理 GAME_FLOW_SELECT_MODE 狀態"""
        if not self.can_handle(state):
            return None
            
        print(f"🎮 Handling SELECT_MODE state")
        
        # 檢查是否有模式目標
        if 'selected_mode' in self.targets:
            return self._handle_mode_selection(game_data)
        else:
            # 隨機選擇
            return self._handle_random_selection(game_data)
            
    def _handle_mode_selection(self, game_data: Any) -> bytes:
        """處理模式目標選擇"""
        if not hasattr(game_data, 'selected_mode'):
            return self.random_generator.generate_selection_input()
            
        current_mode = game_data.selected_mode
        target_mode = self.targets['selected_mode']
        
        print(f"🎯 Mode selection: {current_mode} -> {target_mode}")
        
        # 檢查是否達到目標
        if current_mode == target_mode:
            print(f"✅ Mode target reached!")
            self.reset_search_state()
            return self.targeted_generator.generate_confirm_input()
                
        # 執行搜尋邏輯 - 使用共用的時間基礎檢測
        return self._execute_mode_search(current_mode, target_mode)
        
    def _handle_random_selection(self, game_data: Any) -> bytes:
        """處理隨機選擇"""
        print("🎲 Random mode selection")
        import random
        if random.random() < 0.4:  # 40%機率按確認
            return self.random_generator.generate_start_input()
        else:
            return self.random_generator.generate_selection_input()
            
    def _execute_mode_search(self, current_value: int, target_value: int) -> bytes:
        """執行模式搜尋邏輯 - 使用共用的時間基礎卡住檢測"""
        self.log_search_status(current_value, target_value, "mode index")
        
        # 檢查是否達到目標
        if current_value == target_value:
            print("✅ Mode Index 匹配！")
            return self.targeted_generator.generate_start_input()
        
        # 使用共用的卡住檢測邏輯
        self.check_stuck_and_switch_direction(current_value, "mode index")
        
        # 根據當前搜尋方向發送輸入（模式選擇使用左右）
        if self.current_search_direction == 'right':
            print("➡️ 每次 protobuf 發送往右 (當前 mode: {})".format(current_value))
            return self.targeted_generator.generate_right_input()
        else:
            print("⬅️ 每次 protobuf 發送往左 (當前 mode: {})".format(current_value))
            return self.targeted_generator.generate_left_input()
        
    def get_state_progress(self) -> dict:
        """獲取狀態進度 - 結合共用和特定資訊"""
        # 獲取基礎進度資訊
        progress = self.get_search_progress()
        
        # 添加模式選擇特定的資訊
        progress.update({
            "has_mode_target": 'selected_mode' in self.targets
        })
        
        if 'selected_mode' in self.targets:
            progress['mode_target'] = self.targets['selected_mode']
            
        return progress
    
    def reset_state(self):
        """重置狀態 - 使用共用邏輯"""
        self.reset_search_state()  # 呼叫基礎類別的重置方法
        print("🔄 SelectMode state reset")
    
    def reset_state(self):
        """重置狀態 - 使用共用邏輯"""
        self.reset_search_state()  # 呼叫基礎類別的重置方法
        print("🔄 SelectMode state reset")
    
    def reset_state(self):
        """重置狀態 - 使用共用邏輯"""
        self.reset_search_state()  # 呼叫基礎類別的重置方法
        print("🔄 SelectMode state reset")
