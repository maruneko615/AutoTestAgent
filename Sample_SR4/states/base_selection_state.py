"""
基礎選擇狀態處理器
提供所有選擇流程的共用參數和邏輯
包含時間基礎的卡住檢測機制
"""

import time
from typing import Optional, Any, Dict
from abc import ABC, abstractmethod

class BaseSelectionStateHandler(ABC):
    """所有選擇狀態的基礎類別"""
    
    # 共用參數 - 所有選擇流程使用相同的設定
    STUCK_THRESHOLD = 1.0  # 卡住檢測閾值（秒）
    DEFAULT_SEARCH_DIRECTION = 'right'  # 預設搜尋方向（先右後左）
    
    def __init__(self):
        # 共用的時間追蹤變數
        self.last_value_change_time = time.time()
        self.last_tracked_value = None
        self.current_search_direction = self.DEFAULT_SEARCH_DIRECTION
        
        # 狀態特定的變數（由子類別定義）
        self.targets = {}
        
        print(f"🔧 {self.get_state_name()} handler initialized (共用時間基礎檢測)")
        print(f"⚙️ 共用參數 - 卡住閾值: {self.STUCK_THRESHOLD}s, 預設方向: {self.DEFAULT_SEARCH_DIRECTION}")
    
    @abstractmethod
    def get_state_name(self) -> str:
        """獲取狀態名稱（由子類別實作）"""
        pass
    
    @abstractmethod
    def get_supported_state(self) -> int:
        """獲取支援的狀態（由子類別實作）"""
        pass
    
    def check_stuck_and_switch_direction(self, current_value: Any, value_name: str = "value") -> bool:
        """
        共用的卡住檢測和方向切換邏輯
        
        Args:
            current_value: 當前的值（index, direction 等）
            value_name: 值的名稱（用於日誌顯示）
            
        Returns:
            bool: 是否發生了方向切換
        """
        current_time = time.time()
        direction_switched = False
        
        # 檢查值是否有變化
        if self.last_tracked_value != current_value:
            # 值有變化，更新記錄
            self.last_tracked_value = current_value
            self.last_value_change_time = current_time
            print(f"📈 {value_name} 變化: {current_value}, 重置時間戳")
        else:
            # 值沒有變化，檢查是否超過閾值
            time_since_last_change = current_time - self.last_value_change_time
            print(f"⏱️ {value_name} 未變化時間: {time_since_last_change:.2f}s")
            
            if time_since_last_change > self.STUCK_THRESHOLD:
                # 超過閾值沒有變化，切換搜尋方向
                self._switch_search_direction()
                self.last_value_change_time = current_time  # 重置時間戳
                direction_switched = True
                print(f"🔄 檢測到 {value_name} 卡住 ({time_since_last_change:.2f}s)，已切換方向")
        
        return direction_switched
    
    def _switch_search_direction(self):
        """切換搜尋方向的共用邏輯"""
        old_direction = self.current_search_direction
        
        # 實作「先右後左」的切換邏輯
        if self.current_search_direction == 'right':
            self.current_search_direction = 'left'
        elif self.current_search_direction == 'left':
            self.current_search_direction = 'right'
        elif self.current_search_direction == 'up':
            self.current_search_direction = 'down'
        elif self.current_search_direction == 'down':
            self.current_search_direction = 'up'
        else:
            # 預設情況，回到預設方向
            self.current_search_direction = self.DEFAULT_SEARCH_DIRECTION
        
        print(f"🔄 搜尋方向切換: {old_direction} -> {self.current_search_direction}")
    
    def reset_search_state(self):
        """重置搜尋狀態的共用邏輯"""
        self.last_tracked_value = None
        self.current_search_direction = self.DEFAULT_SEARCH_DIRECTION
        self.last_value_change_time = time.time()
        print(f"🔄 {self.get_state_name()} 搜尋狀態重置 (共用邏輯)")
    
    def get_search_progress(self) -> Dict[str, Any]:
        """獲取搜尋進度的共用邏輯"""
        current_time = time.time()
        return {
            "state": self.get_state_name(),
            "stuck_time": current_time - self.last_value_change_time,
            "search_direction": self.current_search_direction,
            "stuck_threshold": self.STUCK_THRESHOLD,
            "last_tracked_value": self.last_tracked_value
        }
    
    def set_targets(self, targets: dict):
        """設定目標的共用方法"""
        self.targets = targets
        print(f"🎯 {self.get_state_name()} 目標設定: {targets}")
    
    @classmethod
    def set_global_stuck_threshold(cls, threshold: float):
        """設定全域卡住閾值"""
        old_threshold = cls.STUCK_THRESHOLD
        cls.STUCK_THRESHOLD = threshold
        print(f"🌐 全域卡住閾值更新: {old_threshold}s -> {threshold}s")
    
    @classmethod
    def set_global_default_direction(cls, direction: str):
        """設定全域預設搜尋方向"""
        old_direction = cls.DEFAULT_SEARCH_DIRECTION
        cls.DEFAULT_SEARCH_DIRECTION = direction
        print(f"🌐 全域預設方向更新: {old_direction} -> {direction}")
    
    def log_search_status(self, current_value: Any, target_value: Any, value_name: str = "value"):
        """記錄搜尋狀態的共用方法"""
        current_time = time.time()
        stuck_time = current_time - self.last_value_change_time
        
        print(f"🔍 {self.get_state_name()} 搜尋狀態:")
        print(f"   當前 {value_name}: {current_value}")
        print(f"   目標 {value_name}: {target_value}")
        print(f"   搜尋方向: {self.current_search_direction}")
        print(f"   卡住時間: {stuck_time:.2f}s / {self.STUCK_THRESHOLD}s")
    
    def reset_search_state(self):
        """重置搜尋狀態的共用方法"""
        self.last_value_change_time = time.time()
        self.last_tracked_value = None
        self.current_search_direction = self.DEFAULT_SEARCH_DIRECTION
        print(f"🔄 {self.get_state_name()} 搜尋狀態已重置")
