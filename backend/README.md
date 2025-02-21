# 프로젝트 실행 가이드

## 1. Docker 설치
서버를 실행하기 위해서는 Docker가 필요합니다. 아래의 링크를 참고하여 운영체제에 맞는 Docker를 설치하세요.

- [Docker 다운로드](https://www.docker.com/get-started)

Docker 설치 후, 정상적으로 동작하는지 확인하기 위해 터미널에서 다음 명령어를 실행하세요.

```sh
docker --version
```

정상적으로 설치되었다면 Docker의 버전이 출력됩니다.

## 2. 프로젝트 디렉토리로 이동

터미널을 열고 해당 프로젝트가 위치한 경로로 이동합니다.

```sh
cd /path/to/project
```

**예시:**

```sh
cd ~/my-project
```

## 3. Docker Compose를 사용하여 서버 실행

Docker Compose를 사용하여 컨테이너를 실행하려면 다음 명령어를 입력하세요.

```sh
docker compose up -d
```

### 명령어 설명:
- `docker compose up` : `docker-compose.yml` 파일을 기반으로 컨테이너를 실행합니다.
- `-d` : 백그라운드 모드로 실행하여 터미널을 차지하지 않도록 합니다.

## 4. 실행 상태 확인

아래 명령어를 사용하여 실행 중인 컨테이너 목록을 확인할 수 있습니다.

```sh
docker ps
```

정상적으로 실행되었다면, 컨테이너 리스트에 해당 프로젝트가 표시됩니다.

## 5. 서버 종료

서버를 종료하려면 다음 명령어를 실행하세요.

```sh
docker compose down
```

## 6. 추가 설정 및 문제 해결

### 포트가 충돌하는 경우
이미 사용 중인 포트와 충돌할 경우, `docker-compose.yml` 파일에서 포트 설정을 변경하거나 실행 중인 다른 컨테이너를 중지하세요.

```sh
docker stop <CONTAINER_ID>
```

### 로그 확인
서버 실행 중 문제가 발생하면 다음 명령어를 사용하여 로그를 확인할 수 있습니다.

```sh
docker compose logs
```

---

위 단계를 따라 하면 Docker 환경에서 서버를 쉽게 실행할 수 있습니다. 🚀

