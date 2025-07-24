# sdis2

## 1. Verificar pré-requisitos
docker --version docker-compose --version

## 2. Construir e executar
docker-compose build docker-compose up -d

## 3. Verificar containers
docker-compose ps

## 4. Visualizar logs em tempo real
Logs do sistema principal
docker-compose logs -f sistema-producao

## 5. Logs de todos os serviços
docker-compose logs -f

## 6. Logs com timestamp
docker-compose logs -f -t sistema-producao
