# 시간다루기

## 밀리초 timestamp의 개념

내가 이 글을 쓰는 지금을 타임스탬프로 찍어보면 '1696659044172'이다.

```javascript
const time = Date.now();
console.log(time); // 1696659044172
```

이는 1970년 1월 1일부터 지금까지 경과한 시간을 밀리초로 반환한 것이다. 그게 1696659044172 밖에 안 되나 싶지만 대략적으로 계산을 해보면 얼추 비슷하게 나온다. ~~선형적으로 증가하는 것은 커봤자인거 같다.~~

```javascript
// 날짜를 출력하는 함수
function printDateTime(year, month, day, hour, minute){
    console.log(
	`${1970 + year}.${month.toString().padStart(2, "0")}.${day.toString().padStart(2, "0")}
${hour.toString().padStart(2, "0")}:${minute.toString().padStart(2, "0")}`
)
}
```

```javascript
const totalSecond = Math.floor(time / 1000);
const second = totalSecond % 60;
const totalMinute = Math.floor(totalSecond / 60);
const minute = totalMinute % 60;
const totalHour = Math.floor(totalMinute / 60);
const hour = totalHour % 24;
const totalDay = Math.floor(totalHour / 24);
let day = totalDay % 365;
const year = Math.floor(totalDay / 365);
const month = Math.floor(day / 30);
day -= month * 30;
printDateTime(year, month+1, day+1, hour, minute);
// 2023.10.23
// 06:10
```

근데 사실 지금은 10월 초이다. 다소 실제 시간과 차이가 있다. 타임스탬프로 정확한 날짜와 시간을 알아내려면 어떻게 해야할까?

## 윤년의 개념

위 계산에서 두 가지 틀린 것이 있다.

먼저 윤년을 고려하지 않았다. 양력에서 일반적으로 일년은 365일이다. 하지만 이렇게만 계산하면 실제 천체의 주기와 날짜가 조금씩 틀어진다고 한다. 그래서 윤년이라는 것을 만들었다. 윤년은 4의 배수인 연도이고, 이 연도는 2월이 29일까지 있어 일년이 366일이 된다. 좀 더 자세히 들어가면 4의 배수이지만 100의 배수이면 윤년이 아니고, 또 4의 배수이자 100의 배수이더라도 400의 배수이면 윤년이라는 다소 아리까리한 추가적인 규칙이 있다.

두 번째로 틀린 것은 모든 달을 30일이라고 가정한 것이다. 윤년이 아니라면 1월은 31일, 2월은 28일, 3월은 31일 이런식으로 달마다 날짜의 수가 정해져 있다.

이 둘을 고려해서 다음과 같이 제대로 계산해볼 수 있다.

```javascript
// 윤년을 확인하는 함수
function isLeapYear(year){
    if (year % 400 === 0) return true
    if (year % 100 === 0) return false
    if (year % 4 === 0) return true
    return false
}
```

```javascript
// 매월이 몇 일까지 있는지 알아내는 함수
const monthOf31 = [1,3, 5, 7, 8, 10, 12]
const monthOf30 = [4,6, 9, 11]
function getDayCountOfMonth(year, month){
    if(monthOf31.includes(month)) return 31;
    if(monthOf30.includes(month)) return 30;
    if(month === 2 && isLeapYear(year)) return 29;
    if(month === 2) return 28;
}
```

```javascript
let daysLeft = totalDay
let realYear = 1970
let dayCountOfYear = isLeapYear(realYear) ? 366 : 365;
while(daysLeft > dayCountOfYear){
    daysLeft -= dayCountOfYear;
    realYear += 1;
    dayCountOfYear = isLeapYear(realYear) ? 366 : 365;
}

let realMonth = 1;
let dayCountOfMonth = getDayCountOfMonth(realYear, realMonth);
while(daysLeft > dayCountOfMonth){
    daysLeft -= dayCountOfMonth;
    realMonth += 1;
    dayCountOfMonth = getDayCountOfMonth(realYear, realMonth);
}

printDateTime(realYear, realMonth, daysLeft+1, hour, minute);
// 2023.10.07
// 06:10
```

어림으로 23일로 계산되었던게 정확히하니 7일로 계산되었다. 그리고 내가 지금 이 글을 쓰고 있는 지금은 23년 10월 7일이 맞다.

16일의 차이가 있었다. 1970년부터 2023년까지 13번의 윤년이 있었다. 그리고 9월까지 모두 30일로 계산하면 270일인데, 실제로는 273일이다. 그래서 13 + 3 만큼의 16일이 더 지난 것으로 계산되었던 것이다.

## UTC의 개념

그런데 조금 이상한 점이 하나있다. 사실 내가 아까 저 타임스탬프를 찍었을 때는 오후 한 시 정도였다. 그런데 계산된 값을 보니 오전 6시라고 되어있다. 이게 어떻게 된 일일까?

사실 timestamp는 UTC(Coordinated Univeral TIme) 기준으로 반환된다. UTC는 영국 그리니치 천문대를 기준으로 하는 시간이라고 한다. 사실 나는 지금 캄보디아에 있다. 그리고 캄보디아는 UTC+7의 시간대이다. 따라서 계산된 오전 6시에 7시간을 더해야지 내가 있는 지역의 시간이 되는 것이다. 그렇게 계산을 해보면 오후 한 시가 딱 나온다.

## 월일 쉽게 계산하기

위 코드에서 내가 프린트로 인자를 넘길 때 월이나 일에 +1을 하는 경우가 있었다 그것은 월과 일이 0으로 시작한다고 가정하고 앞 선 계산을해서 그런 것이었다.

특정 연월에서 몇 달을 더하거나 뺴야하는 상황이 있을 수 있다. 이 때 그 계산법이 조금 헷갈릴 수 있다. 시작하는 달이 0이 아니라 1이기 때문이다. 12달이 모이면 1년이 늘어난다. 마치 12진법과 비슷하다. 그런데 시작하는 달이 0이 아니라 1이라는 것이다.(일도 마찬가지이다.)

따라서 1을 빼줘서 일반적인 12진법 처럼 바꿔서 계산을 진행한다. 그리고 계산 후 나온 달에 + 1을 해주면 원하는 값을 얻을 수 있다.

```java
int year = 2023;
int month = 9;
int diff = -10; // 10개월 전 연월 구하기

int months = year * 12 + month - 1 + diff;
int targetMonth = months % 12 + 1;
int targetYear = months / 12;
```
