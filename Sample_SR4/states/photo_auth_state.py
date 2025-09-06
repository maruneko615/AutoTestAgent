"""
GAME_FLOW_PHOTO_AUTH 狀態處理器
處理照片認證狀態 (EGameFlowState = 13)
"""

import sys
import os
from typing import Optional, Any

# 添加父目錄到路徑
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from config.game_config import GameFlowState
from .base_state_handler import BaseStateHandler

class PhotoAuthStateHandler(BaseStateHandler):
    def __init__(self):
        super().__init__("PHOTO_AUTH", GameFlowState.GAME_FLOW_PHOTO_AUTH)
        
        
    def can_handle(self, state: int) -> bool:
        return state == GameFlowState.GAME_FLOW_PHOTO_AUTH
        
    def handle_state(self, state: int, game_data: Any) -> Optional[bytes]:
        if not self.can_handle(state):
            return None
            
        print(f"📸 Handling PHOTO_AUTH state")
        
        # 預設處理邏輯
        return self.handle_random_input(game_data)
