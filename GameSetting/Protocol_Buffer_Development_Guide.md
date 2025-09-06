# 自動測試 Protocol Buffer 開發文件

## 概述
本文件定義了遊戲自動測試框架的Protocol Buffer結構，用於遊戲狀態追蹤和輸入命令傳輸。
Protocol Buffer文件會根據`AutoTest_Game_Setting.md`的內容自動生成，不需要手動維護。

## 架構設計
系統分為兩個主要的proto文件：
- `GameFlowData.proto` - 遊戲狀態和流程數據
- `InputCommand.proto` - 輸入命令和控制

## 自動生成流程
- 自動解析`AutoTest_Game_Setting.md`中的枚舉定義
- 生成對應的Protocol Buffer結構
- 支援遊戲狀態、輸入按鍵、VR輸入和遊戲選項的動態配置

## GameFlowData.proto

### 主要訊息結構
```protobuf
message GameFlowData {
  EGameFlowState current_state = 1;
  GameSelections selections = 2;
}
```

### 動態生成內容
- `EGameFlowState` - 根據設定文件中的遊戲狀態枚舉生成
- 各種遊戲選項枚舉 - 根據設定文件中的選項定義生成
- `GameSelections` - 包含所有遊戲選項的訊息結構

## InputCommand.proto

### 輸入命令結構
```protobuf
message InputCommand {
  repeated EInputKeyType active_keys = 1;
  repeated VrInput vr_inputs = 2;
}

message VrInput {
  EInputVrType type = 1;
  float value = 2;
}
```

### 動態生成內容
- `EInputKeyType` - 根據設定文件中的按鍵定義生成
- `EInputVrType` - 根據設定文件中的VR輸入定義生成

## 設計原則

### 輸入處理策略
- **空陣列設計**: 沒有操作時傳送空陣列，避免傳送false值
- **按需傳輸**: 只傳送當前激活的按鍵和有數值變化的VR輸入
- **同時多輸入**: 支援同時按下多個按鍵的場景

### 動態配置優勢
- **遊戲無關**: 不綁定特定遊戲，可適用於不同專案
- **自動同步**: Protocol Buffer結構自動與設定文件同步
- **易於維護**: 只需修改設定文件，proto文件自動更新

## 使用範例

### 遊戲狀態更新
```protobuf
GameFlowData {
  current_state: SELECTMODE
  selections {
    game_mode: LOCALVERSUS
    track: BEIJING
    route_direction: CLOCKWISE
  }
}
```

### 輸入命令範例
```protobuf
// 同時按下開始鍵和氮氣
InputCommand {
  active_keys: [START, NITRO]
  vr_inputs: []
}

// VR輸入範例
InputCommand {
  active_keys: []
  vr_inputs: [
    {type: STEER, value: 0.5}
  ]
}

// 沒有操作時
InputCommand {
  active_keys: []
  vr_inputs: []
}
```

## 技術規格
- Protocol Buffer版本: proto3
- 編碼格式: 二進制
- 生成語言: Python 3
- 目標平台: 跨平台測試環境

## 開發注意事項
- 修改遊戲配置時，需重新執行生成器
- 枚舉命名遵循protobuf慣例 (UPPER_CASE)
- 生成的proto文件不應手動編輯
- 新增遊戲選項時，需在設定文件中定義對應的枚舉
