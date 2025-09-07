# AutoTestBuilder 功能需求規格

## 工具概述
AutoTestBuilder 是定制化測試工具建置器，使用 Q CLI 根據自然語言指令和遊戲配置生成針對特定測試需求的定制化 AutoTestAgent。

## 核心功能

### 雙模式執行
- **本地互動模式** - 開發階段使用，支援自然語言指令輸入
- **GitHub Action 模式** - 正式流程使用，接收自然語言指令自動建置

### 動態配置分析
- **遊戲狀態提取** - 從 GameSetting.md 動態提取遊戲狀態枚舉
- **按鍵映射分析** - 動態提取並生成按鍵映射代碼
- **UDP 配置解析** - 自動解析連線設定
- **跨遊戲適配** - 無論配置如何變化都能自動適配

### Q CLI 整合機制
- **環境檢測** - 區分 Windows 和 Linux/macOS 環境
- **結構化提示詞** - 使用與 AgentMaker 相似的提示詞結構
- **程式碼品質保證** - 完整的語法檢查和驗證
- **WSL 格式修復** - 自動修復 WSL 環境下的格式問題

## 技術規格

### 執行環境
- **平台**: Windows 10/11 + Linux/macOS
- **Python**: 3.8+
- **依賴**: Amazon Q CLI

### 指令格式
```bash
# 本地互動模式
python AutoTestBuilder.py --interactive

# GitHub Action 模式
python AutoTestBuilder.py --command="每次都在選擇賽道選擇上海"
```

### 自然語言指令範例
```
# 賽道選擇指令
"每次都在選擇賽道選擇上海"
"選擇賽道時固定選擇北京"

# 車輛選擇指令  
"在選擇車輛時固定選擇極速王者"
"選擇車輛流程依序選擇"

# 模式選擇指令
"在主選單隨機選擇選項"
```

### 程式架構
```
AutoTestBuilder
├── 配置分析器
│   ├── 遊戲狀態提取 (_extract_states)
│   ├── 按鍵定義提取 (_extract_keys)
│   └── UDP配置提取 (_extract_udp_config)
├── Q CLI 調用引擎
│   ├── 結構化提示詞建構
│   ├── 環境適配執行
│   └── 輸出格式修復
├── 程式碼處理器
│   ├── 程式碼提取 (_extract_code_from_output)
│   ├── 格式清理 (_clean_generated_code)
│   └── 語法驗證 (_validate_generated_code)
└── 日誌系統
    ├── 操作記錄
    └── 錯誤追蹤
```

## 執行流程

### 本地互動模式
1. **啟動互動介面** - 顯示指令提示
2. **接收用戶指令** - 解析自然語言測試參數
3. **動態分析配置** - 提取遊戲狀態和按鍵映射
4. **呼叫 Q CLI** - 生成定制化程式碼
5. **程式碼處理** - 清理和驗證生成的程式碼
6. **儲存結果** - 輸出 AutoTestAgent_Custom.py
7. **循環等待** - 繼續接收下一個指令

### GitHub Action 模式
1. **接收參數** - 從命令列獲取自然語言指令
2. **載入配置** - 讀取 GameSetting.md 和基礎 AutoTestAgent
3. **動態分析** - 提取遊戲相關配置信息
4. **生成程式碼** - 呼叫 Q CLI 生成定制化邏輯
5. **品質檢查** - 驗證程式碼語法和完整性
6. **輸出結果** - 產生最終測試工具

## 定制化邏輯實作

### 動態狀態匹配
```python
# 根據實際遊戲配置動態生成，current_flow_state欄位需要根據ProtoSchema\GameFlowData.proto的GameFlowData的流程名稱而定
if hasattr(game_data, 'current_flow_state') and game_data.current_flow_state == {state_value}:
    # 在指定狀態執行特定操作
    selected_key = "{target_key}"
    self.log(f"🎯 定制化邏輯: {user_instruction}")
else:
    # 其他狀態使用隨機輸入
    selected_key = random.choice(self.available_keys)
```

