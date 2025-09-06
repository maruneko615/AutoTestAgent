"""
狀態管理器
根據 EGameFlowState 管理所有狀態處理器
每個狀態都有對應的獨立處理器
"""

import time
import random
from typing import Dict, Any, Optional

from config.game_config import GameFlowState, GAME_FLOW_STATE_NAMES, SELECTION_OPTIONS, InputKeyType, TRACK_NAMES
from input.random_input import RandomInputGenerator

# 導入所有狀態處理器
from states.copyright_state import CopyrightStateHandler
from states.warning_state import WarningStateHandler
from states.logo_state import LogoStateHandler
from states.pv_state import PvStateHandler
from states.coin_page_state import CoinPageStateHandler
from states.select_bike_state import SelectBikeStateHandler  # 重新啟用
from states.select_scene_state import SelectSceneStateHandler  # 重新啟用
from states.race_state import RaceStateHandler
from states.race_end_state import RaceEndStateHandler
from states.game_over_state import GameOverStateHandler
from states.ranking_state import RankingStateHandler
from states.promotion_state import PromotionStateHandler
from states.account_entry_state import AccountEntryStateHandler
from states.photo_auth_state import PhotoAuthStateHandler
from states.select_mode_state import SelectModeStateHandler  # 重新啟用
from states.pay_for_level_state import PayForLevelStateHandler
from states.ride_show_state import RideShowStateHandler
from states.load_flow_state import LoadFlowStateHandler
from states.load_game_state import LoadGameStateHandler
from states.cutscene_state import CutsceneStateHandler
from states.map_beat_show_state import MapBeatShowStateHandler
from states.sign_name_state import SignNameStateHandler
from states.continue_state import ContinueStateHandler
from states.hardware_detect_state import HardwareDetectStateHandler
from states.load_continue_state import LoadContinueStateHandler
from states.load_standby_state import LoadStandbyStateHandler
from states.operator_setting_state import OperatorSettingStateHandler
from states.airspring_adjust_state import AirspringAdjustStateHandler
from states.player_registration_state import PlayerRegistrationStateHandler
from states.warning_for_selection_state import WarningForSelectionStateHandler
from states.battle_map_state import BattleMapStateHandler
from states.m23_read_state import M23ReadStateHandler
from states.race_finish_show_state import RaceFinishShowStateHandler
from states.player_info_state import PlayerInfoStateHandler
from states.local_beat_show_state import LocalBeatShowStateHandler
from states.agent_logo_state import AgentLogoStateHandler
from states.ue_logo_state import UeLogoStateHandler
from states.criware_logo_state import CriwareLogoStateHandler
from states.static_coin_page_state import StaticCoinPageStateHandler
from states.load_race_result_state import LoadRaceResultStateHandler

