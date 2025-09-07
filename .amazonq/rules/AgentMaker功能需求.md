# AgentMaker 功能需求規格

## 工具概述
AgentMaker 是使用 Q CLI 根據配置文件和 Protobuf Schema 生成 AutoTestAgent 程式碼的工具。

## 核心功能

### 輸入文件分析
- 讀取 `GameSetting\AutoTest_Game_Setting.md` 遊戲配置
- 分析 `ProtoSchema\GameFlowData.proto` 遊戲流程數據定義
- 分析 `ProtoSchema\InputCommand.proto` 輸入指令定義
- 驗證所有必要文件存在性

### 動態分析能力
- **遊戲狀態提取** - 從 GameSetting.md 提取狀態定義
- **按鍵映射分析** - 從 InputCommand.proto 動態提取實際按鍵
- **按鍵屏蔽處理** - 智能對應 GameSetting.md 中的按鍵名稱到實際枚舉
- **UDP 配置解析** - 提取連線參數（IP、Port）
- **跨遊戲適配** - 無論 Proto 內容如何變化都能自動適配

### 智能選項選擇
- **目標隨機化** - 為有操作邏輯的流程隨機選擇目標選項
- **導航邏輯** - 根據當前索引和目標索引進行智能導航
- **邊界處理** - 檢測選項到底的情況並切換方向
- **穩定性確認** - 達到目標後等待1秒確認穩定性
- **輸入頻率控制** - 避免過於頻繁的輸入操作

### 程式碼生成
- **Q CLI 整合** - 呼叫 Amazon Q CLI 生成程式碼
- **提示詞建構** - 根據分析結果建立動態提示詞
- **程式碼品質檢查** - 驗證生成的程式碼語法正確性
- **Windows 專用優化** - 生成適合 Windows 環境的程式碼

## 技術規格

### 執行環境
- **平台**: Windows 10/11
- **Python**: 3.8+
- **依賴**: Amazon Q CLI

### 輸出規格
- **檔案**: AutoTestAgent.py
- **特性**: 
  - UDP 通訊功能
  - 動態按鍵映射
  - 動態日誌系統 (使用 game_data.DESCRIPTOR.fields 遍歷所有欄位)
  - 持續監聽與自動重連
  - Windows 友善的錯誤處理

### 關鍵特色
- **配置驅動** - 完全基於輸入文件生成程式碼
- **動態適配** - 自動分析 Proto 文件結構
- **智能按鍵映射** - 提取實際可用按鍵
- **品質保證** - 內建程式碼驗證機制

## 執行流程

1. **文件驗證** - 檢查所有輸入文件存在
2. **配置分析** - 解析 GameSetting.md
3. **Schema 分析** - 動態分析 Proto 文件
4. **提示詞建構** - 根據分析結果建立 Q CLI 提示
5. **程式碼生成** - 呼叫 Q CLI 生成 AutoTestAgent
6. **品質檢查** - 驗證生成程式碼的正確性
7. **輸出儲存** - 儲存最終的 AutoTestAgent.py

## 錯誤處理
- 輸入文件缺失檢測
- Proto 文件格式驗證
- Q CLI 執行失敗處理
- 生成程式碼語法檢查

---
建立時間: 2025-09-07
狀態: 已實作並測試
