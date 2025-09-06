"""
GAME_FLOW_LOAD_RACE_RESULT 狀態處理器
處理載入比賽結果狀態 (EGameFlowState = 39)
"""

import sys
import os
from typing import Optional, Any

# 添加父目錄到路徑
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from config.game_config import GameFlowState
from .base_state_handler import BaseStateHandler

class LoadRaceResultStateHandler(BaseStateHandler):
    def __init__(self):
        super().__init__("LOAD_RACE_RESULT", GameFlowState.GAME_FLOW_LOAD_RACE_RESULT)
        
        
    def can_handle(self, state: int) -> bool:
        return state == GameFlowState.GAME_FLOW_LOAD_RACE_RESULT
        
    def handle_state(self, state: int, game_data: Any) -> Optional[bytes]:
        if not self.can_handle(state):
            return None
            
        print(f"📥 Handling LOAD_RACE_RESULT state")
        
        # 載入狀態通常不需要輸入
        return self.handle_basic_input(game_data)
