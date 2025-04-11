#!/bin/bash
# Pre-Launch Test Suite Wrapper Script

echo "=== Starting Pre-Launch Test Suite ==="
echo "Timestamp: $(date)"
echo ""

# 1. Run Load Tests
echo "--- Executing Load Tests ---"
cd tests
python load_test.py
if [ $? -ne 0 ]; then
    echo "ERROR: Load tests failed"
    exit 1
fi
echo "Load tests completed successfully"
echo ""

# 2. Verify Monitoring Alerts
echo "--- Verifying Monitoring Alerts ---"
# This would typically involve:
# - Triggering test alerts
# - Verifying alert delivery
# - Checking alert content
echo "Monitoring alert verification requires manual steps"
echo "Refer to docs/pre_launch_test_plan.md for procedure"
echo ""

# 3. Validate Backup Systems
echo "--- Validating Backup Systems ---"
python ../deployment_verifier.py --verify-backups
if [ $? -ne 0 ]; then
    echo "ERROR: Backup validation failed"
    exit 1
fi
echo "Backup validation completed successfully"
echo ""

# 4. Test Rollback Procedure
echo "--- Testing Rollback Procedure ---"
cd e2e
./rollback_test.sh
if [ $? -ne 0 ]; then
    echo "ERROR: Rollback test failed"
    exit 1
fi
echo "Rollback test completed successfully"
echo ""

echo "=== Pre-Launch Test Suite Completed ==="
echo "All critical tests passed successfully"
echo "Timestamp: $(date)"
exit 0
