"""
遊戲配置定義模組
定義遊戲中的各種枚舉和常數
"""

import sys
import os

# 修復 protobuf 版本相容性問題（必須在導入 pb2 檔案之前設定）
os.environ['PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION'] = 'python'

# 添加Proto路徑
proto_path = os.path.join(os.path.dirname(__file__), '..', '..', 'ProtoSchema')
sys.path.append(proto_path)

try:
    import GameFlowData_pb2 as GameFlowData
    import InputCommand_pb2 as InputCommand
except ImportError as e:
    print(f"✗ Failed to import proto modules in game_config: {e}")

# 遊戲流程狀態枚舉
class GameFlowState:
    GAME_FLOW_COPYRIGHT = 0
    GAME_FLOW_WARNING = 1
    GAME_FLOW_LOGO = 2
    GAME_FLOW_PV = 3
    GAME_FLOW_COIN_PAGE = 4
    GAME_FLOW_SELECT_BIKE = 5
    GAME_FLOW_SELECT_SCENE = 6
    GAME_FLOW_RACE = 7
    GAME_FLOW_RACE_END = 8
    GAME_FLOW_GAME_OVER = 9
    GAME_FLOW_RANKING = 10
    GAME_FLOW_PROMOTION = 11
    GAME_FLOW_ACCOUNT_ENTRY = 12
    GAME_FLOW_PHOTO_AUTH = 13
    GAME_FLOW_SELECT_MODE = 14
    GAME_FLOW_PAY_FOR_LEVEL = 15
    GAME_FLOW_RIDE_SHOW = 16
    GAME_FLOW_LOAD_FLOW = 17
    GAME_FLOW_LOAD_GAME = 18
    GAME_FLOW_CUTSCENE = 19
    GAME_FLOW_MAP_BEAT_SHOW = 20
    GAME_FLOW_SIGN_NAME = 21
    GAME_FLOW_CONTINUE = 22
    GAME_FLOW_HARDWARE_DETECT = 23
    GAME_FLOW_LOAD_CONTINUE = 24
    GAME_FLOW_LOAD_STANDBY = 25
    GAME_FLOW_OPERATOR_SETTING = 26
    GAME_FLOW_AIRSPRING_ADJUST = 27
    GAME_FLOW_PLAYER_REGISTRATION = 28
    GAME_FLOW_WARNING_FOR_SELECTION = 29
    GAME_FLOW_BATTLE_MAP = 30
    GAME_FLOW_M23_READ = 31
    GAME_FLOW_RACE_FINISH_SHOW = 32
    GAME_FLOW_PLAYER_INFO = 33
    GAME_FLOW_LOCAL_BEAT_SHOW = 34
    GAME_FLOW_AGENT_LOGO = 35
    GAME_FLOW_UE_LOGO = 36
    GAME_FLOW_CRIWARE_LOGO = 37
    GAME_FLOW_STATIC_COIN_PAGE = 38
    GAME_FLOW_LOAD_RACE_RESULT = 39

# 賽道類型枚舉
class TrackType:
    TRACK_NONE = 0
    TRACK_LAS_VEGAS = 1
    TRACK_BEIJING = 2
    TRACK_SEOUL = 3
    TRACK_SHANGHAI = 4
    TRACK_THAILAND = 5
    TRACK_CHONGQING = 6
    TRACK_PHYSICS_TEST = 7
    TRACK_PHYSICS_TEST_2 = 8
    TRACK_DELIA_HUANG_TEST = 9
    TRACK_SHOU_WEIKU_TEST = 10

# 路線方向枚舉
class RouteDirection:
    ROUTE_DIRECTION_CLOCKWISE = 0      # 順時針（正走）
    ROUTE_DIRECTION_COUNTER_CLOCKWISE = 1  # 逆時針（反走）

