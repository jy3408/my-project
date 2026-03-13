# =============================================================================
# 골든타임 우선순위 알고리즘
# =============================================================================
# "골든타임"이란 식재료가 버려지기 직전, 가장 먼저 소비해야 하는 시점을 의미합니다.
# 유통기한 임박도에 따라 0~100 사이의 우선순위 점수를 계산합니다.
#
# 점수 계산 규칙:
# - 유통기한 없음:         score = 0       → 상태: "기한미입력"
# - 이미 지남 (≤ 0일):    score = 100     → 상태: "기한초과" (경고)
# - 3일 이내 (골든타임):  score = 90 + (3 - days_left) * 3  → 상태: "골든타임"
# - 7일 이내 (주의):       score = 50 + (7 - days_left) * 5  → 상태: "주의"
# - 그 외 (여유):          score = max(0, 50 - days_left)     → 상태: "여유"
# =============================================================================

from datetime import date
from models import Ingredient, GoldenTimeIngredient


def calculate_golden_time(
    ingredients: list[Ingredient],
    today: date | None = None
) -> list[GoldenTimeIngredient]:
    """
    식재료 목록에 골든타임 우선순위 점수를 부여하고 내림차순으로 정렬합니다.

    Args:
        ingredients: 우선순위를 계산할 식재료 목록
        today: 기준일 (None이면 오늘 날짜 자동 사용, 테스트 시 특정 날짜 지정 가능)

    Returns:
        GoldenTimeIngredient 리스트 (우선순위 높은 순으로 정렬됨)
    """
    if today is None:
        today = date.today()

    result: list[GoldenTimeIngredient] = []

    for ingredient in ingredients:
        days_left, score, status = _calculate_score(ingredient, today)
        result.append(
            GoldenTimeIngredient(
                ingredient=ingredient,
                days_left=days_left,
                priority_score=score,
                status=status
            )
        )

    # 우선순위 점수 기준 내림차순 정렬 (점수가 같으면 식재료명 가나다 순)
    result.sort(key=lambda x: (-x.priority_score, x.ingredient.name))

    return result


def _calculate_score(ingredient: Ingredient, today: date) -> tuple[int | None, int, str]:
    """
    단일 식재료의 골든타임 점수를 계산합니다.

    Args:
        ingredient: 점수를 계산할 식재료
        today: 기준일

    Returns:
        (days_left, priority_score, status) 튜플
        - days_left: 남은 일수 (유통기한 없으면 None)
        - priority_score: 0~100 우선순위 점수
        - status: 상태 레이블 문자열
    """

    # -------------------------------------------------------------------------
    # Case 1: 유통기한 미입력
    # - 스캔 시 유통기한을 인식하지 못했거나 사용자가 입력하지 않은 경우
    # -------------------------------------------------------------------------
    if ingredient.expiry_date is None:
        return None, 0, "기한미입력"

    # 남은 일수 계산 (양수: 아직 유효, 0 또는 음수: 만료)
    days_left = (ingredient.expiry_date - today).days

    # -------------------------------------------------------------------------
    # Case 2: 이미 유통기한이 지난 경우
    # - 최고 점수 100점 부여 → 즉각 처리 필요 경고
    # -------------------------------------------------------------------------
    if days_left <= 0:
        return days_left, 100, "기한초과"

    # -------------------------------------------------------------------------
    # Case 3: 골든타임 (3일 이내)
    # - 1일 남음: 90 + (3-1)*3 = 96
    # - 2일 남음: 90 + (3-2)*3 = 93
    # - 3일 남음: 90 + (3-3)*3 = 90
    # -------------------------------------------------------------------------
    if days_left <= 3:
        score = 90 + (3 - days_left) * 3
        return days_left, score, "골든타임"

    # -------------------------------------------------------------------------
    # Case 4: 주의 구간 (7일 이내)
    # - 4일 남음: 50 + (7-4)*5 = 65
    # - 5일 남음: 50 + (7-5)*5 = 60
    # - 7일 남음: 50 + (7-7)*5 = 50
    # -------------------------------------------------------------------------
    if days_left <= 7:
        score = 50 + (7 - days_left) * 5
        return days_left, score, "주의"

    # -------------------------------------------------------------------------
    # Case 5: 여유 구간 (8일 이상)
    # - 8일 남음: max(0, 50-8) = 42
    # - 50일 남음: max(0, 50-50) = 0
    # - 51일 이상: 0점 (완전 여유)
    # -------------------------------------------------------------------------
    score = max(0, 50 - days_left)
    return days_left, score, "여유"
