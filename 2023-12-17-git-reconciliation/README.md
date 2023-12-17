# Git Reconciliation

Git은 분산된 환경에서 여러 사람이 작업할 수 있도록 하는 형상관리 툴이다. 하나의 어플리케이션이 되기 위해서 분산된 환경에서 작업된 작업물도 결국 하나로 합쳐져야 한다. 분산된 환경에서 작업을 할 수 있도록 하는 것이 `브랜치` 개념이고, 이 서로 다른 브랜치를 하나로 합치는 것이 `조정(reconciliation)`이다.

reconciliation은 서로 '달라진' 두 브랜치를 하나로 합칠 때 필요한 작업이다. 만약 두 브랜치가 하나라도 다른 커밋을 가지고 있다면 두 브랜치가 서로 다른 것이다. 또한 어느 시점 이전으로는 같은 커밋을 가지고 있는 경우에만 reconciliation을 할 수 있다. 그래서 앞 서 '달라진'이라고 적은 것이다.

A브랜치와 B브랜치를 합친다면, A브랜치의 형상, B브랜치의 형상, 그리고 A와 B가 같았던 지점의 형상 이 3가지 형상을 비교하여 reconciliation이 일어나게 된다.

git의 reconciliation에는 `fast-foward`, `rebase`, `merge` 3가지 방식이 있다. B브랜치가 A브랜치를 합치는 상황을 가정하고 설명하자면, A와 B가 같았던 지점의 형상이 B브랜치의 형상과 같다면 fast-foward reconciliation을 하게된다. 만약 이렇지 않고 A형상, B형상, A와 B가 같았던 지점의 형상 모두가 다르면 rebase나 merge 방식으로 reconciliation하게 된다.

# Rebase

main branch에 빈 source.txt 파일을 만들고 커밋했다. 그리고 A브랜치에서 source.txt를 수정하여 커밋하고, 다시 B브랜치를 만들어 source.txt 수정하고 커밋하였다. 그리고 A브랜치와 B브랜치에서 각각에서 겹치지 않는 파일을 만들어 커밋했다.

<div style="text-align: center;">
    <img src="https://raw.githubusercontent.com/habibi03336/case-study/master/2023-12-17-git-reconciliation/img/branch.png" alt="branches" width="800"/>
</div>

이 상태에서 B브랜치에서 A브랜치를 rebase하면 에러가 발생한다. A브랜치와 B브랜치에서 동일하게 source.txt를 건드렸기 때문이다. A형상과 B형상 중 무엇을 따라야하는지 git은 알지 못한다. 따라서 에러를 발생시키고 둘 중 하나를 선택하라고 하는 것이다. 계속하려면 수동으로 선택 및 스테이징 한 후 "git rebase --continue"를 하면 된다.

```bash
❯ git checkout B-branch-rebase
Switched to branch 'B-branch-rebase'
❯ git rebase A-branch
Auto-merging source.txt
CONFLICT (content): Merge conflict in source.txt
error: could not apply e1dda3f... change source.txt by B branch
hint: Resolve all conflicts manually, mark them as resolved with
hint: "git add/rm <conflicted_files>", then run "git rebase --continue".
hint: You can instead skip this commit: run "git rebase --skip".
hint: To abort and get back to the state before "git rebase", run "git rebase --abort".
Could not apply e1dda3f... change source.txt by B branch
```

파일이 아래와 같이 변경되면서 둘 중 하나를 선택해야함을 나타낸다. B브랜치의 내용을 남기고 진행해보겠다.

```txt
<<<<<<< HEAD
A changes
=======
B changes
>>>>>>> e1dda3f (change source.txt by B branch)
```

```bash
git add sources.txt
git rebase --continue
```

rebase를 하고 나니 B branch의 로그가 다음과 같이 변경되었다. A 브랜치 이후에 B의 변경사항을 담은 커밋을 한 것으로 reconciliation 되었다. 이는 A브랜치에서 B의 커밋을 cherry pick 한 것과 같다. 즉, A브랜치에서 B의 변경사항을 commit한 것과 같다. 기존 B브랜치의 히스토리가 변하게 된다.

