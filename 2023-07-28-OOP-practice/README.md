# 자바로 객체 지향 프로그래밍 실습하기

<!-- 객체 지향 프로그래밍(OOP)를 많이 들어왔다. OOP와 관련된 내용을 양반식으로 앉아서 달달 외우는 것은 그다지 의미가 없다. OOP는 유연하고 유지보수가 용이한 소프트웨어를 만들기 위한 개발 패러다임이기 때문이다. OOP의 사상을 따르는 개발을 진행할 때 비로소 그 의미가 드러난다.

모든 소프트웨어는 `유연하고 유지보수가 용이한 소프트웨어`가 되고 싶어한다. 그러한 소프트웨어는 애질리티를 가지고 있다. 그러한 소프트웨어는 상황에 적응한다. 그러한 소프트웨어는 살아있다. `사회와 소통하는 살아있는 소프트웨어` 내가 만들고 싶은 것이다. -->

재무제표 데이터에서 돈의 단위를 바꿔주는 기능을 OOP를 적용하여 개발하고자한다. 예를 들어, 자본이 10,000원이고 매출이 5,000원인 데이터가 주어졌을 때, 환율에 따라 달러, 엔, 위안으로 바꿔주거나 그 반대를 수행하는 기능이다. 이 소스코드를 추후 재무제표 API 개발에 활용할 생각이다.

# 요구사항

1. 어떤 분기의 재무제표가 특정 통화 기준으로 표시되어있다. 이를 요청된 통화 기준으로 변환한다.

   1. 영업이익이나 매출과 같이 특정 기간 동안 집계되는 경우 해당 기간의 평균 환율로 변환을 한다.
   2. 자본, 부채, 현금및현금성자산 같이 분기 말 기준으로 측정되는 것은 분기 말 환율로 변환을 해야한다.

2. 일본 통화, 미국 통화, 중국 통화, 한국 통화 4개 국가의 통화 간 변환이 가능해야한다. 추후에 통화가 추가 될 수도 있다.

# 과정

## 클래스 정의

막상 OOP를 해보려고하니 막막한 심정이었다. 여러 방식으로 객체를 정의하고 데이터를 관리할 수 있는데 어떤 방향으로 가야하는지 감이 오지를 않았다. 그래서 첫 발을 떼는게 쉽지 않았다. 그렇다고 가만히 있을 수만은 없었다. 그래서 환전의 가장 작은 단위인 'Account(계정)' 클래스를 정의하는 것으로 첫 삽을 떳다.

Account 클래스의 배열을 가지는 Statement(재무제표) 클래스를 정의했다. Statement 클래스에 통화를 바꾸는 메소드를 만들었다. Statement가 환율을 아는데 필요한 데이터인 연도, 분기, 현재 통화 데이터를 모두 가지고 있다. Statment가 메소드 인자로 ExchangeOffice(환율교환소)를 받아서 ExchangeOffice로부터 환율을 얻어 Account를 업데이트 하도록 했다.

Account의 종류에 따라서 사용하는 환율이 달라진다. Account가 손인계산서 계정 (매출이나 영업이익 등)이면 분기 평균환율, 손익계산서 외의 계정(자본이나 부채 등)이면 분기말 환율을 적용한다. if문을 통해서 Account 객체의 이름에 따라 처리를 해주려고 했는데 그렇게 하면 새로운 Account가 생겨날 때 Statement 쪽의 코드를 바꿔야하는 상황이 생긴다. 따라서 Account 클래스에서 손익계산서 계정인지 아닌지를 반환하는 메소드를 만들었다.

```java
public void changeCurrency(String toCurrency, ExchangeOffice ex){
   double averageRatio = ex.getAverageRatio(year, quarter, currency, toCurrency);
   double finalRatio = ex.getFinalRatio(year, quarter, currency, toCurrency);
   currency = toCurrency;
   for(Account acc : accounts){
      if(acc.isIncome()){
            acc.setAmount((long)(acc.getAmount() * averageRatio));
      } else {
            acc.setAmount((long)(acc.getAmount() * finalRatio));
      }
   }
}
```

Enum을 활용해서 Account type을 정의했다. Account의 type에 올 수 있는 데이터를 명확히 하고, 각 상수 데이터에 매핑되는 추가적인 정보(이름, 손익계산서인지 여부)도 쉽게 관리 할 수 있었다. Enum을 Account 클래스 내부에 정의할지 외부로 분리할지 생각을 해봤다. Account type이 사용되는 맥락이 항상 Account 객체와 함께 쓰이기 때문에 Account 클래스 내부에 정의하여 Account를 통해서 조회할 수 있도록 하는 것이 좋다는 결론을 내렸다.

통화를 나타내는 것을 문자열이 아니라 Enum을 사용할까 고민을 해봤다. "USD", "KRW"와 같이 문자열로 나타내도 컨벤션만 잘 지킨다면 그닥 문제가 되지는 않는 상황이다. 그래서 우선은 그냥 놔두기로 했다.

만들어진 클래스의 다이어그램은 다음과 같다. IntelliJ에 클래스 다이어그램을 자동으로 만들어주는 기능이 있다.

<div style="text-align: center;">
    <img src="https://raw.githubusercontent.com/habibi03336/case-study/master/2023-07-28-OOP-practice/img/class-diagram.png" alt="class diagram" width="800"/>
</div>

## 환율 데이터 만들기

