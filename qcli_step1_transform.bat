@echo off
echo ========================================
echo QCLI Step 1: Transform InputCommand ONLY
echo ========================================
echo.

echo Step 1: Copy Sample to Sample_Step1...

REM Check if source exists
if not exist "Sample" (
    echo [ERROR] Source Sample directory not found
    pause
    exit /b 1
)

REM Remove existing target
if exist "Sample_Step1" (
    echo Removing existing Sample_Step1...
    rmdir /s /q "Sample_Step1" 2>nul
    timeout /t 2 >nul
)

echo Copying Sample to Sample_Step1...
xcopy "Sample" "Sample_Step1" /E /I /H /Y /Q

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

echo Step 3: Create InputCommand transformation prompt...

echo Transform InputCommand TODO in Sample_Step1 based on ProtoSchema/InputCommand.proto: > prompt.txt
echo. >> prompt.txt
echo Fix input_generator.py: generate_key_input, generate_complex_input, create_vr_input >> prompt.txt
echo Fix game_config.py: InputKeyType, VrInputType enums >> prompt.txt
echo Fix dynamic_game_config.py: InputKeyType/VrInputType imports >> prompt.txt
echo Fix selection_state_handler.py: EInputKeyType import >> prompt.txt
echo Fix state_manager.py: InputCommand creation >> prompt.txt
echo Fix random_input.py: __init__, generate_input, generate_basic_input, generate_complex_input >> prompt.txt
echo. >> prompt.txt
echo ONLY modify InputCommand TODO, keep GameFlowData TODO unchanged >> prompt.txt

echo Prompt created!
echo.

echo Step 4: Execute Q CLI transformation via WSL...
wsl bash -ic "cd $(wslpath '%cd%') && q chat --trust-all-tools \"$(cat prompt.txt)\""

echo Step 5: Cleanup...
del prompt.txt

echo.
echo ========================================
echo Step 1 Transformation completed!
echo Result: Sample_Step1 with InputCommand implementation
echo ========================================
pause
