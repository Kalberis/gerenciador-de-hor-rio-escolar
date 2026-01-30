# Testando o deploy Kubernetes

## Pré-requisitos
- Cluster Kubernetes ativo (minikube, kind, GKE, EKS, etc)
- kubectl configurado

## Passos para aplicar os manifestos

```sh
cd k8s
kubectl apply -f db-deployment.yaml
kubectl apply -f redis-deployment.yaml
kubectl apply -f web-deployment.yaml
kubectl apply -f nginx-deployment.yaml
```

## Verificando recursos

```sh
kubectl get pods
kubectl get svc
```

## Acessando a aplicação
- O serviço nginx estará exposto na porta 80 do cluster.
- Se estiver usando minikube:
  ```sh
  minikube service horario-escolar-nginx
  ```
- Para logs:
  ```sh
  kubectl logs deployment/horario-escolar-web
  ```

## Observações
- Ajuste variáveis de ambiente conforme necessário nos arquivos YAML.
- Certifique-se de que as imagens Docker estejam disponíveis para o cluster (use um registry ou minikube docker-env).
