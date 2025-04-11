# On-Call Schedule and Procedures

## Rotation Schedule (Q3 2023)
| Week       | Primary Engineer     | Secondary Engineer   | Manager On-Call     |
|------------|----------------------|----------------------|---------------------|
| Jul 3-9    | Alice Chen           | Bob Johnson          | Sarah Williams      |
| Jul 10-16  | David Kim            | Alice Chen           | Michael Brown       |
| Jul 17-23  | Bob Johnson          | David Kim            | Sarah Williams      |
| Jul 24-30  | Alice Chen           | Bob Johnson          | Michael Brown       |

## On-Call Responsibilities
1. **Primary Engineer**:
   - First responder to all alerts
   - Initial triage and diagnosis
   - Escalation if needed within 30 minutes

2. **Secondary Engineer**:
   - Backup for primary
   - Assists with complex issues
   - Takes over after 2 hours if primary unavailable

3. **Manager**:
   - Coordinates major incidents
   - Handles customer communications
   - Approves emergency changes

## Shift Details
- **Hours**: 24/7 coverage
- **Handoff**: Daily at 9:00 AM EST via Slack
- **Compensation**: 1.5x hourly rate for off-hours

## Tools Access
1. Production Access:
   - Read-only by default
   - Temporary write access during incidents

2. Required Credentials:
   - VPN configuration
   - Monitoring dashboard access
   - ChatOps integration

## Incident Severity Levels
| Level | Response Time | Example                      |
|-------|---------------|------------------------------|
| SEV1 | Immediate     | System-wide outage           |
| SEV2 | 30 minutes    | Critical feature failure     |
| SEV3 | 2 hours       | Performance degradation      |
| SEV4 | Next business | Minor UI issues              |
