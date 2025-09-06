"""
需求解析器 - Sample 基礎範本版本
Sample 不需要解析 requirement，只需要提供固定的目標配置
AutoTestBuilder 會修改這個檔案中的 fixed_targets
"""

import re
from typing import Dict, Any, Optional

class TargetParser:
    def __init__(self):
        # Sample 基礎範本的預設目標配置 (AutoTestBuilder 會修改這裡)
        # 預設為空，只有 AutoTestBuilder 指定的目標才會被設定
        self.fixed_targets = {}
        
    def parse_requirement(self, requirement: Optional[str] = None) -> Dict[str, Any]:
        """返回固定目標配置 (不需要 requirement 參數)"""
        print("📋 使用 Sample 基礎範本的固定目標配置")
        
        if 'selected_track' in self.fixed_targets:
            from .game_config import TRACK_NAMES
            track_name = TRACK_NAMES.get(self.fixed_targets['selected_track'], f"Track_{self.fixed_targets['selected_track']}")
            print(f"🎯 Target track: {track_name} ({self.fixed_targets['selected_track']})")
            
        if 'selected_vehicle' in self.fixed_targets:
            from .game_config import VEHICLE_NAMES
            vehicle_name = VEHICLE_NAMES.get(self.fixed_targets['selected_vehicle'], f"Vehicle_{self.fixed_targets['selected_vehicle']}")
            print(f"🎯 Target vehicle: {vehicle_name} ({self.fixed_targets['selected_vehicle']})")
            
        if not self.fixed_targets:
            print("📋 沒有指定目標，所有選擇將使用隨機模式")
            
        return self.fixed_targets
        
    def get_target_description(self, targets: Dict[str, Any]) -> str:
        """獲取目標描述"""
        descriptions = []
        
        if 'selected_track' in targets:
            from .game_config import TRACK_NAMES
            track_name = TRACK_NAMES.get(targets['selected_track'], f"Track_{targets['selected_track']}")
            descriptions.append(f"賽道: {track_name}")
            
        if 'selected_vehicle' in targets:
            from .game_config import VEHICLE_NAMES
            vehicle_name = VEHICLE_NAMES.get(targets['selected_vehicle'], f"Vehicle_{targets['selected_vehicle']}")
            descriptions.append(f"車輛: {vehicle_name}")
            
        return ", ".join(descriptions) if descriptions else "Sample 基礎範本配置"
        
    def validate_targets(self, targets: Dict[str, Any]) -> bool:
        """驗證目標的有效性"""
        return True  # Sample 基礎範本的目標總是有效的
