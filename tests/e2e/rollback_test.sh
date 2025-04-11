#!/bin/bash
# Rollback Procedure Test Script
set -e

echo "=== Starting Rollback Test ==="

# 1. Get current deployment version
CURRENT_VERSION=$(kubectl get deployment hr-analytics -o=jsonpath='{.spec.template.spec.containers[0].image}' | cut -d':' -f2)
echo "Current version: $CURRENT_VERSION"

# 2. Deploy new version (simulate failed update)
NEW_VERSION="v2.1.0-rc1"
echo "Deploying test version: $NEW_VERSION"
kubectl set image deployment/hr-analytics hr-analytics=hrregistry/hr-analytics:$NEW_VERSION

# 3. Verify deployment failure (simulated)
echo "Waiting 30s for deployment to stabilize..."
sleep 30
kubectl rollout status deployment/hr-analytics --timeout=30s && {
    echo "ERROR: Test deployment succeeded unexpectedly"
    exit 1
}

# 4. Execute rollback
echo "Initiating rollback..."
kubectl rollout undo deployment/hr-analytics

# 5. Verify rollback success
echo "Verifying rollback..."
kubectl rollout status deployment/hr-analytics --timeout=60s
RESTORED_VERSION=$(kubectl get deployment hr-analytics -o=jsonpath='{.spec.template.spec.containers[0].image}' | cut -d':' -f2)

if [ "$RESTORED_VERSION" == "$CURRENT_VERSION" ]; then
    echo "SUCCESS: Rollback to version $CURRENT_VERSION verified"
    exit 0
else
    echo "ERROR: Rollback failed. Current version: $RESTORED_VERSION"
    exit 1
fi
