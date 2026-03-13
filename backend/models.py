# =============================================================================
# Pydantic 데이터 모델 정의
# - API 요청(Request)과 응답(Response)의 데이터 구조를 정의합니다.
# - Pydantic은 타입 힌트를 기반으로 자동 데이터 검증을 수행합니다.
# =============================================================================

from pydantic import BaseModel, Field
from typing import Optional
from datetime import date


# -----------------------------------------------------------------------------
# 사용자 건강 프로필
# - 회원가입 온보딩 단계에서 수집하는 정보
# -----------------------------------------------------------------------------
class UserHealthProfile(BaseModel):
    diseases: list[str] = Field(
        default=[],
        description="사용자 질환 목록. 예: ['당뇨', '고혈압']"
    )
    allergies: list[str] = Field(
        default=[],
        description="사용자 알레르기 목록 (알레르기 id 사용). 예: ['egg', 'milk']"
    )


# -----------------------------------------------------------------------------
# 식재료 정보
# - 냉장고 스캔 또는 수동 입력으로 등록되는 식재료 단위
# -----------------------------------------------------------------------------
class Ingredient(BaseModel):
    name: str = Field(description="식재료명. 예: '계란', '우유', '당근'")
    expiry_date: Optional[date] = Field(
        default=None,
        description="유통기한. None이면 유통기한 미입력 상태"
    )
    quantity: Optional[str] = Field(
        default=None,
        description="수량/용량. 예: '3개', '1L', '500g'"
    )


# -----------------------------------------------------------------------------
# 필터링된 식재료 단위 (차단된 경우)
# - 왜 차단되었는지 사유를 함께 제공합니다.
# -----------------------------------------------------------------------------
class BlockedIngredient(BaseModel):
    ingredient: Ingredient
    reason: str = Field(
        description="차단 사유. 예: '알레르기: 난류', '질환 제한: 당뇨'"
    )


# -----------------------------------------------------------------------------
# 필터링 결과
# - 안전한 식재료와 차단된 식재료로 분류된 결과
# -----------------------------------------------------------------------------
class FilteredResult(BaseModel):
    safe_ingredients: list[Ingredient] = Field(
        description="사용 가능한 식재료 목록"
    )
    blocked_ingredients: list[BlockedIngredient] = Field(
        description="사용 불가 식재료 목록 (차단 사유 포함)"
    )


# -----------------------------------------------------------------------------
# 골든타임 우선순위가 부여된 식재료
# - 유통기한 임박도에 따라 우선순위 점수(priority_score)가 추가됩니다.
# -----------------------------------------------------------------------------
class GoldenTimeIngredient(BaseModel):
    ingredient: Ingredient
    days_left: Optional[int] = Field(
        description="유통기한까지 남은 일수. None이면 유통기한 없음"
    )
    priority_score: int = Field(
        description=(
            "우선순위 점수 (0~100). 높을수록 먼저 소비해야 함. "
            "100: 유통기한 초과(경고), 90+: 골든타임(3일 이내), "
            "50+: 주의(7일 이내), 0: 여유 있음"
        )
    )
    status: str = Field(
        description="상태 레이블. 예: '골든타임', '주의', '여유', '기한초과', '기한미입력'"
    )


# -----------------------------------------------------------------------------
# 대체 식재료 옵션 (단일 대체재)
# -----------------------------------------------------------------------------
class SubstituteOption(BaseModel):
    name: str = Field(description="대체 식재료명. 예: '스테비아'")
    reason: str = Field(description="대체 이유. 예: '혈당 영향 없이 단맛을 냄'")
    health_benefit: str = Field(description="건강 이점. 예: '혈당 지수 0, 칼로리 제로'")


# -----------------------------------------------------------------------------
# 대체 식재료 추천 결과 (차단된 재료 1개에 대한 추천)
# -----------------------------------------------------------------------------
class SubstituteRecommendation(BaseModel):
    blocked_ingredient: BlockedIngredient = Field(
        description="차단된 원래 식재료 (차단 사유 포함)"
    )
    substitutes: list[SubstituteOption] = Field(
        description="추천 대체 식재료 목록 (최대 3개)"
    )
    has_substitute: bool = Field(
        description="대체재가 1개 이상 있으면 True, 없으면 False"
    )


# -----------------------------------------------------------------------------
# 식재료별 탄소 절감 상세
# -----------------------------------------------------------------------------
class IngredientCarbonDetail(BaseModel):
    ingredient_name: str = Field(description="식재료명")
    weight_kg: float = Field(description="추정 무게 (kg)")
    carbon_factor: float = Field(description="사용된 탄소 배출 계수 (kg CO2e/kg)")
    co2_saved_kg: float = Field(description="이 식재료로 절감한 CO2 (kg)")


# -----------------------------------------------------------------------------
# 탄소 절감 계산 결과
# -----------------------------------------------------------------------------
class CarbonSavingResult(BaseModel):
    total_co2_saved_kg: float = Field(
        description="총 CO2 절감량 (kg)"
    )
    car_km_equivalent: float = Field(
        description="자동차 주행 거리 환산 (km). '자동차 N km 주행 절약'"
    )
    tree_days_equivalent: float = Field(
        description="나무 흡수 일수 환산. '나무 1그루가 N일간 흡수하는 양'"
    )
    ingredient_details: list[IngredientCarbonDetail] = Field(
        description="식재료별 탄소 절감 상세 내역"
    )
    impact_message: str = Field(
        description="사용자에게 보여줄 친숙한 환경 임팩트 메시지"
    )


# -----------------------------------------------------------------------------
# 통합 레시피 추천 요청
# - 필터링 + 골든타임 계산 + 레시피 추천을 한 번에 요청
# -----------------------------------------------------------------------------
class RecipeRecommendationRequest(BaseModel):
    user_profile: UserHealthProfile = Field(
        description="사용자 건강 프로필 (질환 + 알레르기)"
    )
    ingredients: list[Ingredient] = Field(
        description="현재 보유 식재료 목록"
    )
    today: Optional[date] = Field(
        default=None,
        description="기준일. None이면 서버 오늘 날짜 사용 (테스트용으로 제공 가능)"
    )


# -----------------------------------------------------------------------------
# 통합 레시피 추천 응답
# -----------------------------------------------------------------------------
class RecipeRecommendationResponse(BaseModel):
    # 1단계: 필터링 결과
    filtered: FilteredResult = Field(
        description="질환/알레르기 기반 필터링 결과"
    )
    # 2단계: 골든타임 우선순위 결과 (안전한 재료 중에서만 계산)
    golden_time_ranked: list[GoldenTimeIngredient] = Field(
        description="유통기한 임박 순으로 정렬된 안전한 식재료 목록"
    )
    # 3단계: 차단된 재료에 대한 대체 식재료 추천
    substitute_recommendations: list[SubstituteRecommendation] = Field(
        default=[],
        description="차단된 재료별 건강한 대체 식재료 목록"
    )
    # 4단계: 탄소 절감 계산 결과
    carbon_saving: Optional[CarbonSavingResult] = Field(
        default=None,
        description="골든타임 재료 소비 시 탄소 절감 효과"
    )
    # 5단계: 추천 레시피 (MVP에서는 placeholder)
    recommended_recipes: list[dict] = Field(
        default=[],
        description="추천 레시피 목록 (추후 AI 연동 시 채워짐)"
    )
    message: str = Field(
        default="분석이 완료되었습니다.",
        description="사용자에게 표시할 안내 메시지"
    )
