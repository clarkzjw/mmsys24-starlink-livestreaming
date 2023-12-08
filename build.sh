cd runner
sudo docker buildx build --platform linux/amd64,linux/arm64 --push -t cr.jinwei.me/dashjs/runner .

cd ..
sudo docker buildx build --platform linux/amd64,linux/arm64 --push -t cr.jinwei.me/dashjs/dashjs -f Dockerfile-dashjs .

cd stats-server
sudo docker buildx build --platform linux/amd64,linux/arm64 --push -t cr.jinwei.me/dashjs/stats-server .

cd ..
sudo docker buildx build --platform linux/amd64,linux/arm64 --push -t cr.jinwei.me/dashjs/livesim2 -f Dockerfile-livesim2 .

sudo docker buildx build --platform linux/amd64,linux/arm64 --push -t cr.jinwei.me/dashjs/nginx -f Dockerfile-nginx .

sudo docker buildx build --platform linux/amd64,linux/arm64 --push -t cr.jinwei.me/dashjs/nginx:emulation -f Dockerfile-nginx-emulation .

cd webassembly
sudo docker buildx build --platform linux/amd64,linux/arm64 --push -t cr.jinwei.me/dashjs/pyodide -f Dockerfile .
