# volume
docker volume create pg_vol

# network
docker network create app

# postgres test
docker run --rm -d \
  --net=app \
  --name postgres \
  -e POSTGRES_PASSWORD=admin \
  -e POSTGRES_USER=admin \
  -e POSTGRES_DB=db \
  -v pg_vol:/var/lib/postgresql/data \
  -p 5432:5432 \
  postgres:16


# postgres prod
docker run --rm -d \
  --net=app \
  --name postgres \
  -e POSTGRES_PASSWORD=admin \
  -e POSTGRES_USER=admin \
  -e POSTGRES_DB=db \
  -v pg_vol:/var/lib/postgresql/data \
  -p 4321:5432 \
  postgres:16


# SQL requests
docker exec -ti postgres psql -U admin db

# superset prod
docker run -d --rm \
  --net=app \
  -p 80:8088 \
  -e SUPERSET_SECRET_KEY=key \
  --name superset \
  apache/superset

# superset test
docker run -d --rm \
  --net=app \
  -p 80:8088 \
  -e SUPERSET_SECRET_KEY=key \
  --platform=linux/amd64 \
  --name superset \
  apache/superset

docker exec -it superset superset fab create-admin \
              --username admin \
              --firstname Superset \
              --lastname Admin \
              --email admin@superset.com \
              --password admin

docker exec -it superset superset db upgrade

docker exec -it superset superset init