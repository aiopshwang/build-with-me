# Evals

Task 14의 러너가 읽는 픽스처: [`personas/`](personas/)의 학습자 3종과 [`scenarios/`](scenarios/)의 시나리오 5종. 학습자는 모델이 연기하고, 시나리오는 그 학습자가 첫 메시지로 뭘 말하고 무엇을 이미 알고 있는지를 정의한다.

## 12런 매트릭스

시나리오 × 페르소나 짝은 5개로 고정: `inventory`×`frozen`, `cafe-map`×`frozen`, `survey`×`overconfident`, `booking`×`overconfident`, `quote`×`impatient`. 다섯 짝 각각 RED(`--arm baseline`)와 GREEN(`--arm candidate`)으로 한 번씩, 전부 Claude 호스트 — 이게 Success Criteria 표가 세는 10런(RED 5 + GREEN 5, Claude 전량)이다. 그 10런과 별개로 Codex 호스트에서 GREEN만 두 번 더 돈다(`--arm candidate --host codex`): `inventory`×`frozen`(저장 없음)과 `survey`×`overconfident`(저장 있음). Codex 2런은 참고용으로 따로 보고하고 Claude의 10런 집계에 섞지 않는다.

| # | 시나리오 | storage | 페르소나 | 조건 | arm | 호스트 |
|---|---|---|---|---|---|---|
| 1 | inventory | none | 얼어붙는 (`frozen`) | RED | baseline | Claude |
| 2 | inventory | none | 얼어붙는 (`frozen`) | GREEN | candidate | Claude |
| 3 | cafe-map | none | 얼어붙는 (`frozen`) | RED | baseline | Claude |
| 4 | cafe-map | none | 얼어붙는 (`frozen`) | GREEN | candidate | Claude |
| 5 | survey | supabase | 과신 (`overconfident`) | RED | baseline | Claude |
| 6 | survey | supabase | 과신 (`overconfident`) | GREEN | candidate | Claude |
| 7 | booking | supabase | 과신 (`overconfident`) | RED | baseline | Claude |
| 8 | booking | supabase | 과신 (`overconfident`) | GREEN | candidate | Claude |
| 9 | quote | none | 조급 (`impatient`) | RED | baseline | Claude |
| 10 | quote | none | 조급 (`impatient`) | GREEN | candidate | Claude |
| 11 | inventory | none | 얼어붙는 (`frozen`) | GREEN(추가) | candidate | Codex (T17에서 `--host codex` 추가 예정 — 지금은 없음) |
| 12 | survey | supabase | 과신 (`overconfident`) | GREEN(추가) | candidate | Codex (T17에서 `--host codex` 추가 예정 — 지금은 없음) |

Claude 10런(RED 5 + GREEN 5) + Codex GREEN 2런 (총 12런). 판정 기준은 설계 스펙의 Success Criteria 표를 그대로 쓴다 — 이 README는 그 표를 다시 정의하지 않는다.

## 실행

```bash
python evals/run_learner.py --scenario <s> --persona <p> --arm baseline|candidate [--host claude|codex] --output <dir>
python evals/count.py <rep-dir>
```

`<s>`는 `scenarios/`의 파일 이름(확장자 제외: `inventory` · `cafe-map` · `survey` · `booking` · `quote`), `<p>`는 `personas/`의 파일 이름(확장자 제외: `frozen` · `overconfident` · `impatient`). `--host`를 생략하면 Claude. 위 표 11·12행만 `--host codex`를 붙인다 (T17에서 `--host codex` 추가 예정 — 지금은 없음).

## 숫자는 카운트만 인용한다

여기와 결과 파일이 인용하는 것은 항상 결정론적 카운트뿐이다 — 파일이 존재하는지, 명령이 0으로 끝났는지, 발화에 특정 패턴이 몇 번 나오는지. 모델의 판정이나 점수는 인용하지 않는다.
