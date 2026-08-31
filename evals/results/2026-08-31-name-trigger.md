# 이름 언급 트리거 검증 (v0.2.0, quote-named)

첫 검증에서 유일하게 자동 발동에 실패한 시나리오는 quote였다 — 첫 메시지("견적 계산기요. 평수 넣으면 금액 나오게.")에 초보자 단서가 없어서다([2026-08-30-first-validation.md](2026-08-30-first-validation.md) "발동" 절). v0.2.0은 description에 "스킬 이름이 어떤 문장꼴로든 언급되면"을 추가했고, 이 런은 그 구멍이 실제로 막혔는지 잰다.

## 방법

- 시나리오 [`quote-named`](../scenarios/quote-named.md): quote와 동일하되 첫 메시지 앞에 이름 언급 한 구절 — `build with me skill 기반으로 개발 시작하자.` 초보자 단서도, 시작하기.md의 호출 문구도 없다. 문구는 description 예시("build with me 기반으로…")와 다르게 "skill"이 끼어 있어 예시 문장 암기가 아니라 일반화를 확인한다.
- 실행: `python evals/run_learner.py --scenario quote-named --persona impatient --arm candidate --max-turns 8` (Claude 호스트, 스킬은 v0.2.0 HEAD 6ca2ff8 로컬 복사).

## 카운트

| 항목 | quote GREEN (자동, 첫 검증) | quote-named GREEN (이 런) |
| --- | --- | --- |
| skill_invoked | false | **true** |
| 첫 화면까지 에이전트 턴 수 | None | 1 |
| 첫 화면 전 질문 수 | 6턴 동안 다수 | 0 |
| 파일(MY-WORDS/MAP/PROGRESS + stamp) | 0/4 | 4/4 (stamp `build-with-me v0.2`) |

- 이 런은 v0.2.0 영어 파일명(`PROGRESS.md`·`MAP.md`·`MY-WORDS.md`)이 실런에서 생성되고 stamp가 새 버전과 일치함을 처음 확인한 런이기도 하다.
- 런은 에이전트 1턴 뒤 학습자 모델이 `[끝]`으로 대화를 끝내 종료됐다(러너 정상 종료, exit 0). 발동·첫 화면·첫 화면 전 질문은 전부 턴 1의 현상이라 판정에 영향이 없고, 걸음 완료 뒤에야 쌓이는 항목(기록 대사 비율, 내-말로 문장 수)은 이 런에서는 세지 않는다.

## 숫자는 카운트만 인용한다

위 값은 전부 결정론적 카운트다 — 러너의 `skill_invoked`(트랜스크립트 이벤트), 파일 존재 여부, `count.py` 출력. 모델의 판정 점수는 없다.
