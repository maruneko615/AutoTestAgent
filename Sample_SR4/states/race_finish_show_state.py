"""
GAME_FLOW_RACE_FINISH_SHOW 狀態處理器
處理比賽完成展示狀態 (EGameFlowState = 32)
"""

import sys
import os
from typing import Optional, Any

# 添加父目錄到路徑
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from config.game_config import GameFlowState
from .base_state_handler import BaseStateHandler

class RaceFinishShowStateHandler(BaseStateHandler):
    def __init__(self):
        super().__init__("RACE_FINISH_SHOW", GameFlowState.GAME_FLOW_RACE_FINISH_SHOW)
        
        
    def can_handle(self, state: int) -> bool:
        return state == GameFlowState.GAME_FLOW_RACE_FINISH_SHOW
        
    def handle_state(self, state: int, game_data: Any) -> Optional[bytes]:
        if not self.can_handle(state):
            return None
            
        print(f"🎉 Handling RACE_FINISH_SHOW state")
        
        # 展示畫面可能可以跳過
        import random
        if random.random() < 0.3:  # 30%機率嘗試跳過
            print("⏭️  Attempting to skip")
            return self.random_generator.generate_start_input()
        else:
            return self.handle_basic_input(game_data)
