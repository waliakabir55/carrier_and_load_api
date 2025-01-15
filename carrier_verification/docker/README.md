# Docker Setup
Local development is done from the carrer_verification directory (parent of docker folder). The commands below are run from the parent directory as well. The local docker build command sets up a basic postgres database with some test data (see db/init.sql). 

You can query the database using the following command:
```bash
curl "http://localhost:8000/api/v1/loads/REF09690" \
-H "X-API-Key: <add-the-api-key-here>"
```

## Local Development

```bash
# Start local development environment from carrer_verification directory (parent of docker folder)
docker compose -f docker/docker-compose.yml --env-file .env up --build

# Stop local environment
docker compose -f docker/docker-compose.yml --env-file .env down -v   
```

## Production

The production environment is run with the following command:
```bash
# Build and run production environment
docker compose -f docker/docker-compose.prod.yml --env-file .env up --build -d

# Stop production environment
docker compose -f docker/docker-compose.prod.yml --env-file .env down -v
```

Health check is done with the following command:
```bash
# Check health of production environment
curl http://localhost:8000/health
```

Loads are queried with the following command:
```bash
# Test with valid reference number
curl -H "X-API-Key: <production_api_key>" http://localhost:8000/api/v1/loads/REF09460

# Test with invalid reference number
curl -H "X-API-Key: <production_api_key>" http://localhost:8000/api/v1/loads/INVALID
```

Carrier verification is done with the following command:
```bash
# Test with valid carrier number
curl -H "X-API-Key: your_production_api_key" http://localhost:8000/verify_carrier/12345
```