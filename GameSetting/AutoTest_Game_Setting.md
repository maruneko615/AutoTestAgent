# 遊戲規格說明文件

## 概述

本文件包含 **[GAME_NAME]** 專案的具體規格資訊，包括遊戲狀態定義、選項配置、通訊協定參數等。此文件需配合 [通用自動測試框架模板](./AutoTest_Framework_Template.md) 使用。

---

## 🎮 遊戲狀態定義

### 1. 狀態列舉 
#### 1.1 遊戲流程 

```cpp
enum class EFlowName : uint8
{
    Flow1 = 0,
    Flow2 = 1,
    Flow3 = 2,
    Flow4 = 3,
    Flow5 = 4,
    Flow6 = 5,
    MAX
};
```

#### 1.2 輸入按鍵定義

```cpp
enum class EKeyName: uint8
{
    Key1 = 0,
    Key2 = 1,
    Key3 = 2,
    Key4 = 3,
    Key5 = 4,
    Key6 = 5,
    Key7 = 6,
    MAX
};
```

---

## 🎯 遊戲流程詳細規格

### 2. 需要操作的流程

#### 2.1 狀態1 (EFlowName::Flow1)

**按鍵操作**：
- Key1、Key2、Key5

**操作邏輯**：
- EOption1：Key1、Key2 

**選項內容**：
```cpp
enum EOption1
{
    Option1_1 = 0,
    Option1_2 = 1,
    Option1_3 = 2
}
```

#### 2.2 狀態2 (EFlowName::Flow2)

**按鍵操作**：
- Key3、Key4、Key5、Key6

**操作邏輯**：
- EOption2：Key3、Key4 切換選項

**選項內容**：
```cpp
enum class EOption2 : uint8
{
    Option2_1 = 0,
    Option2_2 = 1,
    Option2_3 = 2,
    Option2_4 = 3,
    MAX
};
```

---

## 🔌 數值設定

### 1. UDPSocket 連線參數

```python
# 連線設定
UDPSOCKET_URL = "udp://[IP_ADDRESS]:[PORT]"
```


