"""
GAME_FLOW_ACCOUNT_ENTRY 狀態處理器
處理帳號輸入狀態 (EGameFlowState = 12)
"""

import sys
import os
from typing import Optional, Any

# 添加父目錄到路徑
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from config.game_config import GameFlowState
from .base_state_handler import BaseStateHandler

class AccountEntryStateHandler(BaseStateHandler):
    def __init__(self):
        super().__init__("ACCOUNT_ENTRY", GameFlowState.GAME_FLOW_ACCOUNT_ENTRY)
        
        
    def can_handle(self, state: int) -> bool:
        return state == GameFlowState.GAME_FLOW_ACCOUNT_ENTRY
        
    def handle_state(self, state: int, game_data: Any) -> Optional[bytes]:
        if not self.can_handle(state):
            return None
            
        print(f"👤 Handling ACCOUNT_ENTRY state")
        
        # 輸入相關邏輯
        import random
        if random.random() < 0.3:  # 30%機率按確認
            return self.random_generator.generate_start_input()
        else:
            return self.random_generator.generate_selection_input()
