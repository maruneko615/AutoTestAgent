"""
GAME_FLOW_LOGO 狀態處理器
處理 Logo 畫面狀態 (EGameFlowState = 2)
"""

import sys
import os
from typing import Optional, Any

# 添加父目錄到路徑
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from config.game_config import GameFlowState
from .base_state_handler import BaseStateHandler

class LogoStateHandler(BaseStateHandler):
    def __init__(self):
        super().__init__("LOGO", GameFlowState.GAME_FLOW_LOGO)
        
    def can_handle(self, state: int) -> bool:
        return state == GameFlowState.GAME_FLOW_LOGO
        
    def handle_state(self, state: int, game_data: Any) -> Optional[bytes]:
        if not self.can_handle(state):
            return None
            
        print(f"🏷️  Handling LOGO state")
        
        # Logo 畫面通常自動播放，偶爾可以跳過
        import random
        if random.random() < 0.2:  # 20%機率嘗試跳過
            print("⏭️  Attempting to skip logo")
            return self.random_generator.generate_start_input()
        else:
            return self.handle_basic_input(game_data)
