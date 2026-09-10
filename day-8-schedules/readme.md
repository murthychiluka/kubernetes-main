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
