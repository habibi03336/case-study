# 텍스트와 바이너리

개발을 하다보면 `텍스트`과 `바이너리`가 구분된다는 것을 종종 보게된다. 예를 들어, HTTP의 경우 텍스트로 데이터를 전송하지만 HTTP2의 경우 바이너리로 데이터를 전송한다.

그런데 텍스트 데이터, 바이너리 데이터가 정확히 어떻게 다른 것일까? 텍스트 데이터도 결국에는 바이너리로 저장이 되는 것은 마찬가지일텐데 말이다. 텍스트와 바이너리가 어떻게 다른지 한 번 알아보자.

# 숫자의 저장

## 텍스트로 저장

16을 저장한다고 해보자. 텍스트로 저장하게 되면 문자 "1"과 "6"으로 저장이 된다. 아스키코드로 "1"이 Ox31이고 "6"이 0x36 이므로 0x31 0x36 이렇게 2바이트로 저장이 된다.

```shell
❯ hexdump -C 16.txt
00000000  31 36                                             |16|
00000002
```

-C 옵션 없이 조회를 하면 아래와 같이 뒤짚힌 듯이 출력이 된다. little-endian system이기 때문에 그러하다. little-endian system은 데이터를 메모리의 뒤쪽부터 저장하는 방식이다. 추가적으로 hexdump는 2바이트씩 데이터를 읽어오기 때문에 2바이트 단위로 순서가 뒤짚힌 듯이 보인다.

- 참고: <https://stackoverflow.com/questions/72151172/why-does-hexdump-reverse-the-input-when-given-xff-x00>

```shell
❯ hexdump  16.txt
0000000 3631
0000002
```

<details>
<summary>텍스트 파일 생성 코드</summary>

```c
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

static int write_to_file(void)
{
    FILE *fp = NULL;

    fp = fopen("16.txt", "w");
    if(fp == NULL){
        perror("fopen error\n");
        return -1;
    }
    fputs("16", fp);
    printf("file position at %ld", ftell(fp));
    fclose(fp);
    return 0;
}

int main(int argc, char **argv){
    write_to_file();
    return 0;
}
```

</details>

## 바이너리로 저장

바이너리로 저장하면 16은 Ox10으로 1바이트로 저장할 수 있다. c에서 1바이트 정수형인 char을 활용해 1바이트로 저장한 후 확인해 보면 다음과 같다.

```shell
❯ hexdump -C 16.bin
00000000  10                                                |.|
00000001
```

<details>
<summary>바이너리 파일 생성 코드</summary>

```c
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

static int write_to_file(void)
{
    FILE *fp = NULL;
    if(!(fp = fopen("16.bin", "w"))){
        return -1;
    }
    char sixteen = 16;
    fwrite(&sixteen, sizeof(char), 1, fp);
    printf("file position at %ld", ftell(fp));
    fclose(fp);
    return 0;
}

int main(int argc, char **argv){
    write_to_file();
    return 0;
}
```

</details>

## 큰 수를 저장할 때 텍스트와 바이너리의 크기 차이

숫자가 커질 수록 두 방식의 크기 차이는 커진다. 현재 시간을 밀리초로 받으니 1689671601194이 나왔다. 이를 바이너리로하면 long타입의 8byte로 저장할 수 있다. 텍스트로 하면 각 자리가 1byte이므로 13byte가 된다.

일반화해서 보면 숫자 자리수가 n일 때 텍스트 형식은 O(n) 바이트의 크기를 가지게 된다. 반면 바이너리의 경우 1bit가 추가 될 때마다 지수적으로 표현할 수 잇는 크기가 커지게 된다. 따라서 대략 O(log n) 바이트의 크기를 가지게 된다.

하지만 숫자 자리수가 무지막지하게 커지는 경우는 잘 없기 때문에 n과 logn의 차이가 생각보다 그렇게 중요하지는 않을 수도 있겠다는 생각이 든다.

# 텍스트의 저장

