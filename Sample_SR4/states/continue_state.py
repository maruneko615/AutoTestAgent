"""
GAME_FLOW_CONTINUE 狀態處理器
處理接關選擇狀態 (EGameFlowState = 22)
"""

import sys
import os
from typing import Optional, Any

# 添加父目錄到路徑
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from config.game_config import GameFlowState
from .base_state_handler import BaseStateHandler

class ContinueStateHandler(BaseStateHandler):
    def __init__(self):
        super().__init__("CONTINUE", GameFlowState.GAME_FLOW_CONTINUE)
        
        # 接關策略設定
        self.continue_decision_made = False
        self.continue_probability = 0.3
        
    def can_handle(self, state: int) -> bool:
        return state == GameFlowState.GAME_FLOW_CONTINUE
        
    def handle_state(self, state: int, game_data: Any) -> Optional[bytes]:
        if not self.can_handle(state):
            return None
            
        print(f"🔄 Handling CONTINUE state")
        
        # 接關邏輯
        import random
        if not self.continue_decision_made:
            should_continue = random.random() < self.continue_probability
            self.continue_decision_made = True
            if should_continue:
                print("💰 Deciding to continue")
                return self.random_generator.generate_coin_input()
            else:
                print("❌ Deciding not to continue")
        return self.handle_basic_input(game_data)
