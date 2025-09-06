"""
遊戲配置定義模組
定義遊戲中的各種枚舉和常數
"""

import sys
import os

# 修復 protobuf 版本相容性問題（必須在導入 pb2 檔案之前設定）
os.environ['PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION'] = 'python'

# TODO: 🔧 來源: ProtoSchema 目錄 - 需要根據實際的 Proto 檔案位置調整路徑
# 添加Proto路徑
proto_path = os.path.join(os.path.dirname(__file__), '..', '..', 'ProtoSchema')
sys.path.append(proto_path)

try:
    import GameFlowData_pb2 as GameFlowData
    import InputCommand_pb2 as InputCommand
except ImportError as e:
    print(f"✗ Failed to import proto modules in game_config: {e}")

# TODO: 🔧 來源: GameFlowData.proto、InputCommand.proto
# TODO: 🔧 列出所有GameFlowData.proto、InputCommand.proto的enum 和名稱映射

# TODO: 🔧 來源: GameFlowData.proto - enum 範本
# 賽道類型枚舉
#class TrackType:
#    TRACK_NONE = 0
#    TRACK_LAS_VEGAS = 1
#    TRACK_BEIJING = 2
#    TRACK_SEOUL = 3 ...


# TODO: 🔧 來源: GameFlowData.proto - 狀態名稱映射，提供中文名稱對應 Proto 枚舉值
# 狀態名稱映射（用於顯示）
# 範本: 賽道名稱映射
# TODO: 🔧 範本
# TRACK_NAMES = {
#    TrackType.TRACK_NONE: "NONE",
#    TrackType.TRACK_LAS_VEGAS: "拉斯維加斯",
#   TrackType.TRACK_BEIJING: "北京",
#    TrackType.TRACK_SEOUL: "首爾",
#    TrackType.TRACK_SHANGHAI: "上海",
#    TrackType.TRACK_THAILAND: "泰國",
#    TrackType.TRACK_CHONGQING: "重慶"
#}

# TODO: 根據.amazonq\rules\AutoTest_Game_Setting.md 的"2. 需要操作的流程"有流程和選項enum的邏輯說明
# 選項索引映射 (用於隨機目標生成)
# TODO: 🔧 範本 - 需要根據實際的 GameFlowData.proto 調整選擇狀態和選項
# 選項索引映射 (用於隨機目標生成)
# SELECTION_OPTIONS = {
#     # TODO: 🔧 範本 - 車輛選擇狀態配置範例
#     GameFlowState.GAME_FLOW_SELECT_BIKE: {
#         'name': '車輛選擇',
#         'options': VEHICLE_NAMES,
#         'max_index': 8
#     },
#     # TODO: 🔧 範本 - 賽道選擇狀態配置範例  
#     GameFlowState.GAME_FLOW_SELECT_SCENE: {
#         'name': '賽道選擇',
#         'options': TRACK_NAMES,
#         'max_index': 10
#     },
#     # TODO: 🔧 範本 - 模式選擇狀態配置範例
#     GameFlowState.GAME_FLOW_SELECT_MODE: {
#         'name': '模式選擇',
#         'options': MODE_NAMES,
#         'max_index': 2
#     }
# }

