# 한국어 PDF파일 내용 전문검색 기능

내가 운영하고 있는 인문사회학회 웹페이지에 글이 이제 500개 정도가 있다. 매 학기 120개 정도의 글이 더 쓰인다. 글이 점점 많아지다보니 전문 검색 기능을 넣고 싶어졌다. 특정 단어를 중심으로 어떤 이야기들이 오갔는지 보거나, 특정 사람이 얼마나 인용되었나 등의 내용을 볼 수 있으면 재미있을 것 같았다.

글을 PDF 파일로 올리기 때문에 `PDF에서 글을 추출하고`, `글을 문장단위로 나누고`, 그 문장 단위로 나뉜 글을 `전문검색을 지원하는 엘라스틱서치 데이터베이스에 넣어서` 기능을 제공하면 되겠다고 생각했다.

## PDF에서 글을 추출하기

기존에도 사용한 단어의 수를 통계내주는 기능을 제공하고 있었다. 이 기능을 위해서 PDF에서 글을 추출해야했다. PDF는 문서처럼 보이지만 사실은 문서보다 이미지에 보다 가까운 형식이다. PDF는 문자열이 아니라 각 글자와 그 위치를 정의한 데이터를 가지고 있다. 따라서 텍스트 파일을 읽을 때 처럼 손쉽게 텍스트를 읽을 수는 없다.

텍스트 추출을 위해 python의 pdfminer 라이브러리를 사용하려고 했다. 이 라이브러리는 글자의 위치값을 기준으로 휴리스틱 알고리즘을 적용해 문자열을 반환하는 기능을 제공했다. 하지만 몇몇 pdf에서 텍스트를 제대로 추출하지 못하는 경우가 있었다.

이러한 문제로 OCR로 텍스트를 추출하는 방법을 시도해봤다. OCR(광학문자인식)은 이미지 속에서 글자를 읽어내는 기술이다. 찾아보니 tesseract, paddleOCR, easyOCR이 가장 대표적인 OCR 프로젝트들이었다. 각 프로젝트 별로 다음과 같은 특징이 있었다.

|               | Tesseract | PaddleOcr | EasyOcr |
| ------------- | --------- | --------- | ------- |
| CPU성능       | 좋다      | 안좋음    | 중간    |
| 한글 인식성능 | 중        | 중상      | 중하    |
| 구두점 인식   | 가능      | 불가능    | 가능    |
| 띄어쓰기 구분 | 상        | 중하      | 중하    |

모든 프로젝트의 한글 인식 성능이 만족스럽지 못했다. Tesseract나 PaddleOCR은 추가로 학습을 하는 파인튜닝이 가능해서 이를 적용해볼까 검토해봤지만, 한글 인식 성능 뿐아니라 다른 문제들도 있어서 파인튜닝만 가지고는 만족할수 없는 상태였다. 또한 학습데이터 마련, 학습 방법 습득 등 허들도 많았다.

또한 Tesseract 같은 경우는 한글 인식으로 해놓으면 정말 한글만 인식을 해서 중간에 나오는 'TV'같은 글자를 제대로 인식하지 못했다. 그렇다고 한글+영어 인식을 하면 한글도 영어로 인식하는 경우가 많았다. PaddleOCR의 경우 가장 한글 인식 성능이 좋았지만 중간중간 오타가 난것처럼 인식하는 경우가 많고, 띄어쓰기 구분이 잘 안되는 경우 모든 글자를 띄어쓰기 없이 인식했다. 문장 단위로 나누고자하는데 구두점을 인식하지 못하는 것도 큰 단점이었다.

결국 OCR도 쓰지 못한다는 결론을 내렸다. 처음으로 돌아가서, 왜 python의 라이브러리들이 제대로 텍스트 추출을 하지 못하는지 조사해봤다. PDF에는 어쨌든 글자 데이터가 모두 있고, 그 위치를 기준으로 한 줄 한 줄 읽는 알고리즘을 적용하면 텍스트가 제대로 추출되는데 큰 문제가 없는게 맞는 것이었다.

