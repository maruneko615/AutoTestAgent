@echo off
echo ========================================
echo QCLI Step 3: Game Logic Implementation
echo ========================================
echo.

echo Step 1: Copy Sample_Step2 to Sample_Step3...

if not exist "Sample_Step2" (
    echo [ERROR] Sample_Step2 directory not found
    echo Please run step1 and step2 first
    pause
    exit /b 1
)

if exist "Sample_Step3" (
    echo Removing existing Sample_Step3...
    rmdir /s /q "Sample_Step3" 2>nul
    timeout /t 2 >nul
)

echo Copying Sample_Step2 to Sample_Step3...
xcopy "Sample_Step2" "Sample_Step3" /E /I /H /Y /Q

if errorlevel 1 (
    echo [ERROR] Copy failed
    pause
    exit /b 1
)

echo Copy completed successfully!
echo.

echo Step 2: Check game setting file...
if not exist ".amazonq\rules\AutoTest_Game_Setting.md" (
    echo [ERROR] Game setting file not found
    pause
    exit /b 1
)

echo Game setting file found!
echo.

echo Step 3: Check WSL availability...
wsl --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] WSL not found, please install it.
    pause
    exit /b 1
)
echo WSL available!
echo.

echo Step 4: Create transformation prompt...

echo Analyze .amazonq/rules/AutoTest_Game_Setting.md file completely, > prompt.txt
echo then implement complete game logic in Sample_Step3 directory. >> prompt.txt
echo. >> prompt.txt
echo TASK 1: Generate All State Handler Files >> prompt.txt
echo Based on section 1.1 game flow in AutoTest_Game_Setting.md: >> prompt.txt
echo - Read all AutoTest_Game_Setting.md enum values from the game setting file >> prompt.txt
echo - File naming pattern: state_name_state.py for each EGameFlowState value >> prompt.txt
echo - CRITICAL: Use snake_case for file names with underscores between words >> prompt.txt
echo - CRITICAL: Use PascalCase for class names matching the file pattern >> prompt.txt
echo - Example: RaceEnd becomes race_end_state.py with RaceEndStateHandler class >> prompt.txt
echo - Example: SelectBike becomes select_bike_state.py with SelectBikeStateHandler class >> prompt.txt
echo - Each state handler should inherit from BaseStateHandler >> prompt.txt
echo - Implement basic state handling with generic input generation >> prompt.txt
echo - Use the state names and IDs from the game setting file >> prompt.txt
echo. >> prompt.txt
echo TASK 2: Implement Special Operation Logic >> prompt.txt
echo Based on section 2 operation flows in AutoTest_Game_Setting.md: >> prompt.txt
echo - Identify which states require special input operations >> prompt.txt
echo - For each special operation state, enhance the corresponding state handler >> prompt.txt
echo - Add specific button operation logic as defined in the game setting >> prompt.txt
echo - Add selection navigation Left Right Up Down as specified >> prompt.txt
echo - Add confirmation logic with Start button >> prompt.txt
echo - Add special buttons like Coin Nitro as required >> prompt.txt
echo - Add stuck detection direction switching delay confirmation >> prompt.txt
echo - Handle game-specific selection options and enums >> prompt.txt
echo. >> prompt.txt
echo TASK 3: Update Core Modules >> prompt.txt
echo - Update Sample_Step3/flow/state_manager.py to register ALL generated state handlers >> prompt.txt
echo - CRITICAL: ABSOLUTELY DO NOT modify ANY existing function names, signatures, or implementations >> prompt.txt
echo - CRITICAL: ABSOLUTELY DO NOT change update_game_state to update_state or any other name >> prompt.txt
echo - CRITICAL: ABSOLUTELY DO NOT modify any existing method parameters or return types >> prompt.txt
echo - CRITICAL: ONLY ADD new import statements and state handler registrations >> prompt.txt
echo - CRITICAL: PRESERVE ALL existing code structure and logic completely unchanged >> prompt.txt
echo - CRITICAL: Import statements must match exact file names and class names >> prompt.txt
echo - CRITICAL: Use snake_case file names in import statements >> prompt.txt
echo - Example: from states.race_end_state import RaceEndStateHandler >> prompt.txt
echo - Example: from states.select_bike_state import SelectBikeStateHandler >> prompt.txt
echo - Update Sample_Step3/config/target_parser.py with game-specific option mappings >> prompt.txt
echo - Update Sample_Step3/main.py UDP URL from game setting parameters >> prompt.txt
echo - Replace all remaining TODO markers with actual implementations >> prompt.txt
echo. >> prompt.txt
echo TASK 4: Configure Parameters >> prompt.txt
echo Based on parameters section in AutoTest_Game_Setting.md: >> prompt.txt
echo - Extract and set UDP connection parameters >> prompt.txt
echo - Configure timing parameters like STUCK_THRESHOLD TARGET_REACHED_DELAY >> prompt.txt
echo - Set default search direction and other behavioral parameters >> prompt.txt
echo - Apply all numerical settings from the game setting file >> prompt.txt
echo. >> prompt.txt
echo CRITICAL REQUIREMENTS: >> prompt.txt
echo - Dynamically read and parse the entire AutoTest_Game_Setting.md file >> prompt.txt
echo - Generate state handlers for ALL game states not just specific ones >> prompt.txt
echo - CRITICAL: Follow consistent naming conventions throughout >> prompt.txt
echo - CRITICAL: File names must use snake_case with underscores >> prompt.txt
echo - CRITICAL: Class names must use PascalCase matching file pattern >> prompt.txt
echo - CRITICAL: Import statements must match exact file and class names >> prompt.txt
echo - CRITICAL: NEVER MODIFY EXISTING FUNCTIONS - ONLY ADD NEW IMPORTS AND REGISTRATIONS >> prompt.txt
echo - CRITICAL: PRESERVE ALL EXISTING METHOD NAMES AND SIGNATURES EXACTLY AS THEY ARE >> prompt.txt
echo - CRITICAL: DO NOT CHANGE update_game_state OR ANY OTHER EXISTING METHOD >> prompt.txt
echo - Only add special logic to states that require operations per section 2 >> prompt.txt
echo - Follow exact game flow definitions and parameter values from the setting file >> prompt.txt
echo - Ensure all state handlers are properly registered in state_manager.py >> prompt.txt
echo - Generate syntactically correct and functionally complete code >> prompt.txt
echo - Make the result functionally equivalent to the reference implementation >> prompt.txt

echo Prompt file created successfully!
echo.

echo Step 5: Execute Q CLI transformation...
wsl bash -ic "cd $(wslpath '%cd%') && q chat --trust-all-tools < prompt.txt"

echo Step 6: Cleanup...
del prompt.txt

echo.
echo ========================================
echo Step 3 Transformation completed!
echo Generated: All state handlers based on game setting file
echo Updated: Core modules with complete game logic
echo Result: Sample_Step3 with dynamic game implementation
echo ========================================
pause
