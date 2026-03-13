# 0. 프로젝트 명칭
**뉴트리렌즈(NutriLens)** - 사용자의 건강 데이터를 기반으로 한 개인화 식단 솔루션

---

## 1. 문제 정의

현대인은 바쁜 일상 속에서 개인의 건강 상태(당뇨, 알레르기 등)를 고려하지 않은 무분별한 식료품 구매를 반복하고 있습니다. 이는 개인의 건강 악화로 이어질 뿐만 아니라, 활용되지 못한 채 버려지는 식재료로 인해 연간 수조 원에 달하는 음식물 쓰레기 발생 및 사회적 비용을 초래하는 페인 포인트(Pain Point)가 존재합니다.

---

## 2. 해결 방안

이를 해결하기 위해 뉴트리렌즈(NutriLens)는 AI Vision 기술을 활용하여 냉장고 속 식재료를 스캔하고, 사용자의 건강 데이터를 결합합니다.
내 냉장고 속 재료 사진을 찍으면, 내 건강 상태(당뇨, 다이어트 등)에 맞춰 오늘 저녁 레시피를 제안하고 부족한 재료만 장바구니에 담아주는 서비스를 제공하고자 합니다. 이를 통해 개인화된 맞춤형 레시피를 제안함으로써 건강한 식습관을 유도하고, 최적의 장바구니 큐레이션으로 불필요한 소비와 자원 낭비를 동시에 해결하고자 합니다.

- **Nutri(뉴트리):** 영양(Nutrition)을 뜻해. 우리 서비스의 핵심인 '건강 데이터'와 '식단'을 상징
- **Lens(렌즈):** 카메라 렌즈, 혹은 세상을 보는 눈. 서비스의 핵심 기술인 '냉장고 이미지 인식'을 상징

---

## 3. 개발 철학

아래의 Andrej Karpathy 가이드라인을 준수합니다.

### 🧠 Development Philosophy: Andrej Karpathy's Guidelines

저희 팀은 효율적인 AI 협업과 코드 실수를 방지하기 위해 **Andrej Karpathy**의 가이드라인을 엄격히 준수하며 개발했습니다.

1. **코딩 전 철저한 사고 (Think Before Coding):** 불명확한 추측을 배제하고 구현 전 가설을 명확히 함.
2. **단순함의 미학 (Simplicity First):** 오버 엔지니어링 없는 최소한의 핵심 코드 구현.
3. **정밀한 코드 수정 (Surgical Changes):** 필요한 부분만 정확히 수정하여 사이드 이펙트 방지.
4. **목표 중심 실행 (Goal-Driven Execution):** 검증 가능한 목표를 설정하고 반복 테스트.

### 📖 원문 가이드라인 (Behavioral Guidelines)

> **Reference:** Derived from Andrej Karpathy's observations on LLM coding pitfalls.

**1. Think Before Coding**
- State assumptions explicitly. If uncertain, ask.
- Present multiple interpretations instead of picking silently.

**2. Simplicity First**
- Minimum code that solves the problem. Nothing speculative.
- No abstractions for single-use code.

**3. Surgical Changes**
- Touch only what you must. Clean up only your own mess.
- Every changed line should trace directly to the user's request.

**4. Goal-Driven Execution**
- Transform tasks into verifiable goals.
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
