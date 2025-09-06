# SR4 AutoTest Agent - 架構澄清說明

## 重要架構澄清

### 實際運作方式

**遊戲端主導的狀態驅動架構**：
- 遊戲端透過 protobuf 主動傳送當前遊戲狀態
- Agent 被動響應，根據接收到的狀態做出對應反應
- Agent **不需要知道**遊戲流程的順序或轉換邏輯

### 這意味著什麼？

#### ✅ **正確的理解**
- Agent 是**狀態響應器**，不是流程控制器
- 每個狀態都是獨立處理的
- 遊戲端決定何時進入哪個狀態
- Agent 只需要對當前狀態做出正確的輸入響應

#### ❌ **錯誤的理解**
- ~~Agent 需要知道流程順序~~
- ~~Agent 需要控制狀態轉換~~
- ~~Agent 需要預測下一個狀態~~

## 架構設計的正確性

### 流程處理器設計 ✅
我們的流程處理器設計是**正確的**：
- 每個處理器專注於處理特定類型的狀態
- 使用 `can_handle(state)` 檢查是否能處理該狀態
- 透過 `handle_state(state, game_data)` 對狀態做出響應

### FlowManager 設計 ✅
FlowManager 的設計也是**正確的**：
- 根據當前狀態自動選擇對應的處理器
- 不需要維護流程順序邏輯
- 專注於狀態分發和響應

## 實際運作流程

```
1. 遊戲端 → protobuf → Agent
   傳送：current_flow_state = GAME_FLOW_SELECT_BIKE
   
2. Agent 接收狀態
   MessageHandler 解析 protobuf
   
3. FlowManager 分發狀態
   找到能處理 GAME_FLOW_SELECT_BIKE 的處理器
   
4. SelectionFlowHandler 處理
   檢查是否有 selected_vehicle 目標
   生成對應的輸入指令
   
5. Agent → protobuf → 遊戲端
   傳送：INPUT_KEY_RIGHT (或其他輸入)
```

## 狀態響應策略

### 目標導向狀態
當遊戲端傳送選擇相關狀態時：
- `GAME_FLOW_SELECT_BIKE` → 檢查 `selected_vehicle` 目標
- `GAME_FLOW_SELECT_SCENE` → 檢查 `selected_track` 目標
- `GAME_FLOW_SELECT_MODE` → 檢查 `game_mode` 目標

### 隨機響應狀態
當沒有特定目標或非選擇狀態時：
- 生成隨機輸入
- 根據狀態類型選擇合適的輸入策略

### 特殊響應狀態
某些狀態需要特定的響應邏輯：
- `GAME_FLOW_RACE` → 生成類比輸入（油門、轉向、煞車）
- `GAME_FLOW_COIN_PAGE` → 隨機決定是否投幣
- `GAME_FLOW_CONTINUE` → 根據策略決定是否接關

## 程式碼範例

### 正確的狀態處理方式

```python
class SelectionFlowHandler:
    def can_handle(self, state: int) -> bool:
        """檢查是否能處理此狀態"""
        return state in [
            GameFlowState.GAME_FLOW_SELECT_BIKE,
            GameFlowState.GAME_FLOW_SELECT_SCENE,
            # ... 其他選擇狀態
        ]
        
    def handle_state(self, state: int, game_data: Any) -> Optional[bytes]:
        """根據當前狀態生成對應輸入"""
        if state == GameFlowState.GAME_FLOW_SELECT_BIKE:
            # 處理車輛選擇邏輯
            if 'selected_vehicle' in self.targets:
                return self._handle_targeted_selection(...)
            else:
                return self._handle_random_selection(...)
```

### 錯誤的流程控制方式

```python
# ❌ 錯誤：Agent 不應該控制流程轉換
def control_game_flow(self):
    if self.current_state == INIT:
        self.transition_to(STANDBY)  # 錯誤！
    elif self.current_state == STANDBY:
        self.transition_to(SELECTION)  # 錯誤！
```

## 設計優勢

### 1. 簡化架構
- Agent 不需要複雜的狀態機
- 不需要維護流程轉換邏輯
- 專注於輸入響應

### 2. 高度解耦
- Agent 與遊戲邏輯解耦
- 遊戲端可以自由改變流程順序
- Agent 仍能正確響應

### 3. 易於測試
- 可以單獨測試每個狀態的響應
- 不需要模擬完整的遊戲流程
- 測試更加穩定和可預測

### 4. 容錯性強
- 即使遊戲端狀態跳躍，Agent 仍能響應
- 不會因為意外的狀態轉換而失效
- 更加健壯和可靠

## 總結

我們的模組化架構設計完全符合實際的運作方式：
- ✅ 狀態驅動，不是流程驅動
- ✅ 被動響應，不是主動控制
- ✅ 專注輸入，不是流程管理
- ✅ 模組化處理，易於維護和擴展

這個架構澄清確保了我們的 Agent 能夠正確地與遊戲端協作，提供穩定和可靠的自動測試功能。

---

**重要提醒**：Agent 是狀態響應器，不是流程控制器！
