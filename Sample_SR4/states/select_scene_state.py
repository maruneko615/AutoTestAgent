"""
GAME_FLOW_SELECT_SCENE 狀態處理器
處理場景選擇狀態 (EGameFlowState = 6)
支援目標導向選擇：selected_track, route_direction
使用共用的選擇邏輯和參數
"""

import sys
import os
import time
from typing import Optional, Any

# 添加父目錄到路徑
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from config.game_config import GameFlowState, TRACK_NAMES
from input.random_input import RandomInputGenerator
from input.targeted_input import TargetedInputGenerator
from .base_selection_state import BaseSelectionStateHandler

class SelectSceneStateHandler(BaseSelectionStateHandler):
    def __init__(self):
        super().__init__()  # 呼叫基礎類別的初始化
        self.random_generator = RandomInputGenerator()
        self.targeted_generator = TargetedInputGenerator()
        
        # 場景選擇特定的追蹤變數
        self.direction_last_value = None
        self.direction_last_change_time = time.time()
        self.direction_search_direction = 'up'  # 路線方向預設向上
    
    def get_state_name(self) -> str:
        """獲取狀態名稱"""
        return "SELECT_SCENE"
        
    def get_supported_state(self) -> int:
        """獲取支援的狀態"""
        return GameFlowState.GAME_FLOW_SELECT_SCENE
        
    def can_handle(self, state: int) -> bool:
        """檢查是否可以處理此狀態"""
        return state == GameFlowState.GAME_FLOW_SELECT_SCENE
        
    def handle_state(self, state: int, game_data: Any) -> Optional[bytes]:
        """處理 GAME_FLOW_SELECT_SCENE 狀態"""
        if not self.can_handle(state):
            return None
            
        print(f"🏞️  Handling SELECT_SCENE state")
        
        # 檢查是否有賽道目標
        if 'selected_track' in self.targets:
            return self._handle_track_selection(game_data)
        # 檢查是否有路線方向目標
        elif 'route_direction' in self.targets:
            return self._handle_direction_selection(game_data)
        else:
            # 隨機選擇
            return self._handle_random_selection(game_data)
            
    def _handle_track_selection(self, game_data: Any) -> bytes:
        """處理賽道目標選擇"""
        if not hasattr(game_data, 'selected_track'):
            return self.targeted_generator.generate_right_input()
            
        current_track = game_data.selected_track
        target_track = self.targets['selected_track']
        
        # 顯示選擇狀態
        current_name = TRACK_NAMES.get(current_track, f"Track_{current_track}")
        target_name = TRACK_NAMES.get(target_track, f"Track_{target_track}")
        print(f"🎯 Track selection: {current_name} ({current_track}) -> {target_name} ({target_track})")
        
        # 使用消息驅動的搜尋邏輯
        return self._execute_track_search(current_track, target_track)
        
    def _handle_direction_selection(self, game_data: Any) -> bytes:
        """處理路線方向目標選擇"""
        if not hasattr(game_data, 'route_direction'):
            return self.random_generator.generate_selection_input()
            
        current_direction = game_data.route_direction
        target_direction = self.targets['route_direction']
        
        # 顯示選擇狀態
        current_name = "正走" if current_direction == 0 else "反走"
        target_name = "正走" if target_direction == 0 else "反走"
        print(f"🎯 Direction selection: {current_name} ({current_direction}) -> {target_name} ({target_direction})")
        
        # 檢查是否達到目標
        if current_direction == target_direction:
            print(f"✅ Direction target reached!")
            # 重置方向搜尋狀態
            self.direction_last_value = None
            self.direction_search_direction = 'up'
            self.direction_last_change_time = time.time()
            return self.targeted_generator.generate_confirm_input()
            
        # 執行搜尋邏輯
        return self._execute_direction_search(current_direction, target_direction)
        
    def set_random_target(self, target_index: int):
        """接收 StateManager 統一設定的隨機目標"""
        self.random_target = target_index
        self.target_reached = False
        self.flow_initialized = True
        print(f"🎯 接收統一設定的隨機目標: {target_index}")
    
    def _handle_random_selection(self, game_data: Any) -> bytes:
        """處理隨機選擇 - 簡化版，目標由 StateManager 統一管理"""
        
        # 檢查是否有遊戲數據
        if not hasattr(game_data, 'selected_track'):
            return self.targeted_generator.generate_right_input()
        
        # 檢查是否已設定隨機目標
        if not hasattr(self, 'random_target'):
            print("⚠️ 尚未設定隨機目標，等待 StateManager 設定")
            return self.targeted_generator.generate_right_input()
        
        current_track = game_data.selected_track
        
        print(f"🎲 隨機目標選擇: {current_track} -> {self.random_target}")
        
        # 檢查是否達到隨機目標
        if current_track == self.random_target:
            if not self.target_reached:
                print(f"✅ 達到隨機目標賽道: {self.random_target}")
                self.target_reached = True
            # 每次達到目標時都重置卡住檢測狀態，避免在按確認時繼續檢測
            self.last_tracked_value = None
            self.last_value_change_time = time.time()
            # 持續按 START 直到流程切換
            print("🔄 持續按 START 直到流程切換...")
            print("🛑 卡住檢測已停止")
            return self.targeted_generator.generate_start_input()
        
        # 執行搜尋邏輯
        return self._execute_track_search(current_track, self.random_target)
    
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
        
        print("🔄 SelectScene state reset - 準備接收新目標")
            
    def _execute_track_search(self, current_value: int, target_value: int) -> bytes:
        """執行賽道搜尋邏輯 - 先檢查目標，未達到才執行搜尋"""
        
        # 首先檢查是否達到目標
        if current_value == target_value:
            print("✅ Track Index 匹配！當前 index {} == 目標 index {}".format(current_value, target_value))
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
        
        self.log_search_status(current_value, target_value, "track index")
        
        # 執行卡住檢測邏輯
        self.check_stuck_and_switch_direction(current_value, "track index")
        
        # 根據當前搜尋方向發送輸入
        if self.current_search_direction == 'right':
            print("➡️ 每次 protobuf 發送往右 (當前 index: {})".format(current_value))
            return self.targeted_generator.generate_right_input()
        else:
            print("⬅️ 每次 protobuf 發送往左 (當前 index: {})".format(current_value))
            return self.targeted_generator.generate_left_input()
        
    def _execute_direction_search(self, current_value: int, target_value: int) -> bytes:
        """執行路線方向搜尋邏輯 - 使用獨立的時間檢測（因為可能同時進行）"""
        current_time = time.time()
        
        # 檢查 direction 是否有變化（使用獨立的追蹤變數）
        if self.direction_last_value != current_value:
            # Direction 有變化，更新記錄
            self.direction_last_value = current_value
            self.direction_last_change_time = current_time
            print(f"📈 Direction 變化: {current_value}, 重置時間戳")
        else:
            # Direction 沒有變化，檢查是否超過閾值
            time_since_last_change = current_time - self.direction_last_change_time
            print(f"⏱️ Direction 未變化時間: {time_since_last_change:.2f}s")
            
            if time_since_last_change > self.STUCK_THRESHOLD:  # 使用共用閾值
                # 超過閾值沒有變化，切換搜尋方向
                self._change_direction_search_direction()
                self.direction_last_change_time = current_time  # 重置時間戳
                print(f"🔄 檢測到方向卡住 ({time_since_last_change:.2f}s)，已切換方向")
        
        # 生成對應方向的輸入
        print(f"🔍 Direction search direction: {self.direction_search_direction}")
        return self.targeted_generator.generate_directional_input(self.direction_search_direction)
        
    def _change_direction_search_direction(self):
        """改變路線方向搜尋方向（場景選擇特定）"""
        old_direction = self.direction_search_direction
        self.direction_search_direction = 'down' if self.direction_search_direction == 'up' else 'up'
        print(f"🔄 Direction search direction changed: {old_direction} -> {self.direction_search_direction}")
        
    def get_state_progress(self) -> dict:
        """獲取狀態進度 - 結合共用和特定資訊"""
        # 獲取基礎進度資訊
        progress = self.get_search_progress()
        
        # 添加場景選擇特定的資訊
        current_time = time.time()
        progress.update({
            "has_track_target": 'selected_track' in self.targets,
            "has_direction_target": 'route_direction' in self.targets,
            "direction_stuck_time": current_time - self.direction_last_change_time,
            "direction_search_direction": self.direction_search_direction
        })
        
        if 'selected_track' in self.targets:
            progress['track_target'] = self.targets['selected_track']
            progress['track_target_name'] = TRACK_NAMES.get(self.targets['selected_track'], f"Track_{self.targets['selected_track']}")
            
        if 'route_direction' in self.targets:
            progress['direction_target'] = self.targets['route_direction']
            progress['direction_target_name'] = "正走" if self.targets['route_direction'] == 0 else "反走"
            
        return progress
