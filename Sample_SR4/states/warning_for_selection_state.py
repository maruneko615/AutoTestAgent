"""
GAME_FLOW_WARNING_FOR_SELECTION 狀態處理器
處理選擇前警告狀態 (EGameFlowState = 29)
"""

import sys
import os
from typing import Optional, Any

# 添加父目錄到路徑
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from config.game_config import GameFlowState
from .base_state_handler import BaseStateHandler

class WarningForSelectionStateHandler(BaseStateHandler):
    def __init__(self):
        super().__init__("WARNING_FOR_SELECTION", GameFlowState.GAME_FLOW_WARNING_FOR_SELECTION)
        
        
    def can_handle(self, state: int) -> bool:
        return state == GameFlowState.GAME_FLOW_WARNING_FOR_SELECTION
        
    def handle_state(self, state: int, game_data: Any) -> Optional[bytes]:
        if not self.can_handle(state):
            return None
            
        print(f"⚠️  Handling WARNING_FOR_SELECTION state")
        
        # 選擇相關邏輯
        import random
        if random.random() < 0.4:  # 40%機率按確認
            return self.random_generator.generate_start_input()
        else:
            return self.random_generator.generate_selection_input()
