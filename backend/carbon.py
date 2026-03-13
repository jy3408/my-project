# =============================================================================
# 탄소 절감 효과 계산 로직
# =============================================================================
# NutriLens를 통해 식재료 폐기를 줄이면 얼마나 탄소 배출을 줄이는지 계산합니다.
#
# 계산 근거:
# - 출처: FAO (국제식량농업기구), WRAP (영국 식품폐기물 저감 기관)
# - 음식물 쓰레기는 전 세계 온실가스의 약 8~10%를 차지함
# - 식재료 1kg 폐기 시 카테고리별 CO2 환산 계수 (kg CO2e / kg 식재료):
#   · 육류/어류: 생산+운송+냉장 전 과정 합산
#   · 유제품: 낙농 과정 메탄 포함
#   · 채소/과일: 상대적으로 낮은 탄소 발자국
# =============================================================================

from models import Ingredient, CarbonSavingResult


# =============================================================================
# 식재료 카테고리별 탄소 배출 계수 (kg CO2e / kg 식재료)
# 출처: Our World in Data "Food's carbon footprint" (2023)
# =============================================================================
CARBON_FACTORS: dict[str, float] = {
    # 육류
    "소고기":  27.0, "한우": 27.0, "쇠고기": 27.0, "갈비": 27.0,
    "돼지고기": 12.1, "삼겹살": 12.1, "목살": 12.1, "돈육": 12.1,
    "닭고기":   6.9, "닭": 6.9, "치킨": 6.9,
    "양고기":  39.2,

    # 어패류
    "연어":    11.9,
    "새우":    11.8,
    "참치":     6.1,
    "고등어":   2.9,
    "오징어":   3.7,

    # 유제품
    "치즈":    21.2,
    "버터":    11.5,
    "우유":     3.2, "두유":  0.9,
    "요거트":   2.2,
    "계란":     4.5, "달걀": 4.5,

    # 채소 (기본값 낮음)
    "당근":  0.4, "감자": 0.5, "양파": 0.5, "마늘": 0.5,
    "토마토": 1.4, "시금치": 0.7, "브로콜리": 0.7, "파프리카": 1.1,
    "배추": 0.4, "무": 0.4, "오이": 0.7,

    # 과일
    "사과":  0.4, "바나나": 0.9, "딸기": 1.1, "포도": 1.4,
    "복숭아": 0.9, "오렌지": 0.4,

    # 곡물/두류
    "쌀":   2.7, "현미": 2.7, "밀가루": 1.4, "귀리": 1.6,
    "두부":  2.0, "콩":  1.8,

    # 가공식품
    "초콜릿": 18.7,
    "커피":   28.5,
}

# 카테고리 매칭이 안 될 때 사용하는 기본값 (채소 평균 기준)
DEFAULT_CARBON_FACTOR = 2.0  # kg CO2e / kg

# 수량 텍스트에서 무게(g)를 추정하지 못할 때 사용하는 기본 무게
DEFAULT_WEIGHT_G = 200  # g (1인분 기준)

# 탄소 절감량을 다른 단위로 환산하기 위한 계수
CO2_PER_KM_CAR = 0.12        # 자동차 1km 주행 시 CO2 배출량 (kg)
CO2_PER_TREE_PER_YEAR = 21.0  # 나무 1그루가 1년간 흡수하는 CO2 (kg)


def calculate_carbon_saving(
    saved_ingredients: list[Ingredient],
) -> "CarbonSavingResult":
    """
    낭비하지 않고 소비한 식재료의 탄소 절감량을 계산합니다.

    Args:
        saved_ingredients: 골든타임 내에 소비한 (= 폐기를 면한) 식재료 목록

    Returns:
        CarbonSavingResult: 총 절감량 + 이해하기 쉬운 비교 수치
    """
    from models import CarbonSavingResult, IngredientCarbonDetail

    ingredient_details = []
    total_co2_saved_kg = 0.0

    for ingredient in saved_ingredients:
        weight_kg = _estimate_weight_kg(ingredient.quantity)
        factor = _get_carbon_factor(ingredient.name)
        co2_saved = round(weight_kg * factor, 3)
        total_co2_saved_kg += co2_saved

        ingredient_details.append(
            IngredientCarbonDetail(
                ingredient_name=ingredient.name,
                weight_kg=weight_kg,
                carbon_factor=factor,
                co2_saved_kg=co2_saved,
            )
        )

    total_co2_saved_kg = round(total_co2_saved_kg, 3)

    # ──── 탄소 절감량을 친숙한 단위로 환산 ────────────────────────────────
    # 자동차 주행 거리 절약 환산
    car_km_equivalent = round(total_co2_saved_kg / CO2_PER_KM_CAR, 1)

    # 나무가 흡수하는 일수로 환산 (나무 1그루 기준)
    tree_days_equivalent = round(
        (total_co2_saved_kg / CO2_PER_TREE_PER_YEAR) * 365, 1
    )

    # 친숙한 메시지 생성
    impact_message = _build_impact_message(
        total_co2_saved_kg, car_km_equivalent, tree_days_equivalent
    )

    return CarbonSavingResult(
        total_co2_saved_kg=total_co2_saved_kg,
        car_km_equivalent=car_km_equivalent,
        tree_days_equivalent=tree_days_equivalent,
        ingredient_details=ingredient_details,
        impact_message=impact_message,
    )


def _get_carbon_factor(ingredient_name: str) -> float:
    """
    식재료명으로 탄소 배출 계수를 반환합니다. (부분 문자열 매칭)
    """
    name_lower = ingredient_name.lower()
    for keyword, factor in CARBON_FACTORS.items():
        if keyword in name_lower or name_lower in keyword:
            return factor
    return DEFAULT_CARBON_FACTOR


def _estimate_weight_kg(quantity: str | None) -> float:
    """
    수량 텍스트에서 무게(kg)를 추정합니다.
    - "500g" → 0.5
    - "1kg" / "1.5kg" → 그대로
    - "3개" / None → 기본값 200g
    """
    if not quantity:
        return DEFAULT_WEIGHT_G / 1000

    q = quantity.lower().replace(" ", "")

    # kg 단위
    if "kg" in q:
        try:
            return float(q.replace("kg", ""))
        except ValueError:
            pass

    # g 단위
    if "g" in q and "kg" not in q:
        try:
            return float(q.replace("g", "")) / 1000
        except ValueError:
            pass

    # ml / L 단위 (음료류 — 밀도 1 근사)
    if "ml" in q:
        try:
            return float(q.replace("ml", "")) / 1000
        except ValueError:
            pass
    if "l" in q and "ml" not in q:
        try:
            return float(q.replace("l", ""))
        except ValueError:
            pass

    # "3개", "2봉" 등 개수 단위 → 기본값 적용
    return DEFAULT_WEIGHT_G / 1000


def _build_impact_message(
    co2_kg: float, car_km: float, tree_days: float
) -> str:
    """
    절감량을 사람이 직관적으로 이해할 수 있는 메시지로 변환합니다.
    """
    if co2_kg < 0.01:
        return "오늘의 첫 절감! 계속 쌓아가면 큰 변화가 됩니다 🌱"

    parts = []

    if car_km >= 1:
        parts.append(f"자동차 {car_km}km 주행과 맞먹는 CO₂를 줄였어요 🚗")

    if tree_days >= 1:
        parts.append(f"나무 한 그루가 {tree_days}일간 흡수하는 양이에요 🌳")

    if not parts:
        return f"CO₂ {co2_kg * 1000:.0f}g 절감! 작은 실천이 지구를 바꿉니다 🌍"

    return " | ".join(parts)
