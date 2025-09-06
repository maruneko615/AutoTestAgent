"""
隨機輸入生成器
生成隨機的按鍵輸入和類比輸入
"""

import random
import sys
import os
from typing import List, Optional

# 添加Proto路徑
proto_path = os.path.join(os.path.dirname(__file__), '..', '..', 'ProtoSchema')
sys.path.append(proto_path)

try:
    import InputCommand_pb2 as InputCommand
except ImportError as e:
    print(f"✗ Failed to import InputCommand_pb2 in random_input: {e}") 

from .input_generator import InputGenerator
from config.game_config import InputKeyType, VrInputType

class RandomInputGenerator(InputGenerator):
    """隨機輸入生成器"""

    # TODO: 🔧 來源: InputCommand.proto : 設定所有input command中的參數
    def __init__(self):
        super().__init__()
        
        # TODO: 🔧 來源: InputCommand.proto 
        # 選擇流程相關的按鍵範本 (上下左右確認)
#       self.selection_keys = [
#            InputKeyType.INPUT_KEY_UP,
 #           InputKeyType.INPUT_KEY_DOWN,
#            InputKeyType.INPUT_KEY_START
#        ]
                
        # VR輸入類型範本
#        self.vr_input_types = [
 #           VrInputType.INPUT_VR_THROTTLE,
#            VrInputType.INPUT_VR_STEER,
  #          VrInputType.INPUT_VR_BRAKE_LEFT,
 #           VrInputType.INPUT_VR_BRAKE_RIGHT
  #      ]
        
    def generate_input(self) -> Optional[bytes]:
        """生成隨機輸入指令"""
        # 70%機率生成簡單輸入，30%機率生成複合輸入
        if random.random() < 0.7:
            return self.generate_selection_input()
        else:
            return self.generate_complex_random_input()
            
    def generate_selection_input(self) -> bytes:
        """生成選擇相關的隨機輸入"""
        # 隨機選擇1-2個按鍵
        num_keys = random.randint(1, 2)
        selected_keys = random.sample(self.selection_keys, num_keys)
        
        # 隨機決定按下或釋放
        is_key_down = random.choice([True, False])
        
        # 記錄輸入生成
        self.log_input_generation(selected_keys, "選擇")
        
        return self.generate_key_input(selected_keys, is_key_down)
        
    def generate_basic_input(self) -> bytes:
        """生成基本隨機輸入"""
        # 隨機選擇1個按鍵
        selected_key = random.choice(self.basic_keys)
        
        # 隨機決定按下或釋放
        is_key_down = random.choice([True, False])
        
        # 記錄輸入生成
        self.log_input_generation([selected_key], "基本")
        
        return self.generate_key_input([selected_key], is_key_down)
        
    def generate_complex_random_input(self) -> bytes:
        """生成複合隨機輸入"""
        # 生成數位輸入
        num_keys = random.randint(1, 2)
        digital_keys = random.sample(self.selection_keys, num_keys)
        is_key_down = random.choice([True, False])
        
        # 30%機率添加類比輸入
        analog_inputs = []
        if random.random() < 0.3:
            vr_input = self.create_vr_input(
                random.choice(self.vr_input_types),
                random.uniform(0.0, 1.0)
            )
            analog_inputs.append(vr_input)
            
        # 記錄輸入生成
        input_type = "複合" if analog_inputs else "數位"
        self.log_input_generation(digital_keys, input_type)
        
        return self.generate_complex_input(digital_keys, is_key_down, analog_inputs)
        
    def generate_race_input(self) -> bytes:
        """生成比賽階段的隨機輸入"""
        # 比賽階段主要使用類比輸入
        analog_inputs = []
        
        # 油門輸入 (0.0-1.0)
        throttle_input = self.create_vr_input(
            VrInputType.INPUT_VR_THROTTLE,
            random.uniform(0.0, 1.0)
        )
        analog_inputs.append(throttle_input)
        
        # 轉向輸入 (-1.0-1.0)
        steer_input = self.create_vr_input(
            VrInputType.INPUT_VR_STEER,
            random.uniform(-1.0, 1.0)
        )
        analog_inputs.append(steer_input)
        
        # 隨機添加煞車輸入
        if random.random() < 0.3:
            brake_type = random.choice([
                VrInputType.INPUT_VR_BRAKE_LEFT,
                VrInputType.INPUT_VR_BRAKE_RIGHT
            ])
            brake_input = self.create_vr_input(brake_type, random.uniform(0.0, 1.0))
            analog_inputs.append(brake_input)
            
        # 可能同時有數位輸入
        digital_keys = []
        if random.random() < 0.2:  # 20%機率有數位輸入
            digital_keys = [random.choice(self.basic_keys)]
            
        is_key_down = True if digital_keys else False
        
        # 記錄輸入生成
        self.log_input_generation(digital_keys if digital_keys else [], "比賽")
        
        return self.generate_complex_input(digital_keys, is_key_down, analog_inputs)
        
        # TODO: 🔧 來源: InputCommand.proto : 根據需求生成input functions
#    def generate_coin_input(self) -> bytes:
#        """生成投幣輸入"""
#        coin_key = [InputKeyType.INPUT_KEY_COIN]  # TODO: 🔧 來源: InputCommand.proto
#        self.log_input_generation(coin_key, "投幣")
#        return self.generate_key_input(coin_key, True)