# 車輛類型枚舉
class VehicleType:
    VEHICLE_MSQ = 0    # 極速王者
    VEHICLE_MAA = 1    # 時空行者
    VEHICLE_MUR = 2    # 萬能天使
    VEHICLE_MHA = 3    # 加速冠軍
    VEHICLE_MRA = 4    # 彎道女王
    VEHICLE_MAD = 5    # 越野達人
    VEHICLE_MCE = 6    # 電光喵喵
    VEHICLE_MQB = 7    # 未來特工

# 輸入按鍵類型枚舉
class InputKeyType:
    INPUT_KEY_UP = 0        # 上方向鍵
    INPUT_KEY_DOWN = 1      # 下方向鍵
    INPUT_KEY_LEFT = 2      # 左方向鍵
    INPUT_KEY_RIGHT = 3     # 右方向鍵
    INPUT_KEY_START = 4     # 開始/確認鍵
    INPUT_KEY_TEST = 5      # 測試鍵
    INPUT_KEY_SERVICE = 6   # 服務鍵
    INPUT_KEY_COIN = 7      # 投幣鍵

# VR 輸入類型枚舉
class VrInputType:
    INPUT_VR_THROTTLE = 0   # 油門
    INPUT_VR_STEER = 1      # 轉向
    INPUT_VR_BRAKE_LEFT = 2 # 左煞車
    INPUT_VR_BRAKE_RIGHT = 3 # 右煞車

# 遊戲模式枚舉（如果需要的話）
class GameMode:
    MODE_SINGLE = 0
    MODE_MULTI = 1
    MODE_TIME_ATTACK = 2

# 狀態名稱映射（用於顯示）
GAME_FLOW_STATE_NAMES = {
    GameFlowState.GAME_FLOW_COPYRIGHT: "COPYRIGHT",
    GameFlowState.GAME_FLOW_WARNING: "WARNING",
    GameFlowState.GAME_FLOW_LOGO: "LOGO",
    GameFlowState.GAME_FLOW_PV: "PV",
    GameFlowState.GAME_FLOW_COIN_PAGE: "COIN_PAGE",
    GameFlowState.GAME_FLOW_SELECT_BIKE: "SELECT_BIKE",
    GameFlowState.GAME_FLOW_SELECT_SCENE: "SELECT_SCENE",
    GameFlowState.GAME_FLOW_RACE: "RACE",
    GameFlowState.GAME_FLOW_RACE_END: "RACE_END",
    GameFlowState.GAME_FLOW_GAME_OVER: "GAME_OVER",
    GameFlowState.GAME_FLOW_RANKING: "RANKING",
    GameFlowState.GAME_FLOW_PROMOTION: "PROMOTION",
    GameFlowState.GAME_FLOW_ACCOUNT_ENTRY: "ACCOUNT_ENTRY",
    GameFlowState.GAME_FLOW_PHOTO_AUTH: "PHOTO_AUTH",
    GameFlowState.GAME_FLOW_SELECT_MODE: "SELECT_MODE",
    GameFlowState.GAME_FLOW_PAY_FOR_LEVEL: "PAY_FOR_LEVEL",
    GameFlowState.GAME_FLOW_RIDE_SHOW: "RIDE_SHOW",
    GameFlowState.GAME_FLOW_LOAD_FLOW: "LOAD_FLOW",
    GameFlowState.GAME_FLOW_LOAD_GAME: "LOAD_GAME",
    GameFlowState.GAME_FLOW_CUTSCENE: "CUTSCENE",
    GameFlowState.GAME_FLOW_MAP_BEAT_SHOW: "MAP_BEAT_SHOW",
    GameFlowState.GAME_FLOW_SIGN_NAME: "SIGN_NAME",
    GameFlowState.GAME_FLOW_CONTINUE: "CONTINUE",
    GameFlowState.GAME_FLOW_HARDWARE_DETECT: "HARDWARE_DETECT",
    GameFlowState.GAME_FLOW_LOAD_CONTINUE: "LOAD_CONTINUE",
    GameFlowState.GAME_FLOW_LOAD_STANDBY: "LOAD_STANDBY",
    GameFlowState.GAME_FLOW_OPERATOR_SETTING: "OPERATOR_SETTING",
    GameFlowState.GAME_FLOW_AIRSPRING_ADJUST: "AIRSPRING_ADJUST",
    GameFlowState.GAME_FLOW_PLAYER_REGISTRATION: "PLAYER_REGISTRATION",
    GameFlowState.GAME_FLOW_WARNING_FOR_SELECTION: "WARNING_FOR_SELECTION",
    GameFlowState.GAME_FLOW_BATTLE_MAP: "BATTLE_MAP",
    GameFlowState.GAME_FLOW_M23_READ: "M23_READ",
    GameFlowState.GAME_FLOW_RACE_FINISH_SHOW: "RACE_FINISH_SHOW",
    GameFlowState.GAME_FLOW_PLAYER_INFO: "PLAYER_INFO",
    GameFlowState.GAME_FLOW_LOCAL_BEAT_SHOW: "LOCAL_BEAT_SHOW",
    GameFlowState.GAME_FLOW_AGENT_LOGO: "AGENT_LOGO",
    GameFlowState.GAME_FLOW_UE_LOGO: "UE_LOGO",
    GameFlowState.GAME_FLOW_CRIWARE_LOGO: "CRIWARE_LOGO",
    GameFlowState.GAME_FLOW_STATIC_COIN_PAGE: "STATIC_COIN_PAGE",
    GameFlowState.GAME_FLOW_LOAD_RACE_RESULT: "LOAD_RACE_RESULT"
}

