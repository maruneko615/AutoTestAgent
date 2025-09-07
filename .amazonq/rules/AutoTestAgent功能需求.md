# AutoTestAgent 功能需求規格

## 工具概述
AutoTestAgent 是由 AgentMaker 生成的 UDP 通訊程式，實現與 Unreal 遊戲的遠端操控。

## 核心功能

### UDP 通訊模組
- **建立 UDP Socket 連線** - 連接到遊戲端指定端口
- **角色註冊機制** - 發送 "role:agent" 並等待 "ok:agent" 確認
- **持續監聽** - 接收 GameFlowData 訊息
- **自動重連** - 連線中斷時每 5 秒重試
- **優雅關閉** - 支援 Ctrl+C 中斷

### 遊戲狀態處理
- **動態狀態匹配** - 根據 GameFlowData.current_flow_state 處理
- **隨機輸入生成** - 預設行為，確保遊戲持續運行
- **按鍵映射** - 使用 EInputKeyType 枚舉發送正確按鍵
- **輸入指令封裝** - 生成完整的 InputCommand 訊息

### 日誌系統
- **即時記錄** - 每個 frame 的接收和發送都記錄
- **動態欄位顯示** - 根據 GameFlowData 實際欄位動態顯示
- **分隔線標記** - 每次操作後加分隔線
- **雙重輸出** - 同時輸出到控制台和 AutoTestAgent.log

## 技術規格

### 執行環境
- **平台**: Windows 10/11 專用
- **Python**: 3.8+
- **依賴**: protobuf

### 通訊協定
- **接收**: GameFlowData (Protobuf over UDP)
- **發送**: InputCommand (Protobuf over UDP)
- **連線**: 127.0.0.1:8587 (可配置)

### 程式架構
```
AutoTestAgent
├── UDP 通訊模組
│   ├── Socket 管理
│   ├── 角色註冊
│   └── 自動重連
├── 狀態處理器
│   ├── 動態狀態匹配
│   └── 隨機輸入生成
├── 日誌系統
│   ├── 即時記錄
│   └── 檔案輸出
└── 主控制器
    ├── 模組協調
    └── 錯誤處理
```

## 執行流程

1. **初始化階段**
   - 載入 Protobuf 模組
   - 建立按鍵映射
   - 初始化日誌系統

2. **連線階段**
   - 建立 UDP Socket
   - 角色註冊 ("role:agent")
   - 等待確認 ("ok:agent")

3. **運行循環**
   - 接收 GameFlowData
   - 記錄所有欄位
   - 生成隨機輸入
   - 發送 InputCommand
   - 記錄發送內容

4. **錯誤處理**
   - 連線中斷重連
   - Protobuf 解析錯誤
   - 優雅程式退出

## Windows 專用特性
- **多執行緒架構** - 使用 threading 模組
- **視窗保持機制** - 程式結束時等待 Enter
- **路徑處理** - 使用 os.path.join() 處理 Windows 路徑
- **友善錯誤提示** - 詳細的錯誤訊息和解決建議

## 品質要求
- **穩定性** - 長時間運行不崩潰
- **即時性** - 快速響應遊戲狀態變化
- **可讀性** - 清晰的日誌輸出
- **可維護性** - 模組化設計

---
建立時間: 2025-09-07
狀態: 已實作並測試
