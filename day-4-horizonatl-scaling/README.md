🚀 Cluster Autoscaler Setup on Amazon EKS
This guide walks you through installing and configuring the Cluster Autoscaler on an Amazon EKS cluster using the AWS cloud provider.

1️⃣ Deploy Cluster Autoscaler
Apply the official Cluster Autoscaler manifest for your Kubernetes version (adjust 1.29.0 if needed):

kubectl apply -f https://raw.githubusercontent.com/kubernetes/autoscaler/cluster-autoscaler-1.29.0/cluster-autoscaler/cloudprovider/aws/examples/cluster-autoscaler-autodiscover.yaml
2️⃣ Verify the Pod
Check that the autoscaler pod is running in the kube-system namespace:


kubectl -n kube-system get pods -l app=cluster-autoscaler
Expected output:


NAME                                  READY   STATUS    RESTARTS   AGE
cluster-autoscaler-6889f6cf54-7pcsh   1/1     Running   0          2m
3️⃣ Edit Deployment (Add Cluster Name)
Edit the deployment to configure your cluster name:


kubectl -n kube-system edit deployment.apps/cluster-autoscaler
Inside the manifest, find the container args section and update:

yaml
Copy code
containers:
  - name: cluster-autoscaler
    - command:
        - ./cluster-autoscaler
        - --v=4
        - --stderrthreshold=info
        - --cloud-provider=aws
        - --skip-nodes-with-local-storage=false
        - --expander=least-waste
        - --node-group-auto-discovery=asg:tag=k8s.io/cluster-autoscaler/enabled,k8s.io/cluster-autoscaler/naresh ###chnage the cluster name in place of naresh my cluster name is naresh
        image: registry.k8s.io/autoscaling/cluster-autoscaler:v1.26.2
        imagePullPolicy: Always
        name: cluster-autoscaler
Save & exit.

4️⃣ Configure IAM Permissions
Cluster Autoscaler requires IAM permissions to scale nodes.
Go to your EKS Node Group IAM Role and attach the following policy.

👉 Either attach AmazonEKSClusterAutoscalerPolicy (AWS Managed)
or create a custom IAM policy with the JSON below.

Example IAM Policy JSON


{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": [
        "autoscaling:DescribeAutoScalingGroups",
        "autoscaling:DescribeAutoScalingInstances",
        "autoscaling:DescribeLaunchConfigurations",
        "autoscaling:DescribeTags",
        "autoscaling:SetDesiredCapacity",
        "autoscaling:TerminateInstanceInAutoScalingGroup",
        "ec2:DescribeLaunchTemplateVersions"
      ],
      "Effect": "Allow",
      "Resource": "*"
    }
  ]
}
Attach this to your Node Group Role.

5️⃣ Update Node Group Scaling Config
Set your min/max/desired node counts for the autoscaler:

aws eks update-nodegroup-config \
  --cluster-name naresh \
  --nodegroup-name ng-af5ac006 \
  --scaling-config minSize=2,maxSize=6,desiredSize=3
6️⃣ Check Autoscaler Logs
Watch the logs to confirm the autoscaler is working:


kubectl -n kube-system logs -f deployment/cluster-autoscaler
Look for lines like:


I0828 17:36:38.403432       1 scale_up.go:422] Pod default/nginx-deployment-12345 is unschedulable ...
I0828 17:36:38.403451       1 scale_up.go:423] Scale-up triggered ...
✅ Validation
Deploy a test workload with more pods than your current node capacity:


kubectl create deployment nginx --image=nginx --replicas=50
Check if new nodes are being added:


kubectl get nodes -w
Scale down pods and watch nodes reduce (if below maxSize and above minSize):


kubectl scale deployment nginx --replicas=1
📝 Notes
minSize ensures at least 2 nodes are always running.

maxSize sets the upper scaling limit.

desiredSize is the starting point but will be adjusted dynamically.

Ensure your Node Group IAM Role has autoscaling permissions, otherwise the pod will stay in Pending or fail to scale.

Only one Cluster Autoscaler pod should be running per cluster (it uses leader election).

```text

Your Deployment has:

resources:
  requests:
    cpu: "100m"
    memory: "128Mi"

And HPA has:

averageUtilization: 50
What does 50% mean?

HPA calculates CPU usage relative to the CPU request.

So:

CPU request = 100m
HPA target  = 50%

50% of 100m = 50m

Therefore, if a pod is using around 50m CPU, its utilization is:

50m / 100m × 100 = 50%
But does 50m automatically increase the pod count?

Not necessarily. This is the important part.

HPA looks at the average CPU utilization across all pods and calculates whether more replicas are needed.

For example, suppose you have 2 pods:

Pod 1 → 80m
Pod 2 → 80m

Average = 80m

80m / 100m × 100 = 80%

Your target is 50%:

Current = 80%
Target  = 50%

So HPA will likely want more replicas.

But if:

Pod 1 → 40m
Pod 2 → 40m

Average = 40m

40m / 100m × 100 = 40%

then you're below the 50% target, so HPA doesn't need to scale up.

Think of it this way
CPU request = 100m
                  │
                  ▼
             HPA target
                50%
                  │
                  ▼
             Target = 50m

If actual average CPU is:

30m → 30% → No scale up
50m → 50% → At target
70m → 70% → Scale up likely
90m → 90% → Scale up likely
One more important point

HPA doesn't simply say:

"CPU crossed 50m → add one pod."

It uses a replica calculation roughly based on:

desired replicas =
current replicas × current utilization / target utilization

For example:

Current replicas = 2
Current CPU      = 100%
Target CPU       = 50%

2 × 100 / 50 = 4

So HPA may calculate:

2 pods → 4 pods

This is why you can sometimes see HPA jump by more than one replica.

So your mental model should be:

100m is the CPU request. 50% HPA target means the target utilization is 50m per pod, but HPA scales based on the average utilization and its replica calculation—not simply because one pod reaches 50m.**
```
```text
pods will increase or decrease based on requests or limits of POD?

HPA scaling is based on resource utilization, and for CPU/memory utilization targets it is calculated relative to the Pod's requests, not its limits. ✅

For example:

resources:
  requests:
    cpu: "100m"
    memory: "128Mi"
  limits:
    cpu: "500m"
    memory: "256Mi"

If HPA says:

averageUtilization: 50

then CPU target is:

Request = 100m
Target  = 50%

50% × 100m = 50m

So roughly:

Actual CPU       Utilization       HPA behavior
------------------------------------------------
30m              30%               Below target
50m              50%               At target
80m              80%               Scale up likely
What is the limit then?

The limit controls the maximum resource the container can consume, not the HPA target.

requests.cpu = 100m
       ↓
Used by scheduler + HPA utilization calculation

limits.cpu = 500m
       ↓
Maximum CPU container is allowed to use

So in your example:

Request = 100m
Limit   = 500m
HPA     = 50%

HPA's target is 50m, not 250m.

One important nuance

HPA can also be configured using an absolute CPU value rather than utilization:

target:
  type: AverageValue
  averageValue: 200m

In that case, the target is 200m actual CPU, and the request isn't used to calculate the percentage.

But with your current:

target:
  type: Utilization
  averageUtilization: 50

👉 HPA uses the CPU request as the baseline.

Easy rule:

HPA Utilization → based on requests; resource limits → cap how much the container can consume.
```
