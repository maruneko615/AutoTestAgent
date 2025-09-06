"""
GAME_FLOW_COPYRIGHT 狀態處理器
處理版權畫面狀態 (EGameFlowState = 0)
"""

import sys
import os
from typing import Optional, Any

# 添加父目錄到路徑
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from config.game_config import GameFlowState
from .base_state_handler import BaseStateHandler

class CopyrightStateHandler(BaseStateHandler):
    def __init__(self):
        super().__init__("COPYRIGHT", GameFlowState.GAME_FLOW_COPYRIGHT)
        
    def can_handle(self, state: int) -> bool:
        return state == GameFlowState.GAME_FLOW_COPYRIGHT
        
    def handle_state(self, state: int, game_data: Any) -> Optional[bytes]:
        if not self.can_handle(state):
            return None
            
        print(f"©️  Handling COPYRIGHT state")
        
        # 版權畫面可能需要按鍵跳過
        import random
        if random.random() < 0.4:  # 40%機率按確認跳過
            print("⏭️  Attempting to skip copyright")
            return self.random_generator.generate_start_input()
        else:
            return self.handle_basic_input(game_data)
