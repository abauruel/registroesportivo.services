#### Install docker on RaspiberryPi OS
```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker pi
```

```shell
docker compose build
dockercompose up -d
```

```shell
docker compose logs -f
```