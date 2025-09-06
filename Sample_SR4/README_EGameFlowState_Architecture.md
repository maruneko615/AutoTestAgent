# SR4 AutoTest Agent - 基於 EGameFlowState 的架構

## 架構概述

根據您的需求，我們重新設計了架構，**每個 EGameFlowState 都有對應的獨立處理器**。這樣 AutoTestBuilder 可以根據需求精準地修改特定狀態的處理邏輯。

## 🎯 **核心設計理念**

### **狀態精準對應**
- 每個 `EGameFlowState` 都有獨立的 Python 檔案
- AutoTestBuilder 根據需求關鍵詞直接定位到特定狀態處理器
- 只修改相關狀態的邏輯，不影響其他狀態

### **需求範例對應**
- **「在選擇場景流程每次都選擇首爾正走」** → 只修改 `select_scene_state.py`
- **「每次進選擇車輛都選預設選項的右邊那台車」** → 只修改 `select_bike_state.py`
- **「投幣頁面永遠不投幣」** → 只修改 `coin_page_state.py`
- **「比賽中永遠全油門」** → 只修改 `race_state.py`

## 📁 **新的架構結構**

```
Sample/
├── main.py                    # 主程式入口
├── core/                      # 核心功能模組
│   ├── websocket_manager.py   # WebSocket 連線管理
│   ├── message_handler.py     # Protobuf 訊息處理
│   └── statistics_manager.py  # 統計和監控
├── flow/
│   └── state_manager.py       # 狀態管理器（替代 flow_manager）
├── states/                    # 🆕 基於 EGameFlowState 的狀態處理器
│   ├── select_scene_state.py  # GAME_FLOW_SELECT_SCENE (6)
│   ├── select_bike_state.py   # GAME_FLOW_SELECT_BIKE (5)
│   ├── coin_page_state.py     # GAME_FLOW_COIN_PAGE (4)
│   ├── race_state.py          # GAME_FLOW_RACE (7)
│   └── ... (其他狀態處理器)
├── input/                     # 輸入生成模組
├── config/                    # 配置模組
└── utils/                     # 工具模組
```

## 🔧 **已實作的狀態處理器**

### 1. **select_scene_state.py** - 場景選擇狀態
- **對應狀態**：`GAME_FLOW_SELECT_SCENE = 6`
- **支援目標**：`selected_track`, `route_direction`
- **搜尋策略**：預設向上，無變化時切換向下
- **應用場景**：「選擇首爾正走」、「每次都選重慶」

### 2. **select_bike_state.py** - 車輛選擇狀態
- **對應狀態**：`GAME_FLOW_SELECT_BIKE = 5`
- **支援目標**：`selected_vehicle`
- **搜尋策略**：預設向右，無變化時切換向左
- **特殊功能**：支援相對位置選擇（如「右邊那台車」）
- **應用場景**：「選擇極速王者」、「預設選項的右邊那台車」

### 3. **coin_page_state.py** - 投幣頁面狀態
- **對應狀態**：`GAME_FLOW_COIN_PAGE = 4`
- **支援策略**：`always`, `never`, `random`
- **可配置參數**：投幣機率
- **應用場景**：「永遠不投幣」、「總是投幣」

### 4. **race_state.py** - 比賽狀態
- **對應狀態**：`GAME_FLOW_RACE = 7`
- **支援策略**：`full_throttle`, `conservative`, `random`, `custom`
- **可配置參數**：油門範圍、轉向範圍、煞車機率
- **應用場景**：「全油門不煞車」、「保守駕駛」

## 🎮 **狀態處理器標準介面**

每個狀態處理器都實作以下標準介面：

```python
class StateHandler:
    def can_handle(self, state: int) -> bool:
        """檢查是否可以處理此狀態"""
        
    def handle_state(self, state: int, game_data: Any) -> Optional[bytes]:
        """處理狀態並生成輸入"""
        
    def set_targets(self, targets: dict):
        """設定目標參數"""
        
    def get_state_name(self) -> str:
        """獲取狀態名稱"""
        
    def reset_state(self):
        """重置狀態"""
        
    def get_state_progress(self) -> dict:
        """獲取狀態進度"""
```

## 🔄 **StateManager 運作流程**

```python
# 1. 接收遊戲狀態
game_data.current_flow_state = GAME_FLOW_SELECT_BIKE

# 2. StateManager 自動選擇對應處理器
handler = state_handlers[GAME_FLOW_SELECT_BIKE]  # select_bike_state.py

# 3. 處理器生成對應輸入
input_command = handler.handle_state(state, game_data)

# 4. 發送輸入到遊戲端
websocket.send(input_command)
```

