---
name: tomd
description: Convert an office/document file (Word .docx, Excel .xlsx, PowerPoint .pptx, PDF, HWP/HWPX 한글, CSV, HTML, images) into a clean Markdown note with YAML frontmatter that matches the surrounding folder's existing notes. Use when the user types /tomd <파일명> or asks to convert/turn a docx/xlsx/pptx/pdf/hwp/한글/엑셀/워드/피피티 file into a .md / markdown note, or to "AI가 읽을 수 있게" 문서를 마크다운으로 변환.
---

# tomd — 문서 → 마크다운 변환 스킬

서로 다른 확장자의 업무 파일(Word·Excel·PPT·PDF·HWP 등)을 AI가 읽기 좋은 **마크다운(.md)** 으로 변환하고, **저장 폴더의 기존 노트와 동일한 YAML 프론트매터 스타일**을 자동으로 입혀 저장한다.

## 호출 방법

사용자가 다음과 같이 호출한다:

```
/tomd <파일명 또는 경로>            # 예: /tomd 라포랩스 위원별 지적사항
/tomd <파일명> --out <저장경로.md>  # 저장 위치 지정
```

`<파일명>`은 정확한 경로가 아니어도 된다. 일부 이름·키워드만 줘도 현재 폴더(및 하위)에서 찾아낸다.

## 지원 형식 → 엔진

| 확장자 | 엔진 |
|---|---|
| `.docx .doc .pptx .ppt .xlsx .xls .pdf .csv .html .htm .png .jpg .jpeg .json .xml .epub` | **markitdown** (`markitdown[all]`) |
| `.hwp` (한글 2007+ 바이너리) | **pyhwp** (`hwp5txt`) |
| `.hwpx` (한글 XML) | 내장 ZIP/XML 파서 |
| `.md .txt` | 그대로 통과(프론트매터만 보강) |

## 절차 (반드시 순서대로)

### 1. 대상 파일 찾기
- 사용자가 준 이름/키워드로 현재 작업 폴더에서 **Glob**으로 후보를 찾는다 (`**/*<키워드>*.{docx,xlsx,pptx,pdf,hwp,hwpx,...}`).
- 후보가 여러 개면 목록을 보여주고 어느 것인지 확인한다. 1개면 그대로 진행.

### 2. 본문 추출 (convert.py 실행)
스킬 폴더의 추출기를 실행한다. 경로에 공백·대괄호가 있을 수 있으니 **반드시 따옴표로 감싼다**.

```bash
python "<이 스킬 폴더>/scripts/convert.py" "<찾은 파일 경로>"
```

- STDOUT으로 JSON 요약이 출력된다: `{ ok, source_format, out_path, char_count, table_count, title_guess, warnings }`.
- `ok:false` 면 `error` 메시지를 사용자에게 그대로 전달하고, HWP 의존성 오류면 `pip install pyhwp` / `pip install "markitdown[all]"` 안내.
- 추출된 **본문(프론트매터 없음)** 은 `out_path` 의 임시 파일(`*.tomd.tmp.md`)에 저장된다.

### 3. 추출 본문 읽기 + 정리
- `out_path` 파일을 **Read** 한다.
- 변환 노이즈를 정리한다:
  - 모든 줄이 `**...**` 로 굵게 감싸져 있으면(원본이 전체 볼드인 경우) 의미 없는 볼드는 제거하고 **제목/핵심 수치 등 강조가 필요한 곳만** 남긴다.
  - 빈 표 셀(`|  |` / `| --- |`)만 있는 무의미한 테이블 골격은 제거하고, 실제 내용은 적절한 제목(`##`)·목록·콜아웃으로 재구성한다.
  - 표 데이터(엑셀 등)는 깨지지 않았는지 확인하고 정렬한다.
- **내용을 창작하지 않는다.** 원문에 없는 사실을 채우지 말 것. 원문이 잘려있으면 잘린 그대로 두거나 `⚠️ (원문 미완성)` 으로 표시.

### 4. 프론트매터 스타일 학습 (중요)
저장 대상 폴더의 **기존 `.md` 노트 1~2개를 Read** 해서 그 폴더의 YAML 프론트매터 규칙을 그대로 따른다.

- 어떤 키를 쓰는지(예: `title, date, type, client, brand, company, source, status, relevance, confidential, tags, author, last-updated, related`), 키 순서, 태그 표기(`"#태그"`), 날짜 포맷(`YYYY-MM-DD`), `related` 위키링크(`[[파일명]]`) 형식을 **그대로 맞춘다**.
- 폴더에 기존 `.md`가 없으면 상위 폴더나 볼트 루트의 `CLAUDE.md`·다른 노트를 참고하고, 그래도 없으면 합리적인 최소 프론트매터(`title, date, type, source, tags, author, last-updated`)를 만든다.
- 값은 **본문 내용 + 폴더 맥락**에서 추론한다 (client/brand/company, 관련 문서 `related` 등). 날짜는 문서 내 날짜 또는 오늘 날짜.

### 5. 최종 노트 저장
- 저장 경로: 사용자가 `--out`을 줬으면 그 경로. 아니면 **원본과 같은 폴더**에 `<정리된이름>.md`.
  - 파일명은 원본의 접두 메타(`[PA]` 등)·깨진 문자(`Q^0A`)를 정리해 읽기 좋게 만든다 (예: `라포랩스_위원별_지적사항_대외커뮤니케이션_QA.md`).
- 같은 이름 파일이 이미 있으면 **덮어쓰기 전에 사용자에게 확인**한다.
- `[프론트매터] + 정리된 본문` 을 **Write** 로 저장.

### 6. 정리 + 보고
- 임시 파일 `*.tomd.tmp.md` 를 **삭제**한다.
- 저장 경로, 소스 형식, 글자 수, 경고(있으면)를 한 줄로 보고한다.

## 의존성 (최초 1회)
이 PC에는 이미 설치 확인됨: `markitdown[all]`, `python-docx`, `openpyxl`, `python-pptx`, `PyMuPDF`, `pyhwp`, `pywin32`.
누락 시:
```bash
pip install "markitdown[all]" pyhwp
```

## 주의
- 경로에 공백·`[]`·한글이 흔하므로 셸 인자는 항상 따옴표로 감싼다.
- 이미지 위주 PDF/HWP는 텍스트가 거의 안 나올 수 있다(OCR 미적용). 그 경우 경고를 그대로 전달한다.
- 한컴오피스 COM 자동 변환은 이 PC에서 불가(설치 껍데기만 존재) → `.hwp`는 pyhwp 경로만 사용.
