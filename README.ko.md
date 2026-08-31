# Build With Me

*코딩을 못 한다는 건 문제가 아니라 시작 조건입니다.*

[![Validate](https://img.shields.io/github/actions/workflow/status/aiopshwang/build-with-me/validate.yml?branch=main&label=validate)](https://github.com/aiopshwang/build-with-me/actions/workflows/validate.yml)
[![Version](https://img.shields.io/github/v/release/aiopshwang/build-with-me?label=version)](https://github.com/aiopshwang/build-with-me/releases)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[English](README.md)

**처음이신가요?** 한 장짜리 시작 문서부터 보세요: [시작하기.md](시작하기.md) (English: [GETTING-STARTED.md](GETTING-STARTED.md)). 이 README는 설치할지 권할지 판단하는 강사·개발자를 위한 문서입니다.

Build With Me는 코딩을 못 하는 사람을 한 문장에서 시작해 몇 분 만에 로컬 화면으로, 그다음엔 공유 가능한 링크로 데려가는 Agent Skill입니다 — 막힐 만한 순간에만 가르칩니다.

- [누구를 위한 것인가](#누구를-위한-것인가)
- [설치와 부르기](#설치와-부르기)
- [무슨 일이 일어나나](#무슨-일이-일어나나)
- [스킬 없이, 스킬 켜고](#스킬-없이-스킬-켜고)
- [폴더에 남는 것](#폴더에-남는-것)
- [이어서 하기](#이어서-하기)
- [공개되기 전에](#공개되기-전에)
- [필요한 것](#필요한-것)
- [Codex에서](#codex에서)
- [막혔을 때](#막혔을-때)
- [근거와 재현 방법](#근거와-재현-방법)
- [범위, 버전, 피드백, 라이선스](#범위-버전-피드백-라이선스)

## 누구를 위한 것인가

**이런 사람에게:** 코딩을 못 한다고 말하는 사람, 처음 해보는 사람, 남에게 보여줄 걸 만들고 싶은 사람, 지난번에 하던 걸 이어서 하려는 사람.

**이런 사람에겐 아닙니다:** 코드를 한 줄씩 설명받고 싶은 개발자, 그리고 코드 리뷰.

## 설치와 부르기

```bash
npx skills add aiopshwang/build-with-me
```

마지막 줄에 초록색 `Done!`이 뜨고 그 위에 build-with-me가 적혀 있으면 설치된 겁니다. 그 뒤로 아무 말이 없는 게 정상이에요 — 부를 때까지 조용히 있습니다.

그 폴더에서 `claude` 또는 `codex`를 켜고 이렇게 칩니다:

```text
코딩은 몰라요. 만들고 싶은 게 있어요.
```

(안 알아들으면: `build-with-me 스킬을 써줘`)

## 무슨 일이 일어나나

골든 패스, 한 걸음에 한 줄:

1. **자기 폴더 하나.** 지금 폴더가 비어 있지 않거나 이미 저장소면 `문서/내앱/<이름>`을 제안하고 그 폴더로 옮기는 일은 사람에게 넘깁니다. 보이는 것: 이 프로젝트만 들어 있는 빈 폴더.
2. **당신의 한 마디.** 첫 대사는 양식이 아니라 안심시키는 말이고, 아이디어가 없으면 질문 대신 예시를 줍니다. 보이는 것: 화면이 뜨기 전에 받는 질문은 정확히 하나.
3. **90초짜리 임시 화면.** 한 마디를 듣자마자 `index.html` 하나를 만들고 미리보기 서버를 켜서 열어줍니다. 보이는 것: 브라우저에 뜬, 내 제목이 적힌 페이지와 "이건 자리만 잡은 거예요"라는 한 줄.
4. **한 줄짜리 북극성.** 에이전트가 먼저 씁니다 — 누가 열면 뭐가 보이고 뭘 하면 뭐가 되는지 — 그리고 당신은 틀린 데만 고칩니다. 보이는 것: 내가 동의한, 내 앱을 설명하는 한 문장.
5. **걸음 지도.** 결과에서 입력까지 거꾸로 파고 그 순서를 뒤집은 것이 걸음 목록입니다. 범위 밖의 요구는 다투지 않고 "그건 2탄"에 적습니다. 보이는 것: `MAP.md`의 체크리스트.
6. **한 번에 한 걸음, 매번 눈에 보이게.** 화면에 새로 생긴 것이 없으면 그 걸음은 끝난 게 아니고, 당신이 보기 전에는 다음으로 넘어가지 않습니다. 보이는 것: 걸음마다 페이지에 하나씩 늘어나는 것.
7. **끝까지 동작하는 기능 하나.** 저장(Supabase)은 "적은 게 어디 남아야 다음 날도 보이죠?"의 답이 저장이어야 할 때만 들어오고, 접근 규칙을 쉬운 말로 먼저 합의합니다. 보이는 것: 내 페이지에 남아 있는 내 데이터.
8. **게이트, 그다음 링크.** GitHub 계정은 정말 필요한 순간에만 손에 넘기고, 네 질문에 답한 뒤에 배포합니다. 보이는 것: 그 네 개의 답이 나오기 전에는 존재하지 않던 공개 주소.

출처: [`SKILL.md`](skills/build-with-me/SKILL.md), [`start-and-decompose.md`](skills/build-with-me/references/start-and-decompose.md), [`storage-questions-first.md`](skills/build-with-me/references/storage-questions-first.md).

## 스킬 없이, 스킬 켜고

같은 재고표 요청("엑셀 재고 파일을 화면으로 보여주는 앱")에 대한 실제 실행 기록 1턴째, 스킬 없이(RED) vs 스킬 켜고(GREEN):

**스킬 없음 — 1턴째 에이전트 응답:**

> 현재 폴더가 비어 있네요. 몇 가지 여쭤볼게요.
>
> **엑셀 재고 파일을 화면으로 보여주는 앱을 만들어 드릴 수 있어요.** 시작하기 전에 몇 가지만 알려주세요.
>
> **1. 엑셀 파일은 어떻게 생겼나요?**
>
> - 품목명, 수량, 단위, 날짜 같은 항목이 있나요?
> - 컬럼(열) 이름들을 알려주실 수 있나요?
>
> (계속 질문 — 화면은 아직 없음)

**build-with-me 켜고 — 같은 시나리오, 1턴째 에이전트 응답:**

> 이 작업은 중요하니 여기까지 적어둘게요 — 다음에 이어서 할 때 이걸 읽어요.
>
> 화면이 뜨면, 제가 생각한 걸 한 줄로 말해볼게요. 틀린 부분만 고쳐주시면 돼요:
>
> **"열면 내가 매주 보는 재고 목록이 한눈에 보이는 화면"**
>
> 맞아요?

첫 검증 10런(Claude, RED 5/GREEN 5)에서 스킬이 켜진 5런 중 5런이 첫 턴에 화면을 열었고, 스킬 없는 5런은 0런이었다. 카운트 방법과 나머지 시나리오는 [evals/results/2026-08-30-first-validation.md](evals/results/2026-08-30-first-validation.md) 참고.

## 폴더에 남는 것

| 무엇 | 왜 있나 |
| --- | --- |
| `PROGRESS.md` | 진행 기록. 걸음이 끝날 때마다 "지금까지 된 것 / 다음" 두 줄. 이어서 할 때 가장 먼저 읽는 파일. |
| `MAP.md` | 지도: 북극성, ✓가 붙는 걸음 목록, "그건 2탄", 두 번 막힌 자리. |
| `MY-WORDS.md` | 걸음마다 학습자 자신의 말로 쓴 한 문장. 빈 걸음은 없습니다 — 나중에 이 앱을 남에게 설명할 때 읽는 파일. |
| `index.html` | 페이지 그 자체. `config.js`와 `access-rules.json`은 저장이 필요할 때만 옆에 생깁니다. |
| `.bwm/` | 미리보기 서버 상태(열려 있는 포트). `archive/`, `.env` 파일들과 함께 git에서 제외됩니다. |
| `CLAUDE.md` / `AGENTS.md` | 다음 세션에 `PROGRESS.md`부터 읽고 "지난번엔 여기까지"라고 말하라는 한 줄이 덧붙습니다. |

`PROGRESS.md`·`MAP.md`·`MY-WORDS.md`에는 열쇠가 없습니다 — 그래서 시작 문서가 막힌 학습자에게 앞의 두 파일을 그대로 강사에게 보내라고 합니다. 템플릿: [`assets/`](skills/build-with-me/assets/).

## 이어서 하기

방법의 핵심은 기록을 **보이게** 한다는 것입니다. 걸음이 끝날 때마다 에이전트는 두 줄을 쓰면서 왜 쓰는지 말합니다("이 작업은 중요하니 여기까지 적어둘게요 — 다음에 이어서 할 때 이걸 읽어요"). git 커밋은 보이지 않게, 기록은 보이게.

새 세션이든 맥락이 정리된 직후(compaction)든 첫 행동은 `PROGRESS.md` 읽기이고, "지난번엔 여기까지: … 다음은 …이에요"라고 말합니다. `CLAUDE.md`/`AGENTS.md`에 덧붙은 한 줄이 이걸 다시 시키므로, 학습자는 맥락이 사라졌다는 사실조차 알 필요가 없습니다.

막히면 `PROGRESS.md`와 `MAP.md`를 강사(또는 동료)에게 보내는 것이 탈출구입니다 — `guard.py pre-share`가 검사하는 바로 그 두 파일입니다. 출처: [`carry-on.md`](skills/build-with-me/references/carry-on.md).

## 공개되기 전에

순서는 고정입니다: **호스팅 계정 → 네 질문 → 배포 → 링크.** 게이트를 통과하기 전에는 공개 주소가 존재하지 않습니다. 첫 공개는 네 개 전부, 재배포는 바뀐 것이 네 질문에 닿지 않으면 한 줄로 통과합니다.

1. **누가 볼 수 있나?** 링크를 아는 사람 누구나. 에이전트는 저장 규칙을 쉬운 말 한 문장으로 말하고, 방금 `guard.py probe`가 실제 API에 물어본 결과를 붙입니다. 남이 남기는 데이터에 이름·연락처가 들어오면 볼 수 있는 사람은 고르는 게 아니라 당신 하나로 잠급니다.
2. **비밀키가 밖에 나가나?** `guard.py pre-share .`가 폴더를 훑고, 그 답을 경고 줄까지 그대로 읽어줍니다.
3. **비용이 무한인가?** 저장소가 없으면 통과. 있으면 무료 요금제인지 한 줄로 확인합니다 — 무료 저장소는 한도에 닿으면 청구되는 게 아니라 멈춥니다.
4. **되돌릴 수 있나?** 내리는 건 에이전트에게 한 마디면 되고, 몇 분 뒤에 주소가 응답하지 않게 됩니다.

**절대 하지 않는 것:** 비밀키를 채팅에 적기 · 자기 서버를 직접 띄우기(미리보기는 이 스킬의 서버 명령으로만) · 정해진 스택(HTML 한 파일 + 저장소 하나) 밖으로 나가기 · 돈·계정·삭제·공개 외의 일에 "해도 될까요?"라고 묻기. 출처: [`publish-safety-gate.md`](skills/build-with-me/references/publish-safety-gate.md), [`guard.py`](skills/build-with-me/scripts/guard.py).

## 필요한 것

- **Claude Code 또는 Codex** — 호출하는 에이전트.
- **Node.js** — `npx` 설치 명령에 필요합니다.
- **Python 3** — 미리보기 서버와 `guard.py`에 필요합니다. 파이썬이 없으면 Windows에서는 [`serve.ps1`](skills/build-with-me/scripts/serve.ps1)이 같은 일을 합니다.
- **Git · GitHub CLI(`gh`) · GitHub 계정** — 공개 걸음에서만. `winget install GitHub.cli`는 에이전트가 직접 돌리고, 가입과 여덟 글자 코드 로그인만 사람에게 넘깁니다.
- **Supabase 계정** — 저장이 필요할 때만. 아니면 아예 나오지 않습니다.
- 측정 환경은 **Windows 11**.

## Codex에서

Codex는 프로젝트의 `AGENTS.md`를 읽습니다 — 그래서 이어가기 한 줄을 `CLAUDE.md`와 `AGENTS.md` 양쪽에 씁니다. 설치하면 스킬은 프로젝트 폴더의 `.agents/skills/build-with-me/`에 들어가고 Claude Code는 같은 곳을 가리키는 링크를 받습니다. Codex에 표시되는 이름과 기본 프롬프트 `$build-with-me: I can't code. Help me build something I can show people.`는 [`agents/openai.yaml`](skills/build-with-me/agents/openai.yaml)이 정합니다.

브라우저 열기는 Codex 샌드박스에서 막히기 때문에, 스킬이 그걸 감지해 그 걸음을 사람에게 넘깁니다 — 주소를 찍어주고 주소창에 붙여넣어 달라고 합니다. `workspace-write` 샌드박스는 아웃바운드 네트워크도 막아서 배포 걸음이 통과할 수 없습니다. 평가 러너가 쓰는 플래그는 [evals/README.md](evals/README.md)를 보세요.

## 막혔을 때

**`Done!`이 뜨고 아무 일도 안 일어나요.** 원래 그렇습니다. `claude`나 `codex`를 켜고 부르는 문장을 말하기 전까지는 아무것도 하지 않습니다.

**안 켜졌어요.** 폴백 문장을 쓰세요: `build-with-me 스킬을 써줘`. 첫 검증에서 5개 시나리오 중 4개는 첫 메시지만으로 켜졌고, 폴백 문장을 덧붙이면 5개 전부 켜졌습니다.

**브라우저가 안 열려요.** 에이전트가 대신 주소를 찍어주고 직접 열어달라고 합니다 — `http://127.0.0.1:<포트>`이고, 포트는 `.bwm/serve.json`에 적혀 있습니다.

**배포가 실패했어요.** 에이전트가 조용히 한 번 재시도하고, 그래도 안 되면 세 줄로 설명합니다: 무슨 일 / 왜 / 뭘 할지. 두 번 실패하면 "오늘은 내 컴퓨터에서 되는 버전까지 마무리할게요"로 마무리하고 재시도 지점을 `PROGRESS.md`에 적습니다.

**링크를 내리고 싶어요.** `내려줘`라고 하면 됩니다. 에이전트가 저장소를 지우거나 비공개로 바꾸고, 몇 분 뒤에 주소가 응답하지 않게 됩니다.

**새로 시작하거나 지우고 싶어요.** `새로 시작`이라고 하면 스킬이 만든 파일만 `archive/<날짜>/`로 옮깁니다 — 지우지 않고, 당신의 다른 파일은 건드리지 않습니다. 스킬을 지우려면 `.agents/skills/build-with-me/`를 삭제하고(`.claude/skills/build-with-me` 링크가 있으면 같이), 업데이트하려면 설치 명령을 다시 실행하면 됩니다.

## 근거와 재현 방법

여기 적히는 결과는 판정 점수가 아닙니다. 이 README나 근거 파일이 결과를 인용할 때는 언제나 결정적인 카운트입니다 — 파일이 존재하는지, 명령이 0으로 끝났는지, 출력에 어떤 문자열이 있는지, 테스트가 확인한 줄인지. 세션이 얼마나 잘 됐는지에 대한 모델의 의견은 인용하지 않습니다.

```bash
python evals/run_learner.py --scenario <s> --persona <p> --arm baseline|candidate [--host claude|codex] --output <dir>
python evals/count.py <rep-dir>
```

매트릭스는 12런입니다: Claude 10런(시나리오×페르소나 다섯 짝을 각각 RED 한 번·GREEN 한 번)에, Codex에서 GREEN만 2런을 더 돌려 따로 보고하고 Claude 10런 집계에는 섞지 않습니다.

- Claude 10런: [evals/results/2026-08-30-first-validation.md](evals/results/2026-08-30-first-validation.md)
- Codex 2런: [evals/results/2026-08-30-codex.md](evals/results/2026-08-30-codex.md)
- 행과 기준값(카운트만): [evals/rubric.json](evals/rubric.json) · 픽스처와 매트릭스: [evals/README.md](evals/README.md)

## 범위, 버전, 피드백, 라이선스

Windows 11에서, Claude Code와 Codex를 호출 에이전트로 삼아 측정했습니다. 호스팅 대상은 GitHub Pages, 저장 대상은 Supabase입니다. macOS에서는 브라우저를 여는 명령만 눈으로 확인했고, 전체 macOS 런은 아직 하지 않았습니다.

**버전.** 현재 0.2.0이고, 무엇이 바뀌었는지는 [CHANGELOG.md](CHANGELOG.md)에 있습니다.

**피드백.** 이슈로 남겨주세요: <https://github.com/aiopshwang/build-with-me/issues>

**라이선스.** MIT. [LICENSE](LICENSE) 참고.
