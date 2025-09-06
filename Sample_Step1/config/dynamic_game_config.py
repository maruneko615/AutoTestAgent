"""
動態遊戲配置定義模組 - 通用模板版本
此檔案將由 AutoTestBuilder 根據實際的 proto 和遊戲設定檔進行修改
"""

import os
import sys
from typing import Dict, Any, Optional

# 設定環境變數以避免 protobuf 版本問題
os.environ['PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION'] = 'python'

# 動態添加 Proto 路徑
proto_paths = [
    os.path.join(os.path.dirname(__file__), '..', '..', 'ProtoSchema'),  # AutoTestBuilder 結構
    os.path.join(os.path.dirname(__file__), '..', 'ProtoSchema'),        # 同級目錄
    '/mnt/d/AutoTest/ProtoSchema',                                       # 固定路徑
]

proto_loaded = False
for proto_path in proto_paths:
    if os.path.exists(proto_path):
        sys.path.append(proto_path)
        proto_loaded = True
        break

if not proto_loaded:
    print("❌ 找不到 ProtoSchema 路徑")
    sys.exit(1)

try:
    import GameFlowData_pb2 as GameFlowData
    import InputCommand_pb2 as InputCommand
except ImportError as e:
    print(f"❌ Failed to import proto modules in dynamic_game_config: {e}")
    raise

# 導入遊戲配置
from .game_config import (
    # TODO: Import GameFlowState from GameFlowData.proto
    # TODO: Import InputKeyType from InputCommand.proto
    # TODO: Import VrInputType from InputCommand.proto
    GAME_FLOW_STATE_NAMES, SELECTION_OPTIONS
)

class DynamicGameConfig:
    """
    動態遊戲配置生成器 - 通用模板
    
    ⚠️ 注意：此類別將由 AutoTestBuilder 根據實際數據進行修改
    AutoTestBuilder 會：
    1. 分析 ProtoSchema 獲取實際的枚舉和欄位
    2. 分析遊戲設定檔獲取選項名稱和範圍
    3. 修改此檔案注入具體的遊戲資訊
    """
    
    def __init__(self):
        # 這些將由 AutoTestBuilder 根據實際數據填充
        self._analyze_proto_schema()
        self._load_game_settings()
    
    def _analyze_proto_schema(self):
        """分析 ProtoSchema 結構"""
        print("🔍 分析 ProtoSchema 結構...")
        
        # 分析 GameFlowData
        game_data = GameFlowData.GameFlowData()
        self.game_fields = {}
        for field in game_data.DESCRIPTOR.fields:
            self.game_fields[field.name] = field.number
        
        # 分析 InputCommand
        input_cmd = InputCommand.InputCommand()
        self.input_fields = {}
        for field in input_cmd.DESCRIPTOR.fields:
            self.input_fields[field.name] = field.number
        
        print(f"✓ 分析完成: {len(self.game_fields)} 個遊戲欄位, {len(self.input_fields)} 個輸入欄位")
    
    def _load_game_settings(self):
        """載入遊戲設定"""
        # 🔧 AutoTestBuilder 會修改此方法以載入實際的遊戲設定
        pass
    
    def get_selection_options(self) -> Dict[int, list]:
        """獲取選擇選項配置"""
        return SELECTION_OPTIONS.copy()
    
    def get_state_names(self) -> Dict[int, str]:
        """獲取狀態名稱映射"""
        return GAME_FLOW_STATE_NAMES.copy()
    
    def is_selection_state(self, state_id: int) -> bool:
        """檢查是否為選擇狀態"""
        return state_id in SELECTION_OPTIONS
    
    def get_input_key_mapping(self) -> Dict[str, int]:
        """獲取輸入按鍵映射"""
        return {
            # TODO: Map input keys from InputCommand.proto
            # 'up': InputKeyType.INPUT_KEY_UP,
            # 'down': InputKeyType.INPUT_KEY_DOWN,
            # 'left': InputKeyType.INPUT_KEY_LEFT,
            # 'right': InputKeyType.INPUT_KEY_RIGHT,
            # 'confirm': InputKeyType.INPUT_KEY_START
        }

# 創建全域實例
_config_instance = None

def get_dynamic_config() -> DynamicGameConfig:
    """獲取動態配置實例（單例模式）"""
    global _config_instance
    if _config_instance is None:
        _config_instance = DynamicGameConfig()
    return _config_instance

# 便利函數
def get_selection_options() -> Dict[int, list]:
    """獲取選擇選項配置"""
    return get_dynamic_config().get_selection_options()

def get_state_names() -> Dict[int, str]:
    """獲取狀態名稱映射"""
    return get_dynamic_config().get_state_names()

def is_selection_state(state_id: int) -> bool:
    """檢查是否為選擇狀態"""
    return get_dynamic_config().is_selection_state(state_id)

def get_input_key_mapping() -> Dict[str, int]:
    """獲取輸入按鍵映射"""
    return get_dynamic_config().get_input_key_mapping()