```bash
commit f29625964a373ee9c1e99aa69c770ec691f8a593 (HEAD -> B-branch-rebase)
Author: 하지훈 <jnh03336@gmail.com>
Date:   Sun Dec 17 17:16:17 2023 +0700

    add b-source.txt

commit 3fca64adec2c90b0308953ba955868d29013a57f
Author: 하지훈 <jnh03336@gmail.com>
Date:   Sun Dec 17 17:14:16 2023 +0700

    change source.txt by B branch

commit 0dd834f044e4f2e5600db47be50651b749a45333 (A-branch)
Author: 하지훈 <jnh03336@gmail.com>
Date:   Sun Dec 17 17:15:22 2023 +0700

    add a-source.txt

commit 7352bba94cd6a63ca4014a85bc810571f5336fa1
Author: 하지훈 <jnh03336@gmail.com>
Date:   Sun Dec 17 17:13:32 2023 +0700

    change source.txt by A branch

commit 06130181c4b6fcbc29cb205722fe160b478fbfe0 (main)
Author: 하지훈 <jnh03336@gmail.com>
Date:   Sun Dec 17 17:13:04 2023 +0700

    initial commit
```

# Merge

위와 같은 상항에서 Merge를 해봤다. 이번에도 역시 conflicts가 발생한다. 이번에도 B 형상을 선택한 후 merge를 진행했다.

다음과 같은 로그로 바뀌었다. rebase와 다른 점은 기존 A,B 브랜치 커밋 해시번호가 변하지 않는다는 점, merge를 했다는 추가적인 커밋이 남았다는 점, A와 B 브랜치의 커밋이 시간 순서대로 섞였다는 점이다. 그리고

```bash
commit 4151b5f96e8f9f67dbddc555904604b92cf3f5d2 (HEAD -> B-branch-merge)
Merge: 12d5e46 0dd834f
Author: 하지훈 <jnh03336@gmail.com>
Date:   Sun Dec 17 17:23:59 2023 +0700

    Merge branch 'A-Branch' into B-branch-merge

commit 12d5e46bdb7328f507019fab1c0b05e7abdc4b5d
Author: 하지훈 <jnh03336@gmail.com>
Date:   Sun Dec 17 17:16:17 2023 +0700

    add b-source.txt

commit 0dd834f044e4f2e5600db47be50651b749a45333 (A-branch)
Author: 하지훈 <jnh03336@gmail.com>
Date:   Sun Dec 17 17:15:22 2023 +0700

    add a-source.txt

commit e1dda3f3b4d208c06a34d75d3c2ff57e2d648d16
Author: 하지훈 <jnh03336@gmail.com>
Date:   Sun Dec 17 17:14:16 2023 +0700

    change source.txt by B branch

commit 7352bba94cd6a63ca4014a85bc810571f5336fa1
Author: 하지훈 <jnh03336@gmail.com>
Date:   Sun Dec 17 17:13:32 2023 +0700

    change source.txt by A branch

commit 06130181c4b6fcbc29cb205722fe160b478fbfe0 (main)
Author: 하지훈 <jnh03336@gmail.com>
Date:   Sun Dec 17 17:13:04 2023 +0700

    initial commit
```

merge의 경우 시간 순으로 A브랜치, B브랜치 커밋을 그대로 가져온다. 그리고 merge 커밋으로 두 브랜치를 합치게된다. 0dd834f 커밋 뒤에 12d5e46 커밋이 있는데도 0dd834f 커밋이 12d5e46의 형상에는 영향을 미치지 않는다. 12d5e46 형상을 직접 확인해봐도 a-source.txt 파일은 없다. 머지 커밋에서야 a-source.txt가 최종 형상에 추가되게 된다.

머지는 두 브랜치의 커밋을 서로 독립적으로 저장하고, 마지막 머지 커밋을 통해서 형상을 합치는 방식인 것이다. git log 상 순서대로 표시되기는 하지만 두 브랜치의 커밋은 머지 전까지 각각의 형상을 가지고 있다. 이런 방식을 통해 여러 브랜치를 합칠 때도 보다 수월하게 reconciliation 할 수 있는 것으로 보인다.

---

## rebase의 활용

rebase는 브랜치의 히스토리를 바꿔버린다. 따라서 여러 사람이 작업을 하는 브랜치에서는 사용을 지양해야한다. 브랜치의 히스토리가 갑자기 바뀌어 버리면 이를 모르는 사람은 코드를 푸시하는데 애를 먹을 것이다.

다만 rebase를 활용하면 좋은 경우가 있다. 개인 작업 브랜치에서 upstream 브랜치로부터 pull을 자주 받는 경우 sync를 위한 머지 커밋이 많이 생기된다. 이런 경우 rebase를 활용하면 upstream과의 sync를 깔끔하게 유지할 수 있다.

---

**참조**  
<https://hades.github.io/2010/03/git-your-friend-not-foe-vol-4-rebasing>
