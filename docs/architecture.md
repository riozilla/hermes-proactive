# Architecture and design rationale

## More initiative requires more than a personality

The proposed design has six cooperating layers: identity, responsibility, observation, execution, verification, and delivery. Each has a different failure mode. A stronger tone cannot collect unavailable messages; a cron cannot remember commitments without persistent state; and a saved draft is not a delivered result.

```text
Already-authorized sources + due checks + time-window crossings
                              |
                    Read-only collection
                              |
                Durable, recoverable signals
                              |
           Cheap gate: meaningful work due or changed?
                              |
             Bounded job + installed operating skill
                              |
          Claim -> prepare -> verify -> commit result
                              |
            Private artifact + responsibility update
                              |
          Shared quiet hours, deduplication, and quota
                              |
           One verified private delivery/return route
```

This is a design, not an included running pipeline. Reuse equivalent components already present in the deployment.

## Responsibility is different from a task list

A responsibility records an accepted outcome, success criterion, owner, next action, next check, authorization requirements, and evidence. Inferred opportunities remain candidates. A waiting state is legitimate; it should not generate a reminder every polling tick. Close an outcome when its real acceptance criterion is met, without stretching it into indefinite monitoring.

## Collection and processing are separate transactions

Persist collected signals together with their collection cursor. Claim pending work with an expiring lease. Do not advance the processing checkpoint until the outcome is durable. Never hold a database transaction open across a model call. A crash after collection must not lose the signal.

Changed counts are insufficient: an event can be edited without changing a count. Unchanged data can still require action when a meeting enters its preparation window. An eligible queued delivery also needs a future wake-up even if no new email arrives.

## Three distinct kinds of state

Keep responsibility state, execution state, and delivery state separate. “Prepared,” “attempted,” “delivered,” and “read” are different. After an ambiguous send timeout, reconcile before retrying; exactly-once behavior cannot be promised by a prompt.

Use supported platform mechanisms to inspect executions. Do not query or mutate Hermes's internal tables for the custom application store. See the [state contract](../skills/proactive-ops/references/STATE-CONTRACT.md).

## Attention is shared

The message cap, spacing, quiet hours, and deduplication keys must be shared across all jobs. Eight independent counters allow eight times the intended interruptions. Reserve slots atomically and do not release an uncertain send reservation as though failure were established.

## Boundaries and resource use

Broad preparation authority covers private, low-risk, reversible work within approved scope. Sending, spending, publishing, security changes, and other consequential actions require an exact authorization. Enforce permissions and budgets in tools/runtime where possible; prompts alone do not enforce them.

A single proactive worker is a starting point, not a latency guarantee. Benchmark the real model server and reserve foreground capacity. A health job inside the gateway cannot alert when that gateway is completely stopped; independent monitoring is a separate capability.

## Deliberate non-goals

This pack does not clone a competitor's internal system, authorize covert monitoring, maximize conversation volume, build a second conflicting task system, or add unlimited self-spawning jobs. It does not change model/provider budgets without approval.
