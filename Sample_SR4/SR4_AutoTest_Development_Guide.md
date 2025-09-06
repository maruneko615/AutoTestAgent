# SR4 AutoTest Agent 開發指南

## 概述

本文件詳細說明了製作 SR4 自動測試代理程式所需的完整資訊，包括遊戲資訊、技術規格、架構設計和實作細節。

---

## 🎮 遊戲基礎資訊

### 1. 遊戲流程狀態定義

```cpp
UENUM(BlueprintType)
enum class EGameFlowState : uint8
{
    Copyright = 0               UMETA(DisplayName = "版權畫面"),
    Warning = 1                 UMETA(DisplayName = "警告畫面"),
    Logo = 2                    UMETA(DisplayName = "Logo 畫面"),
    PV = 3                      UMETA(DisplayName = "宣傳影片"),
    CoinPage = 4                UMETA(DisplayName = "投幣頁面"),
    SelectMode = 5              UMETA(DisplayName = "模式選擇"),
    SelectScene = 6             UMETA(DisplayName = "賽道選擇"),
    SelectBike = 7              UMETA(DisplayName = "車輛選擇"),
    Race = 8                    UMETA(DisplayName = "比賽進行"),
    RaceEnd = 9                 UMETA(DisplayName = "比賽結束"),
    LoadGame = 10               UMETA(DisplayName = "載入遊戲"),
    LoadFlow = 11               UMETA(DisplayName = "載入流程"),
    LoadStandby = 12            UMETA(DisplayName = "載入待機"),
    LoadContinue = 13           UMETA(DisplayName = "載入繼續"),
    LoadRaceResult = 14         UMETA(DisplayName = "載入比賽結果"),
    Continue = 15               UMETA(DisplayName = "繼續遊戲"),
    GameOver = 16               UMETA(DisplayName = "遊戲結束"),
    Cutscene = 17               UMETA(DisplayName = "過場動畫"),
    BattleMap = 18              UMETA(DisplayName = "戰鬥地圖"),
    Ranking = 19                UMETA(DisplayName = "排行榜"),
    PlayerInfo = 20             UMETA(DisplayName = "玩家資訊"),
    PlayerRegistration = 21     UMETA(DisplayName = "玩家註冊"),
    AccountEntry = 22           UMETA(DisplayName = "帳號輸入"),
    SignName = 23               UMETA(DisplayName = "簽名輸入"),
    PhotoAuth = 24              UMETA(DisplayName = "照片認證"),
    Promotion = 25              UMETA(DisplayName = "促銷活動"),
    StaticCoinPage = 26         UMETA(DisplayName = "靜態投幣頁面"),
    LocalBeatShow = 27          UMETA(DisplayName = "本地最佳成績顯示"),
    MapBeatShow = 28            UMETA(DisplayName = "地圖最佳成績顯示"),
    RaceFinishShow = 29         UMETA(DisplayName = "比賽完成顯示"),
    RideShow = 30               UMETA(DisplayName = "騎乘展示"),
    PayForLevel = 31            UMETA(DisplayName = "付費升級"),
    OperatorSetting = 32        UMETA(DisplayName = "操作員設定"),
    HardwareDetect = 33         UMETA(DisplayName = "硬體檢測"),
    AirspringAdjust = 34        UMETA(DisplayName = "氣壓調整"),
    M23Read = 35                UMETA(DisplayName = "M23 讀取"),
    WarningForSelection = 36    UMETA(DisplayName = "選擇警告"),
    UELogo = 37                 UMETA(DisplayName = "UE Logo"),
    AgentLogo = 38              UMETA(DisplayName = "代理商 Logo"),
    CriwareLogo = 39            UMETA(DisplayName = "CriWare Logo")
};
```

### 2. 遊戲選項配置

