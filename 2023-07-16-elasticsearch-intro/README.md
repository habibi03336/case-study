# 엘라스틱서치 시작하기

운영체제나 환경에 영향을 받지 않기 위해서 이미 있는 엘라스틱 서치 도커 이미지를 활용할 수 있다. 로컬 환경의 ISA에 맞춰 도커 이미지를 다운로드 받는다.

<https://www.docker.elastic.co/r/elasticsearch>

엘라스틱 서치는 기본으로 9200번 포트로 열린다. 로컬의 9200 포트와 도커 컨테이너의 9200번 포트를 바인딩하여 컨테이너를 시작한다.

    docker run -p 9200:9200 035ac81895b7

하지만 이 상태로 localhost:9200에 접근하면 아무런 데이터도 오지 않는다.
엘라스틱서치는 기본적으로 https를 활성화해놓는다. 따라서 로컬에서 http로 ssl없이 접근하기 위해서는 https를 비활성화해야한다. 아래 명령어로 컨네이너 내부 쉘에 접속한다.

    docker exec -it {container id} /bin/bash

그리고 엘라스틱서치 폴더의 config 폴더로 들어간다. elasticsearch.yml 파일에서 아래 항목들을 false로 설정해준다. 그리고 도커 컨테이너를 중지했다 다시 시작하면 새로한 설정이 적용된다.

```yml
xpack.security.enabled: false

xpack.security.enrollment.enabled: false

xpack.security.http.ssl:
    enabled: false
    ...

xpack.security.transport.ssl:
    enabled: false
    ...
```

이제 로컬에서 localhost:9200으로 접속하여 엘라스틱 서치와 통신 할 수 있다. 다음과 같은 데이터를 반환한다.

```json
{
	"name": "7c26b20fcf5d",
	"cluster_name": "docker-cluster",
	"cluster_uuid": "CKrtALx9TEeelPmLAd-lTg",
	"version": {
		"number": "8.8.2",
		"build_flavor": "default",
		"build_type": "docker",
		"build_hash": "98e1271edf932a480e4262a471281f1ee295ce6b",
		"build_date": "2023-06-26T05:16:16.196344851Z",
		"build_snapshot": false,
		"lucene_version": "9.6.0",
		"minimum_wire_compatibility_version": "7.17.0",
		"minimum_index_compatibility_version": "7.0.0"
	},
	"tagline": "You Know, for Search"
}
```

# 기본적인 통신해보기

