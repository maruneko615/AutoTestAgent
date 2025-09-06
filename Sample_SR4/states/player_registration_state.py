"""
GAME_FLOW_PLAYER_REGISTRATION 狀態處理器
處理玩家註冊狀態 (EGameFlowState = 28)
"""

import sys
import os
from typing import Optional, Any

# 添加父目錄到路徑
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from config.game_config import GameFlowState
from .base_state_handler import BaseStateHandler

class PlayerRegistrationStateHandler(BaseStateHandler):
    def __init__(self):
        super().__init__("PLAYER_REGISTRATION", GameFlowState.GAME_FLOW_PLAYER_REGISTRATION)
        
        
    def can_handle(self, state: int) -> bool:
        return state == GameFlowState.GAME_FLOW_PLAYER_REGISTRATION
        
    def handle_state(self, state: int, game_data: Any) -> Optional[bytes]:
        if not self.can_handle(state):
            return None
            
        print(f"📝 Handling PLAYER_REGISTRATION state")
        
        # 輸入相關邏輯
        import random
        if random.random() < 0.3:  # 30%機率按確認
            return self.random_generator.generate_start_input()
        else:
            return self.random_generator.generate_selection_input()
