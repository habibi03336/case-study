# Git이 발생시키는 예외 알아보기

## 로컬 브랜치를 처음 리모트 브랜치로 푸시할 때

로컬 깃 레포지토리를 만들고, github에 리모트 레포지토를 만들었다. 그리고 로컬에 첫 커밋을 하고 푸시를 시도했다.

```sh
mkdir git-study
cd git-study
git init
gh repo create
touch mySourceCode.java
git add .
git commit -m 'initial commit'
git push
```

그러면 아래와 같은 예외가 발생한다.

```sh
fatal: The current branch main has no upstream branch.
To push the current branch and set the remote as upstream, use

    git push --set-upstream origin main

To have this happen automatically for branches without a tracking
upstream, see 'push.autoSetupRemote' in 'git help config'.
```

이 오류 메세지에서 upstream branch는 내가 푸시를 하고자하는 리모트 레포지토리의 브랜치를 의미한다. git push라고 간략하게 명령어를 입력했지만 사실 이 명령어를 완전히 입력하면 다음과 같다.

```bash
git push <remote_name> <local_branch_name>:<corresponding_remote_branch_name>
```

remote_name의 리모트 레포지토리에 local_branch_name을 corresponding_remote_branch_name에 푸시하겠다는 의미이다. 뒤에를 모두 생략하면 기본으로 upstream으로 설정된 브랜치에 푸시를 시도한다. 발생한 예외는 upstream으로 설정된 리모트 브랜치가 없어서 발생한 것이다.

```bash
git push --set-upstream origin main
```

따라서 리모트의 main 브랜치를 upstream으로 설정하는 `--set-upstream origin main` 옵션이 필요하다. 내 로컬 브랜치의 이름이 main이기 때문에 upstream 브랜치 이름도 똑같이 맞춰 안내해준 것이다.

원하면 리모트의 다른 브랜치를 upstream으로 설정할 수도 있다. 다만 로컬과 리모트의 브랜치 이름이 다르면 리모트의 어떤 브랜치를 로컬의 어떤 브랜치의 upstream으로 설정하는 것인지 보다 명시적으로 입력해주어야 한다.

```bash
git push --set-upstream origin main:habibi-hello
```

## 로컬 브랜치를 pull되지 않은 커밋이 있는 리모트 브랜치에 푸시하려고 할 때

로컬에서 새로운 파일 mySourceCode2.java를 생성하고 커밋했다. 그리고 리모트에 othersSourceCode1을 생성하고 커밋했다. 그 다음 푸시를 하려고 해봤다.

```bash
To https://github.com/habibi03336/git-study.git
 ! [rejected]        main -> main (fetch first)
error: failed to push some refs to 'https://github.com/habibi03336/git-study.git'
hint: Updates were rejected because the remote contains work that you do
hint: not have locally. This is usually caused by another repository pushing
hint: to the same ref. You may want to first integrate the remote changes
hint: (e.g., 'git pull ...') before pushing again.
hint: See the 'Note about fast-forwards' in 'git push --help' for details.
```

로컬에서 가지지 않은 변경사항이 있다는 이유로 push가 거절되었다. 깃을 활용하는 주요 이유는 여러 사람의 작업을 하나의 upstream에 잘 통합하기 위해서이다. 그런데 만약 upstream에 변경이 있는데도 불구하고 push를 허용하면 다른 사람의 변경 내용을 모른채 로컬의 작업을 계속 푸시하여 문제가 생길 수 있다. 로컬 작업자가 upstream의 변경 내용을 모르는 것 자체가 개발에 문제를 발생시킬 가능성이 높고, 더욱이 upstream의 변경 내용을 이전 코드로 다시 덮어써버릴 위험도 있다.

따라서 pull을 먼저 해서 로컬에서 upstream의 변경 내용을 확인하는 작업을 먼저 하라고 git에서 안내해주는 것이다. 그래서 pull을 했더니 다음과 같은 예외가 발생한다.

```bash
hint: You have divergent branches and need to specify how to reconcile them.
hint: You can do so by running one of the following commands sometime before
hint: your next pull:
hint:
hint:   git config pull.rebase false  # merge
hint:   git config pull.rebase true   # rebase
hint:   git config pull.ff only       # fast-forward only
hint:
hint: You can replace "git config" with "git config --global" to set a default
hint: preference for all repositories. You can also pass --rebase, --no-rebase,
hint: or --ff-only on the command line to override the configured default per
hint: invocation.
fatal: Need to specify how to reconcile divergent branches.
```

힌트를 읽어보니 다양한 브랜치가 있다고 한다. 다양한 브랜치가 있다는 것은 원래 리모트와 로컬이 같은 브랜치인 것처럼 유지되어야 하는데 이 둘이 달라졌음을 의미한다. 그도 그럴 것이 로컬 브랜치는 mySourceCode2.java 파일을 커밋했고, 리모트 브랜치는 othersSourceCode.java를 커밋했다. 둘은 서로 다른 커밋을 가지는 다른 브랜치가 된 것이다.

