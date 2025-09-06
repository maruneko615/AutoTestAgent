# Agent 流程處理開發標準

## 1. 核心架構原則

### 1.1 每次訊息必須回應原則
- 收到任何遊戲訊息都必須產生回應
- 不允許忽略或跳過任何訊息
- 回應可以是操作指令或空指令，但必須有回應

### 1.2 FSM (有限狀態機) 架構設計
```python
class GameFlowFSM:
    def process_game_data(self, game_data) -> Optional[InputCommand]:
        # 每次都返回 InputCommand 或 None
        return self.current_stage.process(game_data)
```

### 1.3 UDP 通訊機制
- 使用非同步 UDP Socket
- 角色註冊：發送 "role:agent"，等待 "ok:agent"
- 直接發送 Protobuf 二進制數據

### 1.4 Stage-based 狀態處理模式
- 每個遊戲狀態對應一個 Stage 處理器
- 通過 FSM 自動分派到對應 Stage
- Stage 負責具體的邏輯處理

## 2. 訊息處理流程

### 2.1 訊息接收與解析流程
```python
def _on_message(self, data: bytes):
    # 1. 解析 Protobuf 訊息
    game_data = self.parse_game_data(data)
    
    # 2. 通過 FSM 處理
    input_command = self.fsm.process_game_data(game_data)
    
    # 3. 發送回應
    if input_command:
        self.send_message(input_command)
```

### 2.2 狀態分派機制 (FSM → Stage)
```python
def _switch_stage(self, flow_state: int):
    stage = self.stage_registry.get(flow_state)
    if stage:
        self.current_stage = stage
```

### 2.3 InputCommand 生成與發送
```python
def create_input_command(self, keys: List[str]) -> bytes:
    input_cmd = InputCommand.InputCommand()
    for key in keys:
        input_cmd.key_inputs.append(self.key_mapping[key])
    input_cmd.is_key_down = True
    input_cmd.timestamp = int(time.time() * 1000)
    return input_cmd.SerializeToString()
```

### 2.4 回應保證機制
- 每個 Stage 的 process() 方法必須返回值
- 即使是"不操作"也要返回空的 InputCommand
- 記錄所有回應以便除錯

## 3. 狀態處理器 (Stage) 設計規範

### 3.1 BaseStage 繼承結構
```python
class BaseStage:
    def can_handle(self, game_data) -> bool:
        raise NotImplementedError
    
    def process(self, game_data) -> Optional[InputCommand]:
        raise NotImplementedError
```

### 3.2 can_handle() 狀態匹配邏輯
```python
def can_handle(self, game_data):
    return game_data.current_flow_state == self.target_state
```

### 3.3 process() 處理邏輯實現
```python
def process(self, game_data):
    # 1. 檢查當前選項
    current_option = game_data.selected_xxx
    
    # 2. 決定操作
    if self.need_navigate(current_option):
        return self.create_navigation_command()
    else:
        return self.create_confirm_command()
```

### 3.4 目標導向與預設行為設計
- 支援設定目標選項
- 沒有目標時使用預設行為
- 智能導航到目標選項

## 4. 配置驅動開發模式

### 4.1 JSON 配置檔案結構
```json
{
  "stages": [
    {
      "stage_name": "模式選擇",
      "flow_states": [14],
      "config": {
        "action_config": {
          "action_sequence": [
            {
              "keys": ["INPUT_KEY_LEFT"],
              "is_key_down": true,
              "delay": 0
            }
          ]
        }
      }
    }
  ]
}
```

### 4.2 動態 Stage 註冊機制
```python
def load_stages_from_config(self, config_file):
    for stage_config in config['stages']:
        stage = self.generate_stage(stage_config)
        for flow_state in stage_config['flow_states']:
            self.fsm.register_stage(flow_state, stage)
```

### 4.3 action_sequence 定義規範
- keys: 按鍵列表
- is_key_down: 按鍵狀態
- delay: 延遲時間
- description: 操作描述

### 4.4 stuck_threshold 與重試邏輯
- 檢測卡住狀態
- 自動重試機制
- 最大重試次數限制

## 5. 選擇邏輯實現標準

### 5.1 導航邏輯 (左右/上下切換)
```python
def navigate_to_target(self, current, target):
    if current < target:
        return self.create_input_command(['Right'])
    elif current > target:
        return self.create_input_command(['Left'])
    else:
        return self.create_input_command(['Start'])
```

### 5.2 循環選擇處理 (環繞邏輯)
```python
def calculate_shortest_path(self, current, target, total_options):
    direct_distance = abs(target - current)
    wrap_distance = total_options - direct_distance
    return direct_distance <= wrap_distance
```

### 5.3 目標達成確認機制
```python
def wait_for_target_delay(self):
    if not self.is_target_reached:
        self.is_target_reached = True
        self.target_reached_time = time.time()
        return False
    return time.time() - self.target_reached_time >= self.target_delay
```

