"""
GAME_FLOW_BATTLE_MAP 狀態處理器
處理戰鬥地圖狀態 (EGameFlowState = 30)
"""

import sys
import os
from typing import Optional, Any

# 添加父目錄到路徑
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from config.game_config import GameFlowState
from .base_state_handler import BaseStateHandler

class BattleMapStateHandler(BaseStateHandler):
    def __init__(self):
        super().__init__("BATTLE_MAP", GameFlowState.GAME_FLOW_BATTLE_MAP)
        
        
    def can_handle(self, state: int) -> bool:
        return state == GameFlowState.GAME_FLOW_BATTLE_MAP
        
    def handle_state(self, state: int, game_data: Any) -> Optional[bytes]:
        if not self.can_handle(state):
            return None
            
        print(f"🗺️  Handling BATTLE_MAP state")
        
        # 預設處理邏輯
        return self.handle_random_input(game_data)
