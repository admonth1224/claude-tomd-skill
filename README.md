# tomd — 문서 → 마크다운 변환 스킬 (Claude Code)

오피스/문서 파일(Word·Excel·PowerPoint·PDF·HWP/HWPX 한글·CSV·HTML·이미지)을 **AI가 읽기 좋은 마크다운(.md)** 으로 변환하고, **저장 폴더의 기존 노트와 동일한 YAML 프론트매터 스타일**을 자동으로 입혀 저장하는 [Claude Code](https://claude.com/claude-code) 스킬입니다.

---

## ✨ 무엇을 하나요

Claude Code에서 `/tomd <파일명>` 한 줄이면:

1. 폴더에서 파일을 찾고 (키워드 일부만 줘도 됨)
2. 내용을 마크다운으로 추출하고
3. **같은 폴더의 기존 `.md` 노트의 프론트매터 형식을 학습**해서
4. 그 스타일에 맞춘 YAML 프론트매터를 붙여 저장합니다.

## 📦 지원 형식

| 확장자 | 엔진 |
|---|---|
| `.docx .doc .pptx .ppt .xlsx .xls .pdf .csv| markitdown |
| `.hwp` (한글 바이너리) | pyhwp (`hwp5txt`) |
| `.hwpx` (한글 XML) | 내장 ZIP/XML 파서 (의존성 없음) |
| `.md .txt` | 그대로 통과 (프론트매터만 보강) |

---

## 🚀 설치 (받는 사람용)

### 사전 요구사항
- [Claude Code](https://claude.com/claude-code) 설치되어 있을 것
- Python 3.10 이상

### Windows
1. 이 폴더(`claude-tomd-skill`)를 압축 해제해 아무 위치에나 둡니다.
2. 폴더 안에서 **PowerShell**을 열고:
   ```powershell
   ./install.ps1
   ```
   > "이 스크립트를 실행할 수 없습니다" 오류가 나면 한 번만:
   > ```powershell
   > powershell -ExecutionPolicy Bypass -File .\install.ps1
   > ```

### macOS / Linux
폴더 안에서 터미널을 열고:
```bash
bash install.sh
```

설치 스크립트가 하는 일:
- 파이썬 의존성 설치 (`pip install -r requirements.txt`)
- `tomd/` 폴더를 `~/.claude/skills/tomd/` 로 복사

설치 후 **Claude Code를 한 번 재시작**하면 `/tomd` 명령이 인식됩니다.

> 📌 수동 설치: `tomd/` 폴더를 `~/.claude/skills/` 안에 복사하고
> `pip install -r requirements.txt` 만 실행해도 동일합니다.

---

## 🔧 사용법

Claude Code 안에서:

```
/tomd 분기실적 보고서                 # 키워드로 폴더에서 찾아 변환
/tomd report.xlsx --out 노트/요약.md   # 저장 위치 지정
```

예시 — 엑셀 한 장이 이렇게 변환됩니다:

```markdown
---
title: 2025 분기 매출
date: 2026-06-01
type: 데이터
tags:
  - "#매출"
---

## 매출
| 분기 | 매출(억) | 성장률 |
| --- | --- | --- |
| 2024 | 711 | - |
| 2025 | 856 | 20% |
```

---

## 🧩 동작 원리

- `tomd/scripts/convert.py` — 확장자를 감지해 적절한 엔진으로 **본문(프론트매터 없음)** 만 추출하고 JSON 요약을 출력하는 순수 추출기.
- `tomd/SKILL.md` — Claude가 따르는 절차서. 추출 본문을 정리하고, **대상 폴더의 기존 노트 프론트매터를 읽어 그 스타일을 모방**한 뒤 최종 노트를 저장합니다.

프론트매터는 폴더마다 자동으로 달라집니다. Obsidian PR 볼트에 넣으면 그 볼트의 규칙을, 다른 프로젝트에 넣으면 그 프로젝트의 규칙을 따릅니다.

## ⚠️ 참고

- 이미지 스캔 PDF/HWP는 OCR이 없어 텍스트가 거의 안 나올 수 있습니다.
- `.hwp` 변환은 `pyhwp`(`hwp5txt`)에 의존합니다. 복잡한 한글 문서는 표·도형이 단순 텍스트로 평탄화될 수 있습니다.

## 📄 라이선스

[MIT](LICENSE) — 자유롭게 수정·재배포 가능합니다.