#### 賽道資訊
```cpp
UENUM(BlueprintType)
enum class ETrackType : uint8
{
    LasVegas = 1        UMETA(DisplayName = "拉斯維加斯"),
    Beijing = 2         UMETA(DisplayName = "北京"),
    Seoul = 3           UMETA(DisplayName = "首爾"),
    Shanghai = 4        UMETA(DisplayName = "上海"),
    Thailand = 5        UMETA(DisplayName = "泰國"),
    Chongqing = 6       UMETA(DisplayName = "重慶")
};
```

#### 車輛資訊
```cpp
UENUM(BlueprintType)
enum class EVehicleType : uint8
{
    MSQ = 0             UMETA(DisplayName = "極速王者"),
    MAA = 1             UMETA(DisplayName = "時空行者"),
    MUR = 2             UMETA(DisplayName = "萬能天使"),
    MHA = 3             UMETA(DisplayName = "加速冠軍"),
    MRA = 4             UMETA(DisplayName = "彎道女王"),
    MAD = 5             UMETA(DisplayName = "越野達人"),
    MCE = 6             UMETA(DisplayName = "電光喵喵"),
    MQB = 7             UMETA(DisplayName = "未來特工")
};
```

#### 路線方向
```cpp
UENUM(BlueprintType)
enum class ERouteDirection : uint8
{
    Clockwise = 0           UMETA(DisplayName = "正走/順時針"),
    CounterClockwise = 1    UMETA(DisplayName = "反走/逆時針")
};
```

---

## 🔌 通訊協定資訊

### 3. WebSocket 連線設定

- **預設伺服器位址**：`ws://127.0.0.1:8587`
- **通訊協定**：二進制 Protobuf
- **連線方式**：WebSocket 客戶端
- **輸入頻率**：60 FPS (16.67ms 間隔)
- **訊息大小**：50 位元組 protobuf 訊息

### 4. Protobuf 訊息結構

#### InputCommand 訊息結構
輸入指令訊息需要包含兩種類型的輸入：
- **數位按鍵輸入**：包含按鍵類型和按下狀態（是否按下）
- **類比輸入**：包含輸入類型和數值（浮點數）

每個數位按鍵輸入需要記錄：
- 按鍵類型（整數）
- 是否按下（布林值）

每個類比輸入需要記錄：
- 輸入類型（整數）
- 輸入數值（浮點數）

#### GameFlowData 訊息結構
遊戲流程資料訊息需要包含：
- 當前遊戲狀態（整數）
- 選擇的賽道（整數）
- 選擇的車輛（整數）
- 路線方向（整數）
- 其他遊戲狀態相關欄位

### 5. 輸入按鍵定義

#### 數位按鍵
```cpp
UENUM(BlueprintType)
enum class EInputKeyType : uint8
{
    Up = 1              UMETA(DisplayName = "上"),
    Down = 2            UMETA(DisplayName = "下"),
    Left = 3            UMETA(DisplayName = "左"),
    Right = 4           UMETA(DisplayName = "右"),
    Start = 5           UMETA(DisplayName = "開始/確認"),
    Coin = 6            UMETA(DisplayName = "投幣")
    // ... 其他按鍵
};
```

#### 類比輸入
```cpp
UENUM(BlueprintType)
enum class EVrInputType : uint8
{
    Throttle = 1        UMETA(DisplayName = "油門"),      // 範圍: 0.0-1.0
    Steer = 2           UMETA(DisplayName = "轉向"),      // 範圍: -1.0-1.0
    BrakeLeft = 3       UMETA(DisplayName = "左煞車"),    // 範圍: 0.0-1.0
    BrakeRight = 4      UMETA(DisplayName = "右煞車")     // 範圍: 0.0-1.0
};
```

---

## 🧠 核心邏輯需求

### 6. 選擇策略邏輯

**統一架構設計**：

1. **StateManager 統一管理**：
   - 流程切換檢測：只在 StateManager 中檢測 `current_flow_state` 變化
   - 隨機目標決定：只在 StateManager 中生成隨機目標
   - 狀態處理器通知：透過 `set_random_target()` 方法通知狀態處理器

