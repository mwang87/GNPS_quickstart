build:
	docker build -t gnpsquickstart .

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
	docker exec -i -t gnpsquickstart /bin/bash
