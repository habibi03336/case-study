# 문자열에서 필요 없는 부분 제거하기

한 기업에 매핑되는 여러 이름을 저장하는 One-to-Many 테이블을 만들고, 이 테이블을 통해 기업 검색 기능을 구현하려고 한다. 하나의 이름만을 쓰는 경우 보다 다양한 입력에 대해서 검색이 가능해진다.

Dart API를 통해 기업 관련 데이터를 얻을 수 있다. 여러 데이터를 제공하지만 이름과 관련된 데이터는 다음 3가지이다.

```json
{
	...
	"corp_name": "에스케이하이닉스(주)",
	"corp_name_eng": "SK hynix Inc.",
	"stock_name": "SK하이닉스",
	...
}
```

몇 개 데이터를 살펴보니 corp_name과 corp_name_eng 데이터가 마음에 들지 않았다. 거의 99% 기업에 대해서 주식회사임을 나타내는 중요하지 않은 문자열이 섞여있었다.

|                 | corp_name                | corp_name_eng                                                                                                                                                         |
| --------------- | ------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 중복되는 문자열 | (주), 주식회사, 유한회사 | 'co., ltd', '.co., ltd', 'co.,ltd' , '.co.,ltd', 'co.,ltd.', 'co., ltd.', 'corporation', 'corp.', 'corp', 'company, limited', 'company limited', 'ltd', 'inc.', 'inc' |

\* 영어는 소문자로 변환한 경우 (실제로는 대문자도 섞여있음)

문자열에서 위에 해당하는 의미없이 중복되는 문자열을 제거하기로 했다.

## 어떻게 하지?

한글 이름에서는 제거대상인 문자열의 변형이 많지 않아서 일일이 비교하는 방식으로 목표를 달성할 수 있다.

하지만 영어 이름의 경우 문자열의 변형이 많다. (일부 혹은 전체가 대문자인 경우도 고려해야한다.) 그래서 일일이 비교하는 방식이 비효율적이기도 하고 좀 복잡하게 느껴진다. 그래서 특정 문자열이 아니라 더 넓은 범위인 문자열의 형식을 표현할 수 있는 정규 표현식을 사용해보기로 했다.

## 분류, 규칙 찾기, 정규표현식 만들기

비슷한 형식끼리 분류하고 각 타입 별 공통된 규칙을 뽑아냈다. 그리고 규칙을 바탕으로 정규표현식을 만들었다. <https://wikidocs.net/4308>를 참고했다.

정규표현식 자체에서 \[cC\]\[oO\]... 이런식으로 소문자 대문자 모든 경우임을 나타내줄 수도 있다. 하지만 이렇게 하면 정규표현식이 지저분해진다. 그래서 표현식이 아니라 비교할 때 대소문자 구분을 무시하도록 해주기로했다.

| 타입            | 변형                                                                     | 규칙                                                                                                                                                                           | 정규표현식          |
| --------------- | ------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------- |
| co., ltd        | 'co., ltd', '.co., ltd', 'co.,ltd' , '.co.,ltd', 'co.,ltd.', 'co., ltd.' | 1. 공백, ".", ","를 제외하고 co., ltd가 연속으로 있다. <br>2. 마지막에 점이 있거나 없다. <br> 3. 제일 앞에 점이 있거나 없다. <br> 4. "co.,"와 "ltd" 사이에 공백이 있거나 없다. | `\.?co., ?ltd\.?`   |
| corp            | 'corp.', 'corp'                                                          | 1. corp가 연속으로 있다. <br> 2. 제일 마지막에 점이 있거나 없다.                                                                                                               | `corp\.?`           |
| coporation      | 'corporation'                                                            | -                                                                                                                                                                              | `corporation`       |
| company limited | 'company, limited', 'company limited'                                    | 1. ","를 제외하고 company limited가 연속으로 있다. <br> 2. "company"와 "limited" 사이에 ","이 있거나 없다.                                                                     | `company,? limited` |
| ltd             | 'ltd'                                                                    | -                                                                                                                                                                              | `ltd`               |
| inc             | 'inc.', 'inc'                                                            | 1. inc가 연속으로 있다. <br> 2. 마지막에 점이 있거나 없다.                                                                                                                     | `inc\.?`            |
|                 |                                                                          |

## 정규식을 활용한 함수 만들기

파이썬은 re 모듈을 통해 정규표현식을 사용할 수 있다. 파이썬에서는 정규표현식을 컴파일 할 때 옵션(re.I)을 통해 대소문자 구분을 무시하도록 할 수 있다. 반복문을 돌면서 정규식 중 이름에 매칭되는 것이 있으면 그 부분을 제거한다.

뒤에 "."이나 ","이 남는 경우가 있어서 이를 없애도록 추가적으로 처리해줬다.

```python
import re

regs = ['\.?co., ?ltd\.?', 'corp\.?', 'corporation', 'company,? limited', 'ltd', 'inc\.?']
patterns = [re.compile(reg, re.I) for reg in regs]
def trim_corp_name_eng(eng_name):
	cleaned_name = eng_name.strip()
	for pattern in patterns:
		result =  pattern.search(eng_name)
		if result:
			start, end = result.span()
			cleaned_name = (eng_name[0:start] + eng_name[end:]).strip()
			break
	if cleaned_name[-1] == '.' or cleaned_name[-1] == ',':
		cleaned_name = cleaned_name[:-1].strip()
	return cleaned_name
```

## 결과

50개 기업을 뽑아서 결과를 확인해봤다.

