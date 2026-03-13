# CLAUDE.md — NutriLens 프로젝트 협업 가이드

> 이 파일은 Claude가 이 프로젝트에서 수석 개발자 역할을 수행하기 위한 지침서입니다.
> 기획자: Chloe (주연) | 갱신일: 2026-03-13

---

## 1. 역할 정의

**Claude의 역할:** 수석 개발자 (Senior AI Developer)
**Chloe의 역할:** 프로덕트 오너 + 기획자

**핵심 원칙:** Andrej Karpathy의 "Simplicity First" — 동작하는 최소한의 코드가 복잡한 완벽한 코드보다 낫다.

**소통 원칙:**
- 모든 응답은 **한국어**로 작성한다 (코드 주석 포함)
- 불확실한 기획 의도는 독단적으로 결정하지 말고 반드시 Chloe에게 질문한다
- 작업 완료 후 반드시 **git push까지 한 번에** 처리한다

---

## 2. 코딩 스타일

```
오버 엔지니어링 금지     → 최소한의 코드로 해결
Surgical Changes        → 필요한 부분만 정밀하게 수정, 주변 코드 건드리지 않기
Think Before Coding     → 모든 기능 구현 전 설계 단계를 거칠 것
한글 주석               → 기획자가 코드를 직접 읽을 수 있도록
```

**금지 패턴:**
- 요청하지 않은 리팩터링, 에러 핸들링 추가, 문서화 추가
- 가상의 미래 요구사항을 위한 추상화 레이어
- 기존 동작 코드를 "더 낫다"는 이유로 임의 변경

---

## 3. 프로젝트 기술 스택

### 백엔드
| 기술 | 버전 | 역할 |
|------|------|------|
| FastAPI | 0.115.0 | API 서버 |
| Pydantic | v2.9.2 | 데이터 유효성 검사 (v1 문법 사용 금지) |
| Supabase | 2.7.4 | PostgreSQL DB + Auth + Storage |
| python-dotenv | 1.0.1 | 환경변수 관리 |
| uvicorn | 0.30.6 | ASGI 서버 |

### 프론트엔드 (현재)
| 기술 | 설명 |
|------|------|
| 단일 HTML 파일 | `frontend/demo.html` — 외부 CDN 없음, 모든 CSS/JS 인라인 |
| 모바일 앱 레이아웃 | 390px 고정폭, 고정 상단바 + 고정 하단 네비 |
| 화면 전환 방식 | `position:absolute` + `opacity` 토글 (transition 없음 = 즉시 전환) |

### 프론트엔드 (목표)
- React Native (네이티브 모듈 + WebView 하이브리드)

### AI
- Gemini 1.5 Pro (이미지 분석 + 레시피 생성) — **현재 미연동, MVP에서 시뮬레이션으로 대체**

---

## 4. 폴더 구조

```
my-project/
├── backend/
│   ├── main.py              # FastAPI 앱 진입점 + 7개 API 엔드포인트
│   ├── models.py            # Pydantic 데이터 모델
│   ├── filtering.py         # 질환/알레르기 필터링 핵심 로직
│   ├── golden_time.py       # 골든타임 우선순위 알고리즘
│   ├── substitutes.py       # 대체 식재료 추천 매핑
│   ├── carbon.py            # 탄소 절감량 계산 (FAO 기준)
│   ├── database.py          # Supabase 클라이언트 초기화
│   ├── data/
│   │   ├── __init__.py      # 패키지 인식용 (비어 있어도 필수)
│   │   └── allergens.py     # 22종 알레르기 + 질환별 금지 식재료 마스터 데이터
│   └── requirements.txt
├── frontend/
│   └── demo.html            # 모바일 앱 스타일 인터랙티브 프로토타입
├── docs/
│   └── screen_wireframes.md # UI/UX 설계안 (디자인 시스템 + 인터랙션 가이드)
├── CLAUDE.md                # 이 파일 — 협업 가이드
├── DEVELOPMENT_LOG.md       # 세션별 개발 기록
├── PRD.md                   # 상세 기획 문서
├── README.md                # GitHub 대문 (기능 요약 + 로드맵)
└── .gitignore
```

---

## 5. API 엔드포인트 현황

| Method | Path | 설명 | 상태 |
|--------|------|------|------|
| GET | `/` | 헬스체크 | ✅ |
| GET | `/api/allergens` | 22종 알레르기 마스터 데이터 | ✅ |
| GET | `/api/diseases` | 지원 질환 목록 | ✅ |
| POST | `/api/filter` | 식재료 필터링 (단독) | ✅ |
| POST | `/api/golden-time` | 골든타임 우선순위 계산 (단독) | ✅ |
| POST | `/api/substitutes` | 대체 재료 추천 | ✅ |
| POST | `/api/carbon-saving` | 탄소 절감량 계산 | ✅ |
| POST | `/api/recommend` | 통합 엔드포인트 (필터+골든타임+대체재+탄소) | ✅ |

---

## 6. DB 스키마 (Supabase)

```sql
-- 사용자
users (id uuid, email text, created_at timestamptz)

-- 건강 프로필 (암호화 필수: AES-256 이상)
health_profiles (
  id uuid,
  user_id uuid → users.id,
  diseases text[],    -- 예: ["당뇨", "고혈압"]
  allergies text[],   -- 예: ["난류", "우유"]
  created_at timestamptz,
  updated_at timestamptz
)

-- 식재료
ingredients (
  id uuid,
  user_id uuid → users.id,
  name text,
  expiry_date date nullable,
  quantity text nullable,   -- 예: "달걀 6개", "우유 500mL"
  created_at timestamptz
)
```

---

## 7. 핵심 비즈니스 로직

### 골든타임 점수 공식
```python
# 0~100점, 높을수록 우선순위 높음
expired (days_left ≤ 0)  → 100점
3일 이내                 → 90 + (3 - days_left) × 3
7일 이내                 → 50 + (7 - days_left) × 5
그 외                    → max(0, 50 - days_left)
유통기한 없음            → 0점
```

### 필터링 방식
- 부분 문자열 매칭 — `"설탕" in ingredient.name`
- `ALLERGENS_22[id].keywords` 배열과 `DISEASE_RESTRICTIONS[disease].forbidden_keywords` 합집합으로 금지 키워드 세트 구성

### 탄소 계산
- FAO/Our World in Data 기준 식품 카테고리별 kg CO₂e/kg 계수
- 수량 파서: "300g" → 0.3kg, "1L" → 1.0kg, "3개" → 평균 중량 추정

---

## 8. 개발 환경 설정

```bash
# 백엔드 실행
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
# → http://localhost:8000/docs (Swagger UI)

# 환경변수 (.env 파일 필요)
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=your-anon-key
```

---

## 9. 협업 규칙

### 작업 완료 시 필수 체크리스트
- [ ] 코드 주석 한글 작성 여부
- [ ] `git add` → `git commit` → `git push origin main` 완료
- [ ] 변경사항을 Chloe에게 한국어로 요약 보고

### 새 기능 추가 시 순서
1. PRD 또는 Chloe 지시 확인 → 불명확하면 질문
2. 영향 범위 파악 (어떤 파일이 바뀌는지)
3. 최소 변경으로 구현
4. 테스트 (로컬 서버 실행 또는 데모 확인)
5. push + 보고

### 절대 하지 말 것
- 요청 없이 파일 삭제
- `git push --force`
- `.env` 파일 커밋
- Chloe가 승인하지 않은 구조 변경
