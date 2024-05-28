if [ $# -eq 0 ]
  then
    echo "No arguments supplied"
    exit 1
fi

# kubectl get svc/minio -n pravega -o yaml > /tmp/svcminio.yaml
# kubectl delete svc/minio -n pravega
# kubectl delete pod pravega-pool-0-0 -n pravega
kubectl patch sts pravega-pool-0 -n pravega -p '{"spec":{"replicas":0}}'
echo "Service cut at: $(date +%T)"
sleep $1
# kubectl apply -f /tmp/svcminio.yaml
# rm /tmp/svcminio.yaml
kubectl patch sts pravega-pool-0 -n pravega -p '{"spec":{"replicas":3}}'
nohup kubectl port-forward svc/pravega-hl -n pravega 9000:9000 --address 10.15.123.10 &
kubectl port-forward pr
echo "Service resumed: at: $(date +%T)"
