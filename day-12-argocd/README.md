```text
Argo CD Complete Setup Guide
What is Argo CD?
Argo CD is a GitOps Continuous Delivery tool for Kubernetes.

It automatically deploys Kubernetes applications from a Git repository.

Argo CD continuously monitors:

Kubernetes manifests
Helm charts
Kustomize files
and syncs them into a Kubernetes cluster.

What is GitOps?
GitOps means:

Git repository is the single source of truth
All Kubernetes configurations are stored in Git
Any changes pushed to Git are automatically deployed to Kubernetes
Benefits:

Version control
Easy rollback
Automated deployments
Infrastructure consistency
Audit tracking
Argo CD Architecture
Main Components
1. API Server
Handles:

UI
CLI
Authentication
API requests
2. Repository Server
Responsible for:

Cloning Git repositories
Reading manifests
Helm rendering
Kustomize rendering
3. Application Controller
Responsible for:

Monitoring applications
Comparing desired state vs live state
Synchronization
Self-healing
Argo CD Workflow
Developer Pushes Code → Git Repository → Argo CD Detects Changes → Syncs to Kubernetes Cluster

Prerequisites
Before installing Argo CD:

You need:

Kubernetes Cluster
kubectl installed
Argo CD CLI
GitHub repository
Internet access
Supported Kubernetes:

EKS
AKS
GKE
Minikube
K3s
Kind
Step 1: Create Namespace
kubectl create namespace argocd
Step 2: Install Argo CD
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
Step 3: Verify Installation
kubectl get pods -n argocd
All pods should be in Running state.

Step 4: Expose Argo CD Server
LoadBalancer
kubectl patch svc argocd-server -n argocd -p '{"spec": {"type": "LoadBalancer"}}'
Get External IP:

kubectl get svc -n argocd
Step 5: Get Initial Admin Password
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
Username:

admin
Step 7: Login to Argo CD
argocd login with loadbalncer url
Provide:

Username
Password
Private Repository Integration
Why Private Repo Authentication is Needed
Private repositories require authentication.

Without authentication:

Argo CD cannot clone repository
Manifests cannot be fetched
Application deployment fails
Authentication Methods
Argo CD supports:

HTTPS + Username/Token
SSH Authentication
Method 1: HTTPS with Personal Access Token
Method : SSH Authentication
Why SSH?
SSH authentication is more secure.

Used mostly in:

Production
Enterprises
Secure environments
Step 1: Generate SSH Key
ssh-keygen -t rsa -b 4096 -C "argocd"
Files created:

~/.ssh/id_rsa
~/.ssh/id_rsa.pub
Step 2: Add Public Key to GitHub
Open:

GitHub → Settings → SSH and GPG Keys

Add:

id_rsa.pub
Creating Argo CD Application
What is an Application?
An Argo CD Application is:

A deployment definition

Connects Git repo to Kubernetes cluster

Defines:

Source repository
Path
Destination cluster
Namespace
Application Parameters Explanation
--repo
Git repository URL.

--path
Folder inside repository containing manifests.

Example:

kubernetes/
manifests/
helm/
--dest-server
Target Kubernetes cluster.

Default cluster:

https://kubernetes.default.svc
--dest-namespace
Namespace where application will deploy.

Sync Application
argocd app sync ecommerce-app
This deploys manifests into Kubernetes.

Auto Sync
What is Auto Sync?
Automatically deploys changes whenever Git repository updates.

Enable Auto Sync
Self Healing
What is Self Healing?
If someone manually changes Kubernetes resources:

Argo CD restores them back to Git state.

Enable:

Pruning
What is Pruning?
Deletes Kubernetes resources removed from Git.

Enable:

Application Lifecycle
Git Push → Argo CD Detects Changes → Compare Desired vs Live State → Sync → Deployment

Application States
Synced
Git state matches cluster state.

OutOfSync
Cluster differs from Git.

Healthy
Application running successfully.

Degraded
Application has issues.

Examples:

CrashLoopBackOff
Failed deployment
Pod failures
Deploy Using YAML
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: myapp-argo-application
  namespace: argocd
spec:
  project: default

  source:
    repoURL: https://github.com/CloudTechDevOps/Kubernetes-0730.git
    targetRevision: HEAD
    path: Day-5-Argocd
  destination: 
    server: https://kubernetes.default.svc
    namespace: myapp

  syncPolicy:
    syncOptions:
    - CreateNamespace=true

    automated:
      selfHeal: true
      prune: true
Apply:

kubectl apply -f app.yaml
Kustomize Integration
Argo CD supports Kustomize.

Repository structure:

base/
overlays/
Multi Cluster Deployment
Argo CD can deploy to multiple clusters.

Add cluster:

argocd cluster add CONTEXT_NAME
List clusters:

argocd cluster list
Argo CD UI Overview
Main sections:

Applications
Repositories
Clusters
Settings
Projects
Summary
Argo CD is a Kubernetes GitOps deployment tool.

Workflow:

Store manifests in Git
Connect repository to Argo CD
Create application
Sync manifests
Argo CD deploys automatically
Git becomes source of truth
Private repositories can be integrated using:

HTTPS tokens
SSH keys
Repository secrets
Argo CD continuously monitors Git and Kubernetes to maintain desired application state.
```
*****************************
```text
Kustomize files are configuration files used by Kustomize, a Kubernetes configuration management tool.

Instead of creating completely separate YAML files for each environment, you create a base configuration and then use Kustomize overlays to customize it.

Example

You might have:

my-app/
├── base/
│   ├── deployment.yaml
│   ├── service.yaml
│   └── kustomization.yaml
│
└── overlays/
    ├── dev/
    │   └── kustomization.yaml
    └── prod/
        └── kustomization.yaml

The kustomization.yaml file tells Kustomize which Kubernetes YAML files to combine and what modifications to apply.

For example:

resources:
  - deployment.yaml
  - service.yaml

namePrefix: dev-

Kustomize can take these files and generate the final Kubernetes manifests that are applied to the cluster.

In Argo CD

Argo CD can point to a Git repository containing Kustomize configuration:

Git Repository
      ↓
Kustomize files
      ↓
Argo CD
      ↓
Generated Kubernetes manifests
      ↓
Kubernetes cluster

So when you hear:

"Argo CD monitors Kubernetes manifests, Helm charts, and Kustomize files"

it means Argo CD can work with plain YAML, Helm-based applications, or Kustomize-based configurations stored in Git.

👉 Simple definition: Kustomize files are Kubernetes configuration files, centered around kustomization.yaml, that let you customize and reuse YAML manifests for different environments.
```
