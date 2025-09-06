"""
GAME_FLOW_SELECT_BIKE 狀態處理器
處理車輛選擇狀態 (EGameFlowState = 7)
使用共用的選擇邏輯和參數
"""

import sys
import os
import time
from typing import Optional, Any

# 添加父目錄到路徑
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from config.game_config import GameFlowState, VEHICLE_NAMES
from input.random_input import RandomInputGenerator
from input.targeted_input import TargetedInputGenerator
from .base_selection_state import BaseSelectionStateHandler

class SelectBikeStateHandler(BaseSelectionStateHandler):
    def __init__(self):
        super().__init__()  # 呼叫基礎類別的初始化
        self.random_generator = RandomInputGenerator()
        self.targeted_generator = TargetedInputGenerator()
    
    def get_state_name(self) -> str:
        """獲取狀態名稱"""
        return "SELECT_BIKE"
        
    def get_supported_state(self) -> int:
        """獲取支援的狀態"""
        return GameFlowState.GAME_FLOW_SELECT_BIKE
        
    def can_handle(self, state: int) -> bool:
        """檢查是否可以處理此狀態"""
        return state == GameFlowState.GAME_FLOW_SELECT_BIKE
        
    def handle_state(self, state: int, game_data: Any) -> Optional[bytes]:
        """處理 GAME_FLOW_SELECT_BIKE 狀態"""
        if not self.can_handle(state):
            return None
            
        print(f"🏍️  Handling SELECT_BIKE state")
        
        # 檢查是否有車輛目標
        if 'selected_vehicle' in self.targets:
            return self._handle_vehicle_selection(game_data)
        else:
            # 隨機選擇
            return self._handle_random_selection(game_data)
            
    def _handle_vehicle_selection(self, game_data: Any) -> bytes:
        """處理車輛目標選擇"""
        if not hasattr(game_data, 'selected_vehicle'):
            return self.random_generator.generate_selection_input()
            
        current_vehicle = game_data.selected_vehicle
        target_vehicle = self.targets['selected_vehicle']
        
        # 顯示選擇狀態
        current_name = VEHICLE_NAMES.get(current_vehicle, f"Vehicle_{current_vehicle}")
        target_name = VEHICLE_NAMES.get(target_vehicle, f"Vehicle_{target_vehicle}")
        print(f"🎯 Vehicle selection: {current_name} ({current_vehicle}) -> {target_name} ({target_vehicle})")
        
        # 檢查是否達到目標
        if current_vehicle == target_vehicle:
            print(f"✅ Vehicle target reached!")
            self.reset_search_state()
            return self.targeted_generator.generate_confirm_input()
                
        # 執行搜尋邏輯 - 使用共用的時間基礎檢測
        return self._execute_vehicle_search(current_vehicle, target_vehicle)
        
    def set_random_target(self, target_index: int):
        """接收 StateManager 統一設定的隨機目標"""
        self.random_target = target_index
        self.target_reached = False
        self.flow_initialized = True
        print(f"🎯 接收統一設定的隨機目標: {target_index}")
    
    def _handle_random_selection(self, game_data: Any) -> bytes:
        """處理隨機選擇 - 簡化版，目標由 StateManager 統一管理"""
        
        # 檢查是否有遊戲數據
        if not hasattr(game_data, 'selected_vehicle'):
            return self.targeted_generator.generate_right_input()
        
        # 檢查是否已設定隨機目標
        if not hasattr(self, 'random_target'):
            print("⚠️ 尚未設定隨機目標，等待 StateManager 設定")
            return self.targeted_generator.generate_right_input()
        
        current_vehicle = game_data.selected_vehicle
        
        print(f"🎲 隨機目標選擇: {current_vehicle} -> {self.random_target}")
        
        # 檢查是否達到隨機目標
        if current_vehicle == self.random_target:
            if not self.target_reached:
                print(f"✅ 達到隨機目標車輛: {self.random_target}")
                self.target_reached = True
            # 每次達到目標時都重置卡住檢測狀態，避免在按確認時繼續檢測
            self.last_tracked_value = None
            self.last_value_change_time = time.time()
            # 持續按 START 直到流程切換
            print("🔄 持續按 START 直到流程切換...")
            print("🛑 卡住檢測已停止")
            return self.targeted_generator.generate_start_input()
        
        # 執行搜尋邏輯
        return self._execute_vehicle_search(current_vehicle, self.random_target)
    
    def reset_state(self):
        """重置狀態 - 為新流程做準備"""
        # 調用基礎類別的重置方法
        if hasattr(super(), 'reset_search_state'):
            super().reset_search_state()
        
        # 重置流程狀態，準備接收新的隨機目標
        if hasattr(self, 'random_target'):
            delattr(self, 'random_target')
        if hasattr(self, 'target_reached'):
            delattr(self, 'target_reached')
        if hasattr(self, 'flow_initialized'):
            delattr(self, 'flow_initialized')
        
        print("🔄 SelectBike state reset - 準備接收新目標")
            
    def _execute_vehicle_search(self, current_value: int, target_value: int) -> bytes:
        """執行車輛搜尋邏輯 - 先檢查目標，未達到才執行搜尋"""
        
        # 首先檢查是否達到目標
        if current_value == target_value:
            print("✅ Vehicle Index 匹配！當前 index {} == 目標 index {}".format(current_value, target_value))
            print("⏹️ 立刻停止發送左右鍵")
            print("🛑 停止卡住檢測和方向切換邏輯")
            print("🎯 進入持續發送 START 模式，直到狀態切換...")
            # 重置卡住檢測狀態，避免在按確認時繼續檢測
            self.last_tracked_value = None
            self.last_value_change_time = time.time()
            return self.targeted_generator.generate_start_input()
        
        # 只有在未達到目標時才執行以下邏輯：
        # 1. 記錄搜尋狀態
        # 2. 卡住檢測
        # 3. 方向切換
        # 4. 發送左右移動指令
        
        self.log_search_status(current_value, target_value, "vehicle index")
        
        # 執行卡住檢測邏輯
        self.check_stuck_and_switch_direction(current_value, "vehicle index")
        
        # 根據當前搜尋方向發送輸入（車輛選擇使用左右）
        if self.current_search_direction == 'right':
            print("➡️ 每次 protobuf 發送往右 (當前 vehicle: {})".format(current_value))
            return self.targeted_generator.generate_right_input()
        else:
            print("⬅️ 每次 protobuf 發送往左 (當前 vehicle: {})".format(current_value))
            return self.targeted_generator.generate_left_input()
        
    def get_state_progress(self) -> dict:
        """獲取狀態進度 - 結合共用和特定資訊"""
        # 獲取基礎進度資訊
        progress = self.get_search_progress()
        
        # 添加車輛選擇特定的資訊
        progress.update({
            "has_vehicle_target": 'selected_vehicle' in self.targets
        })
        
        if 'selected_vehicle' in self.targets:
            progress['vehicle_target'] = self.targets['selected_vehicle']
            progress['vehicle_target_name'] = VEHICLE_NAMES.get(self.targets['selected_vehicle'], f"Vehicle_{self.targets['selected_vehicle']}")
            
        return progress
    
    def reset_state(self):
        """重置狀態 - 為新流程做準備"""
        # 調用基礎類別的重置方法
        if hasattr(super(), 'reset_search_state'):
            super().reset_search_state()
        
        # 重置流程狀態，準備下次進入時重新隨機選擇
        if hasattr(self, 'flow_initialized'):
            delattr(self, 'flow_initialized')
        if hasattr(self, 'random_target'):
            delattr(self, 'random_target')
        if hasattr(self, 'target_reached'):
            delattr(self, 'target_reached')
        # 保留 last_flow_state 用於流程切換檢測
        
        print("🔄 SelectBike state reset - 準備新流程")