환율 데이터를 실제 API에서는 DB로부터 받아올 생각이다. KRW, USD, JPY, CNY에 대해서 서로 간의 환율을 모두 따로 본다면 6가지 경우에 대해서 환율을 저장해야 한다. 또한 새로운 통화가 추가 될 때 마다 기존에 있는 통화 n개 만큼의 데이터가 필요해진다. 따라서 기축 통화인 달러를 통해서 최종 환율을 구하는 방식을 적용하려고 한다. 예를 들어, 원을 엔으로 바꾼다면 원과 엔의 환율을 바로 불러오는 것이 아니라, 원과 달러의 환율 그리고 엔과 달러의 환율 두 가지를 통해 원과 엔의 환율을 구한다. 이렇게 하면 새로운 통화가 추가될 때도 해당 통화와 달러 간의 환율 데이터만 추가하면 된다.

ExchangeOffice 클래스의 환율을 계산하는 기능을 객채지향적인 고려 없이 그냥 알고리즘 문제 풀 듯이 작성해봤다. 딱히 마음에 들지 않는 부분이 없었다. 그대로 쓰기로 했다. DB에서 조회하는 부분만 DAO로 뺴주면 스프링에서 그대로 넣어서 쓸 수 있을 것 같다. DAO에 필요한 메소드를 인터페이스화하고, ExchangeOffice에서 생성자 주입 방식으로 DI 받도록 구성했다.

```java
public double getAverageRatio(int year, int quarter, String fromCurrency, String toCurrency){
   double 달러에서시작통화로환율;
   if(fromCurrency.equals("USD")){
      달러에서시작통화로환율 = 1;
   } else {
      달러에서시작통화로환율 = exchangeRatioRepository.averageRatioFromDollar(year, quarter, fromCurrency);
   }
   if(toCurrency.equals("USD")){
      return 달러에서시작통화로환율;
   }
   double 달러에서목표통화로환율 = exchangeRatioRepository.averageRatioFromDollar(year, quarter, toCurrency);
   return  (1 / 달러에서시작통화로환율) * 달러에서목표통화로환율;
}
```

## 테스트 작성해보기

너무 쉽게 끝나는 거 같아서 JUnit을 활용해 테스트도 작성해보기로 했다. 재무제표가 통화에 따라서 제대로 데이터를 잘 바꾸는지 테스트를 작성하면 된다. 테스트를 작성하는데 특별히 어려운 점은 없을 것으로 보였다. 테스트 용으로 ExchangeOffice에 DI할 모킹 DAO 객체만 추가적으로 만들어주면 된다. 모킹을 하는데 테스트 외부에서 모킹 클래스를 만드는 것보다 테스트를 정의하는 곳에서 모킹 클래스의 동작을 바로 정의 및 확인 할 수 있는 것이 훨씬 좋겠다고 생각했다. 훨씬 직관적이고, 테스트의 결과를 쉽게 예상 할 수 있기 때문이다. 찾아보니 Mockito라는 라이브러리를 활용하여 테스트 내부에서 쉽게 모킹 클래스를 생성하고 그 동작을 제어할 수 있었다. 이를 활용하여 기본적인 테스트 하나를 정의했다. 다행히 테스트를 스무스하게 통과했다.

```java
void 환전기능기본테스트Test() {
   // given
   List<Account> accounts = new ArrayList<>();
   accounts.add(new Account(Account.Type.sales, 100_000));
   accounts.add(new Account(Account.Type.operatingProfit, 50_000));
   accounts.add(new Account(Account.Type.netProfit, 30_000));
   accounts.add(new Account(Account.Type.equity, 40_000));
   accounts.add(new Account(Account.Type.debt, 45_000));
   accounts.add(new Account(Account.Type.cashEquivalents, 25_000));
   Statement statement = new Statement(
            "1",
            "LG CNS",
            "1",
            "K-IFRS 연결",
            "KRW",
            2020,
            1,
            accounts
   );

   ExchangeRatioRepository repo = mock(ExchangeRatioRepository.class);
   when(repo.averageRatioFromDollar(2020, 1, "KRW")).thenReturn(1200d);
   when(repo.averageRatioFromDollar(2020, 1, "JPY")).thenReturn(110d);
   when(repo.finalRatioFromDollar(2020, 1, "KRW")).thenReturn(1300d);
   when(repo.finalRatioFromDollar(2020, 1, "JPY")).thenReturn(105d);
   ExchangeOffice exchangeOffice = new ExchangeOfficeImpl(repo);

   // execute
   statement.changeCurrency("JPY", exchangeOffice);
   accounts = statement.getAccounts();
   Map<Account.Type, Long> accountAmount = new HashMap<>();
   for(Account account: accounts){
      accountAmount.put(account.getType(), account.getAmount());
   }

   // expected
   assertTrue(statement.getCurrency().equals("JPY"));
   assertEquals(accountAmount.get(Account.Type.sales), 9166l);
   assertEquals(accountAmount.get(Account.Type.operatingProfit), 4583l);
   assertEquals(accountAmount.get(Account.Type.netProfit), 2750l);
   assertEquals(accountAmount.get(Account.Type.equity), 3230l);
   assertEquals(accountAmount.get(Account.Type.debt), 3634l);
   assertEquals(accountAmount.get(Account.Type.cashEquivalents), 2019l);
}
```

# 후기

OOP를 간단하게 실습해봤다. 재미있었다. 더 좋은 방식, 더 좋은 코드에 대해 고민하는 것이 진짜 개발자가 된 것 같다는 느낌도 들었다. OOP는 확실히 더 공부하고, 더 고민하고 싶은 주제다.

OOP는 불만에서 출발하는 것이라는 생각이 든다. 뭔가 코드가 복잡해 보이고, 뭔가 코드가 유지보수하기 어려워보인다는 불만에서 시작한다. 그 불만이 OOP로 어떻게 프로그래밍을 할지에 대한 방향성을 제시하는 것 같다.