텍스트의 경우 어떻게 저장될까? 결과를 보면 데이터가 저장된 모습이 거의 똑같다. 어쩌면 당연하다. 다만 텍스트 형식은 36 바이트가 나왔고, 바이너리 형식은 37 바이트가 나왔다. c에서 문자열을 처리하는 방식과 관련이 있는 것 같다. 36자인데 char[]의 크기는 37로 나온다.

```shell
❯ hexdump -C text.txt
00000000  68 65 6c 6c 6f 20 77 6f  72 6c 64 21 20 74 68 69  |hello world! thi|
00000010  73 20 69 73 20 68 65 6c  6c 6f 20 66 72 6f 6d 20  |s is hello from |
00000020  6d 61 72 73                                       |mars|
00000024
```

```shell
❯ hexdump -C text.bin
00000000  68 65 6c 6c 6f 20 77 6f  72 6c 64 21 20 74 68 69  |hello world! thi|
00000010  73 20 69 73 20 68 65 6c  6c 6f 20 66 72 6f 6d 20  |s is hello from |
00000020  6d 61 72 73 00                                    |mars.|
00000025
```

# 구조체의 저장

바이너리 파일의 경우 구조체를 저장하기 좋다. 아래와 같은 구조체를 저장하면 16바이트로 이름을 저장하고 4바이트로 나이를 저장한다. 파일을 읽어올 때 매핑되는 구조체를 명시하면, 구조체에 정의된 데이터 타입의 크기에 맞춰 데이터를 읽어온다.

```c
struct person
{
    char name[16];
    int age;
};
```

구조체 크기인 20 바이트씩 데이터가 순차적으로 저장된 것을 알 수 있다. 0x28은 사실 나이 데이터인데 ASCII 상 '('로 표시된 것도 확인할 수 있다.

```shell
❯ hexdump -C person_info
00000000  6b 69 6d 00 00 00 00 00  00 00 00 00 00 00 00 00  |kim.............|
00000010  28 00 00 00 6d 69 6b 65  00 00 00 00 00 00 00 00  |(...mike........|
00000020  00 00 00 00 17 00 00 00                           |........|
00000028
```

<details>
<summary>구조체를 파일로 저장하는 코드</summary>

```c

static int write_data(struct person *p)
{
    int fd;
    ssize_t ret;
    fd = open("person_info", O_CREAT | O_WRONLY | O_APPEND, 0644);
    if(fd == -1){
        printf("open() fall\n");
        return -1;
    }
    ret = write(fd, p, sizeof(struct person));
    if(ret == -1)
    {
        printf("write has failed");
        close(fd);
        return -1;
    } else if (ret != sizeof(struct person))
    {
        printf("write has failed, partial write");
        close(fd);
        return -1;
    }
    close(fd);
    return 0;
}

int main(int argc, char **argv)
{
    struct person persons[] = {
        {"kim", 40},
        {"mike", 23}
    };
    write_data(&persons[0]);
    write_data(&persons[1]);
    return 0;
}
```

</details>

<br>

텍스트 파일로 구조화된 데이터를 저장하려면 json이나 xml과 같은 구조적인 형식을 활용하면 된다.

바이너리로 데이터를 저장하면 용량적인 이점은 있을 수 있는 대신 데이터를 로드할 때 타입을 정확하게 맞춰줘야 한다. 이는 정적 타이핑 언어와 잘 맞는 특징이다. 정적 타이핑 언어의 경우 읽어오는 데이터의 타입이 명확하지 않으면 프로그래밍이 오히려 어렵다. 반면에 json등의 텍스트 파일로 저장을 하면 용량이 조금 더 크지만 데이터를 보다 동적으로 저장할 수 있다. 이는 동적 타이핑 언어와 잘 맞는 특성이다. 동적 타이핑 언어의 경우 읽어오는 데이터의 형식이 명확하지 않아도 된다. 따라서 읽어오는 데이터에 대한 외부적인 정보 없이도 일단 읽어와서 확인해 볼 수 있다. 개발하는데 좀 더 편하게 느껴질 수 있는 지점이다.

---

**참고**

- 인프런, 리눅스 시스템 프로그래밍 - 이론과 실습
