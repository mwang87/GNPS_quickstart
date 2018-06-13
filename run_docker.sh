docker rm gnpsquickstart
docker run -d -p 5050:5050 --name gnpsquickstart gnpsquickstart /app/run_server.sh