class StateManager:
    def __init__(self):
        self.current_state = None
        self.previous_state = None
        self.game_data = None
        self.targets = {}
        self.running = False
        
        # 隨機輸入生成器（備用）
        self.random_generator = RandomInputGenerator()
        
        # 初始化所有狀態處理器 - 完整的 40 個 EGameFlowState
        self.state_handlers = {
            GameFlowState.GAME_FLOW_COPYRIGHT: CopyrightStateHandler(),
            GameFlowState.GAME_FLOW_WARNING: WarningStateHandler(),
            GameFlowState.GAME_FLOW_LOGO: LogoStateHandler(),
            GameFlowState.GAME_FLOW_PV: PvStateHandler(),
            GameFlowState.GAME_FLOW_COIN_PAGE: CoinPageStateHandler(),
            GameFlowState.GAME_FLOW_SELECT_BIKE: SelectBikeStateHandler(),  # 重新啟用
            GameFlowState.GAME_FLOW_SELECT_SCENE: SelectSceneStateHandler(),  # 重新啟用
            GameFlowState.GAME_FLOW_RACE: RaceStateHandler(),
            GameFlowState.GAME_FLOW_RACE_END: RaceEndStateHandler(),
            GameFlowState.GAME_FLOW_GAME_OVER: GameOverStateHandler(),
            GameFlowState.GAME_FLOW_RANKING: RankingStateHandler(),
            GameFlowState.GAME_FLOW_PROMOTION: PromotionStateHandler(),
            GameFlowState.GAME_FLOW_ACCOUNT_ENTRY: AccountEntryStateHandler(),
            GameFlowState.GAME_FLOW_PHOTO_AUTH: PhotoAuthStateHandler(),
            GameFlowState.GAME_FLOW_SELECT_MODE: SelectModeStateHandler(),  # 重新啟用
            GameFlowState.GAME_FLOW_PAY_FOR_LEVEL: PayForLevelStateHandler(),
            GameFlowState.GAME_FLOW_RIDE_SHOW: RideShowStateHandler(),
            GameFlowState.GAME_FLOW_LOAD_FLOW: LoadFlowStateHandler(),
            GameFlowState.GAME_FLOW_LOAD_GAME: LoadGameStateHandler(),
            GameFlowState.GAME_FLOW_CUTSCENE: CutsceneStateHandler(),
            GameFlowState.GAME_FLOW_MAP_BEAT_SHOW: MapBeatShowStateHandler(),
            GameFlowState.GAME_FLOW_SIGN_NAME: SignNameStateHandler(),
            GameFlowState.GAME_FLOW_CONTINUE: ContinueStateHandler(),
            GameFlowState.GAME_FLOW_HARDWARE_DETECT: HardwareDetectStateHandler(),
            GameFlowState.GAME_FLOW_LOAD_CONTINUE: LoadContinueStateHandler(),
            GameFlowState.GAME_FLOW_LOAD_STANDBY: LoadStandbyStateHandler(),
            GameFlowState.GAME_FLOW_OPERATOR_SETTING: OperatorSettingStateHandler(),
            GameFlowState.GAME_FLOW_AIRSPRING_ADJUST: AirspringAdjustStateHandler(),
            GameFlowState.GAME_FLOW_PLAYER_REGISTRATION: PlayerRegistrationStateHandler(),
            GameFlowState.GAME_FLOW_WARNING_FOR_SELECTION: WarningForSelectionStateHandler(),
            GameFlowState.GAME_FLOW_BATTLE_MAP: BattleMapStateHandler(),
            GameFlowState.GAME_FLOW_M23_READ: M23ReadStateHandler(),
            GameFlowState.GAME_FLOW_RACE_FINISH_SHOW: RaceFinishShowStateHandler(),
            GameFlowState.GAME_FLOW_PLAYER_INFO: PlayerInfoStateHandler(),
            GameFlowState.GAME_FLOW_LOCAL_BEAT_SHOW: LocalBeatShowStateHandler(),
            GameFlowState.GAME_FLOW_AGENT_LOGO: AgentLogoStateHandler(),
            GameFlowState.GAME_FLOW_UE_LOGO: UeLogoStateHandler(),
            GameFlowState.GAME_FLOW_CRIWARE_LOGO: CriwareLogoStateHandler(),
            GameFlowState.GAME_FLOW_STATIC_COIN_PAGE: StaticCoinPageStateHandler(),
            GameFlowState.GAME_FLOW_LOAD_RACE_RESULT: LoadRaceResultStateHandler(),
        }
        
        # 輸入間隔控制 - 每秒發送一次隨機輸入
        self.input_interval = 1.0  # 1秒間隔
        self.last_input_time = 0
        
        # 狀態統計
        self.state_enter_time = {}
        self.state_durations = {}
        
        # 隨機目標生成
        self.random_targets = {}  # 儲存每個狀態的隨機目標
        self.continuous_start_mode = {}  # 儲存是否進入持續發送 START 模式
        self.last_received_index = {}  # 儲存上次接收到的實際 index
        self.last_index_change_time = {}  # 儲存上次 index 變化的時間
        self.current_direction = {}  # 儲存當前移動方向：'right' 或 'left'
        
        print("🎮 State manager initialized with EGameFlowState-based handlers")
        print(f"📋 Registered {len(self.state_handlers)} state handlers")
        
    def set_targets(self, targets: Dict[str, Any]):
        """設定測試目標"""
        self.targets = targets
        
        # 將目標傳遞給所有狀態處理器
        for state_id, handler in self.state_handlers.items():
            handler.set_targets(targets)
        
        if targets:
            print(f"🎯 State manager targets set: {targets}")
        else:
            print("🎲 State manager using random mode")
    
    def generate_random_target_for_state(self, state: int) -> Optional[int]:
        """為指定狀態生成隨機目標索引"""
        if state in SELECTION_OPTIONS:
            selection_info = SELECTION_OPTIONS[state]
            max_index = selection_info['max_index']
            target_index = random.randint(0, max_index)
            
            # 獲取選項名稱
            option_name = selection_info['options'].get(target_index, f"選項{target_index}")
            state_name = selection_info['name']
            
            print(f"🎯 {state_name} - 隨機目標: 索引 {target_index} ({option_name})")
            
            return target_index
        return None
        
    def update_game_state(self, game_data):
        """更新遊戲狀態"""
        self.game_data = game_data
        
        if hasattr(game_data, 'current_flow_state'):
            new_state = game_data.current_flow_state
            
            # 檢查狀態變化
            if self.current_state != new_state:
                self._handle_state_transition(self.current_state, new_state)
                self.previous_state = self.current_state
                self.current_state = new_state
                
    def _handle_state_transition(self, from_state: Optional[int], to_state: int):
        """處理狀態轉換"""
        current_time = time.time()
        
        # 記錄狀態持續時間
        if from_state is not None and from_state in self.state_enter_time:
            duration = current_time - self.state_enter_time[from_state]
            if from_state not in self.state_durations:
                self.state_durations[from_state] = []
            self.state_durations[from_state].append(duration)
            
        # 記錄新狀態進入時間
        self.state_enter_time[to_state] = current_time
        
        # 顯示狀態轉換
        from_name = GAME_FLOW_STATE_NAMES.get(from_state, f"State_{from_state}") if from_state is not None else "None"
        to_name = GAME_FLOW_STATE_NAMES.get(to_state, f"State_{to_state}")
        print(f"🔄 State transition: {from_name} -> {to_name}")
        
        # 狀態切換時立刻停止持續發送 START 模式
        if from_state is not None and from_state in self.continuous_start_mode:
            print(f"⏹️  狀態切換，停止持續發送 START 模式")
            del self.continuous_start_mode[from_state]
        
        # 🎯 統一處理：進入選擇狀態時生成隨機目標
        if to_state in SELECTION_OPTIONS:
            target_index = self.generate_random_target_for_state(to_state)
            if target_index is not None:
                self.random_targets[to_state] = target_index
                # 重置狀態追蹤
                self.last_received_index[to_state] = None
                self.last_index_change_time[to_state] = time.time()
                self.current_direction[to_state] = 'right'  # 預設先往右
                # 確保不在持續 START 模式
                if to_state in self.continuous_start_mode:
                    del self.continuous_start_mode[to_state]
                
                # 🎯 通知狀態處理器設定目標
                if to_state in self.state_handlers:
                    handler = self.state_handlers[to_state]
                    if hasattr(handler, 'set_random_target'):
                        handler.set_random_target(target_index)
                        print(f"🎯 統一設定隨機目標: {target_index} (狀態: {to_name})")
        
        # 重置離開狀態的處理器
        if from_state is not None and from_state in self.state_handlers:
            self.state_handlers[from_state].reset_state()
            print(f"🔄 重置狀態處理器: {from_name}")
        
    def generate_input(self) -> Optional[bytes]:
        """生成輸入指令 - 每次收到 protobuf 就發送一次"""
        # 移除時間間隔控制，每次收到消息都處理
        
        # 直接使用狀態處理器處理當前狀態（不再使用 StateManager 的隨機目標邏輯）
        input_result = self._handle_with_state_handlers()
        
        if input_result is not None:
            return input_result
        else:
            # 如果沒有狀態處理器能處理，使用隨機輸入
            state_name = GAME_FLOW_STATE_NAMES.get(self.current_state, f"State_{self.current_state}")
            print(f"🎲 No handler found for state {state_name}, using random input")
            return self.random_generator.generate_basic_input()
    
    def _handle_random_target_selection(self) -> Optional[bytes]:
        """處理隨機目標導向選擇 - 基於實際 index 變化判斷"""
        if self.current_state is None or self.current_state not in self.random_targets:
            return None
        
        # 檢查是否已經進入持續發送 START 模式
        if self.current_state in self.continuous_start_mode:
            print(f"🔄 每次 protobuf 發送 START...")
            return self.random_generator.generate_start_input()
            
        target_index = self.random_targets[self.current_state]
        
        # 從遊戲數據中獲取當前實際的 index
        current_actual_index = self._get_current_index_from_game_data()
        if current_actual_index is None:
            print(f"⚠️  無法從遊戲數據獲取當前 index，跳過本次處理")
            return None
        
        print(f"🎮 當前狀態: {GAME_FLOW_STATE_NAMES.get(self.current_state, 'Unknown')}")
        print(f"📊 當前實際 index: {current_actual_index}, 目標 index: {target_index}")
        
        # 檢查是否達到目標 - 一選到目標就立刻停止左右移動
        if target_index == current_actual_index:
            print(f"✅ Index 匹配！當前 index {current_actual_index} == 目標 index {target_index}")
            print(f"⏹️  立刻停止發送左右鍵")
            print(f"🎯 進入持續發送 START 模式，直到狀態切換...")
            
            # 進入持續發送 START 模式
            self.continuous_start_mode[self.current_state] = True
            
            # 清除此狀態的目標，避免重複判斷
            if self.current_state in self.random_targets:
                del self.random_targets[self.current_state]
                print(f"🗑️  已清除狀態 {self.current_state} 的目標")
            
            # 立即發送第一個 START
            return self.random_generator.generate_start_input()
        
        # 還沒選到目標，繼續移動
        return self._handle_direction_based_movement(current_actual_index, target_index)
    
    def _handle_direction_based_movement(self, current_index: int, target_index: int) -> Optional[bytes]:
        """基於實際 index 變化的移動邏輯 - 每次收到 protobuf 都發送按鍵"""
        state = self.current_state
        current_time = time.time()
        
        # 檢查上次的 index 是否有變化
        last_index = self.last_received_index.get(state)
        if last_index is not None and last_index != current_index:
            print(f"📈 Index 有變化: {last_index} -> {current_index}")
            # Index 有變化，更新變化時間
            self.last_index_change_time[state] = current_time
        elif last_index is not None and last_index == current_index:
            # Index 沒變化，檢查是否超過1秒
            time_since_change = current_time - self.last_index_change_time.get(state, current_time)
            if time_since_change > 1.0:
                print(f"📉 Index 超過1秒沒變化: {current_index}，判斷已到底，切換方向")
                # 切換方向
                current_direction = self.current_direction.get(state, 'right')
                if current_direction == 'right':
                    print(f"🔄 從往右切換為往左")
                    self.current_direction[state] = 'left'
                else:
                    print(f"🔄 從往左切換為往右")
                    self.current_direction[state] = 'right'
                # 重置變化時間
                self.last_index_change_time[state] = current_time
            else:
                print(f"⏳ Index 沒變化但未超過1秒 ({time_since_change:.1f}s)，繼續當前方向")
        
        # 更新上次接收的 index
        self.last_received_index[state] = current_index
        
        # 每次收到 protobuf 都發送按鍵（根據當前方向）
        direction = self.current_direction.get(state, 'right')
        
        if direction == 'right':
            print(f"➡️  每次 protobuf 發送往右 (當前 index: {current_index})")
            return self.random_generator.generate_key_input([InputKeyType.INPUT_KEY_RIGHT], True)
        else:
            print(f"⬅️  每次 protobuf 發送往左 (當前 index: {current_index})")
            return self.random_generator.generate_key_input([InputKeyType.INPUT_KEY_LEFT], True)
    
    def _get_current_index_from_game_data(self) -> Optional[int]:
        """從遊戲數據中獲取當前選擇的實際 index"""
        if not self.game_data:
            print(f"⚠️  遊戲數據為空")
            return None
            
        try:
            if self.current_state == GameFlowState.GAME_FLOW_SELECT_BIKE:
                # 車輛選擇：檢查 selected_vehicle 欄位
                if hasattr(self.game_data, 'selected_vehicle'):
                    current_index = self.game_data.selected_vehicle
                    print(f"🚗 從遊戲數據獲取車輛 index: {current_index}")
                    return current_index
                else:
                    print(f"⚠️  遊戲數據中沒有 selected_vehicle 欄位")
                    
            elif self.current_state == GameFlowState.GAME_FLOW_SELECT_SCENE:
                # 賽道選擇：檢查 selected_track 欄位
                if hasattr(self.game_data, 'selected_track'):
                    current_index = self.game_data.selected_track
                    track_name = TRACK_NAMES.get(current_index, f"Track_{current_index}")
                    print(f"🏁 從遊戲數據獲取賽道 index: {current_index} ({track_name})")
                    return current_index
                else:
                    print(f"⚠️  遊戲數據中沒有 selected_track 欄位")
                    # 列出遊戲數據中的所有可用欄位
                    available_fields = [attr for attr in dir(self.game_data) if not attr.startswith('_')]
                    print(f"📋 可用欄位: {available_fields}")
                    
            elif self.current_state == GameFlowState.GAME_FLOW_SELECT_MODE:
                # 模式選擇：檢查 selected_mode 欄位
                if hasattr(self.game_data, 'selected_mode'):
                    current_index = self.game_data.selected_mode
                    print(f"🎮 從遊戲數據獲取模式 index: {current_index}")
                    return current_index
                else:
                    print(f"⚠️  遊戲數據中沒有 selected_mode 欄位")
                    
        except Exception as e:
            print(f"❌ 獲取遊戲數據 index 時發生錯誤: {e}")
            
        return None
    
    def _handle_fallback_selection(self, target_index: int) -> Optional[bytes]:
        """當無法獲取遊戲數據時的備用選擇邏輯 - 簡化版本"""
        print(f"⚠️  備用邏輯：無法獲取遊戲數據，暫停處理")
        return None  # 沒有遊戲數據就不處理，等下次循環
            
    def _handle_with_state_handlers(self) -> Optional[bytes]:
        """使用狀態處理器處理當前狀態"""
        if self.current_state is None:
            return None
            
        # 檢查是否有對應的狀態處理器
        if self.current_state in self.state_handlers:
            handler = self.state_handlers[self.current_state]
            state_name = GAME_FLOW_STATE_NAMES.get(self.current_state, f"State_{self.current_state}")
            print(f"🎯 Using dedicated handler for state {state_name}")
            return handler.handle_state(self.current_state, self.game_data)
                
        return None
        
    def start(self):
        """啟動狀態管理"""
        self.running = True
        print("🚀 State manager started")
        
    def stop(self):
        """停止狀態管理"""
        self.running = False
        self._print_state_statistics()
        
        # 重置所有狀態處理器
        for handler in self.state_handlers.values():
            handler.reset_state()
            
        print("⏹️  State manager stopped")
        
    def _print_state_statistics(self):
        """打印狀態統計"""
        if not self.state_durations:
            return
            
        print(f"\n📊 === State Duration Statistics ===")
        for state, durations in self.state_durations.items():
            state_name = GAME_FLOW_STATE_NAMES.get(state, f"State_{state}")
            avg_duration = sum(durations) / len(durations)
            total_duration = sum(durations)
            print(f"  {state_name}: {len(durations)} times, avg {avg_duration:.2f}s, total {total_duration:.2f}s")
            
    def get_current_state_name(self) -> str:
        """獲取當前狀態名稱"""
        if self.current_state is None:
            return "Unknown"
        return GAME_FLOW_STATE_NAMES.get(self.current_state, f"State_{self.current_state}")
        
    def has_targets(self) -> bool:
        """檢查是否有設定目標"""
        return bool(self.targets)
        
    def get_state_handler(self, state: int):
        """獲取指定狀態的處理器"""
        return self.state_handlers.get(state)
        
    def get_all_state_handlers(self) -> Dict[int, Any]:
        """獲取所有狀態處理器"""
        return self.state_handlers.copy()
        
    def get_current_state_handler(self):
        """獲取當前狀態對應的處理器"""
        if self.current_state is None:
            return None
        return self.state_handlers.get(self.current_state)
        
    def get_state_progress_summary(self) -> Dict[str, Any]:
        """獲取所有狀態的進度摘要"""
        progress_summary = {}
        
        for state_id, handler in self.state_handlers.items():
            if hasattr(handler, 'get_state_progress'):
                state_name = GAME_FLOW_STATE_NAMES.get(state_id, f"State_{state_id}")
                progress_summary[state_name] = handler.get_state_progress()
                
        return progress_summary
        
    def register_state_handler(self, state: int, handler):
        """註冊新的狀態處理器"""
        self.state_handlers[state] = handler
        handler.set_targets(self.targets)  # 設定當前目標
        state_name = GAME_FLOW_STATE_NAMES.get(state, f"State_{state}")
        print(f"📝 Registered handler for state {state_name}")
        
    def unregister_state_handler(self, state: int):
        """取消註冊狀態處理器"""
        if state in self.state_handlers:
            del self.state_handlers[state]
            state_name = GAME_FLOW_STATE_NAMES.get(state, f"State_{state}")
            print(f"🗑️  Unregistered handler for state {state_name}")
            
    def get_registered_states(self) -> list:
        """獲取已註冊的狀態列表"""
        return list(self.state_handlers.keys())
        
    def is_state_supported(self, state: int) -> bool:
        """檢查狀態是否有對應的處理器"""
        return state in self.state_handlers
