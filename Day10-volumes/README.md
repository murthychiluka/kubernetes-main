```text
Documenting the setup for keeping DB credentials in AWS Secret Manager. End-to-end production-style flow.
End-to-end architecture

For your EKS hands-on, the overall setup should look like this:

                     AWS
                      │
          ┌───────────┴───────────┐
          │                       │
          ↓                       ↓
   AWS Secrets Manager       IAM Role
   myapp/database            EBS CSI Role
          │
          │
          ↓
   EKS Pod Identity
          │
          ↓
   ServiceAccount
   app-secrets-sa
          │
          ↓
 Secrets Store CSI Driver
          │
          ↓
    AWS Provider
          │
          ↓
      Kubernetes Pod
       /          \
      /            \
     ↓              ↓
Secret file      K8s Secret
/mnt/secrets     myapp-database-secret
                     │
                     ↓
              Environment Variable
                     │
                     ↓
                 Application
                     │
                     ↓
                   MySQL
1. Create the database secret in AWS Secrets Manager

Instead of putting this in Kubernetes:

MYSQL_PASSWORD: mypassword

store it in AWS Secrets Manager.

Example:

{
  "username": "myuser",
  "password": "mypassword",
  "database": "mydb"
}

For example:

Secret name:
myapp/database

Rule: Don't put actual passwords in GitHub, Git, Helm values, ConfigMaps, or Deployment YAMLs.

2. Create IAM permissions

Create an IAM policy allowing the application to read the specific secret.

Ideally:

secretsmanager:GetSecretValue

for:

arn:aws:secretsmanager:us-east-1:<account-id>:secret:myapp/database*

Avoid giving:

secretsmanager:*

to the application.

Follow the least privilege principle.

3. Create IAM role for EKS Pod Identity

Your application should assume the IAM role through EKS Pod Identity.

Conceptually:

Pod
 ↓
ServiceAccount
 ↓
EKS Pod Identity
 ↓
IAM Role
 ↓
Secrets Manager

The IAM role should have only the Secrets Manager permissions required by the application.

4. Install EKS Pod Identity Agent

On EKS, make sure:

kubectl get pods -n kube-system | grep eks-pod-identity

shows the Pod Identity Agent running.

This is what allows Kubernetes Pods to obtain AWS credentials through their IAM role association.

5. Create Kubernetes ServiceAccount

Example:

apiVersion: v1
kind: ServiceAccount
metadata:
  name: app-secrets-sa
  namespace: default

The Pod will use:

serviceAccountName: app-secrets-sa
6. Create EKS Pod Identity Association

Associate:

Kubernetes ServiceAccount
        ↓
app-secrets-sa
        ↓
IAM Role
        ↓
Secrets Manager permissions

Verify with:

aws eks list-pod-identity-associations \
  --cluster-name murthy \
  --region us-east-1

You should see the association.

7. Install Secrets Store CSI Driver

You already did this.

Verify:

kubectl get pods -n kube-system | grep csi-secrets-store

You want:

3/3 Running

Also make sure token requests are configured because you're using Pod Identity:

tokenRequests:
  - audience: pods.eks.amazonaws.com

You discovered this issue yourself today, which is a very useful troubleshooting lesson.

8. Install AWS Secrets Manager provider

You need the AWS provider for the Secrets Store CSI Driver.

Conceptually:

Secrets Store CSI Driver
          ↓
AWS Provider
          ↓
AWS Secrets Manager

Verify the provider Pod is running.

9. Create SecretProviderClass

Your working configuration is essentially:

apiVersion: secrets-store.csi.x-k8s.io/v1
kind: SecretProviderClass
metadata:
  name: myapp-secrets
  namespace: default

spec:
  provider: aws

  parameters:
    usePodIdentity: "true"
    region: us-east-1

    objects: |
      - objectName: "myapp/database"
        objectType: "secretsmanager"

  secretObjects:
    - secretName: myapp-database-secret
      type: Opaque

      data:
        - objectName: myapp_database
          key: DB_CONFIG

There are two important sections here.

AWS secret to mount
parameters:
  objects:

This gives you:

AWS Secrets Manager
        ↓
/mnt/secrets-store/myapp_database
AWS secret → Kubernetes Secret
secretObjects:

This gives you:

AWS Secrets Manager
        ↓
Kubernetes Secret
myapp-database-secret
10. Mount the CSI volume into the Pod

Your Deployment needs:

volumeMounts:
  - name: secrets-store
    mountPath: /mnt/secrets-store
    readOnly: true

and:

volumes:
  - name: secrets-store
    csi:
      driver: secrets-store.csi.k8s.io
      readOnly: true

      volumeAttributes:
        secretProviderClass: myapp-secrets

This causes the secret to be mounted into the Pod.

11. Use the secret as an environment variable

If your application wants environment variables:

env:
  - name: DB_CONFIG
    valueFrom:
      secretKeyRef:
        name: myapp-database-secret
        key: DB_CONFIG

Then inside the application:

DB_CONFIG

contains the value obtained from AWS Secrets Manager.

12. Test the entire chain

This is the checklist I recommend keeping.

AWS
aws secretsmanager get-secret-value \
  --secret-id myapp/database \
  --region us-east-1
IAM

Verify the role:

aws iam get-role \
  --role-name <role-name>
Pod Identity
aws eks list-pod-identity-associations \
  --cluster-name murthy \
  --region us-east-1
CSI Driver
kubectl get pods -n kube-system | grep csi-secrets
SecretProviderClass
kubectl get secretproviderclass
Pod
kubectl get pods
Mounted secret
kubectl exec -it <pod> -- \
cat /mnt/secrets-store/myapp_database
Kubernetes Secret
kubectl get secrets

Expected:

myapp-database-secret
Environment variable
kubectl exec -it <pod> -- env | grep DB_CONFIG
13. What should NOT be in Git

This is very important for your CI/CD work.

❌ Don't commit this
env:
  - name: DB_PASSWORD
    value: "mypassword"
❌ Don't put passwords in ConfigMap
data:
  DB_PASSWORD: mypassword
❌ Don't put real passwords in values.yaml
mysqlPassword: mypassword
❌ Don't put AWS access keys in Kubernetes
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
✅ Instead
GitHub
   ↓
Kubernetes YAML
   ↓
ServiceAccount
   ↓
EKS Pod Identity
   ↓
IAM
   ↓
AWS Secrets Manager
   ↓
Database credentials
14. ConfigMap vs Secret vs Secrets Manager

This is worth remembering for interviews and real projects:

Requirement	Recommended
Application configuration	ConfigMap
Kubernetes-level sensitive value	Kubernetes Secret
Database password	AWS Secrets Manager
API keys	AWS Secrets Manager
TLS/private credentials	Secrets Manager / appropriate secret store
Non-sensitive environment variables	ConfigMap
AWS permissions	IAM + EKS Pod Identity

For your EKS environment, I'd prefer:

ConfigMap
   ↓
non-sensitive configuration

AWS Secrets Manager
   ↓
passwords / credentials / API keys
15. Your final production-style architecture

For your current lab, I'd aim for this:

                 GitHub
                    │
                    │ Kubernetes YAML
                    ↓
                 ArgoCD
                    │
                    ↓
                  EKS
                    │
          ┌─────────┴─────────┐
          │                   │
    ConfigMap             ServiceAccount
          │                   │
          │             EKS Pod Identity
          │                   │
          │                   ↓
          │              IAM Role
          │                   │
          │                   ↓
          │          AWS Secrets Manager
          │                   │
          │            DB credentials
          │                   │
          └─────────┬─────────┘
                    ↓
               Application
                    │
                    ↓
                 MySQL/RDS
One final security improvement

For a production application, I would not necessarily sync the AWS secret into a Kubernetes Secret unless the application requires it.

You have now learned both options:

Option A — preferred when possible:

Secrets Manager
      ↓
CSI
      ↓
Mounted secret file

Fewer copies of the credential.

Option B — when the application needs Kubernetes Secret/env variables:

Secrets Manager
      ↓
CSI
      ↓
Kubernetes Secret
      ↓
Environment variable

This is more convenient but creates another copy of the secret inside Kubernetes.

Your hands-on learning path from here

I'd recommend doing the exercises in this order:

1. ConfigMap
      ↓
2. Kubernetes Secret
      ↓
3. AWS Secrets Manager
      ↓
4. EKS Pod Identity
      ↓
5. Secrets Store CSI Driver
      ↓
6. Mount secret as file
      ↓
7. Sync to Kubernetes Secret
      ↓
8. Consume as environment variable
      ↓
9. Connect application to MySQL
      ↓
10. Add secret rotation
      ↓
11. Integrate with ArgoCD
      ↓
12. Production security / least privilege

You have already completed 1–8, including troubleshooting a real InvalidIdentityToken and CSI tokenRequests problem. That's excellent hands-on EKS experience.
```
