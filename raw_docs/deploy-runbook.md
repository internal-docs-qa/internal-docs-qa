# Deployment Runbook

## Before deploying

Confirm all CI checks pass on the main branch. Notify the team channel
at least 30 minutes before a production deploy.

## Rolling back

If error rates exceed 2% after a deploy, roll back immediately using
the previous image tag. Do not attempt a forward fix during an incident.
