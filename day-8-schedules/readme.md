```text
Pod affinity is a Kubernetes scheduling rule that says:

"Try to place this Pod on a node where another particular Pod is already running."

It is useful when two applications should be close to each other, for example:

Frontend Pod
     ↓
Backend Pod

Try to place them on the same node
1. Pod affinity vs pod anti-affinity
Feature	Meaning
Pod affinity	Put Pods together
Pod anti-affinity	Keep Pods apart

Example:

Affinity:
Backend → "I want to be near frontend"

Anti-affinity:
Backend → "I don't want another backend replica on my node"
Let's test pod affinity

We'll create:

A redis Pod with label app: redis
A backend Pod that has required pod affinity to Redis

Pod affinity is a scheduling rule used to place a Pod close to other Pods matching specific labels. For example, I can require a backend Pod to run on the same node as a Redis Pod using podAffinity with requiredDuringSchedulingIgnoredDuringExecution and the kubernetes.io/hostname topology key."
```
```text
Pod anti-affinity = keep matching Pods apart

Suppose you have 2 backend replicas:

backend-1
backend-2

With pod anti-affinity, you can tell Kubernetes:

"Don't place these two Pods on the same node."

So ideally:

Node-A                 Node-B
┌───────────┐          ┌───────────┐
│ backend-1 │          │ backend-2 │
└───────────┘          └───────────┘

Instead of:

Node-A
┌────────────────────┐
│ backend-1          │
│ backend-2          │
└────────────────────┘
Example
affinity:
  podAntiAffinity:
    requiredDuringSchedulingIgnoredDuringExecution:
      - labelSelector:
          matchLabels:
            app: backend
        topologyKey: kubernetes.io/hostname

The important part is:

podAntiAffinity:

and:

topologyKey: kubernetes.io/hostname

hostname means different Kubernetes nodes.

So with 2 nodes:

backend-1 → Node-A
backend-2 → Node-B
Why do we use it?

For high availability.

Imagine both replicas are on the same node:

Node-A
 ├── backend-1
 └── backend-2

If Node-A fails:

Node-A ❌
   ↓
backend-1 ❌
backend-2 ❌

Your application is down.

With anti-affinity:

Node-A              Node-B
backend-1           backend-2

If Node-A fails:

Node-A ❌           Node-B ✅
backend-1 ❌        backend-2 ✅

You still have one replica serving traffic.
```
