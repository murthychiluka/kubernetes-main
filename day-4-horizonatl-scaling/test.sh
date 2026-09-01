for j in {1..10}; do  
    for i in {1..1000}; do  
        curl -s -o /dev/null -w "%{http_code}\n" http://a4e243c5e0c19421ebb17e5b2231df50-1741334213.us-east-1.elb.amazonaws.com &  
    done  
    wait  # Wait for all background curl processes to finish before next iteration
done

```text
You can create a temporary CPU-load pod:

kubectl run cpu-load \
  --image=busybox \
  --restart=Never \
  -- /bin/sh -c "while true; do :; done"

Then watch:

kubectl get hpa -w
```
