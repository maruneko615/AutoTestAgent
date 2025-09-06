"""
GAME_FLOW_COIN_PAGE 狀態處理器
處理投幣頁面狀態 (EGameFlowState = 4)
支援投幣策略客製化
"""

import sys
import os
import time
from typing import Optional, Any

# 添加父目錄到路徑
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from config.game_config import GameFlowState
from input.random_input import RandomInputGenerator

class CoinPageStateHandler:
    def __init__(self):
        self.random_generator = RandomInputGenerator()
        self.targets = {}
        
        # 投幣策略設定
        self.coin_strategy = "random"  # "random", "always", "never"
        self.coin_probability = 0.15   # 隨機模式下的投幣機率
        
        print("🪙 CoinPage state handler initialized")
        
    def can_handle(self, state: int) -> bool:
        """檢查是否可以處理此狀態"""
        return state == GameFlowState.GAME_FLOW_COIN_PAGE
        
    def handle_state(self, state: int, game_data: Any) -> Optional[bytes]:
        """處理 GAME_FLOW_COIN_PAGE 狀態"""
        if not self.can_handle(state):
            return None
            
        print(f"🪙 Handling COIN_PAGE state")
        
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
        # 永遠不投幣，只進行基本輸入
        return self.random_generator.generate_basic_input()
        
    def _handle_random_coin(self, game_data: Any) -> bytes:
        """隨機投幣策略"""
        print(f"🎲 Random coin strategy (probability: {self.coin_probability:.1%})")
        import random
        choice = random.random()
        
        if choice < self.coin_probability:
            print("💰 Inserting coin...")
            return self.random_generator.generate_coin_input()
        elif choice < self.coin_probability + 0.1:  # 額外10%機率按確認
            print("✅ Pressing start...")
            return self.random_generator.generate_start_input()
        else:
            return self.random_generator.generate_basic_input()
            
    def set_coin_strategy(self, strategy: str, probability: float = 0.15):
        """設定投幣策略"""
        if strategy in ["random", "always", "never"]:
            self.coin_strategy = strategy
            self.coin_probability = max(0.0, min(1.0, probability))
            print(f"🎯 Coin strategy set to: {strategy}")
            if strategy == "random":
                print(f"🎲 Coin probability: {self.coin_probability:.1%}")
        else:
            print(f"❌ Invalid coin strategy: {strategy}")
            
    def set_targets(self, targets: dict):
        """設定目標（投幣頁面通常不需要目標）"""
        self.targets = targets
        
        # 檢查是否有投幣策略相關的設定
        if 'coin_strategy' in targets:
            strategy = targets['coin_strategy']
            probability = targets.get('coin_probability', 0.15)
            self.set_coin_strategy(strategy, probability)
            
    def get_state_name(self) -> str:
        """獲取狀態名稱"""
        return "COIN_PAGE"
        
    def get_supported_state(self) -> int:
        """獲取支援的狀態"""
        return GameFlowState.GAME_FLOW_COIN_PAGE
        
    def reset_state(self):
        """重置狀態"""
        # 投幣頁面狀態通常不需要重置特殊狀態
        print("🔄 CoinPage state reset")
        
    def get_state_progress(self) -> dict:
        """獲取狀態進度"""
        return {
            "state": "COIN_PAGE",
            "coin_strategy": self.coin_strategy,
            "coin_probability": self.coin_probability
        }
        
    def should_insert_coin(self) -> bool:
        """判斷是否應該投幣（供外部查詢使用）"""
        if self.coin_strategy == "always":
            return True
        elif self.coin_strategy == "never":
            return False
        else:
            import random
            return random.random() < self.coin_probability
