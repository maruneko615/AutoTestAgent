"""
GAME_FLOW_RACE 狀態處理器
處理比賽狀態 (EGameFlowState = 7)
支援比賽策略客製化
"""

import sys
import os
import time
from typing import Optional, Any

# 添加父目錄到路徑
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from config.game_config import GameFlowState, VrInputType
from input.random_input import RandomInputGenerator

class RaceStateHandler:
    def __init__(self):
        self.random_generator = RandomInputGenerator()
        self.targets = {}
        
        # 比賽策略設定
        self.race_strategy = "random"  # "random", "full_throttle", "conservative", "custom"
        self.throttle_range = (0.0, 1.0)
        self.steer_range = (-1.0, 1.0)
        self.brake_probability = 0.3
        
        # 比賽統計
        self.race_start_time = None
        
        print("🏁 Race state handler initialized")
        
    def can_handle(self, state: int) -> bool:
        """檢查是否可以處理此狀態"""
        return state == GameFlowState.GAME_FLOW_RACE
        
    def handle_state(self, state: int, game_data: Any) -> Optional[bytes]:
        """處理 GAME_FLOW_RACE 狀態"""
        if not self.can_handle(state):
            return None
            
        # 記錄比賽開始時間
        if self.race_start_time is None:
            self.race_start_time = time.time()
            print("🚦 Race started!")
            
        print(f"🏁 Handling RACE state - strategy: {self.race_strategy}")
        
        # 根據策略生成輸入
        if self.race_strategy == "full_throttle":
            return self._handle_full_throttle_strategy(game_data)
        elif self.race_strategy == "conservative":
            return self._handle_conservative_strategy(game_data)
        elif self.race_strategy == "custom":
            return self._handle_custom_strategy(game_data)
        else:
            return self._handle_random_strategy(game_data)
            
    def _handle_full_throttle_strategy(self, game_data: Any) -> bytes:
        """全油門策略"""
        print("🚀 Full throttle strategy")
        
        analog_inputs = []
        
        # 永遠全油門
        throttle_input = self.random_generator.create_vr_input(
            VrInputType.INPUT_VR_THROTTLE,
            1.0  # 全油門
        )
        analog_inputs.append(throttle_input)
        
        # 輕微隨機轉向
        import random
        steer_input = self.random_generator.create_vr_input(
            VrInputType.INPUT_VR_STEER,
            random.uniform(-0.3, 0.3)  # 輕微轉向
        )
        analog_inputs.append(steer_input)
        
        # 不添加煞車輸入
        
        return self.random_generator.generate_complex_input([], False, analog_inputs)
        
    def _handle_conservative_strategy(self, game_data: Any) -> bytes:
        """保守策略"""
        print("🐌 Conservative strategy")
        
        analog_inputs = []
        
        # 中等油門
        import random
        throttle_input = self.random_generator.create_vr_input(
            VrInputType.INPUT_VR_THROTTLE,
            random.uniform(0.5, 0.8)  # 中等油門
        )
        analog_inputs.append(throttle_input)
        
        # 小幅轉向
        steer_input = self.random_generator.create_vr_input(
            VrInputType.INPUT_VR_STEER,
            random.uniform(-0.5, 0.5)  # 小幅轉向
        )
        analog_inputs.append(steer_input)
        
        # 偶爾煞車
        if random.random() < 0.2:  # 20%機率煞車
            brake_type = random.choice([
                VrInputType.INPUT_VR_BRAKE_LEFT,
                VrInputType.INPUT_VR_BRAKE_RIGHT
            ])
            brake_input = self.random_generator.create_vr_input(
                brake_type, 
                random.uniform(0.2, 0.6)  # 輕度煞車
            )
            analog_inputs.append(brake_input)
            
        return self.random_generator.generate_complex_input([], False, analog_inputs)
        
    def _handle_custom_strategy(self, game_data: Any) -> bytes:
        """客製化策略"""
        print("⚙️  Custom strategy")
        
        analog_inputs = []
        import random
        
        # 使用自定義油門範圍
        throttle_input = self.random_generator.create_vr_input(
            VrInputType.INPUT_VR_THROTTLE,
            random.uniform(self.throttle_range[0], self.throttle_range[1])
        )
        analog_inputs.append(throttle_input)
        
        # 使用自定義轉向範圍
        steer_input = self.random_generator.create_vr_input(
            VrInputType.INPUT_VR_STEER,
            random.uniform(self.steer_range[0], self.steer_range[1])
        )
        analog_inputs.append(steer_input)
        
        # 根據設定的機率煞車
        if random.random() < self.brake_probability:
            brake_type = random.choice([
                VrInputType.INPUT_VR_BRAKE_LEFT,
                VrInputType.INPUT_VR_BRAKE_RIGHT
            ])
            brake_input = self.random_generator.create_vr_input(
                brake_type, 
                random.uniform(0.0, 1.0)
            )
            analog_inputs.append(brake_input)
            
        return self.random_generator.generate_complex_input([], False, analog_inputs)
        
    def _handle_random_strategy(self, game_data: Any) -> bytes:
        """隨機策略（預設）"""
        print("🎲 Random strategy")
        return self.random_generator.generate_race_input()
        
    def set_race_strategy(self, strategy: str, **kwargs):
        """設定比賽策略"""
        if strategy in ["random", "full_throttle", "conservative", "custom"]:
            self.race_strategy = strategy
            print(f"🎯 Race strategy set to: {strategy}")
            
            # 設定客製化參數
            if strategy == "custom":
                if 'throttle_range' in kwargs:
                    self.throttle_range = kwargs['throttle_range']
                    print(f"🚗 Throttle range: {self.throttle_range}")
                if 'steer_range' in kwargs:
                    self.steer_range = kwargs['steer_range']
                    print(f"🎯 Steer range: {self.steer_range}")
                if 'brake_probability' in kwargs:
                    self.brake_probability = kwargs['brake_probability']
                    print(f"🛑 Brake probability: {self.brake_probability:.1%}")
        else:
            print(f"❌ Invalid race strategy: {strategy}")
            
    def set_targets(self, targets: dict):
        """設定目標"""
        self.targets = targets
        
        # 檢查是否有比賽策略相關的設定
        if 'race_strategy' in targets:
            strategy = targets['race_strategy']
            custom_params = {
                k: v for k, v in targets.items() 
                if k in ['throttle_range', 'steer_range', 'brake_probability']
            }
            self.set_race_strategy(strategy, **custom_params)
            
    def get_state_name(self) -> str:
        """獲取狀態名稱"""
        return "RACE"
        
    def get_supported_state(self) -> int:
        """獲取支援的狀態"""
        return GameFlowState.GAME_FLOW_RACE
        
    def reset_state(self):
        """重置狀態"""
        self.race_start_time = None
        print("🔄 Race state reset")
        
    def get_state_progress(self) -> dict:
        """獲取狀態進度"""
        progress = {
            "state": "RACE",
            "race_strategy": self.race_strategy
        }
        
        if self.race_start_time:
            race_time = time.time() - self.race_start_time
            progress['race_time'] = race_time
            
        if self.race_strategy == "custom":
            progress.update({
                'throttle_range': self.throttle_range,
                'steer_range': self.steer_range,
                'brake_probability': self.brake_probability
            })
            
        return progress
        
    def get_race_duration(self) -> Optional[float]:
        """獲取當前比賽持續時間"""
        if self.race_start_time is not None:
            return time.time() - self.race_start_time
        return None