여러 케이스를 좀 조사해 보니 애플 OS의 엔진으로 PDF로 변환된 경우 pdfminer가 제대로 텍스트 추출하지 못했다. 구두점이나 영어 단어의 순서가 엉켜있는 채로 추출되었다. 애플 OS에서 사용하는 PDF 관련 엔진인 Quartz가 다른 엔진과는 다소 다른 스펙을 따르는 것이 아닌가 싶다.

그러면 애플의 Quartz엔진의 스펙을 고려해서 텍스트를 추출해주는 라이브러리를 찾으면 되지 않을까? 하는 생각이 들었고, pymupdf, pdfplumber, pdftotext 등의 라이브러리를 시도해봤다. 그 결과 pymupdf와 pdfplumber는 pdfminer와 동일한 문제가 있었지만, pdftotext의 경우 애플 PDF에서도 깔끔하게 텍스트를 추출하는 것을 확인할 수 있었다.

## 텍스트를 문장 별로 나누기

텍스트를 문장 별로 나누어 저장해야 더 깔끔한 검색 결과를 보여주고, 활용도가 더 높을 것이라고 생각했다. 처음에는 구두점이나 `?`, `!`, `"` 와 같은 특수문자를 기준으로 문장을 나눠야 하나? 하는 생각을 했다. 대부분의 경우 이러한 패턴으로 처리할 수는 있을 것이지만 또 항상 그렇다고는 말 할 수 없었다.

예를 들어 일반적으로 `?`뒤에 빈 칸이 있으면 문장이 끝났음을 나타내지만, '믿는 종교가 무엇인가? 라는 질문에 나는 항상 무교라고 대답한다.'라고 쓸 수도 있다. 종종있는 이러한 패턴때문에 규칙중심으로 문장을 나누는 것에 확신이 없었다.