엘라스틱은 REST API 기반의 통신을 지원한다. 통신 방식에 대한 정확한 설명은 [공식문서](https://www.elastic.co/guide/en/elasticsearch/reference/current/docs.html)에서 볼 수 있다.

## POST 요청

    curl -XPOST -H "Content-Type: application/json" http://localhost:9200/movies/_doc -d '{"title": "parasite", "director":"bong joon-ho", "production":"barunson e&a"}'

```json
{
	"_index": "movies",
	"_id": "1FG4OokB7r3ifgAtgyDq",
	"_version": 1,
	"result": "created",
	"_shards": { "total": 2, "successful": 1, "failed": 0 },
	"_seq_no": 1,
	"_primary_term": 1
}
```

## GET 요청

    curl -XGET http://localhost:9200/movies/_doc/1FG4OokB7r3ifgAtgyDq

```json
{
	"_index": "movies",
	"_id": "1FG4OokB7r3ifgAtgyDq",
	"_version": 1,
	"_seq_no": 1,
	"_primary_term": 1,
	"found": true,
	"_source": {
		"title": "parasite",
		"director": "bong joon-ho",
		"production": "barunson e&a"
	}
}
```

## 업데이트 POST 요청

    curl -XPOST -H "Content-Type: application/json" http://localhost:9200/movies/_doc/1FG4OokB7r3ifgAtgyDq -d '{"title": "parasite", "director":"bong joon-ho", "production":"barunson e&a", "starring":["song gang-ho", "lee sun-kyun", "cho yeo-jeong"]}'

```json
{
	"_index": "movies",
	"_id": "1FG4OokB7r3ifgAtgyDq",
	"_version": 2,
	"result": "updated",
	"_shards": { "total": 2, "successful": 1, "failed": 0 },
	"_seq_no": 3,
	"_primary_term": 1
}
```

## DELETE 요청

    curl -XDELETE http://localhost:9200/movies/_doc/1FG4OokB7r3ifgAtgyDq

```json
{
	"_index": "movies",
	"_id": "1FG4OokB7r3ifgAtgyDq",
	"_version": 3,
	"result": "deleted",
	"_shards": { "total": 2, "successful": 1, "failed": 0 },
	"_seq_no": 4,
	"_primary_term": 1
}
```

# 데이터 삽입

<https://github.com/wikibook/elasticsearch/tree/master/05.%EA%B2%80%EC%83%89>에서 더미데이터를 얻어서 bulk API를 통해 데이터를 삽입한다. bulk api는 여러 명령을 배치로 처리하여 성능이 더 좋다.

    curl -XPOST -H "Content-Type: application/json" localhost:9200/\_bulk --data-binary @5_1_books.json

하지만 위 링크 데이터를 그대로 삽입하려고 하면 에러가 발생한다. 메타 데이터에 알 수 없는 매개변수 "\_type"이 있다는 에러이다. [엘라스틱 7.0 이후에서 type 개념이 없어져 생기는 오류다.](https://www.elastic.co/guide/en/elasticsearch/reference/7.17/removal-of-types.html) 따라서 메타 데이터에 있는 type 매개변수를 모두 삭제한 후 데이터를 삽입한다.

```json
{
	"error": {
		"root_cause": [
			{
				"type": "illegal_argument_exception",
				"reason": "Action/metadata line [1] contains an unknown parameter [_type]"
			}
		],
		"type": "illegal_argument_exception",
		"reason": "Action/metadata line [1] contains an unknown parameter [_type]"
	},
	"status": 400
}
```

# 검색 API 예시

books 인덱스에서 author에 shakespeare가 들어가는 문서를 페이지 많은 순으로 검색해보자. 단 모든 필드가 아닌 제목, 저자, 카테고리, 페이지만 반환한다.

## 쿼리 파라미터 이용

    curl 'localhost:9200/books/\_search?q=author:shakespeare&\_source=title,category,author,pages&sort=pages:desc&pretty'

<details>
<summary>결과</summary>

```json
{
	"took": 3,
	"timed_out": false,
	"_shards": {
		"total": 1,
		"successful": 1,
		"skipped": 0,
		"failed": 0
	},
	"hits": {
		"total": {
			"value": 6,
			"relation": "eq"
		},
		"max_score": null,
		"hits": [
			{
				"_index": "books",
				"_id": "Xc7-V4kBoIixDwcAuQF5",
				"_score": null,
				"_ignored": ["plot.keyword"],
				"_source": {
					"title": "Hamlet",
					"author": "William Shakespeare",
					"category": "Tragedies",
					"pages": 172
				},
				"sort": [172]
			},
			{
				"_index": "books",
				"_id": "W87-V4kBoIixDwcAuQF5",
				"_score": null,
				"_ignored": ["plot.keyword"],
				"_source": {
					"title": "Romeo and Juliet",
					"author": "William Shakespeare",
					"category": "Tragedies",
					"pages": 125
				},
				"sort": [125]
			},
			{
				"_index": "books",
				"_id": "Xs7-V4kBoIixDwcAuQF5",
				"_score": null,
				"_ignored": ["plot.keyword"],
				"_source": {
					"title": "Othello",
					"author": "William Shakespeare",
					"category": "Tragedies",
					"pages": 100
				},
				"sort": [100]
			},
			...(중략)
		]
	}
}
```

</details>

## request body 이용

    curl -H "Content-Type: application/json" 'localhost:9200/books/\_search?pretty' -d '
    {
    	"\_source": false,
    	"fields": ["title", "author", "category", "pages"],
        "sort": [{ "pages" : "desc" }],
    	"query": {
    		"term" : { "author" : "shakespeare" }
    	}
    }'

<details>
<summary>결과</summary>

```json
{
	"took": 4,
	"timed_out": false,
	"_shards": {
		"total": 1,
		"successful": 1,
		"skipped": 0,
		"failed": 0
	},
	"hits": {
		"total": {
			"value": 6,
			"relation": "eq"
		},
		"max_score": null,
		"hits": [
			{
				"_index": "books",
				"_id": "Xc7-V4kBoIixDwcAuQF5",
				"_score": null,
				"_ignored": ["plot.keyword"],
				"fields": {
					"pages": [172],
					"author": ["William Shakespeare"],
					"title": ["Hamlet"],
					"category": ["Tragedies"]
				},
				"sort": [172]
			},
			{
				"_index": "books",
				"_id": "W87-V4kBoIixDwcAuQF5",
				"_score": null,
				"_ignored": ["plot.keyword"],
				"fields": {
					"pages": [125],
					"author": ["William Shakespeare"],
					"title": ["Romeo and Juliet"],
					"category": ["Tragedies"]
				},
				"sort": [125]
			},
			{
				"_index": "books",
				"_id": "Xs7-V4kBoIixDwcAuQF5",
				"_score": null,
				"_ignored": ["plot.keyword"],
				"fields": {
					"pages": [100],
					"author": ["William Shakespeare"],
					"title": ["Othello"],
					"category": ["Tragedies"]
				},
				"sort": [100]
			},
			...(중략)
		]
	}
}
```

</details>

# Aggregation API

Aggregation은 3가지 종류로 나뉜다.

1. Bucket aggregation: 문서를 특정 조건에 따라 분류하는 기능
   - missing: 문서에 특정 필드가 정의되지 않았거나, 해당 필드에 NULL값이 있는 문서의 개수를 샌다.
   - range: 경우 구간 별로 속하는 문서의 개수를 반환한다.
2. Metrics aggregation: 계산된 값을 만들어 내는 기능
   - avg: 여러 문서의 특정 필드 평균 값을 계산한다.
   - cardinality: 특정 필드가 가지는 값의 유니한 개수를 센다.
3. Pipeline aggregation: 다른 어그리게이션으로부터 나온 값을 활용하여 추가적인 작업을 하는 기능
   - normalize: 메트릭스 어그리게이션을 통해 계산된 값을 바탕으로 값을 추가적으로 노말라이즈해 반환.

[이 외에도 각 종류별로 훨씬 많은 기능이 있다.](https://www.elastic.co/guide/en/elasticsearch/reference/current/search-aggregations.html)

## Aggregation API 활용 예시

셰익스피어가 언제 가장 왕성히 집필을 했는지 알아보고 싶다.

셰익스피어가 쓴 책을 10년 단위로 구분하고, 쓴 총 장수를 더한다. 그리고 해당 10년 동안 총 장수의 몇 퍼센트를 집필했는지를 보고자한다.

    curl -H "Content-Type: application/json" 'localhost:9200/books/_search?pretty' -d '
    	{
    		"size":0,
    		"query": {
    				"term" : { "author": "shakespeare" }
    		},
    		"aggs": {
    			"page_by_date": {
    				"date_histogram": {
    					"field": "written",
    					"fixed_interval": "3650d"
    				},
    				"aggs": {
    					"pages": {
    						"sum": {
    							"field": "pages"
    						}
    					},
    					"percent_of_total_pages": {
    						"normalize": {
    							"buckets_path": "pages",
    							"method": "percent_of_sum",
    							"format": "00.00%"
    						}
    					}
    				}
    			}
    		}
    	}'

<details>
<summary>결과</summary>

```json
{
	"took": 9,
	"timed_out": false,
	"_shards": {
		"total": 1,
		"successful": 1,
		"skipped": 0,
		"failed": 0
	},
	"hits": {
		"total": {
			"value": 6,
			"relation": "eq"
		},
		"max_score": null,
		"hits": []
	},
	"aggregations": {
		"page_by_date": {
			"buckets": [
				{
					"key_as_string": "1560-04-10T00:00:00.000Z",
					"key": -12929760000000,
					"doc_count": 1,
					"pages": {
						"value": 125.0
					},
					"percent_of_total_pages": {
						"value": 0.19409937888198758,
						"value_as_string": "19.41%"
					}
				},
				{
					"key_as_string": "1570-04-08T00:00:00.000Z",
					"key": -12614400000000,
					"doc_count": 0,
					"pages": {
						"value": 0.0
					},
					"percent_of_total_pages": {
						"value": null
					}
				},
				{
					"key_as_string": "1580-04-05T00:00:00.000Z",
					"key": -12299040000000,
					"doc_count": 0,
					"pages": {
						"value": 0.0
					},
					"percent_of_total_pages": {
						"value": null
					}
				},
				{
					"key_as_string": "1590-04-03T00:00:00.000Z",
					"key": -11983680000000,
					"doc_count": 2,
					"pages": {
						"value": 269.0
					},
					"percent_of_total_pages": {
						"value": 0.41770186335403725,
						"value_as_string": "41.77%"
					}
				},
				{
					"key_as_string": "1600-03-31T00:00:00.000Z",
					"key": -11668320000000,
					"doc_count": 3,
					"pages": {
						"value": 250.0
					},
					"percent_of_total_pages": {
						"value": 0.38819875776397517,
						"value_as_string": "38.82%"
					}
				}
			]
		}
	}
}
```

</details>

# [Elasticsearch QueryDSL](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl.html)

`엘라스틱서치 QueryDSL`은 쿼리에 특환된 JSON 형식의 언어이다. QueryDSL을 활용하여 원하는 데이터를 찾을 수 있다. [QueryDSL에는 두 가지 컨텍스트가 있다.](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-filter-context.html)

1. Query Context: 연관 점수(relevance score)를 계산하여 검색의 결과를 반환한다.
2. Filter Context: 쿼리에 매칭이 되는지 안되는지(Yes or No)를 판단하여 결과를 반환한다.

## 예시

제목에 햄릿이 들어가지 않고, 셰익스피어가 저자인 책 중에서 플랏에 love가 많이 들어간 것에 높은 점수를 주는 QueryDSL

```json
{
	"query": {
		"bool": {
			"must_not": { "term": { "title": "hamlet" } },
			"should": [{ "term": { "plot": "love" } }],
			"filter": [{ "term": { "author": "shakespeare" } }]
		}
	}
}
```

<details>
<summary>결과</summary>

```json
{
	"took": 8,
	"timed_out": false,
	"_shards": {
		"total": 1,
		"successful": 1,
		"skipped": 0,
		"failed": 0
	},
	"hits": {
		"total": {
			"value": 5,
			"relation": "eq"
		},
		"max_score": 2.482685,
		"hits": [
			{
				"_index": "books",
				"_id": "W87-V4kBoIixDwcAuQF5",
				"_score": 2.482685,
				"_ignored": ["plot.keyword"],
				"_source": {
					"title": "Romeo and Juliet",
					"author": "William Shakespeare",
					"category": "Tragedies",
					"written": "1562-12-01T20:40:00",
					"pages": 125,
					"sell": 182700000,
					"plot": "Meanwhile, Benvolio talks with his cousin Romeo, Montague's son, about Romeo's recent depression. Benvolio discovers that it stems from unrequited infatuation for a girl named Rosaline, one of Capulet's nieces. Persuaded by Benvolio and Mercutio, Romeo attends the ball at the Capulet house in hopes of meeting Rosaline. However, Romeo instead meets and falls in love with Juliet. Juliet's cousin, Tybalt, is enraged at Romeo for sneaking into the ball, but is only stopped from killing Romeo by Juliet's father, who doesn't wish to shed blood in his house. After the ball, in what is now called the \"balcony scene\", Romeo sneaks into the Capulet orchard and overhears Juliet at her window vowing her love to him in spite of her family's hatred of the Montagues. Romeo makes himself known to her and they agree to be married. With the help of Friar Laurence, who hopes to reconcile the two families through their children's union, they are secretly married the next day."
				}
			},
			{
				"_index": "books",
				"_id": "XM7-V4kBoIixDwcAuQF5",
				"_score": 2.0321493,
				"_ignored": ["plot.keyword"],
				"_source": {
					"title": "King Lear",
					"author": "William Shakespeare",
					"category": "Tragedies",
					"written": "1603-05-01T04:36:00",
					"pages": 88,
					"sell": 91300000,
					"plot": "In the first scene the Earl of Gloucester and the Earl of Kent meet and observe that King Lear has awarded equal shares of his realm to the Duke of Cornwall and the Duke of Albany (and even before this the formal division of the next scene has taken place). Then the Earl of Gloucester introduces his illegitimate son Edmund to the Earl of Kent. In the next scene, King Lear, who is elderly and wants to retire from power, decides to divide his realm among his three daughters, and declares he'll offer the largest share to the one who loves him best. The eldest, Goneril, speaks first, declaring her love for her father in fulsome terms. Moved by her flattery Lear proceeds to grant to Goneril her share as soon as she's finished her declaration, before Regan and Cordelia have a chance to speak. He then awards to Regan her share as soon as she has spoken. When it is finally the turn of his youngest daughter, Cordelia, at first she refuses to say anything (\"Nothing, my Lord\") and then declares there is nothing to compare her love to, nor words to properly express it; she speaks honestly but bluntly, which infuriates him. In his anger he disinherits Cordelia and divides her share between Regan and Goneril. Kent objects to this unfair treatment. Enraged by Kent's protests, Lear banishes him from the country. Lear summons the Duke of Burgundy and the King of France, who have both proposed marriage to Cordelia. Learning that Cordelia has been disinherited, the Duke of Burgundy withdraws his suit, but the King of France is impressed by her honesty and marries her anyway."
				}
			},
			{
				"_index": "books",
				"_id": "Wc7-V4kBoIixDwcAuQF3",
				"_score": 0.0,
				"_ignored": ["plot.keyword"],
				"_source": {
					"title": "The Tempest",
					"author": "William Shakespeare",
					"category": "Comedies",
					"written": "1610-03-01T11:34:00",
					"pages": 62,
					"sell": 275600000,
					"plot": "Magician Prospero, rightful Duke of Milan, and his daughter, Miranda, have been stranded for twelve years on an island after Prospero's jealous brother Antonio (aided by Alonso, the King of Naples) deposed him and set him adrift with the then-3-year-old Miranda. Gonzalo, the King's counsellor, had secretly supplied their boat with plenty of food, water, clothes and the most-prized books from Prospero's library. Possessing magic powers due to his great learning, Prospero is reluctantly served by a spirit, Ariel, whom Prospero had rescued from a tree in which he had been trapped by the witch Sycorax. Prospero maintains Ariel's loyalty by repeatedly promising to release the \"airy spirit\" from servitude. Sycorax had been banished to the island, and had died before Prospero's arrival. Her son, Caliban, a deformed monster and the only non-spiritual inhabitant before the arrival of Prospero, was initially adopted and raised by him. He taught Prospero how to survive on the island, while Prospero and Miranda taught Caliban religion and their own language. Following Caliban's attempted rape of Miranda, he had been compelled by Prospero to serve as the magician's slave. In slavery, Caliban has come to view Prospero as a usurper and has grown to resent him and his daughter. Prospero and Miranda in turn view Caliban with contempt and disgust."
				}
			},
			{
				"_index": "books",
				"_id": "Ws7-V4kBoIixDwcAuQF5",
				"_score": 0.0,
				"_ignored": ["plot.keyword"],
				"_source": {
					"title": "The Merchant of Venice",
					"author": "William Shakespeare",
					"category": "Comedies",
					"written": "1596-02-01T04:42:00",
					"pages": 97,
					"sell": 124100000,
					"plot": "Bassanio, a young Venetian of noble rank, wishes to woo the beautiful and wealthy heiress Portia of Belmont. Having squandered his estate, he needs 3,000 ducats to subsidise his expenditures as a suitor. Bassanio approaches his friend Antonio, a wealthy merchant of Venice who has previously and repeatedly bailed him out. Antonio agrees, but since he is cash-poor – his ships and merchandise are busy at sea – he promises to cover a bond if Bassanio can find a lender, so Bassanio turns to the Jewish moneylender Shylock and names Antonio as the loan's guarantor."
				}
			},
			{
				"_index": "books",
				"_id": "Xs7-V4kBoIixDwcAuQF5",
				"_score": 0.0,
				"_ignored": ["plot.keyword"],
				"_source": {
					"title": "Othello",
					"author": "William Shakespeare",
					"category": "Tragedies",
					"written": "1603-07-01T13:34:00",
					"pages": 100,
					"sell": 141200000,
					"plot": "Before Brabantio reaches Othello, news arrives in Venice that the Turks are going to attack Cyprus; therefore Othello is summoned to advise the senators. Brabantio arrives and accuses Othello of seducing Desdemona by witchcraft, but Othello defends himself successfully before an assembly that includes the Duke of Venice, Brabantio's kinsmen Lodovico and Gratiano, and various senators. He explains that Desdemona became enamored of him for the sad and compelling stories he told of his life before Venice, not because of any witchcraft. The senate is satisfied, but Brabantio leaves saying that Desdemona will betray Othello. By order of the Duke, Othello leaves Venice to command the Venetian armies against invading Turks on the island of Cyprus, accompanied by his new wife, his new lieutenant Cassio, his ensign Iago, and Iago's wife, Emilia as Desdemona's attendant."
				}
			}
		]
	}
}
```

plot에 love가 없는 경우에는 0점으로 평가되었다. 또한 로미오와 줄리엣의 경우 love가 2번, 킹 리어의 경우 love가 3번 나왔는데, 로미오와 줄리엣의 점수가 더 높았다. 횟수만으로 점수를 평가하는 것이 아니라 비율 등을 고려하는 것으로 보인다.

</details>

# [매핑](https://www.elastic.co/guide/en/elasticsearch/reference/current/mapping.html)

매핑은 특정 필드의 데이터 타입을 정의하는 명세이다. RDB의 스키마와 비슷하다. 인덱스 별로 하나의 필드는 하나의 데이터 타입을 가질 수 있다. 다음 명령어로 현재 설정된 매핑을 볼 수 있다. 별다른 설정을 하지 않으면 들어오는 데이터에 따라 엘라스틱서치가 자동으로 데이터 타입을 선택한다.

    curl 'http://localhost:9200/books/_mapping?pretty'

```json
{
	"books": {
		"mappings": {
			"properties": {
				"author": {
					"type": "text",
					"fields": {
						"keyword": {
							"type": "keyword",
							"ignore_above": 256
						}
					}
				},
				"category": {
					"type": "text",
					"fields": {
						"keyword": {
							"type": "keyword",
							"ignore_above": 256
						}
					}
				},
				"pages": {
					"type": "long"
				},
				"plot": {
					"type": "text",
					"fields": {
						"keyword": {
							"type": "keyword",
							"ignore_above": 256
						}
					}
				},
				"sell": {
					"type": "long"
				},
				"title": {
					"type": "text",
					"fields": {
						"keyword": {
							"type": "keyword",
							"ignore_above": 256
						}
					}
				},
				"written": {
					"type": "date"
				}
			}
		}
	}
}
```

새로운 필드에 대해 매핑을 추가할 수는 있지만 이미 매핑된 필드에 대한 데이터 타입 변경 기능은 없다. 데이터 타입 변경이 필요한 경우 새로운 인덱스를 생성하고 데이터를 옮겨야 한다. 따라서 처음부터 매핑 데이터 타입을 신중하게 고르는 것이 좋다.

---

**참고**

- 시작하세요! 엘라스틱서치 (위키북스, 김종민, 2015)
- 엘라스틱서치 공식문서: <https://www.elastic.co/guide/en/elasticsearch/reference/current/index.html>
