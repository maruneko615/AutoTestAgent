# SR4 AutoTest Agent - 模組化版本

## 概述

這是 SR4 自動測試代理程式的模組化實作版本。**Sample 目錄本身維持隨機測試模式**，而 **AutoTestBuilder 負責根據 GitHub Actions 的 requirement 參數動態修改 Sample，創建具備目標導向功能的測試配置**。

### 架構核心概念
- **Sample 目錄**：基礎模板，保持原始隨機測試邏輯
- **AutoTestBuilder**：建構工具，負責：
  1. 複製 Sample 目錄
  2. 根據 requirement 解析目標需求
  3. 修改複製目錄中的相關檔案（如 `target_parser.py`）
  4. 應用必要的技術修正（protobuf 相容性等）
  5. 生成可執行的目標導向測試配置

## 重要更新和問題解決記錄

### 2025-08-04 重大更新（最新修正）

#### 0. 選擇策略邏輯修正 🔧
**問題**：原始隨機選擇邏輯不正確，每次都重新隨機選擇目標，沒有正確的流程控制
**修正後的正確邏輯**：
- **進入新流程時**：隨機決定目標 index（只決定一次）
- **執行搜尋階段**：持續左右移動直到 current_index == target_index
- **達到目標後**：不斷按 START 直到流程切換
- **流程切換後**：立刻停止，重置狀態準備下次新流程

**實作細節**：
```python
# 新流程檢測
def _is_new_flow(self) -> bool:
    return not hasattr(self, 'flow_initialized')

# 隨機目標初始化（只在新流程時執行一次）
def _initialize_random_target(self):
    if not hasattr(self, 'flow_initialized'):
        import random
        self.random_target = random.randint(0, max_index)
        self.target_reached = False
        self.flow_initialized = True

# 正確的隨機選擇邏輯
def _handle_random_selection(self, game_data):
    current_value = game_data.selected_track  # 或 selected_vehicle
    
    # 檢測新流程並初始化隨機目標
    if self._is_new_flow():
        self._initialize_random_target()
    
    # 檢查是否達到隨機目標
    if current_value == self.random_target:
        if not self.target_reached:
            self.target_reached = True
        # 持續按 START 直到流程切換
        return generate_start_input()
    
    # 執行搜尋邏輯
    return self._execute_search(current_value, self.random_target)
```

**修正範圍**：
- `states/select_scene_state.py` - 賽道選擇邏輯
- `states/select_bike_state.py` - 車輛選擇邏輯
- `states/base_selection_state.py` - 新增 `reset_search_state()` 方法

### 2025-08-04 重大更新

#### 1. Protobuf 相容性問題解決
**問題**：系統 protobuf 版本更新至 6.31.1 後，原本正常運作的輸入生成功能出現相容性問題。
**解決方案**：
- 在所有 protobuf 相關模組匯入前設定環境變數：`os.environ['PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION'] = 'python'`
- 已在 `game_config.py` 和 `main.py` 中實作此修正
- 確保所有 pb2 檔案匯入前都已設定此環境變數

#### 2. 選擇狀態處理器架構重構
**改進**：建立共用基礎類別 `BaseSelectionStateHandler` 來統一選擇邏輯
**特點**：
- 時間基礎的卡住檢測：`STUCK_THRESHOLD = 1.0` 秒（取代原本的計數方式）
- 預設搜尋方向：`DEFAULT_SEARCH_DIRECTION = 'right'`
- 「右優先，後左」搜尋策略：先嘗試右方向，卡住時切換至左方向
- 統一的 `reset_state()` 方法實作

#### 3. LEFT 輸入指令問題分析
**發現**：LEFT 輸入指令生成正常，問題出在 protobuf 序列化相容性
**技術細節**：
- `generate_left_input()` 和 `generate_right_input()` 都能正確產生 50 位元組的 protobuf 訊息
- 問題根源是系統 protobuf 版本更新導致的描述符建立錯誤
- 透過環境變數設定解決相容性問題

#### 4. 首爾測試配置建立
**實作**：建立專門的首爾賽道測試配置
- 複製 Sample 目錄建立 `Seoul_Test_20250804_202628`
- 修改 `target_parser.py` 設定 `fixed_targets = {'selected_track': 3}`
- 對應首爾賽道索引：`TRACK_SEOUL = 3`

#### 5. AutoTestBuilder 工作流程確立
**核心機制**：AutoTestBuilder 動態修改 Sample 創建目標導向配置
- Sample 目錄保持原始隨機測試狀態
- AutoTestBuilder 根據 GitHub Actions requirement 參數進行動態修改
- 自動應用所有必要的技術修正和目標設定
- 生成時間戳命名的測試配置目錄

