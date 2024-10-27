# Docker compose selfhost

## Quick Navigation with `192.168.31.20`
| Port | Name | Desc | Nav |
| ---- | ---- | -----|-----|
|  --  | [rsstt](https://github.com/Rongronggg9/RSS-to-Telegram-Bot) |  A Telegram RSS bot that cares about your reading experience | <img src="https://raw.githubusercontent.com/Rongronggg9/RSS-to-Telegram-Bot/refs/heads/dev/docs/resources/RSStT_icon.svg" height="30px"/> |
|`5001`| [dockge](https://github.com/louislam/dockge)|  A fancy, easy-to-use and reactive self-hosted docker compose.yaml stack-oriented manager  | [<img src="https://raw.githubusercontent.com/louislam/dockge/refs/heads/master/frontend/public/icon.svg" height="30px"/>](http://192.168.31.20:5001) |
|`5244`| [alist](https://github.com/alist-org/alist) | A file list/WebDAV program that supports multiple storages, powered by Gin and Solidjs | [<img src="https://camo.githubusercontent.com/bec0bddf2142a503a536f5edb60c830a5a1a24780b9963e6a16192105289d501/68747470733a2f2f63646e2e6a7364656c6976722e6e65742f67682f616c6973742d6f72672f6c6f676f406d61696e2f6c6f676f2e737667" height="30px" />](http://192.168.31.20:5244) |
|`8096`| [jellyfin](https://github.com/jellyfin/jellyfin) | The Free Software Media System| [<img src="https://avatars.githubusercontent.com/u/45698031?s=200&v=4" height="30px"/>](http://192.168.31.20:8096) |
|`7070`| [qbittorent](https://github.com/c0re100/qBittorrent-Enhanced-Edition) | [Unofficial] qBittorrent Enhanced, based on qBittorrent | [<img src="https://avatars.githubusercontent.com/u/2131270?s=200&v=4" height="30px"/>](http://192.168.31.20:7070) |
|`4567`| [suwayomi](https://github.com/Suwayomi/docker-tachidesk) |  A rewrite of Tachiyomi for the Desktop | [<img src="https://avatars.githubusercontent.com/u/81182076?s=200&v=4" height="30px"/>](http://192.168.31.20:4567)|
|`181` | [ttrss](https://github.com/HenryQW/Awesome-TTRSS) | A PHP and Ajax feed reader | [<img src="https://tt-rss.org/images/icon_classic_128.png" height="30px"/>](http://192.168.31.20:181)|
|`25600`| [komga](https://github.com/gotson/komga)|Media server for comics/mangas/BDs/magazines/eBooks with API, OPDS and Kobo Sync support | [<img src="https://raw.githubusercontent.com/gotson/komga/master/.github/readme-images/app-icon.png" height="30px"/>](http://192.168.31.20:25600)|
|~~`8096`~~| ~~[emby](https://github.com/fejich/docker-embyhack)~~ |  ~~使用 Docker Compose 编排整合 emby 伪站授权~~ | [<img src="https://emby.media/community/uploads/monthly_2020_06/logoemby.png.6d40431387e2fb250dba418c1c996be6.png" height="30px">](http://192.168.31.20:8096)|
<!--
|``| []() |  | [<img src="" height="30px"/>](http://192.168.31.20:) |

TODO:
- VSCode
- superng6/bilibili-helper
- codercom/code-server
- wrfly/container-web-tty
- filebrowser/filebrowser
-->


## Waiting list
- Logesq FR via: https://discuss.logseq.com/t/local-on-server-storage-for-self-hosted-logseq/6613
  - docker compose via: https://github.com/logseq/logseq/blob/master/docs/docker-web-app-guide.md



## Command References
```shell
# Install 
# on mint via: https://docs.docker.com/engine/install/ubuntu/
for pkg in docker.io docker-doc docker-compose docker-compose-v2 podman-docker containerd runc; do sudo apt-get remove $pkg; done
sudo apt-get install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
# if on ubuntu it should be VERSION_CODENAME instead of UBUNTU_CODENAME
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \\
  $(. /etc/os-release && echo "$UBUNTU_CODENAME") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
cat /etc/apt/sources.list.d/docker.list
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin -o Acquire::http::proxy="http://127.0.0.1:10800/"


# Enable Docker
# on wsl1 without systemd
sudo duckerd
# On wsl2 / unix
sudo systemctl start docker
sudo systemctl enable docker


# Restart docker
sudo systemctl daemon-reload
sudo systemctl restart docker


# Proxies
# user (works)
mkdir -p ~/.docker
vim ~/.docker/config.json
# sudo
sudo vim /etc/docker/daemon.json
'''
{
  "proxies": {
    "http-proxy": "http://proxy.example.com:3128",
    "https-proxy": "https://proxy.example.com:3129",
    "no-proxy": "*.test.example.com,.example.org,127.0.0.0/8"
  }
}
'''
# registry-mirrors has died in China...
    # https://docker.mirrors.ustc.edu.cn
    # https://ustc-edu-cn.mirror.aliyuncs.com
# systemd environment (ignored)
sudo mkdir -p /etc/systemd/system/docker.service.d
sudo echo "[Service]\nEnvironment='HTTP_PROXY=http://127.0.0.1:10800/'\nEnvironment='HTTPS_PROXY=http://127.0.0.1:10800/'\nEnvironment='NO_PROXY=localhost,127.0.0.1,.example.com'" > /etc/systemd/system/docker.service.d/proxy.conf


# Add current user to docker
sudo usermod -aG docker ${USER}


# Docker-compose with current user
DOCKER_CONFIG=${DOCKER_CONFIG:-$HOME/.docker}
mkdir -p $DOCKER_CONFIG/cli-plugins
curl -SL https://github.com/docker/compose/releases/download/v2.27.1/docker-compose-linux-x86_64 -o $DOCKER_CONFIG/cli-plugins/docker-compose
chmod +x $DOCKER_CONFIG/cli-plugins/docker-compose


# using environment variables via: https://stackoverflow.com/a/76832150
# start cotainer 
docker compose -f ./docker-compose.yml --env-file .env up -d
# clean container
docker compose -f ./docker-compose.yml --env-file .env clean
# remove container
docker compose -f ./docker-compose.yml --env-file .env rm
# end container
docker compose -f ./docker-compose.yml --env-file .env down


# look container running
docker ps
# look containner log
docker logs
# docker Info
docker info
```
> [!NOTE]
Emby mount volume drive needs `w` permission, otherwise it not works. So some settings are required:
```shell
# Origin permission: drwxr-xr-x
chmod 777 -R $HOME/Music && chmod 777 -R $HOME/Videos
```

## Similar
- https://github.com/awesome-selfhosted/awesome-selfhosted
- https://github.com/bboysoulcn/awesome-dockercompose
