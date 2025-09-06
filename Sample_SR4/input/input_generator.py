"""
輸入生成基礎類別
定義輸入生成的基本介面和共用功能
"""

import time
import uuid
import sys
import os
from abc import ABC, abstractmethod
from typing import List, Optional

# 添加Proto路徑
proto_path = os.path.join(os.path.dirname(__file__), '..', '..', 'ProtoSchema')
sys.path.append(proto_path)

try:
    import InputCommand_pb2 as InputCommand
except ImportError as e:
    print(f"✗ Failed to import InputCommand_pb2 in input_generator: {e}")

class InputGenerator(ABC):
    """輸入生成器基礎類別"""
    
    def __init__(self):
        self.session_id = str(uuid.uuid4())
        
    @abstractmethod
    def generate_input(self) -> Optional[bytes]:
        """生成輸入指令 - 抽象方法"""
        pass
        
    def generate_key_input(self, keys: List[int], is_key_down: bool) -> bytes:
        """生成按鍵輸入指令"""
        input_cmd = InputCommand.InputCommand()
        input_cmd.key_inputs.extend(keys)
        input_cmd.is_key_down = is_key_down
        input_cmd.timestamp = int(time.time() * 1000)  # 毫秒時間戳
        
        return input_cmd.SerializeToString()
        
    def generate_complex_input(self, digital_keys: List[int], is_key_down: bool, 
                             analog_inputs: Optional[List] = None) -> bytes:
        """生成複合輸入指令"""
        # 創建數位輸入
        digital_input = InputCommand.InputCommand()
        digital_input.key_inputs.extend(digital_keys)
        digital_input.is_key_down = is_key_down
        digital_input.timestamp = int(time.time() * 1000)
        
        # 創建複合指令
        complex_cmd = InputCommand.ComplexInputCommand()
        complex_cmd.digital_inputs.append(digital_input)
        
        # 添加類比輸入（如果有的話）
        if analog_inputs:
            complex_cmd.analog_inputs.extend(analog_inputs)
            
        complex_cmd.timestamp = int(time.time() * 1000)
        
        return complex_cmd.SerializeToString()
        
    def create_vr_input(self, vr_type: int, value: float) -> object:
        """創建VR輸入值"""
        vr_input = InputCommand.VrInputValue()
        vr_input.vr_type = vr_type
        vr_input.value = value
        vr_input.timestamp = int(time.time() * 1000)
        return vr_input
        
    def get_key_name(self, key_value: int) -> str:
        """獲取按鍵名稱"""
        key_names = {
            0: "UP",
            1: "DOWN", 
            2: "LEFT",
            3: "RIGHT",
            4: "START",
            5: "NITRO",
            6: "TEST",
            7: "SERVICE",
            8: "COIN",
            9: "EMERGENCY",
            10: "LEFT_LEG",
            11: "RIGHT_LEG",
            12: "SPEED_UP",
            13: "LEFT_MACHINE",
            14: "SEAT_DETECT"
        }
        return key_names.get(key_value, f"KEY_{key_value}")
        
    def log_input_generation(self, keys: List[int], input_type: str = "digital"):
        """記錄輸入生成"""
        key_names = [self.get_key_name(key) for key in keys]
        print(f"📤 生成{input_type}輸入指令: [{', '.join(key_names)}]")