### 5.4 選項名稱映射管理
```python
self.option_names = {
    0: "本地對戰",
    1: "全球對戰"
}
```

## 6. 通訊協定規範

### 6.1 角色註冊流程
```python
# 發送角色識別
await self._send_message("role:agent".encode('utf-8'))

# 等待確認
if message_str == "ok:agent":
    self._role_registered = True
```

### 6.2 Protobuf 訊息格式標準
- GameFlowData: 遊戲狀態訊息
- InputCommand: 輸入指令訊息
- 使用 SerializeToString() 序列化
- 直接發送二進制數據

### 6.3 錯誤處理與重連機制
```python
try:
    # 處理訊息
except Exception as e:
    self.log.error(f"處理錯誤: {e}")
    # 繼續運行，不中斷
```

## 7. 開發實作指南

### 7.1 新狀態處理器創建步驟
1. 繼承 BaseStage
2. 實現 can_handle() 方法
3. 實現 process() 方法
4. 添加到配置檔案
5. 測試驗證

### 7.2 配置檔案編寫規範
- 每個狀態獨立配置
- 明確定義 action_sequence
- 包含完整的按鍵映射
- 添加描述說明

### 7.3 測試驗證方法
```python
# 模擬遊戲數據測試
mock_data = MockGameData(state=14, mode=1)
result = stage.process(mock_data)
assert result is not None
```

### 7.4 除錯與日誌記錄
```python
print(f"🎮 處理狀態: {game_data.current_flow_state}")
print(f"📤 發送指令: {keys}")
print(f"✅ 處理完成")
```

## 8. 最佳實踐與注意事項

### 8.1 效能優化建議
- 避免重複創建 Protobuf 物件
- 使用快取機制
- 最小化序列化操作

### 8.2 常見錯誤避免
- 不要忽略任何訊息
- 確保所有分支都有回應
- 檢查 Protobuf 欄位存在性

### 8.3 擴展性考量
- 模組化設計
- 配置驅動
- 介面統一

### 8.4 維護性設計原則
- 清晰的命名規範
- 完整的註釋說明
- 統一的錯誤處理

## 9. 範例與模板

### 9.1 標準 Stage 實作範例
```python
class SelectModeStage(BaseStage):
    def __init__(self):
        super().__init__("模式選擇")
        self.mode_names = {0: "本地對戰", 1: "全球對戰"}
    
    def can_handle(self, game_data):
        return game_data.current_flow_state == 14
    
    def process(self, game_data):
        current_mode = game_data.selected_mode
        if current_mode != 0:  # 導航到本地對戰
            return self.create_input_command(['Left'])
        else:  # 確認選擇
            return self.create_input_command(['Start'])
```

### 9.2 配置檔案模板
```json
{
  "stage_name": "狀態名稱",
  "stage_type": "action",
  "flow_states": [狀態編號],
  "description": "狀態描述",
  "config": {
    "action_config": {
      "action_sequence": [
        {
          "keys": ["按鍵名稱"],
          "is_key_down": true,
          "delay": 0,
          "description": "操作描述"
        }
      ]
    }
  }
}
```

### 9.3 測試案例模板
```python
def test_stage_processing():
    stage = YourStage()
    mock_data = MockGameData(state=X, option=Y)
    result = stage.process(mock_data)
    assert result is not None
    assert len(result.key_inputs) > 0
```

### 9.4 常用程式碼片段
```python
# 創建輸入指令
def create_input_command(self, keys):
    input_cmd = InputCommand.InputCommand()
    for key in keys:
        input_cmd.key_inputs.append(self.key_mapping[key])
    input_cmd.is_key_down = True
    input_cmd.timestamp = int(time.time() * 1000)
    return input_cmd.SerializeToString()

# 狀態匹配
def can_handle(self, game_data):
    return game_data.current_flow_state == self.target_state

# 導航邏輯
def navigate_to_option(self, current, target):
    if current < target:
        return ['Right']
    elif current > target:
        return ['Left']
    else:
        return ['Start']
```

## 10. 版本控制與文件維護

### 10.1 文件版本管理
- 版本號格式：主版本.次版本.修訂版本
- 記錄每次變更的原因和影響
- 保持向後相容性

### 10.2 變更記錄追蹤
- 新增功能記錄
- 修復問題記錄
- 效能改進記錄

### 10.3 向後相容性保證
- 保持 API 介面穩定
- 漸進式升級策略
- 廢棄功能預警

### 10.4 團隊協作規範
- 統一的程式碼風格
- 完整的 PR 審查
- 定期的技術分享

---

**版本**: 1.0  
**建立日期**: 2025-01-27  
**維護者**: AutoTest 開發團隊
