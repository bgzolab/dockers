# Docker compose selfhost

## Navigations

<!-- BEGIN NAV -->
| Port | Name | Desc | Nav |
| ---- | ---- | ---- | ---- |
| -- | [nvidia](https://github.com/NVIDIA/nvidia-docker) | GPU smoke test |  |
| -- | [onedrive](https://github.com/abraunegg/onedrive) | OneDrive client for Linux |  |
| -- | [rsstt](https://github.com/Rongronggg9/RSS-to-Telegram-Bot) | A Telegram RSS bot that cares about your reading experience |  |
| -- | [sunshine](https://github.com/LizardByte/Sunshine) | Self-hosted game stream host for Moonlight |  |
| -- | [telegram-to-rss](https://github.com/aigoncharov/telegram-to-rss) | Telegram channel to RSS |  |
| -- | [timemachine](https://github.com/mbentley/docker-timemachine) | SMB Time Machine backup target for macOS |  |
| `8001` | [alist](https://github.com/alist-org/alist) | A file list/WebDAV program that supports multiple storages, powered by Gin and Solidjs | [↗](http://192.168.31.20:8001) |
| `8002` | [dockge](https://github.com/louislam/dockge) | A fancy, easy-to-use and reactive self-hosted docker compose.yaml stack-oriented manager | [↗](http://192.168.31.20:8002) |
| `8003` | [fusion-rss](https://github.com/0x2E/fusion) | A lightweight, self-hosted friendly RSS aggregator and reader | [↗](http://192.168.31.20:8003) |
| `8004` | [gitea](https://github.com/go-gitea/gitea) | Git with a cup of tea, painless self-hosted git service | [↗](http://192.168.31.20:8004) |
| `8005` | [komga](https://github.com/gotson/komga) | Media server for comics/mangas/BDs/magazines/eBooks with API, OPDS and Kobo Sync support | [↗](http://192.168.31.20:8005) |
| `8006` | [logseq](https://github.com/logseq/logseq) | A local-first, non-linear, outliner notebook | [↗](http://192.168.31.20:8006) |
| `8007` | [motrix](https://github.com/agalwood/Motrix) | Download manager UI + aria2 | [↗](http://192.168.31.20:8007) |
| `8008` | [n8n](https://github.com/n8n-io/n8n) | Workflow automation for technical people | [↗](http://192.168.31.20:8008) |
| `8009` | [nezha](https://github.com/nezhahq/nezha) | Self-hosted server monitoring and status dashboard | [↗](http://192.168.31.20:8009) |
| `8010` | [open-webui](https://github.com/open-webui/open-webui) | User-friendly AI interface for Ollama / OpenAI | [↗](http://192.168.31.20:8010) |
| `8011` | [postgresql](https://hub.docker.com/_/postgres) | PostgreSQL + Adminer database playground | [↗](http://192.168.31.20:8011) |
| `8012` | [qbittorrent](https://github.com/c0re100/qBittorrent-Enhanced-Edition) | [Unofficial] qBittorrent Enhanced, based on qBittorrent | [↗](http://192.168.31.20:8012) |
| `8013` | [qinglong](https://github.com/whyour/qinglong) | Timed task management platform supporting Python3, JavaScript, Shell, Typescript | [↗](http://192.168.31.20:8013) |
| `8014` | [readeck](https://codeberg.org/readeck/readeck) | A bookmark manager and read-it-later app | [↗](http://192.168.31.20:8014) |
| `8015` | [rss-reader](https://github.com/srcrs/rss-reader) | 一个极简的RSS在线浏览工具 | [↗](http://192.168.31.20:8015) |
| `8016` | [suwayomi](https://github.com/Suwayomi/docker-tachidesk) | A rewrite of Tachiyomi for the Desktop | [↗](http://192.168.31.20:8016) |
| `8017` | [ttrss](https://github.com/HenryQW/Awesome-TTRSS) | A PHP and Ajax feed reader | [↗](http://192.168.31.20:8017) |
| `8018` | [wallabag](https://github.com/wallabag/wallabag) | Self-hosted read-it-later app | [↗](http://192.168.31.20:8018) |
| `8019` | [wewe-rss](https://github.com/cooderl/wewe-rss) | WeChat public account RSS generator | [↗](http://192.168.31.20:8019) |
| `8020` | [windows](https://github.com/dockur/windows) | Windows 11 VM in Docker | [↗](http://192.168.31.20:8020) |
| `8021` | [yacd](https://github.com/haishanh/yacd) | Yet Another Clash Dashboard | [↗](http://192.168.31.20:8021) |
| `8096` | [jellyfin](https://github.com/jellyfin/jellyfin) | The Free Software Media System | [↗](http://192.168.31.20:8096) |
<!-- END NAV -->


## Rules

### Names

1. 每个服务一个目录，放在仓库根目录；
2. 数据统一用相对路径 `./data` 挂载，并把运行时数据加进 `.gitignore`。
3. 目录名和 Compose 项目名一致，全小写、多词用 `-` 连接（kebab-case）。

> [!NOTE]
> 不要用 `camelCase` / `PascalCase` / 下划线 / 大写字母。原因：Compose 会把项目名强制转成小写，而 Dockge 按目录名精确匹配（区分大小写）。像 `fusionRss` 这样即使从 Dockge 启动，也会出现 `fusionRss` 和 `fusionrss` 两个条目，其中一个永远显示“不由 Dockge 管理”。
> - 反例：`fusionRss`；正例：`fusion-rss`、`rss-reader`、`open-webui`。

### Compose 文件头

每个 compose 文件的前两行固定为：

```yaml
# 服务描述
# https://项目地址
services:
  ...
```

`scripts/nav.py` 只从这里读描述和项目链接；端口仍然从 `ports` 读。改完 compose 后跑 `./scripts/nav.py`，README 导航表会整表重写。

### Ports

宿主机端口分三类，只有第三类需要编号：

1. **协议 / 客户端固定端口**：不动。
   - Gitea SSH `2222`
   - qBittorrent `6881/tcp+udp`、aria2 `6888/tcp+udp`
   - Sunshine `47984-47990/tcp`、`47998-48000/udp`、`48010`
   - Time Machine `137/138/139/445`
   - Windows RDP `3389/tcp+udp`
   - Jellyfin `8096`（客户端默认端口 + 局域网自动发现）
2. **内部依赖**：不发布 `ports`，同一个 Compose 网络里直接用服务名访问。
   - 例：`postgres`、`redis`、`flaresolverr`、ttrss 的 mercury/opencc。
   - `expose` 只是声明，不是访问控制；不写 `ports` 才是真的不对外。
   - aria2 RPC `6800` 默认也不发布；确实需要外部 AriaNg 时再临时加回，并确保 `.env` 里的 `ARIA2_RPC_SECRET` 非空。
3. **Web UI**：统一 `8001-8999`，按上面的 [Navigation](#navigation) 表取号。
   - 新服务取「当前最大号 + 1」，**不复用已退役的号**，避免旧书签误打到新服务。
   - 只改宿主机侧：`"80NN:<容器端口>"`，容器内端口不动。
   - 所有 `ports` 一律加引号；范围和 `/udp` 必须加。
   - 当前已用 `8001-8021`，下一个 `8022`；`8096` 被 Jellyfin 固定占用，顺延到它时跳过。
   - Navigation 表由 `scripts/nav.py` 从 compose 生成，是唯一端口登记表；不要手动改表，改完 compose 跑一次脚本即可。

改端口后要 `docker compose --env-file ../.env up -d` 重建容器，`restart` 不会重新分配端口。需要同步的外部 URL：

| 服务 | 变量 |
| --- | --- |
| gitea | `GITEA__server__ROOT_URL` |
| wallabag | `SYMFONY__ENV__DOMAIN_NAME` |
| ttrss | `SELF_URL_PATH` |
| n8n | `WEBHOOK_URL` / `N8N_HOST` |

> 不要在 `.env` 里给每个服务建端口变量。端口一年改不了几次，上面的表更好查；`.env` 只放密码、路径、主机 IP 这类跨文件共享或需要保密的值。

## All container managed by dockge

Dockge 只把 stacks 根目录（容器内 `/opt/stacks`，即本仓库根目录）下、包含 `compose.yml` / `compose.yaml` / `docker-compose.yml` / `docker-compose.yaml` 的一级目录当作自己管理的 stack；[^dockge-judge]

[^dockge-judge]: 判断逻辑就是 `fs.existsSync(path)`（`backend/stack.ts` 的 `isManagedByDockge`）。同时它用 `docker compose ls --all` 读取宿主机上所有 Compose 项目（包括已退出的）。只在后者出现、没有同名目录的项目就会显示为未管理：只能查看，不能编辑、启停。

常见原因：

1. Compose 文件在仓库外启动（例如 `/opt/...`），容器还在。
2. 目录已删除或改名，旧容器还在。
3. 目录名和 Compose 项目名大小写不一致（Compose 项目名强制小写，Dockge 目录名区分大小写）。

处理方式：

1. 把 compose 文件放进 `仓库根/<小写项目名>/`，数据用相对路径挂载，然后从 Dockge 启动；
2. 不再需要的旧项目用 `docker rm -f <容器>` 清掉，`docker compose ls` 里没有它，提示自然消失。

## Command References

日常的拉镜像、起停容器、看日志都不需要 `sudo`。只有安装 Docker Engine 和修改系统服务需要 root，而且只做一次。

### 一次性系统安装（需要 sudo）

```shell
# Install Docker Engine
# on mint via: https://docs.docker.com/engine/install/ubuntu/
for pkg in docker.io docker-doc docker-compose docker-compose-v2 podman-docker containerd runc; do sudo apt-get remove $pkg; done
sudo apt-get install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
# if on ubuntu it should be VERSION_CODENAME instead of UBUNTU_CODENAME
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \\
  $(. /etc/os-release && echo "$UBUNTU_CODENAME") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo systemctl enable --now docker

# 把当前用户加入 docker 组，之后执行 docker 不需要 sudo
sudo usermod -aG docker "$USER"
# 重新登录，或立即在当前 shell 生效
newgrp docker
```

> WSL1 没有 systemd 时，用 `sudo dockerd` 手动启动。

### 普通用户操作（无需 sudo）

Compose 文件在各自的服务目录里，共享变量在仓库根目录的 `.env`。

```shell
# Docker Compose 也可以只装在用户目录
DOCKER_CONFIG=${DOCKER_CONFIG:-$HOME/.docker}
mkdir -p "$DOCKER_CONFIG/cli-plugins"
curl -SL https://github.com/docker/compose/releases/download/v2.27.1/docker-compose-linux-x86_64 -o "$DOCKER_CONFIG/cli-plugins/docker-compose"
chmod +x "$DOCKER_CONFIG/cli-plugins/docker-compose"

# 进入某个服务目录后操作（示例：gitea）
cd gitea
docker compose --env-file ../.env up -d      # 启动 / 更新
docker compose ps                            # 查看状态
docker compose logs -f                       # 跟踪日志
docker compose rm                            # 删除已停止的容器
docker compose down                          # 停止并删除容器

# 也可以从仓库根目录指定 compose 文件
docker compose -f gitea/docker-compose.yml --env-file .env up -d

# 全局查看
docker ps
docker logs -f gitea
docker info
```

代理统一在路由器处理，各 compose 文件不再注入 `http_proxy`。

### Scripts

| 脚本 | 作用 |
| --- | --- |
| `scripts/check.sh` | 校验所有 tracked stack 的 compose 语法；再跑 `nav.py --check`，确认导航表没有过期 |
| `scripts/nav.py` | 读取每个 compose 前两行（第 1 行描述、第 2 行 URL）和 compose 端口，强制重写 README 导航表；有 Web 端口才生成 `↗`，无端口 Nav 留空，同时检查宿主机端口重复 |
| `scripts/up.sh` | 批量 `up -d --remove-orphans`；`--running` 只重部署所有 service 都 running 的 stack，有任何 restarting/stopped 就跳过 |

```shell
./scripts/check.sh                       # 全量校验
./scripts/nav.py                         # 重新生成导航
./scripts/nav.py --check                 # 只检查，不写文件
./scripts/up.sh --changed                # 只重启本次 git 改动涉及的 stack
./scripts/up.sh --changed HEAD~1         # 改动已经提交时，对比上一个提交
./scripts/up.sh --running                # 只重部署所有 service 都 running 的 stack
./scripts/up.sh --running --dry-run      # 先看会动哪些完整 running 的 stack
./scripts/up.sh --all --dry-run          # 先看要执行哪些命令
./scripts/up.sh gitea dockge             # 指定 stack
./scripts/up.sh --all --pull             # 先拉镜像再重建
```

README 的导航表现在是**纯生成物**：每个 compose 文件前两行是描述和项目 URL，端口在 `ports` 里；改完跑 `./scripts/nav.py`，脚本会整表覆盖，不要手改表格。有 Web 端口的 Nav 生成 `↗`，没有端口的 Nav 留空。

> [!NOTE]
Emby mount volume drive needs `w` permission, otherwise it not works. So some settings are required:
```shell
# Origin permission: drwxr-xr-x
chmod 777 -R $HOME/Music && chmod 777 -R $HOME/Videos
```

## Git hooks

```shell
# Enable the secret-scanning pre-commit hook (once per clone)
git config core.hooksPath .githooks
```

The hook scans staged additions and blocks likely secrets. Use `git commit --no-verify` only when you are sure it is a false positive.

## Similar Repository

1. https://github.com/awesome-selfhosted/awesome-selfhosted
2. https://github.com/bboysoulcn/awesome-dockercompose
