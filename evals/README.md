# Evals

Task 14의 러너가 읽는 픽스처: [`personas/`](personas/)의 학습자 3종과 [`scenarios/`](scenarios/)의 시나리오 5종. 학습자는 모델이 연기하고, 시나리오는 그 학습자가 첫 메시지로 뭘 말하고 무엇을 이미 알고 있는지를 정의한다.

## 10런 매트릭스

시나리오 5개 × 조건(RED/GREEN) = 10런. 각 조건 안에서 페르소나 배분은 얼어붙는 2 · 과신 2 · 조급 1. RED는 `--arm baseline`(스킬 없이), GREEN은 `--arm candidate`(스킬 적용). 호스트는 Claude 8런 + Codex 2런(저장 없음 1 · 저장 있음 1).

| # | 시나리오 | storage | 페르소나 | 조건 | arm | 호스트 |
|---|---|---|---|---|---|---|
| 1 | cafe-map | none | 얼어붙는 | RED | baseline | Claude |
| 2 | cafe-map | none | 얼어붙는 | GREEN | candidate | Claude |
| 3 | inventory | none | 과신 | RED | baseline | Codex |
| 4 | inventory | none | 과신 | GREEN | candidate | Claude |
| 5 | survey | supabase | 얼어붙는 | RED | baseline | Claude |
| 6 | survey | supabase | 얼어붙는 | GREEN | candidate | Codex |
| 7 | booking | supabase | 과신 | RED | baseline | Claude |
| 8 | booking | supabase | 과신 | GREEN | candidate | Claude |
| 9 | quote | none | 조급 | RED | baseline | Claude |
| 10 | quote | none | 조급 | GREEN | candidate | Claude |

Claude 8런(1·2·4·5·7·8·9·10), Codex 2런(3·6, 저장 없음 1·저장 있음 1). 판정 기준은 설계 스펙의 Success Criteria 표를 그대로 쓴다 — 이 README는 그 표를 다시 정의하지 않는다.

## 실행

```bash
python evals/run_learner.py --scenario <s> --persona <p> --arm baseline|candidate --output <dir>
python evals/count.py <rep-dir>
```

`<s>`는 `scenarios/`의 파일 이름(확장자 제외), `<p>`는 `personas/`의 파일 이름(확장자 제외).

## 숫자는 카운트만 인용한다

여기와 결과 파일이 인용하는 것은 항상 결정론적 카운트뿐이다 — 파일이 존재하는지, 명령이 0으로 끝났는지, 발화에 특정 패턴이 몇 번 나오는지. 모델의 판정이나 점수는 인용하지 않는다.
