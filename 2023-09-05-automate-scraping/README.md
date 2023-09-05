# 스크래핑 파이썬 스크립트 실행 자동화

재무제표 데이터와 환율 데이터를 특정 주기마다 스크래핑하는 스크립트를 서버 쪽에서 동작시키려고 한다. 이것을 어떻게 실현할지까지 여러가지 선택지가 있다.

1. 서버 OS의 크론탭 활용 vs 도커 컨테이너의 크론탭 활용

   서버 OS의 크론탭을 활용하면, 잠깐만 동작하는 도커 컨테이너를 항상 켜놓을 필요가 없어서 좋다.

   도커 컨테이너의 크론탭을 활용하면, 서버 머신을 건드리지 않고, 크론탭 설정 또한 독립적으로 관리할 수 있어서 좋다.

   **내가 돌리는 스크립트는 하루 및 한 달 주기로 하나의 머신에서 아주 잠깐만 돌아가면 된다. 따라서 이를 위해서 도커 컨테이너를 계속 켜놓는 것은 비효율적이다. 따라서 서버 측 크론탭을 활용하기로 했다.**

2. 서버 OS 크론탭을 활용하는 경우, 파이썬 가상 환경 활용 vs 도커 이미지 활용

   파이썬의 경우 라이브러리를 환경을 관리하는 것이 필요하다. 서버에 접속해서 anaconda와 같은 파이썬 가상환경을 활용할 수도 있고, 도커 이미지를 활용할 수도 있다. 도커 이미지를 활용하는 것이 좀 더 서버 머신에 독립적이게 관리할 수 있어서 좋아보인다.

   **서버에 접속해서 아나콘다를 설치하고 라이브러리를 다운받고 하는 과정을 하기가 싫었다. 그래서 로컬에서 도커 이미지를 하나 만들고 이 이미지를 서버에서 쓰기로 했다.**

# 스크립트 돌아가는 방식

1. 크론탭이 쉘 스크립트를 실행시킨다.
2. 쉘 스크립트가 도커 이미지를 실행시킨다.
3. 도커 컨테이너 내에서 파이썬 스크립트를 실행한다.

# 파이썬 환경용 도커 이미지 만들기

도커 이미지는 Dockerfile로부터 정의된다.

## 이미지 사이즈 이슈

python:3.8 이미지를 베이스로 하여 이미지를 구성할 경우 데비안OS를 사용하게 되고, 이미지 사이즈가 1.1G나 되었다. 너무 큰 것 같아서 알아보니 컨테이너용 경량 리눅스인 alpine이 있다는 것을 알게되었다. 이를 활용하니 이미지 크기가 129MB로 1/10 수준으로 줄어들었다. [alpine 기반 파이썬의 사용을 지양해야한다는 내용도 있던데,](https://eden-do.tistory.com/64) 내가 실행시키는 파이썬 스크립트가 매우 작으므로 큰 문제가 될 거 같지는 않아 alpine을 사용하기로 했다.

## 컨테이너 실행 이슈

이미지가 실행 될 때마다 처음에 스크래퍼의 최신 코드를 받아와서 설치하는 로직을 추가하고 싶었다. ENTRYPOINT 설정을 활용하면, 이미지를 실행할 때 옵션으로 주는 명령어가 무시되는 문제가 있었다. COMMAND 설정을 활용하면 옵션으로 주어지는 명령어만 실행했다.

챗GPT에게 물어보니 ENTRYPOINT를 설정하면 dockerfile에 있는 CMD와 컨테이너 실행시 옵션으로 주는 명령어 모두 ENTRYPOINT의 인자값으로 넘어간다는 것을 알게되었다. 그렇기 때문에 shell script를 하나 만들어서 그 안에 필요한 커맨드를 넣고 마지막에 `exec "$@"`를 추가해서 인자로 넘어온 명령을 실행하게 해줄 수 있다. 그렇게 하면 컨테이너 실행시 항상 특정 명령어가 실행되고 그 이후에 사용자가 넘긴 명령어가 실행되게 된다.

```dockerfile
FROM alpine
RUN \
    apk update && \
    apk add py3-pip && \
    pip install python-dotenv && \
    apk add git && \
    git clone https://github.com/habibi03336/dart-scraper.git && \
    cd dart-scraper && \
    pip install -r requirements.txt && \
    pip install . && \
    cd /etc && \
    echo > entrypoint.sh '#!/bin/bash' && \
    echo >> entrypoint.sh 'cd ../dart-scraper' && \
    echo >> entrypoint.sh 'git pull' && \
    echo >> entrypoint.sh 'pip install --root-user-action=ignore .' && \
    echo >> entrypoint.sh 'exec "$@"' && \
    chmod a+x entrypoint.sh

ENTRYPOINT ["sh", "/etc/entrypoint.sh"]
```

# 컨테이너 내부에서 파이썬 스크립트를 동작시키는 쉘스크립트

1. 볼륨(-v) 기능을 활용해 현재 경로의 스크립트 파일을 컨테이너 내부의 경로와 연동한다. `-v {호스트경로}:{컨테이너 경로}`

2. 이미지 이름(python-scrape-env) 뒤에 실행할 명령어를 적는다.

   docker run --rm -v $(pwd):/home python-scrape-env python /home/hello.py

# 크론탭에 등록하기

서버 머신의 크론탭에 특정 주기마다 쉘스크립트를 동작하도록 등록해준다. 서버 머신은 UTC 기준으로 크론탭을 동작시킨다. 한국 시간은 UTC+9이므로 이를 반영해서 등록해준다.

1. 매일 한국 시간 새벽 3시 재무제표 데이터 스크래핑을 해야한다.
2. 매월 1일 UTC 기준 자정에 환율 데이터 스크래핑을 해야한다.

한국 시간 03:00은 UTC 기준 18:00 이다. 크론탭 문법을 참고하여 다음과 같이 크론탭에 등록해준다.

<div style="text-align: center;">
    <img src="https://raw.githubusercontent.com/habibi03336/case-study/master/2023-09-05-automate-scraping/img/crontab-syntax.webp" alt="quick sort recursion" width="500"/>
</div>

```crontab
0 18 * * * sh /home/ec2-user/db/automate/activate_finance_scrape.sh
0 0 1 * * sh /home/ec2-user/db/automate/activate_exchange_rate_scrape.sh
```

# 결과물 및 후기

<https://github.com/habibi03336/auto-scrape-finance-db>이 이번 작업으로 나온 결과물이다. 저번에 SSL 인증서 발급을 자동화한적이 있었는데, 이번에 좀 더 복잡한 자동화를 해봤다. 이제 자동으로 재무제표와 환율 데이터가 스크래핑된다고 생각하니 뭔가 뿌듯하다.