[좀 찾아보니 Kiwi라는 라이브러리에서 문장 분리 기능을 제공하는 것을 발견했다.](https://github.com/bab2min/kiwipiepy/tree/main/benchmark/sentence_split) 이 라이브러리를 검토해보니 문장 분리 성능이 나름 만족할만 했다.

```python
from kiwipiepy import Kiwi
kiwi = Kiwi()

text = '''믿는 종교가 무엇인가? 라는 질문에 나는 항상 무교라고 대답한다.
특별히 믿는 종교가 없기에 주기적으로 교회를 다니는 것도 아니고 절을 다니는 것도 아니다.'''
sentences = kiwi.split_into_sents(text)
print(sentences)
# [
#    Sentence(text='믿는 종교가 무엇인가? 라는 질문에 나는 항상 무교라고 대답한다.', start=0, end=36, tokens=None, subs=[]),
#    Sentence(text='특별히 믿는 종교가 없기에 주기적으로 교회를 다니는 것도 아니고 절을 다니는 것도 아니다.', start=37, end=87, tokens=None, subs=[])
# ]
```

## 엘라스틱서치 설정하기

엘라스틱 서치는 역색인을 통해 전문 검색 기능을 제공한다. 물론 SQL에서도 비슷한 방식을 적용할 수 있다.
예를 들어, id가 12인 "나는 이타심을 다른 사람의 마음을 헤아려보는 것이라고 정의하고자 한다." 라는 문장과 id가 13인 "이렇게 정의하면 이타심은 꼭 필요한 것이라는 생각이 든다."라는 문장이 있다고 해보자. 이 문장의 명사만 추출해서 인덱스가 걸린 many-to-one 테이블에 저장하여 문장 검색을 지원한다고 해보자. 그러면 many-to-one 테이블에 다음과 같이 저장된다.

| 단어   | 문장id |
| ------ | ------ |
| 나     | 12     |
| 마음   | 12     |
| 사람   | 12     |
| 생각   | 13     |
| 이타심 | 12     |
| 이타심 | 13     |
| 정의   | 12     |
| 정의   | 13     |

이런식으로 전문 검색을 지원할 수도 있다. 하지만 이 방식은 매우 비효율적이다. 왜냐하면 모든 단어의 개수만큼 인덱스의 길이가 길어지기 때문이다. 사실 쓰이는 단어의 종류 자체는 한정적이기 떄문에 같은 단어를 별도의 인덱스로 저장하는 비효율적이다. 더욱이 인덱스가 커질 수록 테이블 인서트 및 삭제 성능도 떨어지기 때문에 성능에 영향이 크다고 할 수 있다. 따라서 아래처럼 저장하는 것이 더 효율적이다.

| 단어   | 문장id |
| ------ | ------ |
| 나     | 12     |
| 마음   | 12     |
| 사람   | 12     |
| 생각   | 13     |
| 이타심 | 12, 13 |
| 정의   | 12, 13 |

이렇게 하면 다른 문장이 새로 색인될 때도 겹치는 단어에 대해서는 추가적인 로우를 만들 필요가 없다. 이렇게 하는 방식을 역색인이라고 한다. 이렇게 보면 `역색인은 중복된 키가 많을 때 색인을 압축해서 표현하는 방법`일 뿐이다.

어쨌든 엘라스틱 서치는 이러한 역색인 방식을 제공하여 검색 기능의 성능을 높인다. 또한 역색인을 하기 위한 텍스트 데이터 전처리 기능을 제공하는 등 편의기능을 많이 제공한다.

### 한글 역색인을 위한 엘라스틱 서치 설정

영어는 의미단위가 띄어쓰기로 잘 나뉘는 편이다. 'we love seoul'라는 문장이 있을 때, we, love, seoul 색인해 놓으면 각각의 색인을 키워드로 'we love seoul' 문장을 찾을 수 있고, 이 과정이 자연스러워 보인다. 하지만 한글의 경우 '우리는 서울을 사랑해요'라는 문장이 있을 때, 띄어쓰기로 단어를 구분해 색인을 하면 '우리는', '서울을', '사랑해요'로 색인이 된다. 따라서 '우리', '서울', '사랑' 이런 키워드로는 문장을 찾을 수 없고 반드시 '우리는', '서울을', '사랑해요' 이렇게 조사까지 붙여야 검색이 가능하다.

따라서 이런 한국어의 특성에 맞춰 문장을 분석하고 색인을 해줘야한다. 다행히도 엘라스틱서치가 공식적으로 지원하는 한글 형태소 분석기(tokenizer)인 nori가 있다.

#### 추가 파일 다운로드

엘라스틱서치에 nori 형태소 분석기를 설치하기 위해서는 엘라스틱서치 폴더에 들어가서 아래 명령어를 실행해준다.

```sh
bin/elasticsearch-plugin install analysis-nori
```

<https://www.elastic.co/guide/en/elasticsearch/plugins/current/analysis-nori.html>

#### 인덱스 생성시, 분석기 설정 및 매핑에 적용

이제 엘라스틱서치에 인덱스를 만들어주면서, nori 형태소 분석기를 사용한다고 설정하고 어떤 필드에 적용할 것인지도 선언해준다. 엘라스틱서치의 인덱스는 한 번 만들어지면 수정이 어렵기 때문에 처음 인덱스를 만들 때 좀 더 신경을 쓰는게 좋다.

```json
curl -X PUT localhost:9200/{index이름} -H 'Content-Type: application/json' -d '
{
    "settings": {
        "index": {
            "analysis": {
                "tokenizer": {
                    "nori_mixed": {
                        "type": "nori_tokenizer",
                        "decompound_mode": "mixed"
                    }
                },
                "filter": {
                    "default_filter": {
                        "type": "nori_part_of_speech",
                        "stoptags": [
                        "E", "IC", "J", "MAG", "MAJ",
    "MM", "SP", "SSC", "SSO", "SC",
    "SE", "XPN", "XSA", "XSN", "XSV",
    "UNA", "NA", "VSV"
                        ]
                    }
                },
                "analyzer": {
                    "korean_analyzer": {
                        "tokenizer": "nori_mixed",
                        "filter": ["default_filter"]
                    }
                }
            }
        }
    },
    "mappings": {
        "properties": {
            "sentence": {
                "type":"text",
                "analyzer": "korean_analyzer"
            }
        }
    }
}
'
```

analyzer는 `캐릭터필터 => 토크나이져(형태소분석기) => 토큰필터`의 3 단계가 있다. 토크나이저가 합성어와 어근을 모두 저장하면 좋겠어서 decompound_mode를 mixed로 설정해주었다. 그리고 조사와 같이 의미가 없는 단어에는 색인을 제외해주기 위해서 토큰필터를 정의해 주었다. 그리고 내가 설정한 토크나이저와 토큰필터를 합쳐 korean_analyzer를 정의해주었다. 그리고 매핑 설정에 이 korean_analyzer를 적용할 필드를 정의해주었다.

- 내가 설정한 analyzer는 캐릭터필터 없이 토크나이저와 토큰필더가 있다.
- 캐릭터 필터는 토크나이져에 들어가기 전에 원문에서 특정 캐릭터나 문자열을 삭제하거나 변환하는 기능이다.
- 토큰필터는 토큰나이저의 결과로 나온 토큰을 변형 및 삭제하는 기능이다.
- [인덱스 설정하는 문법](https://esbook.kimjmin.net/06-text-analysis/6.3-analyzer-1/6.4-custom-analyzer)
- [nori 형태소 분석기 관련 설정들](https://esbook.kimjmin.net/06-text-analysis/6.7-stemming/6.7.2-nori)

#### 확인해주기

다음과 같은 명령어로 analyzer가 어떤 분석결과를 내는지 확인해 볼 수 있다.

```sh
curl -X GET localhost:9200/test/_analyze -H 'Content-Type:application/json' -d '{"analyzer": "korean_analyzer", "text": ["주변인의 감정으로 세상을 구경하고 있던 날이었다."]}'
```

결과는 다음과 같았다. 합성어인 '주변인'이 '주변', '인', '주변인' 3가지로 잘 분석되고, 조사와 같은 검색키워드가 되지 않는 토큰이 없는 걸 볼 수 있다.

<details>
<summary>korean_analyzer 분석결과</summary>

```json
{
   "tokens":[
      {
         "token":"주변인",
         "start_offset":0,
         "end_offset":3,
         "type":"word",
         "position":0,
         "positionLength":2
      },
      {
         "token":"주변",
         "start_offset":0,
         "end_offset":2,
         "type":"word",
         "position":0
      },
      {
         "token":"인",
         "start_offset":2,
         "end_offset":3,
         "type":"word",
         "position":1
      },
      {
         "token":"감정",
         "start_offset":5,
         "end_offset":7,
         "type":"word",
         "position":3
      },
      {
         "token":"세상",
         "start_offset":10,
         "end_offset":12,
         "type":"word",
         "position":5
      },
      {
         "token":"구경",
         "start_offset":14,
         "end_offset":16,
         "type":"word",
         "position":7
      },
      {
         "token":"있",
         "start_offset":19,
         "end_offset":20,
         "type":"word",
         "position":10
      },
      {
         "token":"날",
         "start_offset":22,
         "end_offset":23,
         "type":"word",
         "position":12
      },
      {
         "token":"이",
         "start_offset":23,
         "end_offset":24,
         "type":"word",
         "position":13
      }
   ]
}
```

</details>

### 색인 및 검색 확인

마지막으로 실제로 데이터를 넣어보고 검색이 잘되는지 확인해보고자 한다. 다음과 같이 REST API로 데이터를 저장할 수 있다. 두 문장을 저장해줬다.

```sh
curl -X POST localhost:9200/test/_doc/t1 -H 'Content-Type:application/json' -d '{"sentence": "주변인의 감정으로 세상을 구경하고 있던 날이었다."}'
curl -X POST localhost:9200/test/_doc/t2 -H 'Content-Type:application/json' -d '{"sentence": "소수의 의견은 때로 화제가 되더라도 주변에 겉돌뿐 세상의 중심으로 들어가지 않는 듯 하다."}'
```

다음 명령으로 데이터가 잘 저장되어있는 걸 확인했다.

```sh
curl -X GET localhost:9200/test/_doc/t1
curl -X GET localhost:9200/test/_doc/t2
```

그러면 검색 API를 통해서 잘 검색이 되는지 확인을 해보자.

<details>
<summary>'주변'으로 검색결과</summary>

```sh
curl -X GET 'localhost:9200/test/_search' -H 'Content-Type:application/json'  -d '{"query": {"match": {"sentence":"주변"}}}'
```

```json
{
   "took":6,
   "timed_out":false,
   "_shards":{
      "total":1,
      "successful":1,
      "skipped":0,
      "failed":0
   },
   "hits":{
      "total":{
         "value":2,
         "relation":"eq"
      },
      "max_score":0.20824991,
      "hits":[
         {
            "_index":"test",
            "_id":"t1",
            "_score":0.20824991,
            "_source":{
               "sentence":"주변인의 감정으로 세상을 구경하고 있던 날이었다."
            }
         },
         {
            "_index":"test",
            "_id":"t2",
            "_score":0.17308576,
            "_source":{
               "sentence":"소수의 의견은 때로 화제가 되더라도 주변에 겉돌뿐 세상의 중심으로 들어가지 않는 듯 하다."
            }
         }
      ]
   }
}
```

</details>

<details>
<summary>'세상'으로 검색결과</summary>

```sh
curl -X GET 'localhost:9200/test/_search' -H 'Content-Type:application/json'  -d '{"query": {"match": {"sentence":"세상"}}}'
```

```json
{
   "took":5,
   "timed_out":false,
   "_shards":{
      "total":1,
      "successful":1,
      "skipped":0,
      "failed":0
   },
   "hits":{
      "total":{
         "value":2,
         "relation":"eq"
      },
      "max_score":0.20824991,
      "hits":[
         {
            "_index":"test",
            "_id":"t1",
            "_score":0.20824991,
            "_source":{
               "sentence":"주변인의 감정으로 세상을 구경하고 있던 날이었다."
            }
         },
         {
            "_index":"test",
            "_id":"t2",
            "_score":0.17308576,
            "_source":{
               "sentence":"소수의 의견은 때로 화제가 되더라도 주변에 겉돌뿐 세상의 중심으로 들어가지 않는 듯 하다."
            }
         }
      ]
   }
}
```

</details>

<details>
<summary>'의견'으로 검색결과</summary>

```sh
curl -X GET 'localhost:9200/test/_search' -H 'Content-Type:application/json'  -d '{"query": {"match": {"sentence":"의견"}}}'
```

```json
{
   "took":14,
   "timed_out":false,
   "_shards":{
      "total":1,
      "successful":1,
      "skipped":0,
      "failed":0
   },
   "hits":{
      "total":{
         "value":1,
         "relation":"eq"
      },
      "max_score":0.6580346,
      "hits":[
         {
            "_index":"test",
            "_id":"t2",
            "_score":0.6580346,
            "_source":{
               "sentence":"소수의 의견은 때로 화제가 되더라도 주변에 겉돌뿐 세상의 중심으로 들어가지 않는 듯 하다."
            }
         }
      ]
   }
}
```

</details>

<details>
<summary>'세상'&'감정'으로 검색결과</summary>

```sh
curl -X GET 'localhost:9200/test/_search' -H 'Content-Type:application/json'  -d '{"query": {"match": {"sentence": {"query": "세상 감정", "operator": "and" }}}}'
```

```json
{
   "took":42,
   "timed_out":false,
   "_shards":{
      "total":1,
      "successful":1,
      "skipped":0,
      "failed":0
   },
   "hits":{
      "total":{
         "value":1,
         "relation":"eq"
      },
      "max_score":0.99997103,
      "hits":[
         {
            "_index":"test",
            "_id":"t1",
            "_score":0.99997103,
            "_source":{
               "sentence":"주변인의 감정으로 세상을 구경하고 있던 날이었다."
            }
         }
      ]
   }
}
```

</details>

예상한대로 잘 동작하는 걸 확인할 수 있다.
