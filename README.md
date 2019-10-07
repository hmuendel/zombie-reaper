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
    resources:
      limits:
        cpu: 100m
        memory: 64Mi
      requests:
        cpu: 1m
        memory: 64Mi
    volumeMounts:
      - name: concourse-work-dir
        mountPath: /mnt
        readOnly: true
```