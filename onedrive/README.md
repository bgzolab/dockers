## Get token run firstly

```shell
docker run -it --name onedrive -v /home/bgzo/workspaces/docker/onedrive/conf:/onedrive/conf \
    -v "/home/bgzo/workspaces/docker/onedrive/data:/onedrive/data" \
    -e "ONEDRIVE_UID=1000" \
    -e "ONEDRIVE_GID=1000" \
    driveone/onedrive:latest
```