## 架構說明

### 模組結構
```
Sample/
├── main.py                    # 主程式入口
├── core/                      # 核心功能模組
│   ├── websocket_manager.py   # WebSocket 連線管理
│   ├── message_handler.py     # Protobuf 訊息處理
│   └── statistics_manager.py  # 統計和監控
├── input/                     # 輸入生成模組
│   ├── input_generator.py     # 輸入生成基礎類別
│   ├── random_input.py        # 隨機輸入生成器
│   └── targeted_input.py      # 目標導向輸入生成器
├── flow/                      # 流程管理模組
│   ├── flow_manager.py        # 遊戲流程管理
│   ├── selection_handler.py   # 選擇階段處理器
│   └── race_handler.py        # 比賽階段處理器
├── config/                    # 配置模組
│   ├── game_config.py         # 遊戲配置定義
│   └── target_parser.py       # 需求解析器
└── utils/                     # 工具模組
    └── proto_loader.py        # Proto 動態載入
```

## 使用方法

### AutoTestBuilder 使用流程
```bash
# AutoTestBuilder 會根據 GitHub Actions 的 requirement 參數自動：
# 1. 複製 Sample 目錄
# 2. 解析需求並修改配置檔案
# 3. 應用技術修正
# 4. 生成可執行的目標導向測試配置

# 範例：GitHub Actions 傳入 requirement="選擇首爾"
# AutoTestBuilder 會：
# - 創建 Seoul_Test_YYYYMMDD_HHMMSS 目錄
# - 修改 target_parser.py 設定 fixed_targets = {'selected_track': 3}
# - 應用 protobuf 相容性修正
```

### 直接執行 Sample（隨機模式）
```bash
# Sample 目錄本身保持隨機測試模式
cd Sample
python main.py

# 指定伺服器位址
python main.py --server ws://192.168.1.100:8587
```

### 執行 AutoTestBuilder 生成的配置
```bash
# 執行目標導向測試配置
cd Seoul_Test_20250804_202628
python main.py
```

### 需求語法範例
- `"選擇首爾"` - 選擇首爾賽道
- `"選擇首爾正走"` - 選擇首爾賽道順時針方向
- `"選擇極速王者"` - 選擇極速王者車輛
- `"選擇上海，開極速王者"` - 選擇上海賽道和極速王者車輛
- `"選擇重慶反走"` - 選擇重慶賽道逆時針方向

## 選擇策略詳細說明

### 正確的隨機選擇流程（v1.2 修正版）

#### 1. **新流程檢測**
```python
def _is_new_flow(self) -> bool:
    """檢測是否為新流程"""
    if not hasattr(self, 'flow_initialized'):
        return True
    return False
```

#### 2. **隨機目標初始化**（只在新流程時執行一次）
```python
def _initialize_random_target(self):
    """初始化隨機目標"""
    if not hasattr(self, 'flow_initialized'):
        import random
        self.random_target = random.randint(0, max_index)  # 隨機選擇目標
        self.target_reached = False
        self.flow_initialized = True
        print(f"🎲 隨機選擇目標 index: {self.random_target}")
```

#### 3. **執行階段**
- **搜尋階段**：current_index != target_index 時，持續發送左右移動指令
- **確認階段**：current_index == target_index 時，持續發送 START 指令
- **完成階段**：流程切換後，重置狀態準備下次新流程

#### 4. **狀態重置**
```python
def reset_state(self):
    """重置狀態 - 為新流程做準備"""
    # 清除流程標記，下次進入時會重新隨機選擇
    if hasattr(self, 'flow_initialized'):
        delattr(self, 'flow_initialized')
    if hasattr(self, 'random_target'):
        delattr(self, 'random_target')
    if hasattr(self, 'target_reached'):
        delattr(self, 'target_reached')
```

### 選擇策略時序圖

```
新流程開始
    ↓
檢測新流程 (_is_new_flow() = True)
    ↓
隨機決定目標 index (只執行一次)
    ↓
┌─────────────────────────────────┐
│ 搜尋循環                          │
│ ┌─────────────────────────────┐   │
│ │ current_index != target?    │   │
│ │ Yes: 發送 LEFT/RIGHT        │   │
│ │ No:  發送 START (持續)      │   │
│ └─────────────────────────────┘   │
└─────────────────────────────────┘
    ↓
流程切換檢測
    ↓
重置狀態 (reset_state())
    ↓
準備下次新流程
```

