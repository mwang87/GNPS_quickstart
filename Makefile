build:
	docker build -f Dockerfile.website -t gnpsquickstart .

clean:
	docker rm gnpsquickstart |:

development: clean
	docker run -it -p 5050:5009 --name gnpsquickstart gnpsquickstart /app/run_dev_server.sh

server: clean
	docker run -d -p 5050:5000 --name gnpsquickstart gnpsquickstart /app/run_server.sh

interactive: clean
	docker run -it -p 5050:5000 --name gnpsquickstart gnpsquickstart /app/run_server.sh

bash: clean
	docker run -it -p 5050:5009 --name gnpsquickstart gnpsquickstart bash

attach:
	docker exec -i -t gnpsquickstart-worker1 /bin/bash



#Docker Compose
server-compose-build-no-cache:
	docker-compose build --no-cache

server-compose-interactive:
	docker-compose build
	docker-compose up

server-compose:
	docker-compose build
	docker-compose up -d

server-compose-production-interactive:
	docker-compose build
	docker-compose -f docker-compose.yml -f docker-compose-production.yml up

server-compose-production:
	docker-compose build
	docker-compose -f docker-compose.yml -f docker-compose-production.yml up -d