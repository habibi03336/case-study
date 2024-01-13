# SQL 실행계획과 쿼리 튜닝

프로젝트에서 성능이 나오지 않는 뷰테이블의 쿼리를 살펴보는 작업을 했다. 실행계획(Explain plan)을 보고 느린 부분을 찾아서 튜닝을 해보는 작업을 했다.

# SQL의 실행계획이란?

SQL의 `실행계획`이란 쿼리가 어떤 절차를 거쳐 실행될지에 대한 DBMS의 계획이다. 이 절차를 계획하는 기준으로 대표적으로 `rule-based optimize`와 `cost-based optimize`가 있는데 일반적으로 `cost-based optimize`가 더 많이 쓰인다. cost-based optimize는 데이터의 실제 분포와 같은 통계적인 정보와 인덱스 유무 등의 정보를 활용하여 cost를 계산하고, 이 cost를 최소화 시키는 실행계획을 택한다.

> Examining the different aspects of an execution plan, from selectivity to parallel execution and
> understanding what information you should be gleaming from the plan can be overwhelming even for
> the most experienced DBA.

[오라클의 실행계획을 설명하는 문서를 보면](https://www.oracle.com/technetwork/database/bi-datawarehousing/oracle-explain-the-explain-0218-4403741.pdf) 경험이 많은 DBA에 있어서도 실행계획을 보고 문제를 발견하는 것은 쉬운 작업이
아니라고 언급되어있다.

실행계획을 총체적으로 완전하게 파악하려고 하는 것은 무리가 되는 경우가 많다. `실행계획을 차근차근 읽고, 이를 바탕으로 느린 부분을 찾아 해결책을 제시할 수 있는 수준`으로 실행계획을 활용하는게 좋다고 생각한다.

# 실행계획을 보면 좋은 점

간단한 테이블에 대한 쿼리의 경우 굳이 실행 계획까지 볼 이유가 없을 수도 있다. 하지만 여러 테이블이 결합(join)된 뷰에 대해 조건절이 붙게 된다면 실행계획을 보는 것이 매우 도움이 된다.

DBMS의 옵티마이저는 전체 뷰를 만든다음 where 조건을 반영하는 것이 아니라, view merging이나 predicate pushing과 같은 [`쿼리 변환(Query Transformation)`](https://docs.oracle.com/en/database/oracle/oracle-database/23/tgsql/query-transformations.html#GUID-B2914447-CD6D-411C-8467-6E10E78F3DE0)을 통해서 효율적으로 쿼리를 실행한다. (만약 이렇지 않는다면 성능 문제로 조건절을 일일이 내부로 넣어줄 수 밖에 없을 것이다.)

따라서 복잡한 뷰에 대한 쿼리를 파악할 때는, 쿼리 변환이 되어 조건절이 실제 테이블에 어떻게 적용되는지를 드러내는 실행계획을 통해 보다 수월하게 문제를 파악할 수 있다.

# 활용 사례: 쿼리 미숙으로 조건절이 적절히 반영되지 않은 상황

계좌 별 금융 거래 테이블(account statement table)에 각 거래의 추가적인 정보에 대해서 left join을 하는 쿼리가 있었다. join 조건에 index가 걸려있었기 때문에 딱히 느릴 이유가 없어 보였다. 하지만 쿼리 실행시 결과를 확인하기 어려울 정도로 쿼리가 느렸다.

실행계획을 확인해보니 특정 부분에서 큰 cost가 발생하고 있었다. 문제가 되었던 쿼리를 단순화 해보면 다음과 같았고, ACCOUNT_STATEMENT에 걸린 LEFT JOIN의 비용이 크게 평가되어 있었다. ~~LEFT JOIN 비용이 크게 잡힌게 이 부분을 들여다보게된 이유이기는 하지만, 실제로 느린 이유가 LEFT JOIN 자체는 아니었다.~~

```sql
SELECT TRX_NO, AC_NO, VALUE_DT, AMOUNT, DRCR, VALUE_DT, DETAIL
FROM ACCOUNT_STATEMENT
LEFT JOIN ( -- 이 조인의 비용이 크게 잡혀있었다. --
   SELECT DISTINCT ACCOUNT_STATEMENT.DETAIL_ID, NVL(CASH_DETAIL.DETAIL, PAYMENT_DETAIL.DETAIL) DETAIL
   FROM ACCOUNT_STATEMENT
   LEFT JOIN CASH_DETAIL ON ACCOUNT_STATEMENT.EXTERNAL_DETAIL_ID = CASH_DETAIL.ID
   LEFT JOIN PAYMENT_DETAIL ON ACCOUNT_STATEMENT.EXTERNAL_DETAIL_ID = PAYMENT_DETAIL.ID
) D ON ACCOUNT_STATEMENT.DETAIL_ID = D.DETAIL_ID
WHERE
   AC_NO = '20230113' AND
   VALUE_DT BETWEEN '2023-01-01' AND '2023-12-31'
```

<div style="text-align: center;">
    <img src="https://raw.githubusercontent.com/habibi03336/case-study/master/2024-01-13-sql-explain-plan/img/explain-cost-example1.png" alt="explain cost" width="600"/>
</div>

CASH_DETAIL 테이블과 PAYMENT_DETAIL 테이블 중 하나의 데이터를 선택해(CASH_DETAIL 우선 선택) ACCOUNT_STATEMENT에 JOIN을 해주는 쿼리였다. 로직 자체는 크게 느릴 이유가 없었다.

하지만 실행계획을 좀 더 자세히 살펴보니 이 쿼리는 느릴 수 밖에 없었다. LEFT JOIN의 외부테이블인 쿼리가 매우 비효율적으로 동작하고 있었기 때문이다. 일반적이라면 AC_NO로 걸러진 레코드에 대해서만 DETAIL을 붙여주면 될 것이다. 하지만 위 쿼리는 ACCOUNT_STATEMENT에서 AC_NO가 '20230113'이고 VALUE_DT가 '2023-01-01'와 '2023-12-31' 사이인 레코드가 가지는 DETAIL ID 중 하나를 가지는 모든 ACCOUNT_STATEMENT의 레코드에 대해서 CASH_DETAIL과 PAYMENT_DETAIL을 조인하고 이에 대해서 DISTINCT를 걸고 있었다. 즉, 아래 쿼리를 실행한 것과 같았다.

```sql
--
SELECT DISTINCT ACCOUNT_STATEMENT.DETAIL_ID, NVL(CASH_DETAIL.DETAIL, PAYMENT_DETAIL.DETAIL) DETAIL
FROM ACCOUNT_STATEMENT
LEFT JOIN CASH_DETAIL ON ACCOUNT_STATEMENT.EXTERNAL_DETAIL_ID = CASH_DETAIL.ID
LEFT JOIN PAYMENT_DETAIL ON ACCOUNT_STATEMENT.EXTERNAL_DETAIL_ID = PAYMENT_DETAIL.ID
WHERE DETAIL_ID IN ('AC_NO가 "20230113"이고 VALUE_DT가 "2023-01-01"와 "2023-12-31" 사이인 레코드가 가지는 DETAIL ID')
```

DETAIL_ID는 ACCOUNT_STATEMENT 레코드의 selectivity가 매우 낮은 데이터였고, 따라서 ACCOUNT_STATEMENT를 거의 풀스캔 하는 것과 같은 결과가 되었던 것이었다.

나는 위 쿼리를 아래와 같이 변경하였고, 그 결과 필요없는 ACCOUNT_STATEMENT 풀스캔이 사라져 쿼리 속도가 0.5초 이내로 개선되었다.

```sql
SELECT TRX_NO, AC_NO, VALUE_DT, AMOUNT, DRCR, VALUE_DT, DETAIL
FROM ACCOUNT_STATEMENT
LEFT JOIN (
   SELECT DISTINCT NVL(CASH_DETAIL.ID, PAYMENT_DETAIL.ID) ID, NVL(CASH_DETAIL.DETAIL, PAYMENT_DETAIL.DETAIL) DETAIL
   FROM
      CASH_DETAIL
   FULL JOIN PAYMENT_DETAIL
   ON CASH_DETAIL.ID = PAYMENT_DETAIL.ID
) DETAIL ON DETAIL.ID = ACCOUNT_STATEMENT.EXTERNAL_DETAIL_ID
```

# 추가 정리: 뷰나 테이블의 메타정보를 확인하는 쿼리 (오라클)

```sql
-- 특정 테이블의 모든 인덱스를 보여줌
SELECT *
FROM all_ind_columns
WHERE table_name = '';

-- view table의 쿼리 조회 (text = sql)
SELECT VIEW_NAME, TEXT
FROM ALL_VIEWS
WHERE view_name LIKE '';

-- 특정 테이블 컬럼의 datatype 조회
SELECT *
FROM ALL_TAB_COLUMNS
WHERE
   TABLE_NAME LIKE '' AND
   COLUMN_NAME LIKE '';

-- 특정 테이블이 가진 contraint 조회
SELECT acc.constraint_name
FROM   ALL_CONS_COLUMNS acc
INNER JOIN ALL_CONSTRAINTS ac
        ON ( acc.CONSTRAINT_NAME = ac.CONSTRAINT_NAME )
WHERE  ac.TABLE_NAME   = '';

-- 어떤 데이터셋이 TABLE인지 VIEW인지 PARTITIONED TABLE인지 보여줌
SELECT *
FROM all_objects
WHERE object_name LIKE '';

-- 어떤 컬럼을 기준으로 파티션 했는지 확인하는 쿼리
SELECT OWNER, NAME, OBJECT_TYPE, COLUMN_NAME, COLUMN_POSITION
FROM ALL_PART_KEY_COLUMNS
WHERE NAME = '';

-- 글로벌 인덱스인지 로컬인덱스인지 확인하기
SELECT index_name, partitioned
FROM all_indexes
WHERE index_name LIKE '';
```
