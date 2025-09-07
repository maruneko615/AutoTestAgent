# 遊戲規格說明文件

## 概述

本文件包含 專案的具體規格資訊，包括遊戲狀態定義、選項配置、通訊協定參數等。此文件需配合 [通用自動測試框架模板](./AutoTest_Framework_Template.md) 使用。

---

## 🎮 遊戲狀態定義
有中文註解就補上，能增加AI分析使用者指令的精確度

### 1. 狀態列舉 
#### 1.1 遊戲流程 

```cpp
enum class EGameFlowState : uint8
{
    Copyright = 0,
    Warning,
    Logo,
    PV,
    // 投幣頁
    CoinPage,
    // 選擇車輛
    SelectBike,
    // 選擇場景
    SelectScene,
    Race,
    RaceEnd,
    GameOver,
    Ranking,
    Promotion,
    AccountEntry,
    // 選擇頭套
    PhotoAuth,
    // 選擇模式
    SelectMode,
    PayForLevel,
    RideShow,
    LoadFlow,
    LoadGame,
    Cutscene,
	// 跨店對戰擊敗演出
    MapBeatShow,
    SignName,
    Continue,
    HardwareDetect,
    LoadContinue,
    LoadStandby,
    OperatorSetting,
    AirspringAdjust,
	// 玩家註冊簽名
    PlayerRegistration,
    WarningForSelection,
	// 對戰地圖
	BattleMap,
	M23_Read,
	// 衝線演出
	RaceFinishShow,
	//玩家資料頁
	PlayerInfo,
	// 本地對戰演出
	LocalBeatShow,
	AgentLogo,
	UELogo,
	CriwareLogo,
	// 靜態CoinPage
	StaticCoinPage,
	//載結算景
	LoadRaceResult,
    MAX
};

```
#### 1.2 輸入按鍵定義

```cpp
enum class EInputKeyType: uint8
{
    // 向上選
	Up = 0,  
    // 向下選           
	Down,
    // 向左選
	Left,
    // 向右選
	Right,
    // 確認
	Start,
    // 確認、氮氣
	Nitro,
	Test,
	Service,
    // 投幣
	Coin,
	// Motion Stop
	Emergency,
	LeftLeg,
	RightLeg,
	// Lean over
	SpeedUp,
	LeftMachine,
	SeatDetact,
	MAX
};

enum class EInputVrType: uint8
{
	Throttle = 0,
	RightBrake,
	LeftBrake,
	Steer,
	MAX
};
```

---

## 🎯 SR4 流程詳細規格

### 2. 需要操作的流程

#### 2.1 投幣頁 (EGameFlowState::CoinPage)

**按鍵操作**：
- Coin、Nitro

#### 2.2 選擇模式 (EGameFlowState::SelectMode)

**按鍵操作**：
- Left、Right、Start

**操作邏輯**：
- EGameMode：Left、Right

**選項內容**：
```cpp
enum EGameMode
{
    LocalVersus,
    GlobalVersus,
}
```

#### 2.3 選擇頭套 (EGameFlowState::PhotoAuth)

**按鍵操作**：
- Left、Right、Start

**操作邏輯**
- EPhotoType：Left、Right

**選項內容**：
```cpp
enum class EPhotoType:uint8
{
	/**
	 * 安全帽
	 */
	Helmet,
	/**
	 * 面紗
	 */
	Veil,
	/**
	 * 潛水眼罩
	 */
	DivingGoggles,
	/**
	 * 面罩
	 */
	FaceMask,
	/**
	 * 漫畫面罩
	 */
	ComicMask,
	/**
	 * 海妖
	 */
	SeaElf,
	/**
	 * 騎士頭盔
	 */
	KnightHelmet,
	/**
	 * Emoji面罩
	 */
	EmojiMask,
	/**
	 * 動物頭套
	 */
	DollHeadgear,
	/**
	 * 川劇臉譜
	 */
	SichuanOperaMakeUp,
	/**
	 * 摺紙面罩
	 */
	Origami,
	/**
	 * 舞獅
	 */
	LionDance,
};
```

---

#### 2.4 賽道選擇流程 (EGameFlowState::SelectScene)

**按鍵操作**：
- Left、Right、Start

**操作邏輯**
- ETrack：Left、Right

**選項內容**：
```cpp
enum class ETrack : uint8
{
    None = 0,
    LasVegas,
    Beijing,
    Seoul,
    Shanghai,
    Thailand,
    Chongqing,
    PhysicsTest,
    PhysicsTest_2,
    DeliaHuangTest,
    ShouWeikuTest,
    MAX
};

```
**按鍵操作**：
- Up、Down

**操作邏輯**
- ERouteDirection：Up、Down

**選項內容**：
UENUM(BlueprintType)
enum class ERouteDirection : uint8
{
    ClockWise,
    CounterClockWise,
    MAX
};

---

#### 2.5 車輛選擇流程 (EGameFlowState::SelectBike)

**按鍵操作**：
- Left、Right、Start

**操作邏輯**
- EVehicleType：Left、Right

**選項內容**：
```cpp
enum class EVehicleType : uint8
{
    /**
     * 極速王者
     */
    Msq,
    /**
     * 時空行者
     */
    Maa,
    /**
     * 萬能天使
     */
    Mur,
    /**
     * 加速冠軍
     */
    Mha,
    /**
     * 彎道女王
     */
    Mra,
    /**
     * 越野達人
     */
    Mad,
    /**
     * 電光喵喵
     */
    Mce,
    /**
     * 未來特工
     */
    Mqb,
    Max
};
```

## 🔌 數值設定

### 1. UDPSocket 連線參數

```python
# 特定連線設定
UDPSOCKET_URL = "udp://127.0.0.1:8587"
```
### 2. 特定參數

```python
# 卡住檢測參數
STUCK_THRESHOLD = 1.0                    # 卡住檢測閾值（秒）
DEFAULT_SEARCH_DIRECTION = 'right'       # 預設搜尋方向
TARGET_REACHED_DELAY = 1.0               # 目標達成延遲時間（秒）

```