## 📝 **AutoTestBuilder 整合**

### **需求解析對應表**

| 需求關鍵詞 | 對應狀態處理器 | EGameFlowState |
|-----------|---------------|----------------|
| 「選擇場景」、「選擇賽道」 | `select_scene_state.py` | `GAME_FLOW_SELECT_SCENE = 6` |
| 「選擇車輛」、「選擇機車」 | `select_bike_state.py` | `GAME_FLOW_SELECT_BIKE = 5` |
| 「投幣」、「coin」 | `coin_page_state.py` | `GAME_FLOW_COIN_PAGE = 4` |
| 「比賽」、「race」 | `race_state.py` | `GAME_FLOW_RACE = 7` |

### **AutoTestBuilder 工作流程**

1. **需求解析**：識別關鍵詞，定位目標狀態處理器
2. **程式碼生成**：只修改對應的狀態處理器檔案
3. **精準替換**：保持其他狀態處理器不變

## 🚀 **擴展指南**

### **新增狀態處理器**

1. 在 `states/` 目錄下創建新的狀態處理器
2. 實作標準介面
3. 在 `StateManager` 中註冊

```python
# 範例：新增 GAME_FLOW_WARNING 處理器
class WarningStateHandler:
    def can_handle(self, state: int) -> bool:
        return state == GameFlowState.GAME_FLOW_WARNING
        
    def handle_state(self, state: int, game_data: Any) -> Optional[bytes]:
        # 實作警告畫面處理邏輯
        pass

# 在 StateManager 中註冊
state_manager.register_state_handler(GameFlowState.GAME_FLOW_WARNING, WarningStateHandler())
```

### **客製化現有處理器**

直接修改對應的狀態處理器檔案：

```python
# 修改 select_bike_state.py 支援特殊需求
def handle_special_requirement(self, requirement: str):
    if "右邊那台車" in requirement:
        return self.handle_relative_selection(game_data, "右邊")
```

## 📊 **完整的 EGameFlowState 對應表**

| 狀態值 | 狀態名稱 | 處理器檔案 | 實作狀態 |
|-------|---------|-----------|---------|
| 0 | GAME_FLOW_COPYRIGHT | `copyright_state.py` | 🔄 待實作 |
| 1 | GAME_FLOW_WARNING | `warning_state.py` | 🔄 待實作 |
| 2 | GAME_FLOW_LOGO | `logo_state.py` | 🔄 待實作 |
| 3 | GAME_FLOW_PV | `pv_state.py` | 🔄 待實作 |
| 4 | GAME_FLOW_COIN_PAGE | `coin_page_state.py` | ✅ 已實作 |
| 5 | GAME_FLOW_SELECT_BIKE | `select_bike_state.py` | ✅ 已實作 |
| 6 | GAME_FLOW_SELECT_SCENE | `select_scene_state.py` | ✅ 已實作 |
| 7 | GAME_FLOW_RACE | `race_state.py` | ✅ 已實作 |
| 8 | GAME_FLOW_RACE_END | `race_end_state.py` | 🔄 待實作 |
| ... | ... | ... | ... |

## 🎯 **架構優勢**

### ✅ **精準性**
- 每個狀態都有專門的處理器
- AutoTestBuilder 可以精確定位修改目標
- 降低意外影響其他功能的風險

### ✅ **可維護性**
- 狀態邏輯完全獨立
- 修改不會影響其他狀態
- 易於測試和驗證

### ✅ **可擴展性**
- 新增狀態處理器很容易
- 支援複雜的客製化需求
- 保持架構的靈活性

### ✅ **效率性**
- AutoTestBuilder 只需要處理特定狀態
- AI 生成的程式碼更加精準
- 減少不必要的程式碼修改

## 🔧 **使用方法**

```bash
# 基本使用（隨機模式）
python main.py

# 目標導向測試
python main.py --requirement "選擇首爾正走，開極速王者"

# 特殊策略測試
python main.py --requirement "投幣頁面永遠不投幣，比賽中全油門"
```

這個基於 EGameFlowState 的架構完美支援您的需求：**每個狀態都有獨立的處理器，AutoTestBuilder 可以精準地針對特定狀態進行客製化修改**！

---

**版本**：3.0 (EGameFlowState-based Architecture)  
**最後更新**：2025-07-31  
**維護者**：AutoTest 開發團隊
