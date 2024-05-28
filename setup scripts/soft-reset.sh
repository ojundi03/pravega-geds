helm uninstall zookeeper bookkeeper pravega
kubectl delete pravegacluster pravega

kubectl delete pv geds-cache
kubectl apply -f manifests/geds-pv.yaml

nohup kubectl port-forward svc/pravega-hl -n pravega 9000:9000 --address 10.15.123.10 &
mc rb --force pravega/tier-2-baseline
mc mb pravega/tier-2-baseline
mc rb --force pravega/tier-2-geds
mc mb pravega/tier-2-geds

kubectl delete pod geds-metadataserver
kubectl apply -f manifests/metadata-server.yml

helm install zookeeper pravega/zookeeper
helm install bookkeeper pravega/bookkeeper 


kubectl create -f manifests/pravega-not-helm-GEDS.yaml
# helm install pravega pravega/pravega -f manifests/values.yaml