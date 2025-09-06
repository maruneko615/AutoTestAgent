# AutoTestAgent UML 說明文件 - Sample 通用模板版本

## 類別圖 (Class Diagram)

```mermaid
classDiagram
    %% 主程式類別
    class GameAutoTestAgent {
        -udp_manager: UDPManager
        -message_handler: MessageHandler
        -statistics_manager: StatisticsManager
        -state_manager: StateManager
        -target_parser: TargetParser
        -running: bool
        -session_id: str
        
        +__init__(server_url: str, requirement: str, enable_log: bool)
        +start() void
        +stop() void
        +_on_message(message: bytes) void
        +_on_error(error) void
        +_on_open() void
        +_on_close() void
    }

    %% 核心模組
    class UDPManager {
        -server_url: str
        -socket: socket
        
        +__init__(server_url: str)
        +connect(on_message: Callable, on_open: Callable, on_close: Callable, on_error: Callable) void
        +send_message(message_data: bytes) void
        +close() void
    }

    class MessageHandler {
        +__init__()
        +parse_message(message: bytes) dict
        +get_current_flow_state() int
        +get_field_value(field_name: str) Any
    }

    class StatisticsManager {
        -session_start_time: float
        -total_inputs_sent: int
        -total_messages_received: int
        -state_durations: dict
        
        +__init__()
        +start_session() void
        +end_session() void
        +record_input_sent() void
        +record_message_received() void
        +print_stats() void
    }

    %% 狀態管理模組
    class StateManager {
        -current_state: int
        -last_state: int
        -state_start_time: float
        -running: bool
        -targets: dict
        -state_handlers: dict
        
        +__init__()
        +update_game_state(game_data) void
        +generate_input() bytes
        +stop() void
        +set_targets(targets: dict) void
        +_handle_state_transition(from_state: int, to_state: int) void
    }

    %% 輸入生成模組
    class InputGenerator {
        +__init__()
        +generate_key_input(keys: List[int], is_key_down: bool) bytes
        +generate_complex_input(digital_keys: List[int], is_key_down: bool, analog_inputs: dict) bytes
        +create_vr_input(vr_type: int, value: float) object
    }

    class RandomInputGenerator {
        -last_input_time: float
        -input_interval: float
        -random_keys_pool: List[int]
        
        +__init__()
        +generate_input() bytes
        +generate_basic_input() bytes
        +generate_start_input() bytes
    }

    class TargetedInputGenerator {
        -target_keys: List[int]
        -input_frequency: float
        
        +__init__()
        +generate_input() bytes
        +generate_left_input() bytes
        +generate_right_input() bytes
        +generate_start_input() bytes
        +generate_confirm_input() bytes
    }

    %% 狀態處理器基類
    class BaseStateHandler {
        <<abstract>>
        -state_name: str
        -state_value: int
        -targets: dict
        -random_generator: RandomInputGenerator
        -targeted_generator: TargetedInputGenerator
        
        +__init__(state_name: str, state_value: int)
        +can_handle(state: int) bool
        +handle_state(state: int, game_data: Any) bytes
        +set_targets(targets: dict) void
        +reset_state() void
        +handle_random_input(game_data: Any) bytes
    }

    class BaseSelectionStateHandler {
        <<abstract>>
        -last_value_change_time: float
        -last_tracked_value: Any
        -current_search_direction: str
        -STUCK_THRESHOLD: float
        -DEFAULT_SEARCH_DIRECTION: str
        
        +__init__()
        +get_state_name() str
        +get_supported_state() int
        +check_stuck_and_switch_direction(current_value: Any, value_name: str) bool
        +reset_search_state() void
        +set_targets(targets: dict) void
    }

    %% 具體狀態處理器 (框架功能展示)
    class GenericStateHandler {
        +__init__()
        +can_handle(state: int) bool
        +handle_state(game_data: Any) bytes
        +handle_random_input(game_data: Any) bytes
        +handle_basic_input(game_data: Any) bytes
        +reset_state() void
    }

    class SelectionStateHandler {
        +__init__()
        +can_handle(state: int) bool
        +handle_state(game_data: Any) bytes
        +get_state_name() str
        +get_supported_state() int
        +check_stuck_and_switch_direction(current_value: Any) bool
        +reset_search_state() void
        +set_targets(targets: dict) void
    }

    %% 配置模組
    class GameConfig {
        +GameFlowState: class
        +InputKeyType: class
        +VrInputType: class
        +STATE_NAMES: dict
        +INPUT_MAPPINGS: dict
    }

    class TargetParser {
        -fixed_targets: dict
        -option_mappings: dict
        
        +__init__()
        +parse_requirement(requirement: str) dict
        +get_target_summary() str
    }

    %% 關係定義
    GameAutoTestAgent --> UDPManager : uses
    GameAutoTestAgent --> MessageHandler : uses
    GameAutoTestAgent --> StatisticsManager : uses
    GameAutoTestAgent --> StateManager : uses
    GameAutoTestAgent --> TargetParser : uses

    StateManager --> BaseStateHandler : manages
    StateManager --> BaseSelectionStateHandler : manages

    BaseStateHandler --> RandomInputGenerator : uses
    BaseStateHandler --> TargetedInputGenerator : uses

    BaseSelectionStateHandler --> TargetedInputGenerator : uses

    BaseStateHandler <|-- GenericStateHandler : inherits
    BaseSelectionStateHandler <|-- SelectionStateHandler : inherits

    TargetedInputGenerator --|> InputGenerator : inherits
    RandomInputGenerator --> InputGenerator : uses

    StateManager --> GameConfig : uses
    TargetParser --> GameConfig : uses
```

