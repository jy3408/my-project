# =============================================================================
# 대체 식재료 추천 로직
# =============================================================================
# 금지된 식재료 대신 사용할 수 있는 건강한 대안을 제안합니다.
#
# 추천 기준:
# 1. 질환 제한으로 차단된 재료 → 같은 역할을 하는 건강 대체재 추천
# 2. 알레르기로 차단된 재료 → 알레르기 없는 동일 용도 재료 추천
# 3. 가능하면 추천 이유와 건강 이점도 함께 제공
# =============================================================================

from models import BlockedIngredient, SubstituteRecommendation


# =============================================================================
# 대체 식재료 마스터 데이터
# - key: 금지 재료에서 감지될 키워드 (소문자, 부분 매칭)
# - value: 대체 재료 목록 (이름, 이유, 건강 이점)
# =============================================================================
SUBSTITUTE_MAP: dict[str, list[dict]] = {

    # ── 당뇨 관련 ────────────────────────────────────────────────────────────
    "설탕": [
        {"name": "스테비아", "reason": "혈당 영향 없이 단맛을 냄", "benefit": "혈당 지수 0, 칼로리 제로"},
        {"name": "알룰로스", "reason": "설탕과 맛이 거의 같지만 혈당에 영향 없음", "benefit": "칼로리 90% 적음"},
    ],
    "꿀": [
        {"name": "스테비아", "reason": "혈당 영향 없이 단맛 대체", "benefit": "혈당 지수 0"},
        {"name": "아가베 시럽", "reason": "GI 지수가 꿀의 절반 수준", "benefit": "혈당 상승 완만"},
    ],
    "흰쌀": [
        {"name": "현미", "reason": "혈당 지수가 낮고 섬유질이 풍부", "benefit": "GI 55 (백미 GI 72 대비 낮음)"},
        {"name": "귀리", "reason": "베타글루칸으로 혈당 조절에 탁월", "benefit": "식이섬유 풍부, 포만감 오래 지속"},
        {"name": "곤약", "reason": "탄수화물이 거의 없어 혈당 영향 최소", "benefit": "칼로리 극히 낮음"},
    ],
    "백미": [
        {"name": "현미", "reason": "혈당 지수가 낮고 섬유질이 풍부", "benefit": "GI 55, 비타민 B군 풍부"},
        {"name": "귀리", "reason": "베타글루칸으로 혈당 조절", "benefit": "식이섬유 풍부"},
    ],
    "감자": [
        {"name": "고구마", "reason": "GI 지수가 감자보다 낮음", "benefit": "GI 55, 베타카로틴 풍부"},
        {"name": "콜리플라워", "reason": "탄수화물이 매우 적음", "benefit": "저탄수, 비타민 C 풍부"},
    ],
    "밀가루": [
        {"name": "아몬드 가루", "reason": "저탄수화물, 고단백 대안", "benefit": "GI 낮음, 비타민 E 풍부"},
        {"name": "코코넛 가루", "reason": "식이섬유 풍부, 저탄수화물", "benefit": "혈당 영향 최소"},
    ],

    # ── 고혈압 관련 ───────────────────────────────────────────────────────────
    "소금": [
        {"name": "저나트륨 소금", "reason": "나트륨을 칼륨으로 50% 대체", "benefit": "혈압 부담 감소"},
        {"name": "레몬즙", "reason": "짠맛 대신 산미로 풍미 강화", "benefit": "나트륨 0, 비타민 C 풍부"},
        {"name": "허브(로즈마리/바질)", "reason": "향으로 소금 필요량을 줄임", "benefit": "항산화 효과"},
    ],
    "간장": [
        {"name": "저염 간장", "reason": "나트륨 40% 줄인 저염 제품", "benefit": "혈압 부담 감소"},
        {"name": "코코넛 아미노스", "reason": "나트륨 65% 적은 대체 조미료", "benefit": "글루텐 프리, 저나트륨"},
    ],
    "된장": [
        {"name": "저염 된장", "reason": "나트륨 함량이 일반의 50% 수준", "benefit": "혈압 부담 감소"},
    ],
    "고추장": [
        {"name": "저염 고추장", "reason": "나트륨 함량을 줄인 제품", "benefit": "혈압 부담 감소"},
        {"name": "생고추+마늘", "reason": "나트륨 없이 매운맛과 향 살림", "benefit": "캡사이신 혈행 개선"},
    ],
    "베이컨": [
        {"name": "닭가슴살", "reason": "포화지방과 나트륨 모두 적음", "benefit": "고단백, 저지방"},
        {"name": "두부", "reason": "가공육 대신 식물성 단백질", "benefit": "나트륨 낮음, 이소플라본 풍부"},
    ],
    "햄": [
        {"name": "닭가슴살", "reason": "나트륨과 포화지방 모두 적음", "benefit": "고단백, 저나트륨"},
        {"name": "훈제 연어", "reason": "나트륨이 햄보다 낮고 오메가3 풍부", "benefit": "심혈관 건강"},
    ],

    # ── 고지혈증 관련 ─────────────────────────────────────────────────────────
    "버터": [
        {"name": "아보카도 오일", "reason": "불포화지방산으로 콜레스테롤 낮춤", "benefit": "올레산 풍부, 심혈관 보호"},
        {"name": "올리브오일", "reason": "지중해식 식단의 핵심 지방", "benefit": "LDL 콜레스테롤 감소"},
        {"name": "그릭 요거트", "reason": "크림 대신 쓸 때 포화지방 대폭 감소", "benefit": "단백질 풍부, 장 건강"},
    ],
    "삼겹살": [
        {"name": "닭가슴살", "reason": "포화지방이 삼겹살의 1/10 수준", "benefit": "고단백, 저지방"},
        {"name": "연어", "reason": "오메가3로 오히려 콜레스테롤 개선", "benefit": "HDL 콜레스테롤 증가"},
        {"name": "두부", "reason": "식물성 단백질로 동물성 지방 대체", "benefit": "이소플라본 LDL 감소 효과"},
    ],
    "계란노른자": [
        {"name": "계란흰자", "reason": "콜레스테롤 없는 순수 단백질", "benefit": "콜레스테롤 0"},
        {"name": "아마씨", "reason": "오메가3와 식이섬유 공급", "benefit": "LDL 감소"},
    ],
    "크림": [
        {"name": "두유", "reason": "포화지방 없는 식물성 크림 대안", "benefit": "콜레스테롤 0"},
        {"name": "귀리 음료", "reason": "베타글루칸이 콜레스테롤 흡수 억제", "benefit": "LDL 감소 효과"},
    ],

    # ── 알레르기 관련 ─────────────────────────────────────────────────────────
    "계란": [
        {"name": "아마씨 1큰술+물 3큰술", "reason": "계란 1개 대체 가능한 식물성 결합제", "benefit": "오메가3 풍부"},
        {"name": "치아씨드+물", "reason": "젤화 특성으로 계란 역할 대체", "benefit": "식이섬유, 칼슘 풍부"},
        {"name": "바나나 1/4개", "reason": "달걀 대신 수분과 결합력 제공", "benefit": "칼륨 풍부"},
    ],
    "달걀": [
        {"name": "아마씨 1큰술+물 3큰술", "reason": "계란 1개 대체 가능한 식물성 결합제", "benefit": "오메가3 풍부"},
        {"name": "두부", "reason": "스크램블드에그 대신 부드러운 질감", "benefit": "식물성 단백질"},
    ],
    "우유": [
        {"name": "귀리 음료(오트밀크)", "reason": "맛과 질감이 우유와 유사", "benefit": "베타글루칸, 칼슘 강화"},
        {"name": "두유", "reason": "단백질 함량이 식물성 음료 중 가장 높음", "benefit": "이소플라본, 저지방"},
        {"name": "아몬드 음료", "reason": "저칼로리 우유 대안", "benefit": "비타민 E 풍부"},
    ],
    "밀": [
        {"name": "쌀가루", "reason": "글루텐 프리 대안, 가장 범용적", "benefit": "소화 부담 적음"},
        {"name": "타피오카 전분", "reason": "쫄깃한 질감 유지", "benefit": "글루텐 프리"},
        {"name": "아몬드 가루", "reason": "저탄수화물 고단백 대안", "benefit": "GI 낮음, 비타민 E"},
    ],
    "땅콩": [
        {"name": "아몬드 버터", "reason": "맛과 용도가 땅콩버터와 유사", "benefit": "비타민 E, 마그네슘 풍부"},
        {"name": "해바라기씨 버터", "reason": "견과류 알레르기 없이 사용 가능", "benefit": "비타민 B6, 철분"},
    ],
    "새우": [
        {"name": "닭가슴살", "reason": "단백질 공급원으로 대체", "benefit": "고단백, 저지방"},
        {"name": "두부", "reason": "식물성 단백질로 대체", "benefit": "이소플라본, 칼슘"},
    ],
    "고등어": [
        {"name": "연어", "reason": "오메가3 지방산이 고등어만큼 풍부", "benefit": "심혈관 건강, EPA/DHA"},
        {"name": "정어리 통조림", "reason": "오메가3 공급 + 알레르기 없음", "benefit": "칼슘, 비타민 D"},
    ],
}


