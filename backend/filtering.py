# =============================================================================
# 질환 / 알레르기 기반 식재료 필터링 로직
# =============================================================================
# 핵심 규칙:
# 1. 사용자의 알레르기 정보 → 22종 알레르기 마스터에서 관련 키워드 추출
# 2. 사용자의 질환 정보 → 질환별 금지 식재료 키워드 추출
# 3. 두 목록을 합쳐 "금지 키워드 집합" 생성
# 4. 각 식재료명에 금지 키워드가 포함되어 있으면 → 차단(blocked)
# 5. 포함되지 않으면 → 안전(safe)
# =============================================================================

from models import Ingredient, FilteredResult, BlockedIngredient, UserHealthProfile
from data.allergens import ALLERGENS_22, DISEASE_RESTRICTIONS


def filter_ingredients(
    user_profile: UserHealthProfile,
    ingredients: list[Ingredient],
    external_restrictions: list[str] | None = None
) -> FilteredResult:
    """
    사용자 건강 프로필을 기반으로 식재료를 안전/차단으로 분류합니다.

    Args:
        user_profile: 사용자의 질환 목록과 알레르기 목록
        ingredients: 필터링할 식재료 목록
        external_restrictions: 공공데이터 API 등 외부에서 추가로 받은 금지 키워드
                                (None이면 내부 데이터만 사용)

    Returns:
        FilteredResult: safe_ingredients(안전) + blocked_ingredients(차단+사유)
    """

    # -------------------------------------------------------------------------
    # Step 1: 알레르기 기반 금지 키워드 수집
    # - 사용자가 선택한 알레르기 id를 22종 마스터에서 찾아 키워드를 모읍니다.
    # - 예: 사용자가 "egg" 선택 → ["계란", "달걀", "난류", "메추리알", "오리알"]
    # -------------------------------------------------------------------------
    allergy_keywords: dict[str, str] = {}
    # {키워드: "알레르기: 난류"} 형태로 저장하여 차단 사유를 추적합니다.

    allergen_map = {a["id"]: a for a in ALLERGENS_22}

    for allergy_id in user_profile.allergies:
        allergen = allergen_map.get(allergy_id)
        if allergen:
            for keyword in allergen["keywords"]:
                reason = f"알레르기: {allergen['name']}"
                # 이미 다른 알레르기로 등록된 키워드가 있으면 사유를 이어 붙입니다.
                if keyword in allergy_keywords:
                    allergy_keywords[keyword] += f", {allergen['name']}"
                else:
                    allergy_keywords[keyword] = reason

    # -------------------------------------------------------------------------
    # Step 2: 질환 기반 금지 키워드 수집
    # - 사용자가 선택한 질환에 해당하는 금지 식재료 키워드를 모읍니다.
    # - 예: "당뇨" 선택 → ["흰쌀", "백미", "설탕", ...]
    # -------------------------------------------------------------------------
    disease_keywords: dict[str, str] = {}

    for disease_name in user_profile.diseases:
        disease_info = DISEASE_RESTRICTIONS.get(disease_name)
        if disease_info:
            for keyword in disease_info["forbidden_keywords"]:
                reason = f"질환 제한: {disease_info['display_name']}"
                if keyword in disease_keywords:
                    disease_keywords[keyword] += f", {disease_info['display_name']}"
                else:
                    disease_keywords[keyword] = reason

    # -------------------------------------------------------------------------
    # Step 3: 외부 데이터 금지 키워드 병합 (공공데이터 API 연동 시 사용)
    # - external_restrictions는 단순 키워드 리스트로 받습니다.
    # - 사유는 "외부 데이터 제한"으로 표시됩니다.
    # -------------------------------------------------------------------------
    external_keyword_map: dict[str, str] = {}
    if external_restrictions:
        for keyword in external_restrictions:
            external_keyword_map[keyword] = "외부 데이터 제한"

    # -------------------------------------------------------------------------
    # Step 4: 전체 금지 키워드 통합
    # - 알레르기 + 질환 + 외부 데이터를 하나의 딕셔너리로 합칩니다.
    # -------------------------------------------------------------------------
    all_forbidden: dict[str, str] = {
        **external_keyword_map,
        **disease_keywords,
        **allergy_keywords,  # 알레르기가 가장 높은 우선순위 (사유 덮어씌움)
    }

    # -------------------------------------------------------------------------
    # Step 5: 각 식재료를 금지 키워드와 대조하여 분류
    # - 부분 문자열 매칭: "계란후라이"에 "계란"이 포함되면 차단
    # - 대소문자 구분 없이 비교 (한글이 주이므로 실질적 영향 적음)
    # -------------------------------------------------------------------------
    safe_ingredients: list[Ingredient] = []
    blocked_ingredients: list[BlockedIngredient] = []

    for ingredient in ingredients:
        ingredient_name = ingredient.name
        blocked_reason = _find_blocking_reason(ingredient_name, all_forbidden)

        if blocked_reason:
            blocked_ingredients.append(
                BlockedIngredient(
                    ingredient=ingredient,
                    reason=blocked_reason
                )
            )
        else:
            safe_ingredients.append(ingredient)

    return FilteredResult(
        safe_ingredients=safe_ingredients,
        blocked_ingredients=blocked_ingredients
    )


def _find_blocking_reason(ingredient_name: str, forbidden_map: dict[str, str]) -> str | None:
    """
    식재료명이 금지 키워드 목록에 해당하는지 확인합니다.

    Args:
        ingredient_name: 검사할 식재료명
        forbidden_map: {금지키워드: 차단사유} 딕셔너리

    Returns:
        차단 사유 문자열 (차단 대상이면), None (안전하면)
    """
    ingredient_lower = ingredient_name.lower()

    for keyword, reason in forbidden_map.items():
        keyword_lower = keyword.lower()
        # 부분 문자열 매칭: 식재료명에 금지 키워드가 포함되어 있으면 차단
        if keyword_lower in ingredient_lower or ingredient_lower in keyword_lower:
            return reason

    return None
