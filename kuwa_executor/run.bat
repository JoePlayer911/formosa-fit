@echo off
echo ============================================
echo   FormosaFit AI - Kuwa Executor Version
echo ============================================
echo.

:: Register model config in Kuwa
pushd "c:\kuwa\GenAI OS\windows\src"
call variables.bat
popd

set EXECUTOR_ACCESS_CODE=.tool/formosafit

pushd "c:\kuwa\GenAI OS\src\multi-chat"
php artisan model:config ".tool/formosafit" "FormosaFit AI" --order "500100"
popd

:: Start the executor
pushd "c:\kuwa\formosafit"
echo Starting FormosaFit executor...
start /b "" "python" "formosafit_executor.py" ^
    "--access_code" ".tool/formosafit" ^
    "--product_db_path" "data/seed_data.json" ^
    "--vlm_provider" "ollama" ^
    "--vlm_model" "moondream" ^
    "--llm_provider" "ollama" ^
    "--llm_model" "llama3.2:3b"
popd

echo.
echo FormosaFit executor started!
echo You can now use it in the Kuwa Multi-Chat UI.
echo.
pause
