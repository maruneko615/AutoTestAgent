"""
GAME_FLOW_GAME_OVER 狀態處理器
處理遊戲結束狀態 (EGameFlowState = 9)
"""

import sys
import os
from typing import Optional, Any

# 添加父目錄到路徑
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from config.game_config import GameFlowState
from .base_state_handler import BaseStateHandler

class GameOverStateHandler(BaseStateHandler):
    def __init__(self):
        super().__init__("GAME_OVER", GameFlowState.GAME_FLOW_GAME_OVER)
        
        
    def can_handle(self, state: int) -> bool:
        return state == GameFlowState.GAME_FLOW_GAME_OVER
        
    def handle_state(self, state: int, game_data: Any) -> Optional[bytes]:
        if not self.can_handle(state):
            return None
            
        print(f"💀 Handling GAME_OVER state")
        
        # 預設處理邏輯
        return self.handle_random_input(game_data)