2. **狀態處理器簡化**：
   - 移除重複邏輯：不再有自己的流程切換檢測和隨機目標生成
   - 專注核心功能：只負責接收目標並執行搜尋邏輯
   - 統一介面：都有 `set_random_target()` 方法接收統一設定的目標

**工作流程**：
```
1. StateManager 檢測到流程切換 (current_flow_state 變化)
2. StateManager 生成隨機目標
3. StateManager 調用 handler.set_random_target(target)
4. 狀態處理器接收目標並開始搜尋
5. 達到目標後持續發送 START
6. StateManager 檢測到下次流程切換，重複步驟 1-6
```

**實作邏輯說明**：
- StateManager 在 `_handle_state_transition()` 中統一處理流程切換
- 進入選擇狀態時自動生成隨機目標並通知狀態處理器
- 狀態處理器透過 `set_random_target()` 接收目標
- 狀態處理器只負責搜尋邏輯，不再處理流程切換檢測

### 7. 卡住檢測機制

**時間基礎檢測**：
- **閾值**：1.0 秒無變化視為卡住
- **搜尋策略**：右優先，卡住時切換至左方向
- **方向切換**：右方向與左方向循環切換

**檢測邏輯說明**：
- 記錄上次數值變化的時間
- 比較當前數值與上次記錄的數值
- 如果數值有變化，更新記錄時間
- 如果數值沒有變化，計算經過的時間
- 如果經過時間超過閾值，切換搜尋方向並重置時間

### 8. 輸入生成策略

**多層次隨機輸入**：
- **70% 機率**：生成簡單選擇輸入（上下左右確認）
- **30% 機率**：生成複合輸入（數位按鍵加類比輸入）
- **比賽階段**：主要使用類比輸入（油門、轉向、煞車）
- **選擇階段**：主要使用數位輸入（上下左右確認）

**輸入頻率要求**：
- **60 FPS**：每 16.67 毫秒發送一次輸入
- **訊息大小**：固定 50 位元組的 protobuf 訊息

---

## 🏗️ 架構設計需求

### 9. 模組化架構

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
├── states/                    # 狀態處理模組
│   ├── base_selection_state.py # 選擇狀態基礎類別
│   ├── select_scene_state.py   # 賽道選擇處理器
│   ├── select_bike_state.py    # 車輛選擇處理器
│   └── ... (40+ 個狀態處理器)
└── utils/                     # 工具模組
    └── proto_loader.py        # Proto 動態載入
