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