# 按鍵名稱映射
INPUT_KEY_NAMES = {
    InputKeyType.INPUT_KEY_UP: "UP",
    InputKeyType.INPUT_KEY_DOWN: "DOWN",
    InputKeyType.INPUT_KEY_LEFT: "LEFT",
    InputKeyType.INPUT_KEY_RIGHT: "RIGHT",
    InputKeyType.INPUT_KEY_START: "START",
    InputKeyType.INPUT_KEY_TEST: "TEST",
    InputKeyType.INPUT_KEY_SERVICE: "SERVICE",
    InputKeyType.INPUT_KEY_COIN: "COIN"
}

# 賽道名稱映射
TRACK_NAMES = {
    TrackType.TRACK_NONE: "NONE",
    TrackType.TRACK_LAS_VEGAS: "拉斯維加斯",
    TrackType.TRACK_BEIJING: "北京",
    TrackType.TRACK_SEOUL: "首爾",
    TrackType.TRACK_SHANGHAI: "上海",
    TrackType.TRACK_THAILAND: "泰國",
    TrackType.TRACK_CHONGQING: "重慶"
}

# 車輛名稱映射
VEHICLE_NAMES = {
    VehicleType.VEHICLE_MSQ: "極速王者",
    VehicleType.VEHICLE_MAA: "時空行者",
    VehicleType.VEHICLE_MUR: "萬能天使",
    VehicleType.VEHICLE_MHA: "加速冠軍",
    VehicleType.VEHICLE_MRA: "彎道女王",
    VehicleType.VEHICLE_MAD: "越野達人",
    VehicleType.VEHICLE_MCE: "電光喵喵",
    VehicleType.VEHICLE_MQB: "未來特工"
}

# 遊戲模式名稱映射
MODE_NAMES = {
    0: "單人模式",
    1: "多人模式", 
    2: "計時賽模式"
}

# 選項索引映射 (用於隨機目標生成)
SELECTION_OPTIONS = {
    GameFlowState.GAME_FLOW_SELECT_BIKE: {
        'name': '車輛選擇',
        'options': VEHICLE_NAMES,
        'max_index': 7  # 0-7 共8台車
    },
    GameFlowState.GAME_FLOW_SELECT_SCENE: {
        'name': '賽道選擇', 
        'options': TRACK_NAMES,
        'max_index': 6  # 0-6 共7條主要賽道 (排除測試賽道)
    },
    GameFlowState.GAME_FLOW_SELECT_MODE: {
        'name': '模式選擇',
        'options': MODE_NAMES,
        'max_index': 2  # 0-2 共3種模式
    }
}
