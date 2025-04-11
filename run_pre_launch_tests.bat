@echo off
REM Pre-Launch Test Suite Wrapper Script for Windows

echo === Starting Pre-Launch Test Suite ===
echo Timestamp: %date% %time%
echo.

REM 1. Run Load Tests
echo --- Executing Load Tests ---
cd tests
python load_test.py
if %errorlevel% neq 0 (
    echo ERROR: Load tests failed
    exit /b 1
)
echo Load tests completed successfully
echo.

REM 2. Verify Monitoring Alerts
echo --- Verifying Monitoring Alerts ---
echo Monitoring alert verification requires manual steps
echo Refer to docs\pre_launch_test_plan.md for procedure
echo.

REM 3. Validate Backup Systems
echo --- Validating Backup Systems ---
python ..\deployment_verifier.py --verify-backups
if %errorlevel% neq 0 (
    echo ERROR: Backup validation failed
    exit /b 1
)
echo Backup validation completed successfully
echo.

REM 4. Test Rollback Procedure
echo --- Testing Rollback Procedure ---
cd e2e
call rollback_test.sh
if %errorlevel% neq 0 (
    echo ERROR: Rollback test failed
    exit /b 1
)
echo Rollback test completed successfully
echo.

echo === Pre-Launch Test Suite Completed ===
echo All critical tests passed successfully
echo Timestamp: %date% %time%
exit /b 0