## 流程圖 (Flowchart) - 框架執行流程

```mermaid
flowchart TD
    A[啟動程式] --> B[建立 UDP 連線]
    B --> C[等待遊戲訊息]
    
    C --> D[收到訊息]
    D --> E[解析遊戲狀態]
    E --> F[更新狀態管理器]
    
    F --> G{什麼類型的狀態?}
    G -->|一般狀態| H[使用隨機輸入]
    G -->|選擇狀態| I[使用目標輸入]
    
    H --> J[生成輸入指令]
    I --> J
    
    J --> K[發送指令給遊戲]
    K --> L[記錄統計]
    L --> C
    
    C --> M{收到停止信號?}
    M -->|是| N[關閉連線]
    M -->|否| D
    N --> O[結束程式]
```

## 序列圖 (Sequence Diagram) - 通用執行流程

```mermaid
sequenceDiagram
    participant Main as main()
    participant Agent as GameAutoTestAgent
    participant UM as UDPManager
    participant MH as MessageHandler
    participant SM as StateManager
    participant SH as StateHandler
    participant IG as InputGenerator

    Main->>Agent: 創建實例(udp_url, session_id)
    Agent->>UM: 初始化 UDP
    Agent->>MH: 初始化訊息處理器
    Agent->>SM: 初始化狀態管理器
    
    Main->>Agent: start()
    Agent->>UM: connect()
    UM->>Agent: _on_message() 回調
    Agent->>SM: 開始狀態監控
    
    loop UDP 連線期間
        UM->>Agent: _on_message(message)
        Agent->>MH: parse_message(message)
        MH->>Agent: 返回遊戲狀態資料
        
        Agent->>SM: update_state(state, data)
        SM->>SM: 檢查狀態轉換
        
        alt 狀態轉換發生
            SM->>SH: reset_state() 重置舊狀態
            SM->>SM: 載入新狀態處理器
        end
        
        Agent->>SM: generate_input()
        SM->>SH: handle_state(game_data)
        
        alt 選擇狀態
            SH->>SH: 檢查是否卡住
            SH->>SH: 檢查是否達到目標
            SH->>IG: generate_targeted_input()
        else 通用狀態
            SH->>IG: generate_random_input()
        end
        
        IG->>SH: 返回輸入指令
        SH->>SM: 返回輸入指令
        SM->>Agent: 返回輸入指令
        
        Agent->>UM: send_message(input)
    end
    
    Main->>Agent: 接收停止信號
    Agent->>SM: stop()
    Agent->>UM: close()
```


## 組件圖 (Component Diagram) - 通用架構

