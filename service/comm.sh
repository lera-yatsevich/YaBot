# postgres prod
docker run --rm -d \
  --net=app \
  --name postgres \
  -e POSTGRES_PASSWORD=admin \
  -e POSTGRES_USER=admin \
  -e POSTGRES_DB=db \
  -v pg_vol:/var/lib/postgresql/data \
  -p 5432:5432 \
  postgres:16


# postgres test
docker run --rm -d \
  --net=app \
  --name postgres \
  -e POSTGRES_PASSWORD=admin \
  -e POSTGRES_USER=admin \
  -e POSTGRES_DB=db \
  -v pg_vol:/var/lib/postgresql/data \
  -p 4321:5432 \
  postgres:16

# volume
docker volume create pg_vol

# network
docker network create app

# postgres on server
docker exec -ti postgres psql -U admin db

# superset

docker run -d --rm \
  -p 80:8088 \
  --name superset \
  --net=app \
  apache/superset

docker exec -it superset superset fab create-admin \
              --username admin \
              --firstname Superset \
              --lastname Admin \
              --email admin@superset.com \
              --password admin

docker exec -it superset superset db upgrade

docker exec -it superset superset init