```

### 10. 狀態處理器設計

**統一架構設計要求**：

需要建立一個基礎選擇狀態處理器類別，包含以下共用參數：
- 卡住檢測閾值：1.0 秒
- 預設搜尋方向：右方向

基礎類別需要包含的共用變數：
- 上次數值變化時間
- 上次追蹤的數值
- 當前搜尋方向

基礎類別需要提供的抽象方法：
- 獲取狀態名稱
- 獲取支援的狀態編號
- 卡住檢測和方向切換邏輯

**狀態處理器統一介面**：
- 繼承基礎選擇狀態處理器類別
- 實作狀態處理方法
- 提供 `set_random_target(target_index)` 方法接收 StateManager 設定的目標
- 支援目標導向和隨機選擇模式
- 使用統一的卡住檢測和方向切換邏輯

**重要設計原則**：
- 狀態處理器不再自行決定隨機目標
- 狀態處理器不再檢測流程切換
- 所有目標設定和流程切換由 StateManager 統一管理
- 狀態處理器專注於搜尋邏輯的實作

---

## 🔧 技術實作細節

### 11. Protobuf 相容性

**版本相容性問題**：
- **問題描述**：系統 protobuf 版本 6.31.1 導致相容性問題
- **解決方案**：在任何 pb2 檔案匯入前設定特定的環境變數

**環境變數設定**：
需要在程式開始時，在匯入任何 protobuf 相關檔案之前，設定環境變數：
- 變數名稱：`PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION`
- 變數值：`python`

**訊息生成要求**：
- 確保生成 50 位元組的 protobuf 訊息
- 正確設定數位和類比輸入結構
- 處理序列化和反序列化

### 12. 目標導向功能

**AutoTestBuilder 動態配置**：
- **Sample 目錄**：保持隨機測試模式
- **AutoTestBuilder**：根據需求參數動態修改
- **工作流程**：
  1. 複製 Sample 目錄
  2. 解析需求並修改配置檔案
  3. 應用技術修正
  4. 生成可執行的目標導向測試配置

**需求語法支援**：
支援以下中文需求語法：
- "選擇首爾" - 選擇首爾賽道
- "選擇首爾正走" - 選擇首爾賽道順時針方向
- "選擇極速王者" - 選擇極速王者車輛
- "選擇上海，開極速王者" - 選擇上海賽道和極速王者車輛
- "選擇重慶反走" - 選擇重慶賽道逆時針方向

**目標解析邏輯**：
需要建立目標解析器，能夠：
- 解析賽道名稱並對應到正確的賽道列舉值
- 解析車輛名稱並對應到正確的車輛列舉值
- 解析方向描述並對應到正確的方向列舉值
- 支援複合需求（同時指定多個目標）
- 返回包含所有解析目標的字典結構

---

## 📊 監控和統計

### 13. 統計分析功能

**即時統計報告**（每 5 秒更新）：
- 訊息發送/接收速率
- 目標達成率分析
- 按鍵操作統計
- 當前目標和進度

**日誌輸出功能**：
- 狀態轉換資訊
- 選擇進度追蹤
- 輸入生成記錄
- 詳細的操作日誌

### 14. 錯誤處理和除錯

**常見問題處理**：
- Protobuf 相關問題
- 網路連線問題
- 選擇邏輯問題
- 輸入生成問題

**除錯工具**：
- 使用診斷腳本測試各模組功能
- 檢查日誌輸出中的狀態轉換
- 驗證 protobuf 匯入和訊息生成

---

## 🚀 完整開發提詞

### 製作 SR4 自動測試程式的完整需求

**基礎通訊**：
1. 使用 WebSocket 連接 ws://127.0.0.1:8587，通過 Protobuf 協定通訊
2. 60 FPS 輸入頻率，生成 50 位元組 protobuf 訊息
3. 解決 Protobuf 6.31.1 版本相容性問題

**遊戲支援**：
4. 支援 40+ 個遊戲狀態的自動處理，包括選擇賽道、車輛、比賽等
5. 支援 6 個賽道（拉斯維加斯、北京、首爾、上海、泰國、重慶）
6. 支援 8 種車輛（極速王者、時空行者、萬能天使等）
7. 支援 2 種路線方向（正走/反走）
8. **使用 IntEnum**：所有遊戲選項使用列舉格式定義，提高程式碼可讀性和維護性

**核心邏輯**：
9. 實作正確的隨機選擇邏輯：新流程時隨機決定目標，智能搜尋直到匹配，達到目標後持續確認
10. 時間基礎卡住檢測（1秒閾值），右優先搜尋策略，自動方向切換
11. 多層次隨機輸入：70%簡單輸入，30%複合輸入，比賽階段使用類比輸入

**架構設計**：
12. 模組化架構：核心功能、輸入生成、流程管理、配置管理、狀態處理、工具模組
13. 每個遊戲狀態都有獨立的處理器，繼承統一的基礎類別
14. 共用的卡住檢測和方向切換邏輯

**進階功能**：
15. 支援目標導向測試：可解析「選擇首爾」、「選擇極速王者正走」等需求語法
16. AutoTestBuilder 動態配置生成機制
17. 完整的統計分析和日誌輸出功能
18. 即時監控和錯誤處理機制

**技術要求**：
19. 使用 websocket-client 和 protobuf 函式庫
20. **使用 IntEnum**：所有常數定義使用列舉格式
21. 完整的錯誤處理和異常恢復機制
22. 支援命令列參數和配置檔案

---

## 📝 版本資訊

- **文件版本**：1.0
- **建立日期**：2025-08-05
- **適用程式版本**：SR4 AutoTest Agent v1.2
- **維護者**：AutoTest 開發團隊

---

## 📚 相關文件

- [SR4 AutoTest Agent README](./README.md)
- [架構說明文件](./README_Architecture_Clarification.md)
- [遊戲流程說明](./sr_4_game_flow.md)
- [功能比較文件](./FUNCTIONALITY_COMPARISON.md)

---

**注意**：本文件包含了製作完整 SR4 自動測試程式所需的所有關鍵資訊。開發時請確保按照文件中的規格和邏輯進行實作，特別注意選擇策略邏輯和卡住檢測機制的正確實作。

### 12. StateManager 統一管理設計

**統一管理職責**：

StateManager 作為整個系統的核心協調者，負責以下關鍵功能：

1. **流程切換檢測**：
   - 監控 `game_data.current_flow_state` 變化
   - 在 `update_game_state()` 中檢測狀態轉換
   - 調用 `_handle_state_transition()` 處理轉換邏輯

2. **隨機目標生成**：
   - 為選擇狀態（SELECT_SCENE, SELECT_BIKE 等）生成隨機目標
   - 使用 `generate_random_target_for_state()` 方法
   - 確保每個流程只生成一次目標

3. **狀態處理器協調**：
   - 通過 `handler.set_random_target(target)` 通知狀態處理器
   - 在狀態轉換時調用 `handler.reset_state()` 重置處理器
   - 統一管理所有狀態處理器的生命週期

**關鍵方法實作**：

```python
def _handle_state_transition(self, from_state, to_state):
    # 1. 記錄狀態持續時間和轉換日誌
    # 2. 停止持續 START 模式
    # 3. 為選擇狀態生成隨機目標
    if to_state in SELECTION_OPTIONS:
        target_index = self.generate_random_target_for_state(to_state)
        self.random_targets[to_state] = target_index
        # 通知狀態處理器
        if to_state in self.state_handlers:
            self.state_handlers[to_state].set_random_target(target_index)
    # 4. 重置離開狀態的處理器
    if from_state in self.state_handlers:
        self.state_handlers[from_state].reset_state()

