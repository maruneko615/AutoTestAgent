# Sample 到 Sample_Agent 轉換器設計文件

## 🎯 轉換目的

將通用的 `Sample` 模板轉換成遊戲專案特定的 `Sample_Agent` 版本。

- **輸入**: Sample 通用模板（包含 TODO 標記）
- **輸出**: 遊戲專用的 Sample_Agent 版本
- **用途**: 從通用 AutoTestAgent 模板生成特定遊戲的測試代理

## 📋 轉換內容

### 1. Proto 配置轉換

#### 1.1 InputCommand 轉換
**目標**: 根據 `ProtoSchema/InputCommand.proto` 生成輸入配置

**轉換檔案**:
- `config/game_config.py` - 替換 InputKeyType 和 VrInputType 的 TODO 標記
- `input/input_generator.py` - 替換 InputCommand 創建邏輯的 TODO 標記
- `input/targeted_input.py` - 替換目標導向輸入的 TODO 標記
- `input/random_input.py` - 替換隨機輸入的 TODO 標記

#### 1.2 GameFlowData 轉換
**目標**: 根據 `ProtoSchema/GameFlowData.proto` 生成遊戲狀態配置

**轉換檔案**:
- `config/game_config.py` - 替換 GameFlowState 和選項枚舉的 TODO 標記
- `config/target_parser.py` - 替換遊戲特定選項映射的 TODO 標記
- `flow/state_manager.py` - 替換狀態管理邏輯的 TODO 標記

### 2. 狀態處理器生成

#### 2.1 具體狀態處理器
**基於**: `states/base_state_handler.py` 和 `states/base_selection_state.py`

**生成策略**:
- 為每個遊戲狀態創建對應的處理器檔案
- 選擇狀態繼承 BaseSelectionStateHandler
- 通用狀態繼承 BaseStateHandler

### 3. 主程式配置

#### 3.1 遊戲特定參數
**更新檔案**:
- `main.py` - 替換 UDP 連線參數和遊戲特定設定

## 📝 轉換規則

### TODO 標記替換
Sample 中包含約 93 個 TODO 標記，主要類型：

- `# TODO: 🔧 來源: InputCommand.proto` → 實際的輸入配置
- `# TODO: 🔧 來源: GameFlowData.proto` → 實際的遊戲狀態配置
- `# TODO: 根據遊戲需求實作` → 具體的遊戲邏輯

### 檔案結構保持
- 保持 Sample 的目錄結構
- 保持模組匯入關係
- 保持繼承架構

### 配置驅動
- 所有遊戲特定內容通過 Proto 定義生成
- 支援不同遊戲的 Proto 結構
- 靈活的選項映射機制

## 🧪 轉換驗證

### 基本驗證
- Python 語法正確性檢查
- 模組匯入功能測試
- 基本執行能力驗證

### 功能驗證
- 與對應遊戲的 Sample_XXX 版本功能一致
- 所有 TODO 標記已正確替換
- 配置檔案完整性檢查

## 📊 轉換結果

### 成功指標
- ✅ 所有 TODO 標記已替換
- ✅ Python 語法正確
- ✅ 模組匯入成功
- ✅ 基本功能運行

### 輸出結構
```
Sample_Agent/
├── config/
│   ├── game_config.py      # 完整遊戲配置
│   ├── target_parser.py    # 遊戲特定解析
│   └── dynamic_game_config.py  # 動態配置
├── core/                   # 核心模組（不變）
├── flow/
│   └── state_manager.py    # 狀態管理邏輯
├── input/                  # 輸入生成模組
├── states/                 # 狀態處理器（擴展）
└── main.py                 # 主程式
```

## 🔄 轉換流程

### 手動轉換步驟
1. **複製 Sample 目錄** 到新的遊戲專用目錄
2. **分析 Proto 檔案** 提取遊戲特定的枚舉和結構
3. **替換 TODO 標記** 使用實際的遊戲配置
4. **生成狀態處理器** 為每個遊戲狀態創建處理器
5. **驗證轉換結果** 確保語法正確和功能完整

### 轉換重點
- 專注於 TODO 標記的準確替換
- 確保與現有 Sample_XXX 版本的一致性
- 保持 Sample 的架構設計不變

---

**📝 版本資訊**:
- **文件版本**: 3.0
- **更新日期**: 2025-01-27
- **適用範圍**: Sample 通用模板轉換
- **維護者**: AutoTest 開發團隊
