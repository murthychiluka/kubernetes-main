```text
Suppose your probe is:

startupProbe:
  httpGet:
    path: /wrongpath
    port: 80
  periodSeconds: 5
  failureThreshold: 6

Kubernetes sends an HTTP request to the NGINX container:

GET /wrongpath
NGINX receives the request.

Because /wrongpath doesn't exist in the default NGINX web root, NGINX normally responds:

HTTP 404 Not Found
Kubernetes considers the startup probe failed because it expects a successful HTTP response (2xx/3xx).

Kubernetes repeats the probe every 5 seconds.

Attempt 1 → 404 → Failed
Attempt 2 → 404 → Failed
Attempt 3 → 404 → Failed
Attempt 4 → 404 → Failed
Attempt 5 → 404 → Failed
Attempt 6 → 404 → Failed
After 6 consecutive failures, Kubernetes considers the container's startup probe to have failed and kills/restarts the container.

If this keeps happening, the Pod can eventually show:

CrashLoopBackOff
One important correction

CrashLoopBackOff is not caused directly by the 6th probe failure.

The sequence is:

/wrongpath
     ↓
NGINX returns 404
     ↓
Startup probe fails
     ↓
6 consecutive failures
     ↓
Kubernetes restarts container
     ↓
Container starts again
     ↓
/wrongpath → 404
     ↓
6 more failures
     ↓
Kubernetes restarts again
     ↓
Repeated restarts
     ↓
CrashLoopBackOff

CrashLoopBackOff essentially means Kubernetes is repeatedly restarting the container and is backing off (waiting longer) between restart attempts.

Also, /wrongpath vs /

Your understanding here is right:

/        → NGINX default index.html → HTTP 200 → Probe succeeds
/wrongpath → Resource doesn't exist → HTTP 404 → Probe fails

So this is a very good way to deliberately test a failing startup probe.
```
```text
Kubernetes has three main container health probes, and the biggest difference is when Kubernetes uses them and what action it takes when they fail.

Simple way to remember
                 Container starts
                       │
                       ▼
                ┌──────────────┐
                │ Startup Probe │
                └──────┬───────┘
                       │
                 SUCCESS
                       │
             ┌─────────┴─────────┐
             ▼                   ▼
      ┌─────────────┐     ┌─────────────┐
      │   Liveness  │     │  Readiness  │
      │    Probe    │     │    Probe    │
      └──────┬──────┘     └──────┬──────┘
             │                   │
          FAILED               FAILED
             │                   │
             ▼                   ▼
        Restart Pod        Remove Pod from
                           Service endpoints
1. Startup Probe — "Has my application started?"

This is what we just discussed.

startupProbe:
  httpGet:
    path: /
    port: 80
  failureThreshold: 6
  periodSeconds: 5

Purpose: Give a slow-starting application time to start.

While startupProbe is running:

Kubernetes does not run liveness/readiness probes yet.
If startup probe succeeds → startup is complete.
If it repeatedly fails → container is restarted.
Example

Your NGINX:

GET /wrongpath
       ↓
     404
       ↓
Startup probe FAILED
       ↓
6 failures
       ↓
Container restarted

Think:

Startup = "Did you start successfully?"

2. Liveness Probe — "Are you still alive?"

Liveness is used after the application has started.

Example:

livenessProbe:
  httpGet:
    path: /
    port: 80
  periodSeconds: 10
  failureThreshold: 3

Imagine NGINX starts successfully:

Startup probe
     ↓
   SUCCESS
     ↓
Liveness probe starts

Later, suppose your application becomes stuck or unhealthy.

GET /
 ↓
500 Internal Server Error
 ↓
Liveness FAILED
 ↓
3 consecutive failures
 ↓
Kubernetes RESTARTS container

Think:

Liveness = "Are you still alive?"

It is about restarting a container that is no longer functioning properly.

3. Readiness Probe — "Can I send traffic to you?"

Readiness is different.

Suppose you have:

             Service
                │
       ┌────────┼────────┐
       ▼        ▼        ▼
     Pod A    Pod B    Pod C
      ✓         ✗        ✓

If Pod B's readiness probe fails:

Pod B
  ↓
Readiness FAILED
  ↓
Remove Pod B from Service endpoints

Traffic goes only to:

Pod A ✓
Pod C ✓

Pod B is NOT restarted just because readiness fails.

Once it becomes ready again:

Readiness SUCCESS
       ↓
Pod added back to Service
       ↓
Traffic can reach it

Think:

Readiness = "Can you receive traffic?"

The key difference
Probe	Question	When?	Failure action
Startup	Has the app started?	During startup	Restart container
Liveness	Is the app still alive?	After startup	Restart container
Readiness	Can the app receive traffic?	After startup	Remove from Service
Very important distinction

Liveness failure:

Probe fails
    ↓
Container RESTART

Readiness failure:

Probe fails
    ↓
Pod removed from Service endpoints
    ↓
NO container restart

Startup failure:

Probe fails repeatedly
    ↓
Container RESTART
Real-world example

Imagine you have an application that takes 60 seconds to start.

Without a startup probe:

Application starts
     ↓
Liveness probe starts immediately
     ↓
Application isn't ready yet
     ↓
Liveness fails
     ↓
Container restarted
     ↓
Application starts again
     ↓
Liveness fails again
     ↓
Restart...

You can get a restart loop.

With a startup probe:

Container starts
      ↓
Startup probe
      ↓
"Give application time to start"
      ↓
Application becomes ready
      ↓
Startup SUCCESS
      ↓
┌─────────────────┐
│ Liveness starts │
│ Readiness starts│
└─────────────────┘
```
