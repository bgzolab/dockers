# TTRSS

## Quick start

```shell
# Env via: https://stackoverflow.com/a/76832150

# On Wsl
sudo duckerd
# On *nix
sudo systemctl start docker
sudo systemctl enable docker

# Config Proxy
mkdir -p ~/.docker
sudo echo "{'proxies':{ 'default':{'httpProxy': 'http://127.0.0.1:8123','httpsProxy': 'http://172.17.0.1:8123','noProxy': 'localhost,127.0.0.1,.daocloud.io'}}}" > ~/.docker/config.json
# Config Proxy #2
sudo mkdir -p /etc/systemd/system/docker.service.d
sudo echo "[Service]\nEnvironment='HTTP_PROXY=http://proxy.example.com:8080/'\nEnvironment='HTTPS_PROXY=http://proxy.example.com:8080/'\nEnvironment='NO_PROXY=localhost,127.0.0.1,.example.com'" > /etc/systemd/system/docker.service.d/proxy.conf
# Config Mirror
sudo mkdir -p /etc/docker
sudo echo "{'registry-mirrors': ['https://docker.mirrors.ustc.edu.cn']}" > /etc/docker/daemon.json

# Restart service
sudo systemctl daemon-reload
sudo systemctl restart docker

# Check Info
sudo docker info

# Start cotainer 
sudo docker-compose -f ./docker-compose.yml --env-file .env up -d
# Clean container
sudo docker-compose -f ./docker-compose.yml --env-file .env clean
# Remove container
sudo docker-compose -f ./docker-compose.yml --env-file .env rm
# End container
sudo docker-compose -f ./docker-compose.yml --env-file .env down
```

## Thanks following repos

- [🐋 Awesome TTRSS | 🐋 Awesome TTRSS](http://ttrss.henry.wang/zh/#%E5%85%B3%E4%BA%8E)
- [Free and open source comics/mangas media server | Komga](https://komga.org/)
- [Embyserver - Docker](https://hub.docker.com/r/emby/embyserver)

## Referencens

- [docker 设置代理，以及国内加速镜像设置-次世代BUG池](https://neucrack.com/p/286)
- [Docker的三种网络代理配置 · 零壹軒·笔记](https://note.qidong.name/2020/05/docker-proxy/)
- [基于Emby搭建媒体服务器 | Tomoya's Blog](https://tomoyadeng.github.io/blog/2019/03/12/building-a-media-server-based-on-emby/index.html)
