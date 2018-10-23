docker rm gnpsquickstart
#docker run -d -p 5050:5000 --name gnpsquickstart gnpsquickstart /app/run_server.sh
docker run -p 5050:5000 --name gnpsquickstart gnpsquickstart /app/run_server.sh