def generate_input(self):
    # 簡化版：直接使用狀態處理器（移除重複的隨機目標邏輯）
    return self._handle_with_state_handlers()
```

**設計優勢**：
- ✅ 避免隨機目標重複設定
- ✅ 統一的流程切換檢測點
- ✅ 清晰的職責分離
- ✅ 狀態處理器邏輯簡化
- ✅ 系統架構更加穩定

**與狀態處理器的協作**：
- StateManager 負責「何時」和「什麼目標」
- 狀態處理器負責「如何搜尋」和「如何達到目標」
- 通過統一介面 `set_random_target()` 進行溝通
- 避免邏輯重複和狀態不同步問題

---

## 📋 **開發檢查清單**

### 基本功能檢查
- [ ] 遊戲狀態正確識別
- [ ] 輸入指令正確生成
- [ ] 目標導向選擇功能
- [ ] 隨機選擇功能
- [ ] 卡住檢測和恢復

### 統一架構檢查
- [ ] StateManager 統一管理流程切換
- [ ] StateManager 統一生成隨機目標
- [ ] 狀態處理器實作 `set_random_target()` 方法
- [ ] 移除狀態處理器中的重複邏輯
- [ ] 避免隨機目標重複設定問題

### 進階功能檢查
- [ ] 多狀態支援
- [ ] 錯誤處理機制
- [ ] 日誌記錄完整
- [ ] 性能優化
- [ ] 程式碼品質

### 測試驗證
- [ ] 單元測試通過
- [ ] 整合測試通過
- [ ] 實際遊戲測試
- [ ] 邊界情況測試
- [ ] 長時間穩定性測試

---

**📝 注意事項**：
- 所有程式碼都要包含完整的中文註解
- 錯誤處理要完整且有意義的錯誤訊息
- 日誌輸出要清晰且有助於除錯
- 程式碼風格要一致且易於維護
- 遵循統一架構設計原則，避免邏輯重複