### 選項切換和判斷邏輯

#### 選項索引差異問題
- **枚舉索引** - GameSetting.md 中定義的枚舉值 (如 ETrack::LasVegas = 1)
- **UI 顯示索引** - 遊戲介面中的實際顯示順序 (可能從 0 開始)
- **選擇邏輯** - 需要根據實際遊戲行為確定按鍵操作次數

#### 選項導航策略
```python
# 策略 1: 基於目標索引的導航
target_index = {target_option_index}  # 目標選項的實際位置
current_index = game_data.{current_option_field}  # 當前選中的選項
if current_index < target_index:
    selected_key = "RIGHT"  # 或 "DOWN"
elif current_index > target_index:
    selected_key = "LEFT"   # 或 "UP"
else:
    selected_key = "START"  # 已在目標選項，確認選擇

# 策略 2: 重置到起始位置再導航
# 先回到第一個選項，再按指定次數移動到目標
selected_key = "LEFT"  # 多次按 LEFT 回到起始位置
# 然後按 RIGHT 移動到目標位置

# 策略 3: 直接確認 (適用於預設選項)
# 如果目標選項是預設選中的，直接確認
selected_key = "START"
```

#### 需要討論的問題
1. **索引對應關係** - 枚舉值與 UI 顯示順序的對應
2. **當前選項檢測** - 如何從 GameFlowData 中獲取當前選中的選項
3. **導航策略選擇** - 採用哪種導航方式最可靠
4. **邊界處理** - 選項列表的循環邏輯 (是否可以從最後一個跳到第一個)
5. **確認時機** - 何時發送 START 按鍵確認選擇

### 智能選項選擇邏輯

#### 目標選擇和導航
- **目標隨機化** - 為有操作邏輯的流程隨機選擇目標選項
- **導航控制** - 根據當前索引和目標索引輸出第一個 input 進行導航
- **邊界檢測** - 遊戲選項切到底後不會動，超過1秒索引不變則輸出另一個 input
- **目標確認** - 選到目標後等待1秒確認是否真的達到目標
- **輸入暫停** - 確認達到目標後停止輸入，直到流程切換

#### 實作邏輯
```python
# 智能選項選擇的核心邏輯
def handle_option_selection(self, game_data, flow_state, current_index, target_option):
    current_time = time.time()
    
    # 1. 檢查是否已達到目標
    if current_index == target_option:
        if not hasattr(self, 'target_reached_time'):
            self.target_reached_time = current_time
            return None  # 停止輸入
        elif current_time - self.target_reached_time > 1.0:
            return None  # 確認穩定，繼續停止輸入
    
    # 2. 檢查輸入頻率和索引變化
    if hasattr(self, 'last_input_time') and current_time - self.last_input_time < 1.0:
        if hasattr(self, 'last_index') and self.last_index == current_index:
            # 索引未變，可能到底了，切換方向
            return self.get_alternative_input(flow_state)
    
    # 3. 正常導航
    self.last_input_time = current_time
    self.last_index = current_index
    return self.get_navigation_input(flow_state, current_index, target_option)
```

### 按鍵映射生成
```python
# 動態生成按鍵映射
self.key_mapping = {
    "{key_name}": EInputKeyType.INPUT_KEY_{key_name},
    # ... 根據實際配置動態生成
}
```

## 品質要求

### 程式碼生成品質
- **語法正確性** - 確保生成的程式碼可執行
- **邏輯準確性** - 正確理解和實作用戶指令
- **狀態匹配精確** - 準確識別目標遊戲狀態
- **跨遊戲適配** - 支援不同遊戲配置

### 錯誤處理機制
- **WSL 格式修復** - 自動檢測和修復字符分行問題
- **程式碼驗證** - 完整的語法和邏輯檢查
- **回退機制** - 生成失敗時的處理策略
- **詳細日誌** - 完整的操作和錯誤記錄

---
建立時間: 2025-09-07
狀態: 實作完成
最後更新: 2025-09-07
