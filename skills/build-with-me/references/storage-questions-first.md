# 저장이 필요한 순간

"적은 게 어디 남아야 다음 날도 보이죠?" — 그 순간에만 이 파일을 읽는다. 이름(저장소·표·열)은 필요가 드러난 뒤에 붙인다.

## 질문 먼저
"이 앱이 나중에 대답해야 할 질문"을 같이 적는다. 에이전트가 3개를 먼저 쓴다 — 예: "오늘 응답이 몇 개예요?", "어제 예약한 사람 이름은?", "가장 많이 고른 답은?" → "빼거나 더할 게 있어요?"

## 구조 도출
질문마다 "이 질문에 답하려면 무엇이 남아 있어야 하나"를 한 줄씩 → 남아야 할 것들을 한데 묶는다 → "그 묶음을 표라고 부를게요." 열 이름은 학습자의 말 그대로(한글 허용 안 함 — 영문 소문자로 에이전트가 바꾸고 한 줄로 알린다).

## Worked Example 한 줄
표에 실제 한 줄을 같이 적어본다: "김민수 / 2026-09-01 14:00 / 2명". 이 한 줄이 열 이름의 검증이다.

## 접근 규칙을 쉬운 말로
"누구나 적을 수 있고, 보는 건 당신뿐" — 남이 남긴 것에 이름·연락처가 들어오면 **항상** 이 규칙. 이름·연락처가 들어오면 고르지 않고 첫 문장으로 잠근다. 개인정보가 없을 때만 두 문장 중 하나를 학습자가 고른다 — 목록을 남에게 보여주는 앱(재고표 공개)은 "누구나 볼 수 있고, 적는 건 당신뿐".

## SQL과 access-rules.json 같이 만들기
[`assets/rls.sql.tmpl`](../assets/rls.sql.tmpl)의 `{{table}}`·`{{columns}}`를 채운 SQL과, 같은 뜻의 `access-rules.json`(형식은 [`assets/access-rules.example.json`](../assets/access-rules.example.json))을 **함께** 만든다. json의 `probe_row`에는 Worked Example 한 줄을 넣는다. 둘이 어긋나면 `guard.py probe`가 잡는다.

## 손 넘기기: 저장소 계정 → SQL → 주소·공개키
세 번 ★ 형식으로.

① "이건 당신이 해야 해요. 화면에 **Start your project**가 보이면 **New project**를 누르세요. 끝나면 '됐어요'라고 해주세요."

② "이건 당신이 해야 해요. 화면에 **SQL Editor**가 보이면 아래 글을 붙여넣고 **Run**을 누르세요. 끝나면 '됐어요'라고 해주세요."

SQL 전문을 보여준다(예외 항목). 아래는 예시다 — 실제로는 "## SQL과 access-rules.json 같이 만들기"에서 채운 SQL을 보여준다.

```sql
-- responses: 누구나 적을 수 있고, 보는 것과 지우는 것은 당신(대시보드)뿐
create table if not exists public.responses (
  id bigint generated always as identity primary key,
  created_at timestamptz not null default now(),
  name text not null,
  slot text not null,
  people int not null
);
alter table public.responses enable row level security;
create policy "anyone can insert" on public.responses for insert to anon with check (true);
-- select/delete 정책 없음 = anon은 볼 수도 지울 수도 없음
```

"빨간 글자가 나오면 첫 줄만 읽어주세요" → 에러 번역 세 줄(무슨 일 / 왜 / 뭘 할지) → 고친 SQL을 다시 준다. **두 번 실패하면** 손 넘기기 실패 경로(`carry-on.md`)로 넘어간다.

③ "이건 당신이 해야 해요. 화면에 **Project Settings → API**가 보이면 **Project URL**과 **anon public** 키를 복사해서 여기에 붙여주세요. 끝나면 '됐어요'라고 해주세요."

## 설정 두 줄 같이 보기
`config.js` 두 줄을 보여주고 한 줄 확인 ★ (모든 강도):

```js
const SUPABASE_URL = "https://xxxx.supabase.co";
const SUPABASE_ANON_KEY = "eyJ...";
```

"위 줄은 저장소 주소, 아래 줄은 공개용 열쇠예요. 이 열쇠는 화면에 실려 나가도 되는 열쇠고, 진짜 문은 아까 만든 접근 규칙이에요. 맞아요?"

배포 전 `guard.py probe <URL> <KEY> access-rules.json` 결과를 쉬운 말로(`publish-safety-gate.md` ①).