```mermaid
flowchart TB
    subgraph "Sample - 通用模板版本"
        subgraph "主程式 (main.py)"
            MAIN[GameAutoTestAgent<br/>主控制器]
        end
        
        subgraph "核心模組 (core/)"
            UM[UDPManager<br/>UDP Socket 連線管理]
            MH[MessageHandler<br/>Protobuf 訊息解析]
            SM_STATS[StatisticsManager<br/>統計資料管理]
        end
        
        subgraph "流程管理 (flow/)"
            SM[StateManager<br/>狀態管理器]
        end
        
        subgraph "輸入生成 (input/)"
            IG[InputGenerator<br/>基礎輸入生成]
            RIG[RandomInputGenerator<br/>隨機輸入生成]
            TIG[TargetedInputGenerator<br/>目標導向輸入]
        end
        
        subgraph "狀態處理 (states/) - 可擴展"
            BSH[BaseStateHandler<br/>狀態處理基類]
            BSSH[BaseSelectionStateHandler<br/>選擇狀態基類]
            
            subgraph "框架功能展示"
                GSH[GenericStateHandler<br/>通用狀態處理]
                SSH[SelectionStateHandler<br/>選擇狀態處理]
            end
        end
        
        subgraph "配置管理 (config/)"
            GC[game_config.py<br/>遊戲配置]
            TP[target_parser.py<br/>目標解析器]
        end
    end
    
    subgraph "外部系統"
        GAME[遊戲程式<br/>UDP Server]
        PROTO[ProtoSchema 檔案<br/>InputCommand.proto<br/>GameFlowData.proto]
    end
    
    %% 連接關係
    MAIN --> UM
    MAIN --> MH
    MAIN --> SM_STATS
    MAIN --> SM
    MAIN --> TP
    
    UM <--> GAME
    MH --> PROTO
    SM --> BSH
    SM --> BSSH
    BSH --> GSH
    BSSH --> SSH
    
    BSH --> RIG
    BSH --> TIG
    BSSH --> TIG
    TIG --> IG
    RIG --> IG
    
    SM --> GC
    TP --> GC
```

## 📝 Sample 通用模板架構特色說明

### 🎯 **通用模板設計**
- **可擴展狀態處理器**: 基礎狀態處理器可根據需要擴展
- **通用配置**: 支援任何遊戲的配置和選項
- **完整測試**: 支援目標導向和隨機測試模式

### 🔧 **模組化設計**
- **BaseStateHandler**: 通用狀態處理基類
- **BaseSelectionStateHandler**: 選擇狀態專用基類
- **繼承架構**: 清晰的繼承關係和職責分離

### 🚀 **輸入生成系統**
- **InputGenerator**: 基礎輸入生成功能
- **TargetedInputGenerator**: 繼承 InputGenerator，提供目標導向輸入
- **RandomInputGenerator**: 使用 InputGenerator，提供隨機輸入

### 🎮 **通用遊戲支援**
- **可配置狀態覆蓋**: 根據 Proto 定義生成所有狀態
- **智能選擇邏輯**: 通用的選擇導航和卡住檢測
- **靈活配置**: 支援任何遊戲的選項和名稱映射

### 🧪 **模板級品質**
- **錯誤處理**: 完整的異常處理機制
- **統計功能**: 詳細的執行統計和報告
- **日誌系統**: 完整的執行日誌記錄
- **目標解析**: 靈活的測試目標設定

這個 UML 設計展現了 Sample 作為一個通用的、可擴展的遊戲自動測試模板，具備完整的架構設計和靈活的配置能力。

---

## 📝 Sample 通用模板特色

### 🔧 **模板化設計**
- **基礎狀態處理器**: 提供通用的狀態處理邏輯
- **選擇狀態基類**: 專門處理選擇流程的智能邏輯
- **配置驅動**: 所有遊戲特定內容通過配置定義

### 🎯 **核心架構優勢**
- **繼承設計**: TargetedInputGenerator 繼承 InputGenerator
- **模組化**: 每個狀態獨立處理器
- **可擴展**: 易於添加新狀態或修改邏輯
- **通用性**: 適用於任何遊戲類型

### 📊 **與具體實作的關係**
| 項目 | Sample (通用模板) | 具體遊戲版本 |
|------|------------------|-------------|
| **狀態處理器** | 基礎類別和範例 | 完整具體處理器 |
| **配置完整性** | TODO 標記 | 完整遊戲配置 |
| **輸入生成** | 繼承模式 | 繼承模式 |
| **測試就緒** | 需要轉換 | 立即可用 |

Sample 代表了 AutoTestAgent 架構的通用模板，是所有具體遊戲版本的基礎參考。
