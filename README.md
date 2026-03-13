# 🥬 NutriLens — 건강을 담은 스마트 냉장고

> **내 몸에 맞는 식재료만 골라, 가장 먼저 먹어야 할 것을 알려드려요.**

냉장고를 찍으면 — 내 질환·알레르기에 맞게 재료를 걸러주고, 오늘 버려질 위기의 재료를 살려 건강한 저녁을 차려드립니다.

---

## 목차

1. [서비스 소개](#1-서비스-소개)
2. [핵심 기능](#2-핵심-기능)
3. [환경적 효과](#3-환경적-효과)
4. [기술 스택](#4-기술-스택)
5. [프로젝트 구조](#5-프로젝트-구조)
6. [빠른 시작](#6-빠른-시작)
7. [API 명세](#7-api-명세)
8. [개발 철학](#8-개발-철학)

---

## 1. 서비스 소개

### 문제

현대인은 바쁜 일상 속에서 자신의 건강 상태(당뇨, 알레르기 등)를 고려하지 않은 채 식료품을 구매하고, 유통기한을 놓쳐 버리는 악순환을 반복합니다.

- **건강 위협**: 당뇨 환자가 설탕을, 알레르기 환자가 해당 식품을 무심코 섭취
- **식재료 낭비**: 국내 연간 음식물 쓰레기 약 **500만 톤**, 처리 비용 **1조 원** 이상
- **탄소 배출**: 음식물 낭비는 전 세계 온실가스 배출의 약 **8~10%** 차지

### 해결

| 문제 | NutriLens 해법 |
|------|---------------|
| 내 몸에 해로운 식재료를 모름 | 질환·알레르기 프로필 기반 **자동 필터링** |
| 대체 재료를 어떻게 써야 할지 모름 | 차단된 재료마다 **건강한 대체 식재료 즉시 추천** |
| 냉장고에 뭐가 있는지 파악하기 어려움 | 사진 한 장으로 **AI 식재료 자동 인식** |
| 유통기한 임박 재료를 그냥 버림 | **골든타임 알고리즘**으로 먼저 쓸 재료 순위화 |
| 내가 환경에 미치는 영향을 모름 | 폐기 방지 시 **CO₂ 절감량 실시간 계산** |

---

## 2. 핵심 기능

### 🔒 건강 프로필 기반 필터링

식약처 지정 **22종 알레르기 유발 물질** + **5개 만성 질환**(당뇨·고혈압·고지혈증·신장질환·통풍) 기준으로 위험 식재료를 자동 차단합니다.

```
예: 당뇨 + 새우 알레르기 사용자가 설탕·소금·새우 스캔
→ 설탕  ❌  질환 제한: 당뇨
→ 소금  ❌  질환 제한: 고혈압 (동시 질환)
→ 새우  ❌  알레르기: 새우
```

### 🔄 대체 식재료 추천

차단된 재료마다 **같은 역할을 하는 건강한 대안**을 즉시 제안합니다.

| 차단 재료 | 대체 추천 | 건강 이점 |
|-----------|----------|----------|
| 설탕 | 스테비아, 알룰로스 | 혈당 지수 0, 칼로리 제로 |
| 소금 | 저나트륨 소금, 레몬즙 | 혈압 부담 감소 |
| 버터 | 아보카도 오일, 올리브오일 | LDL 콜레스테롤 감소 |
| 우유 | 귀리 음료, 두유 | 알레르기 없음, 베타글루칸 |
| 달걀 | 아마씨+물, 치아씨드 | 오메가3 풍부 |
| 삼겹살 | 닭가슴살, 연어 | 포화지방 1/10 수준 |

### ⏱ 골든타임 알고리즘

유통기한까지 남은 일수를 **0~100점 우선순위 점수**로 변환해 오늘 먼저 써야 할 재료를 정확히 알려줍니다.

| 상태 | 조건 | 점수 범위 | 표시 색상 |
|------|------|----------|----------|
| 기한초과 | D+0 이상 | 100점 | 🔴 빨강 |
| 골든타임 | D-1 ~ D-3 | 90~96점 | 🟠 주황 |
| 주의 | D-4 ~ D-7 | 50~65점 | 🟡 노랑 |
| 여유 | D-8 이상 | 0~42점 | ⚪ 회색 |

### 🌍 탄소 절감 계산

FAO·WRAP 데이터 기반으로 **식재료별 탄소 배출 계수**를 적용해 오늘 낭비를 줄인 환경 임팩트를 수치로 보여줍니다.

```
소고기 300g 소비 → 8.1 kg CO₂ 절감 = 자동차 67.5km 주행 절약
```

---

## 3. 환경적 효과

NutriLens는 건강 앱인 동시에 **기후 행동 도구**입니다.

```
식재료 1kg 폐기 = 평균 2~27 kg CO₂ 배출
(육류 최대 27 kg · 채소 최소 0.4 kg)
```

앱이 계산하는 3가지 환경 지표:

| 지표 | 설명 |
|------|------|
| **CO₂ 절감량 (kg)** | 폐기 방지한 식재료의 탄소 발자국 총합 |
| **자동차 주행 절약 (km)** | CO₂ ÷ 0.12 kg/km 환산 |
| **나무 흡수 일수** | CO₂ ÷ (21 kg/년 ÷ 365일) 환산 |

> 출처: Our World in Data "Food's carbon footprint" (2023), FAO Food Wastage Footprint (2013)

---

## 4. 기술 스택

| 영역 | 기술 | 선택 이유 |
|------|------|----------|
| **백엔드** | FastAPI (Python) | Gemini AI 연동 최적화, 비동기 처리 |
| **데이터 검증** | Pydantic v2 | 자동 타입 검증, API 문서 자동 생성 |
| **데이터베이스** | Supabase (PostgreSQL) | 인증·DB·스토리지 통합, 무료 시작 |
| **프론트엔드** | React Native | iOS/Android 동시 지원, 카메라 네이티브 접근 |
| **AI** | Gemini 1.5 Pro | 냉장고 사진 멀티모달 분석 |
| **인프라** | Supabase | Row Level Security로 건강 데이터 보호 |

---

## 5. 프로젝트 구조

```
my-project/
├── backend/
│   ├── main.py           # FastAPI 진입점 · 7개 API 엔드포인트
│   ├── models.py         # Pydantic 데이터 모델
│   ├── filtering.py      # 질환/알레르기 필터링 로직
│   ├── golden_time.py    # 골든타임 우선순위 알고리즘
│   ├── substitutes.py    # 대체 식재료 추천 로직
│   ├── carbon.py         # 탄소 절감 계산 로직
│   ├── database.py       # Supabase 연결 설정
│   ├── requirements.txt  # Python 의존성
│   └── data/
│       └── allergens.py  # 식약처 22종 · 질환별 금지 식재료 마스터 데이터
├── frontend/
│   └── demo.html         # 앱 화면 인터랙티브 프로토타입 (브라우저에서 바로 실행)
├── docs/
│   └── screen_wireframes.md  # 7개 화면 텍스트 와이어프레임
└── PRD.md                # 상세 기획 문서
```

---

## 6. 빠른 시작

### 백엔드 실행

```bash
cd backend
pip install -r requirements.txt

# .env 파일 생성
echo "SUPABASE_URL=https://your-project.supabase.co" > .env
echo "SUPABASE_KEY=your-anon-key" >> .env

uvicorn main:app --reload
```

서버 실행 후:
- **API 문서**: http://localhost:8000/docs
- **헬스체크**: http://localhost:8000

### 프로토타입 확인

`frontend/demo.html` 파일을 브라우저에서 열면 앱 화면을 바로 확인할 수 있습니다.

---

## 7. API 명세

| Method | 경로 | 기능 |
|--------|------|------|
| `GET` | `/api/allergens` | 식약처 22종 알레르기 목록 조회 |
| `GET` | `/api/diseases` | 지원 질환 목록 조회 |
| `POST` | `/api/filter` | 식재료 필터링 (안전 / 차단 분류) |
| `POST` | `/api/golden-time` | 골든타임 우선순위 점수 계산 |
| `POST` | `/api/substitutes` | 차단 재료에 대한 대체 식재료 추천 |
| `POST` | `/api/carbon-saving` | 탄소 절감량 계산 |
| `POST` | `/api/recommend` | 통합: 필터링 + 골든타임 + 대체재 + 탄소 계산 |

### 통합 API 요청 예시

```json
POST /api/recommend
{
  "user_profile": {
    "diseases": ["당뇨", "고혈압"],
    "allergies": ["milk"]
  },
  "ingredients": [
    { "name": "설탕",   "expiry_date": "2026-03-20", "quantity": "200g" },
    { "name": "당근",   "expiry_date": "2026-03-14", "quantity": "300g" },
    { "name": "소고기", "expiry_date": "2026-03-13", "quantity": "500g" }
  ]
}
```

### 응답 구조

```json
{
  "filtered": {
    "safe_ingredients": [...],
    "blocked_ingredients": [
      { "ingredient": { "name": "설탕" }, "reason": "질환 제한: 당뇨" }
    ]
  },
  "golden_time_ranked": [
    { "ingredient": { "name": "당근" }, "days_left": 1, "priority_score": 93, "status": "골든타임" }
  ],
  "substitute_recommendations": [
    {
      "blocked_ingredient": { "ingredient": { "name": "설탕" }, "reason": "질환 제한: 당뇨" },
      "substitutes": [
        { "name": "스테비아", "reason": "혈당 영향 없이 단맛을 냄", "health_benefit": "혈당 지수 0, 칼로리 제로" }
      ],
      "has_substitute": true
    }
  ],
  "carbon_saving": {
    "total_co2_saved_kg": 13.77,
    "car_km_equivalent": 114.8,
    "tree_days_equivalent": 239.2,
    "impact_message": "자동차 114.8km 주행 절약과 같아요 🚗 | 나무 1그루가 239.2일간 흡수하는 양 🌳"
  }
}
```

---

## 8. 개발 철학

**Andrej Karpathy의 'Simplicity First'** 가이드라인을 준수합니다.

| 원칙 | 실천 내용 |
|------|----------|
| **Think Before Coding** | 기능 구현 전 기획자와 의도 정렬, 불확실하면 질문 |
| **Simplicity First** | 오버 엔지니어링 금지 · 최소한의 핵심 코드만 작성 |
| **Surgical Changes** | 필요한 부분만 정확히 수정 · 사이드 이펙트 방지 |
| **Goal-Driven Execution** | "버그 고쳐줘" → "재현 테스트 작성 후 통과시키기" |

---

더 자세한 기획 내용은 **[PRD 바로가기](./PRD.md)** · **[화면 와이어프레임](./docs/screen_wireframes.md)** 에서 확인하실 수 있습니다.
