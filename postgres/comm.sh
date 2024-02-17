# postgres
docker run --rm -d \
  --net=app \
  --name postgres \
  -e POSTGRES_PASSWORD=admin \
  -e POSTGRES_USER=admin \
  -e POSTGRES_DB=db \
  -v pg_vol:/var/lib/postgresql/data \
  -p 5432:5432 \
  postgres:16

# volume
docker volume create pg_vol

# network
docker network create app

# postgres on server
docker exec -ti postgres psql -U admin db
