# 📒 money-log · 한 줄 AI 가계부

> 🔗 **Live Demo (모바일 PWA & 웹 앱):** [https://money-log.onrender.com](https://money-log.onrender.com)  
> *(무료 서버 슬립 모드 특성상 첫 접속 시 20~30초 정도 로딩이 걸릴 수 있습니다.)*

`"점심 김밥 3,500원"`, `"택시 1만5천원"`처럼 자연어 한 줄로 지출을 기록하면 **Gemini AI**가 카테고리를 자동 분류해 저장해 주는 개인 가계부입니다.  
**TDD(테스트 주도 개발)**로 검증된 단일 Python 코어 로직을 **터미널 CLI**와 **노션 문서형 FastAPI 웹 앱(PWA)**이 그대로 공유합니다.

## ✨ 주요 기능
- **자연어 금액 파싱:** `4500`, `4,500원`, `1만5천원`, `3만원` 등 한국어 금액 표기 인식
- **AI 자동 카테고리 분류:** Gemini API를 통해 `식비 / 카페 / 교통 / 쇼핑 / 기타` 자동 분류 (오프라인·API 오류 시 `기타`로 안전 폴백)
- **노션 스타일 3페이지 웹 UI (PWA):**
  - `✍️ 오늘의 기록`: 한 줄 입력, 원클릭 빠른 입력 칩, 이번 달 누적 지출 및 예산 요약
  - `🧾 지출 내역서`: 카테고리별 필터, 키워드 검색, 내역 삭제
  - `📊 월별 리포트`: 카테고리별 지출 비중 가로 막대 차트, 월 목표 예산 설정 및 초과 경고
  - **커스텀 테마 & 모바일 최적화:** 6종 밀크 파스텔 테마(연분홍·연노랑·연초록·연파랑·연보라·연모카), 라이트/다크 모드 전환, 스마트폰 홈 화면 앱 설치(PWA) 지원

## 🗂️ 프로젝트 구조
```text
money-log/
├── pyproject.toml           # 패키지 및 의존성 설정
├── README.md
├── GOAL.md                  # 핵심 요구사항 명세
├── data/                    # 실제 지출 CSV 저장소 (.gitignore 제외)
├── src/money_log/
│   ├── models.py            # Expense 데이터 모델
│   ├── parser.py            # 한 줄 입력 항목/금액 파싱
│   ├── classifier.py        # Gemini AI 카테고리 분류기
│   ├── storage.py           # CSV 읽기 / 쓰기 / 삭제
│   ├── report.py            # 월별 카테고리 합계 및 예산 비교
│   ├── cli.py               # 터미널 CLI 인터페이스
│   ├── web.py               # FastAPI REST API 및 정적 파일 서버
│   └── static/              # index.html, manifest.json, favicon.png
└── tests/                   # 89개 pytest 단위·통합 테스트
```

## 🚀 설치 및 실행 방법

### 1. 가상환경 설정 및 패키지 설치
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
```
*(선택)* AI 자동 분류를 사용하려면 `.env.example`을 복사해 `.env`를 만들고 `GEMINI_API_KEY`를 입력합니다.

### 2. 테스트 실행 (`89 passed`)
```powershell
pytest
```

### 3. 웹 앱 실행 (PC & 스마트폰 PWA)
```powershell
uvicorn money_log.web:app --host 0.0.0.0 --port 8000 --reload
```
- 브라우저에서 `http://127.0.0.1:8000` 접속
- 배포된 HTTPS 주소 접속 후 스마트폰 브라우저 메뉴에서 **"홈 화면에 추가 / 앱 설치"**로 모바일 앱처럼 사용 가능

### 4. 터미널 CLI 실행
```powershell
python -m money_log add "아이스 아메리카노 4,500원"
python -m money_log list
python -m money_log report 2026-11 --budget 300000
python -m money_log delete 1
```