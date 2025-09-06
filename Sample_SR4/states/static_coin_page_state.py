"""
GAME_FLOW_STATIC_COIN_PAGE 狀態處理器
處理靜態投幣頁面狀態 (EGameFlowState = 38)
"""

import sys
import os
from typing import Optional, Any

# 添加父目錄到路徑
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from config.game_config import GameFlowState
from .base_state_handler import BaseStateHandler

class StaticCoinPageStateHandler(BaseStateHandler):
    def __init__(self):
        super().__init__("STATIC_COIN_PAGE", GameFlowState.GAME_FLOW_STATIC_COIN_PAGE)
        
        # 投幣策略設定
        self.coin_strategy = "random"  # "random", "always", "never"
        self.coin_probability = 0.12   # 靜態投幣頁面機率稍低
        
    def can_handle(self, state: int) -> bool:
        return state == GameFlowState.GAME_FLOW_STATIC_COIN_PAGE
        
    def handle_state(self, state: int, game_data: Any) -> Optional[bytes]:
        if not self.can_handle(state):
            return None
            
        print(f"🪙 Handling STATIC_COIN_PAGE state")
        
        # 根據策略決定是否投幣
        if self.coin_strategy == "always":
            return self._handle_always_coin(game_data)
        elif self.coin_strategy == "never":
            return self._handle_never_coin(game_data)
        else:
            return self._handle_random_coin(game_data)
            
    def _handle_always_coin(self, game_data: Any) -> bytes:
        """總是投幣策略"""
        print("💰 Always coin strategy - inserting coin")
        import random
        if random.random() < 0.8:  # 80%機率投幣
            return self.random_generator.generate_coin_input()
        else:  # 20%機率按確認
            return self.random_generator.generate_start_input()
            
    def _handle_never_coin(self, game_data: Any) -> bytes:
        """永不投幣策略"""
        print("🚫 Never coin strategy - not inserting coin")
        return self.random_generator.generate_basic_input()
        
    def _handle_random_coin(self, game_data: Any) -> bytes:
        """隨機投幣策略"""
        print(f"🎲 Random coin strategy (probability: {self.coin_probability:.1%})")
        import random
        choice = random.random()
        
        if choice < self.coin_probability:
            print("💰 Inserting coin...")
            return self.random_generator.generate_coin_input()
        elif choice < self.coin_probability + 0.08:  # 額外8%機率按確認
            print("✅ Pressing start...")
            return self.random_generator.generate_start_input()
        else:
            return self.random_generator.generate_basic_input()
            
    def set_coin_strategy(self, strategy: str, probability: float = 0.12):
        """設定投幣策略"""
        if strategy in ["random", "always", "never"]:
            self.coin_strategy = strategy
            self.coin_probability = max(0.0, min(1.0, probability))
            print(f"🎯 Static coin strategy set to: {strategy}")
            if strategy == "random":
                print(f"🎲 Static coin probability: {self.coin_probability:.1%}")
        else:
            print(f"❌ Invalid coin strategy: {strategy}")
            
    def set_targets(self, targets: dict):
        """設定目標"""
        super().set_targets(targets)
        
        # 檢查是否有投幣策略相關的設定
        if 'coin_strategy' in targets:
            strategy = targets['coin_strategy']
            probability = targets.get('coin_probability', 0.12)
            self.set_coin_strategy(strategy, probability)