<div style="text-align: center;">
    <img src="https://raw.githubusercontent.com/habibi03336/case-study/master/2023-11-12-git-exceptions/img/before-reconciliation.png" alt="before reconciliation" width="600"/>
</div>

이제 서로 달라진 브랜치를 원래의 목적에 맞게 다시 하나의 브랜치로 합지는 조정(reconciliation) 과정이 필요하다. 힌트를 읽어보니 이 때 조정의 방식으로 merge, rebase, fast-foward only 3가지가 있다고 한다.

3가지 모두 시도해봤는데 머지, 리베이스, fast-foward only 3가지 모두 동일하게 동작했다. 로컬의 커밋 이후에 리모트의 변경을 가져오는 새로운 커밋이 하나 더 생겼다. 리모트를 보니 기존의 커밋이 사라지고 로컬 커밋을 동일하게 가지고 있었다. 파일 단위에서 겹치는 변경사항이 없다보니 fast-foward 조정이 모든 전략에 동일하게 일어난 것으로 보인다.

<div style="text-align: center;">
    <img src="https://raw.githubusercontent.com/habibi03336/case-study/master/2023-11-12-git-exceptions/img/after-reconciliation.png" alt="after reconciliation" width="600"/>
</div>

로컬과 upstream인 리모트가 서로 다른 브랜치가 되었을 때 이를 하나의 브랜치로 다시 합치는 조정 작업이 필요하고 따라서 push나 pull 명령어에 대해서 예외가 발생한 것이다.

> Tip!  
> 리모트 브랜치를 따서 작업을 할 때 리모트 브랜치를 먼저 따고 로컬 브랜치 따는 것이 좋다. 로컬 브랜치를 먼저 따고 리모트 브랜치를 따면 짧은 사이 리모트에 변경이 생기는 경우 로컬에서 리모트로 푸시할 때 조정 작업을 거쳐야 하기 때문이다.

## 로컬 브랜치 간 이동을 하려고 할 때

main 브랜치에서 develop 브랜치를 만들었다. 그리고 main 브랜치에서 mySourceCode.java를 수정하고 커밋했다. 그리고 main 브랜치에서 mySourceCode.java를 추가적으로 수정하고 커밋을 하지 않은채 develop 브랜치로 checkout을 시도했더니 다음과 같은 예외가 발생했다. (main 커밋 이후 develop 브랜치에서 mySourceCode.java를 수정하고 main으로 checkout을 시도해도 똑같은 예외가 발생한다.)

```bash
git checkout develop
error: Your local changes to the following files would be overwritten by checkout:
        mySourceCode.java
Please commit your changes or stash them before you switch branches.
Aborting
```

checkout을 하면 mySourceCode.java의 변경 내용이 사라진다는 안내를 해주면서 checkout을 막았다. 그리고 checkout을 하기 전에 변경 사항을 커밋하거나 stash하라는 안내를 한다.

이 예외는 브랜치를 checkout하는 과정에서 어떤 파일의 변경내용이 사라질 때 나는 것임을 확인할 수 있다. 변경사항이 있더라도 checkout 과정에서 변경내용이 있는 파일을 덮어쓰지 않는다면 이 예외는 발생하지 않는다.

main 브랜치와 develop 브랜치는 mySourceCode.java에 대해서 서로 다른 형상을 가지고 있다. 따라서 이 두 브랜치 간에 checkout을 할 때는 main 브랜치에 현재까지 커밋된 mySourceCode.java(develop -> main 일 때) 혹은 develop 브랜치에 현재까지 커밋된 mySourceCode.java 형상을 불러오게 된다(main -> develop일 때). 이렇게 형상을 불러오는 과정에서 로컬 파일을 덮어쓰게 된다.

커밋을 하더라도 두 브랜치 간 checkout을 하면 파일을 덮어쓰는 것은 똑같지만 변경사항이 이미 한 브랜치에 커밋이 되어있기 때문에 언제든 불러올 수 있다. 하지만 커밋 없이 브랜치를 옮기게 되면 변경사항은 어디에도 커밋되지 않았기 때문에 관리되지 않고 사라져 버린다. 깃은 이점을 탐지하여 예외를 발생시키는 것이다.

깃은 변경사항이 사라지지 않도록 아예 커밋을 하거나 stash라는 기능을 활용해서 임시적으로 변경사항을 저장하고 checkout하라고 안내한다. 만약 변경사항이 중요하지 않다면 변경사항을 제거해버리고(git restore) checkout해도 된다.

stash를 하면 restore를 한 것처럼 변경사항이 사라진다. 하지만 변경사항을 어딘가에 저장했다는 안내가 나온다. 변경사항이 별도로 저장되고 이전 커밋의 상태로 돌아갔기 때문에 checkout이 가능하다.

```bash
git stash
Saved working directory and index state WIP on main: dfd0440 feat: mysource code 1 by main branch
```

별도로 저장된 변경사항을 나중에 다음과 같이 불러올 수 있다. 그러면 가장 최근 stash 되었던 형상으로 돌아오게 된다.

```bash
git stash pop
```

커밋을 할 상태는 아닌데 변경사항을 잃지 않으면서 checkout을 하고 싶다면 stash를 활용하면 된다.