### 與舊版本的差異對比

| 項目 | 舊版本 (錯誤) | 新版本 (修正) |
|------|---------------|---------------|
| 目標選擇 | 每次調用都可能重新選擇 | 新流程時只選擇一次 |
| 確認邏輯 | 隨機決定是否按確認 | 達到目標後持續按確認 |
| 流程控制 | 沒有明確的流程檢測 | 正確的新流程檢測機制 |
| 狀態重置 | 不完整的重置 | 完整的狀態重置準備新流程 |
| 行為一致性 | 行為不可預測 | 邏輯清晰可預測 |

## 功能特點

### 1. 智能選擇機制（已優化 - 2025-08-04 最新修正）
- **正確的隨機選擇流程**：
  1. **新流程檢測**：進入選擇狀態時檢測是否為新流程
  2. **目標隨機化**：新流程時隨機決定目標 index（只決定一次）
  3. **智能搜尋**：使用左右導航直到 current_index == target_index
  4. **持續確認**：達到目標後持續按 START 直到流程切換
  5. **狀態重置**：流程切換後重置狀態，準備下次新流程

- **搜尋策略**：右優先搜尋，卡住時自動切換至左方向
- **卡住檢測**：時間基礎檢測（1秒無變化）取代計數方式
- **流程控制**：正確的新流程檢測和狀態重置機制
- **共用基礎類別**：`BaseSelectionStateHandler` 統一選擇邏輯

### 2. 隨機測試模式（已修正選擇邏輯）
- **正確的隨機流程**：
  - 進入新選擇流程時隨機決定目標（賽道/車輛 index）
  - 使用智能搜尋策略導航到隨機目標
  - 達到目標後持續按確認直到流程切換
  - 流程切換後重置狀態，下次重新隨機選擇
- **多樣化輸入**：支援簡單輸入和複合輸入
- **60FPS頻率**：維持穩定的輸入發送頻率
- **Protobuf 相容**：自動處理 protobuf 版本相容性問題

### 3. 狀態管理
- **流程追蹤**：完整追蹤遊戲流程狀態轉換
- **統計分析**：詳細的操作統計和性能分析
- **錯誤處理**：完善的異常處理和恢復機制

## 支援的遊戲選項

### 賽道選擇
- 拉斯維加斯 (TRACK_LAS_VEGAS = 1)
- 北京 (TRACK_BEIJING = 2)
- 首爾 (TRACK_SEOUL = 3)
- 上海 (TRACK_SHANGHAI = 4)
- 泰國 (TRACK_THAILAND = 5)
- 重慶 (TRACK_CHONGQING = 6)

### 車輛選擇
- 極速王者 (VEHICLE_MSQ = 0)
- 時空行者 (VEHICLE_MAA = 1)
- 萬能天使 (VEHICLE_MUR = 2)
- 加速冠軍 (VEHICLE_MHA = 3)
- 彎道女王 (VEHICLE_MRA = 4)
- 越野達人 (VEHICLE_MAD = 5)
- 電光喵喵 (VEHICLE_MCE = 6)
- 未來特工 (VEHICLE_MQB = 7)

### 路線方向
- 正走/順時針 (ROUTE_DIRECTION_CLOCKWISE = 0)
- 反走/逆時針 (ROUTE_DIRECTION_COUNTER_CLOCKWISE = 1)

## 技術規格

### 網路設定
- **WebSocket 連接埠**：8587
- **預設位址**：ws://127.0.0.1:8587
- **通訊協定**：二進制 Protobuf

### 性能參數
- **輸入頻率**：60 FPS (16.67ms 間隔)
- **卡住檢測閾值**：1.0 秒無變化視為卡住（時間基礎檢測）
- **搜尋策略**：右優先，卡住時切換至左方向
- **輸入訊息大小**：50 位元組 protobuf 訊息

### 相依性和環境設定
- Python 3.x
- websocket-client
- protobuf（需要相容性設定）
- **重要**：必須在 protobuf 匯入前設定環境變數：
  ```python
  os.environ['PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION'] = 'python'
  ```
- 對應的 Proto 檔案 (InputCommand_pb2.py, GameFlowData_pb2.py)

### Protobuf 相容性注意事項
- 系統 protobuf 版本 6.31.1 需要特殊環境變數設定
- 環境變數必須在任何 pb2 檔案匯入前設定
- 已在 `game_config.py` 和 `main.py` 中實作自動設定

## 開發指南

### 新增選擇目標
1. 在 `config/target_parser.py` 中新增解析邏輯
2. 在 `config/game_config.py` 中定義對應的枚舉
3. 在 `flow/selection_handler.py` 中新增欄位映射