def get_substitutes(
    blocked_ingredients: list[BlockedIngredient],
) -> list["SubstituteRecommendation"]:
    """
    차단된 식재료 목록을 받아 각각의 대체 식재료를 추천합니다.

    Args:
        blocked_ingredients: 필터링에서 차단된 식재료 목록 (차단 사유 포함)

    Returns:
        SubstituteRecommendation 리스트 (차단된 재료 + 추천 대체재 목록)
    """
    from models import SubstituteRecommendation, SubstituteOption

    result = []

    for blocked in blocked_ingredients:
        ingredient_name = blocked.ingredient.name.lower()
        matched_substitutes = []

        # 대체 재료 매핑에서 부분 문자열 매칭으로 검색
        for keyword, options in SUBSTITUTE_MAP.items():
            if keyword in ingredient_name or ingredient_name in keyword:
                for opt in options:
                    # 중복 방지: 같은 이름의 대체재가 이미 추가된 경우 건너뜀
                    if not any(s.name == opt["name"] for s in matched_substitutes):
                        matched_substitutes.append(
                            SubstituteOption(
                                name=opt["name"],
                                reason=opt["reason"],
                                health_benefit=opt["benefit"],
                            )
                        )

        result.append(
            SubstituteRecommendation(
                blocked_ingredient=blocked,
                substitutes=matched_substitutes,
                has_substitute=len(matched_substitutes) > 0,
            )
        )

    return result
