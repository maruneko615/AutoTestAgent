"""
GAME_FLOW_RANKING 狀態處理器
處理排行榜狀態 (EGameFlowState = 10)
"""

import sys
import os
from typing import Optional, Any

# 添加父目錄到路徑
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from config.game_config import GameFlowState
from .base_state_handler import BaseStateHandler

class RankingStateHandler(BaseStateHandler):
    def __init__(self):
        super().__init__("RANKING", GameFlowState.GAME_FLOW_RANKING)
        
        
    def can_handle(self, state: int) -> bool:
        return state == GameFlowState.GAME_FLOW_RANKING
        
    def handle_state(self, state: int, game_data: Any) -> Optional[bytes]:
        if not self.can_handle(state):
            return None
            
        print(f"🏆 Handling RANKING state")
        
        # 預設處理邏輯
        return self.handle_random_input(game_data)
