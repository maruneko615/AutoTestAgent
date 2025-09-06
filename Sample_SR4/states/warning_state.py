"""
GAME_FLOW_WARNING 狀態處理器
處理警告畫面狀態 (EGameFlowState = 1)
"""

import sys
import os
from typing import Optional, Any

# 添加父目錄到路徑
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from config.game_config import GameFlowState
from .base_state_handler import BaseStateHandler

class WarningStateHandler(BaseStateHandler):
    def __init__(self):
        super().__init__("WARNING", GameFlowState.GAME_FLOW_WARNING)
        
    def can_handle(self, state: int) -> bool:
        return state == GameFlowState.GAME_FLOW_WARNING
        
    def handle_state(self, state: int, game_data: Any) -> Optional[bytes]:
        if not self.can_handle(state):
            return None
            
        print(f"⚠️  Handling WARNING state")
        
        # 警告畫面通常需要確認
        import random
        if random.random() < 0.6:  # 60%機率按確認
            print("✅ Confirming warning")
            return self.random_generator.generate_start_input()
        else:
            return self.handle_basic_input(game_data)