### 新增輸入策略
1. 繼承 `input/input_generator.py` 中的 `InputGenerator` 類別
2. 實作 `generate_input()` 方法
3. 在 `flow/flow_manager.py` 中整合新策略

### 新增流程處理
1. 在 `flow/` 目錄下建立新的處理器
2. 在 `flow/flow_manager.py` 中註冊處理器
3. 定義對應的狀態判斷邏輯

## 除錯和監控

### 日誌輸出
程式會輸出詳細的執行日誌，包括：
- 狀態轉換資訊
- 選擇進度追蹤
- 輸入生成記錄
- 統計資料報告

### 統計資訊
每 5 秒會輸出統計報告，包括：
- 訊息發送/接收速率
- 當前目標和進度
- 按鍵操作統計
- 目標達成率

## 故障排除

### 常見問題和解決方案

#### 0. 選擇邏輯問題（已修正）
**問題**：隨機選擇時每次都重新選擇目標，或選擇邏輯不正確
**解決方案**：
- 確保使用修正後的選擇邏輯
- 檢查 `_is_new_flow()` 和 `_initialize_random_target()` 方法
- 驗證 `reset_state()` 方法正確重置流程狀態
- 確認達到目標後持續按 START 直到流程切換

#### 1. Protobuf 相關問題
**問題**：Proto 模組載入失敗或輸入生成異常
**解決方案**：
- 確保在所有 pb2 檔案匯入前設定：`os.environ['PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION'] = 'python'`
- 檢查 ProtoSchema 路徑是否正確
- 驗證 protobuf 版本相容性

#### 2. 網路連線問題
**問題**：WebSocket 連線失敗
**解決方案**：
- 確認伺服器位址和連接埠 (預設 ws://127.0.0.1:8587)
- 檢查防火牆設定
- 驗證遊戲伺服器是否正在運行

#### 3. 選擇邏輯問題（已修正）
**問題**：目標解析失敗、選擇卡住、或隨機選擇行為不正確
**解決方案**：
- 檢查需求字串格式是否正確
- 確認使用修正後的選擇邏輯：
  - 新流程時隨機決定目標（只決定一次）
  - 智能搜尋直到達到目標
  - 達到目標後持續按 START
  - 流程切換後正確重置狀態
- 程式會自動檢測卡住狀態（1秒閾值）並切換搜尋方向
- 確認目標索引映射是否正確

#### 4. 輸入生成問題
**問題**：LEFT 或 RIGHT 輸入指令無效
**解決方案**：
- 驗證 protobuf 環境變數設定
- 檢查輸入訊息是否為 50 位元組
- 確認 InputCommand protobuf 結構正確

### 除錯工具和診斷
- 使用 `test_protobuf_import.py` 診斷 protobuf 匯入問題
- 使用 `test_input_generation.py` 測試輸入生成功能
- 檢查日誌輸出中的狀態轉換和錯誤訊息

### 已知限制
- 系統 protobuf 版本更新可能導致相容性問題
- 時間基礎的卡住檢測可能受到系統延遲影響
- 搜尋方向切換邏輯依賴於遊戲狀態回應時間
- **選擇邏輯限制**：依賴正確的流程檢測，如果遊戲狀態異常可能影響新流程判斷

---

**版本**：1.2  
**最後更新**：2025-08-04  
**維護者**：AutoTest 開發團隊

### 版本歷史
- **v1.2 (2025-08-04 最新)**：
  - **修正選擇策略邏輯**：實作正確的「進入新流程時隨機決定目標，然後執行搜尋直到匹配，再持續按START直到流程切換」邏輯
  - 新增新流程檢測機制 (`_is_new_flow()`)
  - 新增隨機目標初始化邏輯 (`_initialize_random_target()`)
  - 修正賽道選擇和車輛選擇的隨機行為
  - 改善狀態重置機制，確保流程切換後正確準備新流程
  - 新增 `reset_search_state()` 共用方法到基礎類別
- **v1.1 (2025-08-04)**：
  - **確立 AutoTestBuilder 架構**：Sample 保持隨機模式，AutoTestBuilder 動態創建目標導向配置
  - 解決 Protobuf 6.31.1 相容性問題
  - 重構選擇狀態處理器架構
  - 實作時間基礎卡住檢測
  - 建立 BaseSelectionStateHandler 共用基礎類別
  - 修正 LEFT 輸入指令問題
  - 新增首爾測試配置範例
- **v1.0 (2025-07-31)**：初始模組化版本
