@echo off
echo ========================================
echo QCLI Step 2: Transform GameFlowData ONLY
echo ========================================
echo.

echo Step 1: Copy Sample_Step1 to Sample_Step2...

REM Check if source exists
if not exist "Sample_Step1" (
    echo [ERROR] Sample_Step1 directory not found
    echo Please run qcli_step1_transform.bat first
    pause
    exit /b 1
)

REM Remove existing target
if exist "Sample_Step2" (
    echo Removing existing Sample_Step2...
    rmdir /s /q "Sample_Step2" 2>nul
    timeout /t 2 >nul
)

echo Copying Sample_Step1 to Sample_Step2...
xcopy "Sample_Step1" "Sample_Step2" /E /I /H /Y /Q

if errorlevel 1 (
    echo [ERROR] Copy failed
    pause
    exit /b 1
)

echo Copy completed successfully!
echo.

echo Step 2: Check WSL availability...
wsl --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] WSL not found, please install it.
    pause
    exit /b 1
)
echo WSL available!
echo.

echo Step 3: Create GameFlowData transformation prompt...

echo Transform GameFlowData TODO in Sample_Step2 based on ProtoSchema/GameFlowData.proto: > prompt.txt
echo. >> prompt.txt
echo MUST generate ALL state handler files for EVERY ProtoSchema/GameFlowData.proto flow enum value >> prompt.txt
echo Read ProtoSchema/GameFlowData.proto and create handler for each GAME_FLOW_* state >> prompt.txt
echo Fix game_config.py: GameFlowState enum >> prompt.txt
echo Fix dynamic_game_config.py: GameFlowState import >> prompt.txt
echo Fix target_parser.py: option mappings >> prompt.txt
echo Fix state_manager.py: state handler imports and registrations >> prompt.txt
echo. >> prompt.txt
echo Generate complete state handlers for ALL states, not just selection states >> prompt.txt
echo ONLY modify GameFlowData TODO, keep InputCommand code unchanged >> prompt.txt

echo Prompt created!
echo.

echo Step 4: Execute Q CLI transformation via WSL...
wsl bash -ic "cd $(wslpath '%cd%') && q chat --trust-all-tools \"$(cat prompt.txt)\""

echo Step 5: Cleanup...
del prompt.txt

echo.
echo ========================================
echo Step 2 Transformation completed!
echo Result: Sample_Step2 with GameFlowData implementation and all state handlers
echo ========================================
pause
