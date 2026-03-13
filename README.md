# my-project

이 프로젝트는 기획자 주연의 연습용 프로젝트입니다.

---

## 🧠 Development Philosophy: Andrej Karpathy's Guidelines

저는 효율적인 AI 협업과 코드 실수를 방지하기 위해 **Andrej Karpathy**의 가이드라인을 엄격히 준수하며 개발했습니다.

1. **코딩 전 철저한 사고 (Think Before Coding):** 불명확한 추측을 배제하고 구현 전 가설을 명확히 함.
2. **단순함의 미학 (Simplicity First):** 오버 엔지니어링 없는 최소한의 핵심 코드 구현.
3. **정밀한 코드 수정 (Surgical Changes):** 필요한 부분만 정확히 수정하여 사이드 이펙트 방지.
4. **목표 중심 실행 (Goal-Driven Execution):** 검증 가능한 목표를 설정하고 반복 테스트.

---

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