| 기존                                      | 다듬은 후                             |
| ----------------------------------------- | ------------------------------------- |
| Creverse, Inc.                            | Creverse                              |
| KOREA AIRPORT SERVICE CO.,LTD             | KOREA AIRPORT SERVICE                 |
| HS INDUSTRIES CO.,LTD                     | HS INDUSTRIES                         |
| HANKOOK STEEL CO.,LTD                     | HANKOOK STEEL                         |
| Withus Pharmaceutical. Co., LTD           | Withus Pharmaceutical                 |
| PARTRONCO.,LTD                            | PARTRON                               |
| JW HOLDINGS CORPORATION                   | JW HOLDINGS ORATION                   |
| HaAINC KOREA CO.,LTD.                     | HaAINC KOREA                          |
| F&F CO.,Ltd                               | F&F                                   |
| MOORIM PAPER CO.,LTD                      | MOORIM PAPER                          |
| Telefield,Inc.                            | Telefield                             |
| InfoBankCorporation                       | InfoBankoration                       |
| HITRON SYSTEMS INC                        | HITRON SYSTEMS                        |
| ESTECHPHARMA CO., LTD                     | ESTECHPHARMA                          |
| DYPNF CO.,LTD                             | DYPNF                                 |
| SUN&L CO.,LTD                             | SUN&L                                 |
| E-WORLD CO.,LTD.                          | E-WORLD                               |
| Cuckoo Holdings Co.,Ltd                   | Cuckoo Holdings                       |
| TEMC Co., Ltd.                            | TEMC                                  |
| Pharmsville Co., Ltd.                     | Pharmsville                           |
| HEUNGKUK METALTECH CO.,LTD.               | HEUNGKUK METALTECH                    |
| HYUNDAI HOME SHOPPING NETWORK CORPORATION | HYUNDAI HOME SHOPPING NETWORK ORATION |
| ILSHIN STONE CO.,LTD                      | ILSHIN STONE                          |
| Maeil Dairies Co., Ltd.                   | Maeil Dairies                         |
| NATURECELL CO.,LTD.                       | NATURECELL                            |
| DAE DONG STEEL CO., LTD.                  | DAE DONG STEEL                        |
| CS Holdings Co.,Ltd.                      | CS Holdings                           |
| KOREA PHARMA Co., Ltd.                    | KOREA PHARMA                          |
| KOLMAR KOREA CO.,LTD                      | KOLMAR KOREA                          |
| Kib plug energy Co., Ltd.                 | Kib plug energy                       |
| KBI DONGKOOK IND CO., LTD                 | KBI DONGKOOK IND                      |
| Linkgenesis Co., Ltd.                     | Linkgenesis                           |
| HD HYUNDAI ENERGY SOLUTIONS CO.,LTD.      | HD HYUNDAI ENERGY SOLUTIONS           |
| HANDYSOFT, Inc.                           | HANDYSOFT                             |
| WOONGJIN CO., LTD.                        | WOONGJIN                              |
| TAPEX INC                                 | TAPEX                                 |
| RPbio Inc.                                | RPbio                                 |
| NOUSBO CO., LTD                           | NOUSBO                                |
| Se Gyung Hi Tech Co., Ltd.                | Se Gyung Hi Tech                      |
| SK D&D Co.,Ltd.                           | SK D&D                                |
| SAMSUNG HEAVY INDUSTRIES CO.,LTD          | SAMSUNG HEAVY INDUSTRIES              |
| KYE-RYONG CONSTRUCTION INDUSTRIAL CO.,LTD | KYE-RYONG CONSTRUCTION INDUSTRIAL     |
| ISAAC Engineering Co., Ltd.               | ISAAC Engineering                     |
| JVMCO.,LTD                                | JVM                                   |
| SAMYOUNG M-TEK C0. LTD.                   | SAMYOUNG M-TEK C0.                    |
| UNION CORPORATION                         | UNION ORATION                         |
| HYUNDAI DEVELOPMENT COMPANY               | HYUNDAI DEVELOPMENT COMPANY           |
| KOLON PLASTICS, INC.                      | KOLON PLASTICS                        |
| KSIGN CO., Ltd.                           | KSIGN                                 |
| Wemade Max Co., Ltd.                      | Wemade Max                            |

## 디버깅

1.  `SAMYOUNG M-TEK C0. LTD.`의 경우 `SAMYOUNG M-TEK C0.`로 완전히 다듬어 지지않아서 살펴보니 'CO(알파벳)'가 아니라 'C0(숫자)'였다. 또한 다른 변형과는 다르게 ','가 없었다. 비슷한 경우가 또 있을 수 있으니 정규식을 맞춰서 수정해줬다.

        	'\.?co., ?ltd\.?' => '\.?c[o0].,? ?ltd\.?'

2.  `corp 타입`과 `coporation 타입`이 거의 같은 형식을 가지는 것 때문에 문제가 발생했다. corpation 문자열이 있을 때 corp 타입에 먼저 매칭이 되서 앞에 corp만 삭제되고 oration이 남는 문제가 있었다. coporation이 있는지부터 먼저 확인하도록 배열의 순서를 바꿔 문제를 해결했다. (다시 봐보니 `co ltd 타입`과 `ltd 타입`도 순서가 거꾸로 되었으면 같은 문제가 발생할 수 있었다.)

## 후기

간단히 정규식을 활용해봤다. 문자열을 다룰 때 정규식을 적극적으로 활용하면 문제를 보다 쉽게 해결할 수 있을 것 같다.
