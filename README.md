# zombie-reaper
sidecar container to reap garden zombie container that keep popping up in current concourse helm chart 5.4.0

it can be used inside the values yaml, as a sidecar container for workers

```yaml
  sidecarContainers:
  - name: zombie-reaper
    image: hmuendel/zombie-reaper
    imagePullPolicy: Always
    securityContext: 
      privileged: true
    ports:
    - containerPort: 8000
      name: monitoring
    resources:
      limits:
        cpu: 100m
        memory: 64Mi
      requests:
        cpu: 1m
        memory: 64Mi
    volumeMounts:
      - name: concourse-work-dir
        mountPath: /concourse-work-dir
        readOnly: true
```


Also an additional service is necessary to allow prometheus to 
discover the scraping enpoint of the reaper metrics.

The service selector must match the pod the reaper is running in

```yaml
apiVersion: v1
kind: Service
metadata:
  annotations:
    prometheus.io/port: "8000"
    prometheus.io/scrape: "true"
  name: devtools-web-reaper-metrics
  namespace: devtools
spec:
  ports:
  - name: reaper-metrics
    port: 8000
    targetPort: reaper-metrics
  selector:
    app: devtools-web
  type: ClusterIP
```