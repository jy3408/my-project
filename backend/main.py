# =============================================================================
# NutriLens FastAPI 백엔드 진입점
# =============================================================================
# FastAPI는 Python 기반의 고성능 웹 프레임워크입니다.
# 이 파일은 서버의 시작점이며, 모든 API 엔드포인트가 정의됩니다.
#
# 서버 실행 방법:
#   cd backend
#   pip install -r requirements.txt
#   uvicorn main:app --reload
#
# API 문서 자동 생성:
#   http://localhost:8000/docs  (Swagger UI)
#   http://localhost:8000/redoc (ReDoc)
# =============================================================================

from datetime import date
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from data.allergens import ALLERGENS_22, DISEASE_LIST
from filtering import filter_ingredients
from golden_time import calculate_golden_time
from substitutes import get_substitutes
from carbon import calculate_carbon_saving
from models import (
    Ingredient,
    UserHealthProfile,
    FilteredResult,
    RecipeRecommendationRequest,
    RecipeRecommendationResponse,
    CarbonSavingResult,
)

# .env 파일에서 환경변수 로드 (SUPABASE_URL, SUPABASE_KEY 등)
load_dotenv()

# =============================================================================
# FastAPI 앱 초기화
# =============================================================================
app = FastAPI(
    title="NutriLens API",
    description="건강 맞춤형 냉장고 관리 및 레시피 추천 서비스 백엔드",
    version="0.2.0",
)

# =============================================================================
# CORS 설정
# - 프론트엔드(React Native 앱 또는 웹)에서 API 호출을 허용하기 위한 설정
# - 개발 환경에서는 모든 출처를 허용 (운영 환경에서는 도메인 제한 필요)
# =============================================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # 운영 환경: ["https://your-domain.com"] 으로 변경
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# 헬스체크 엔드포인트
# =============================================================================
@app.get("/", tags=["시스템"])
def root():
    """서버 상태 확인용 엔드포인트"""
    return {"status": "ok", "message": "NutriLens API가 정상 실행 중입니다."}


# =============================================================================
# GET /api/allergens
# - 식약처 지정 22종 알레르기 마스터 데이터 반환
# - 사용자 알레르기 선택 화면(온보딩 Step 2)에서 사용
# =============================================================================
@app.get("/api/allergens", tags=["마스터 데이터"])
def get_allergens():
    """식약처 지정 22종 알레르기 유발 물질 목록을 반환합니다."""
    return {"allergens": ALLERGENS_22, "total": len(ALLERGENS_22)}


# =============================================================================
# GET /api/diseases
# - 지원하는 질환 목록 반환
# - 사용자 질환 선택 화면(온보딩 Step 1)에서 사용
# =============================================================================
@app.get("/api/diseases", tags=["마스터 데이터"])
def get_diseases():
    """NutriLens가 지원하는 질환 목록을 반환합니다."""
    return {"diseases": DISEASE_LIST, "total": len(DISEASE_LIST)}


# =============================================================================
# POST /api/filter
# - 식재료 필터링 단독 실행
# =============================================================================
@app.post("/api/filter", response_model=FilteredResult, tags=["핵심 기능"])
def filter_ingredients_api(
    user_profile: UserHealthProfile,
    ingredients: list[Ingredient]
):
    """사용자 건강 프로필을 기반으로 식재료를 안전/차단으로 분류합니다."""
    if not ingredients:
        raise HTTPException(status_code=400, detail="식재료 목록이 비어 있습니다.")
    return filter_ingredients(user_profile, ingredients)


# =============================================================================
# POST /api/golden-time
# - 골든타임 우선순위 계산 단독 실행
# =============================================================================
@app.post("/api/golden-time", tags=["핵심 기능"])
def golden_time_api(
    ingredients: list[Ingredient],
    today: date | None = None
):
    """식재료 목록에 골든타임 우선순위 점수를 부여하고 정렬하여 반환합니다."""
    if not ingredients:
        raise HTTPException(status_code=400, detail="식재료 목록이 비어 있습니다.")
    return calculate_golden_time(ingredients, today)


# =============================================================================
# POST /api/substitutes
# - 차단된 식재료에 대한 대체 식재료 추천
# - 스캔 결과 화면에서 "대체 재료 보기" 버튼 클릭 시 호출
# =============================================================================
@app.post("/api/substitutes", tags=["핵심 기능"])
def substitutes_api(blocked_ingredients: list[dict]):
    """
    차단된 식재료 목록을 받아 건강한 대체 식재료를 추천합니다.

    요청 예시:
    [
        {
            "ingredient": {"name": "설탕", "expiry_date": null},
            "reason": "질환 제한: 당뇨"
        }
    ]

    응답 예시:
    [
        {
            "blocked_ingredient": {...},
            "substitutes": [
                {"name": "스테비아", "reason": "혈당 영향 없이 단맛을 냄", "health_benefit": "혈당 지수 0"}
            ],
            "has_substitute": true
        }
    ]
    """
    from models import BlockedIngredient, Ingredient as IngModel

    parsed = []
    for item in blocked_ingredients:
        ing_data = item.get("ingredient", {})
        ing = IngModel(
            name=ing_data.get("name", ""),
            expiry_date=ing_data.get("expiry_date"),
            quantity=ing_data.get("quantity"),
        )
        parsed.append(BlockedIngredient(ingredient=ing, reason=item.get("reason", "")))

    return get_substitutes(parsed)


# =============================================================================
# POST /api/carbon-saving
# - 식재료 폐기를 줄였을 때의 탄소 절감 효과 계산
# - 레시피 추천 화면 하단 "환경 임팩트" 섹션에서 사용
# =============================================================================
@app.post("/api/carbon-saving", response_model=CarbonSavingResult, tags=["환경 임팩트"])
def carbon_saving_api(ingredients: list[Ingredient]):
    """
    소비(폐기 방지)한 식재료 목록을 받아 탄소 절감량을 계산합니다.

    요청 예시:
    [
        {"name": "소고기", "quantity": "300g"},
        {"name": "우유", "quantity": "1L"},
        {"name": "당근", "quantity": "200g"}
    ]
    """
    if not ingredients:
        raise HTTPException(status_code=400, detail="식재료 목록이 비어 있습니다.")
    return calculate_carbon_saving(ingredients)


# =============================================================================
# POST /api/recommend
# - 통합 엔드포인트: 필터링 + 골든타임 + 대체재 추천 + 탄소 계산 + 레시피
# - 메인 화면의 "스캔 결과" 및 "레시피 추천" 화면에서 사용
# =============================================================================
@app.post("/api/recommend", response_model=RecipeRecommendationResponse, tags=["핵심 기능"])
def recommend_api(request: RecipeRecommendationRequest):
    """
    식재료를 스캔한 후 전체 분석 결과를 한 번에 반환합니다.

    처리 순서:
    1. 질환/알레르기 기반 필터링
    2. 안전한 식재료에 대해서만 골든타임 점수 계산
    3. 차단된 식재료에 대한 대체 식재료 추천
    4. 골든타임 재료 소비 시 탄소 절감량 계산
    5. 레시피 추천 (MVP: placeholder, 추후 AI 연동)
    """
    if not request.ingredients:
        raise HTTPException(status_code=400, detail="식재료 목록이 비어 있습니다.")

    # Step 1: 질환/알레르기 필터링
    filtered = filter_ingredients(request.user_profile, request.ingredients)

    # Step 2: 안전한 식재료에 대해서만 골든타임 계산
    golden_time_ranked = calculate_golden_time(
        filtered.safe_ingredients,
        request.today
    )

    # Step 3: 차단된 재료에 대한 대체 식재료 추천
    substitute_recommendations = get_substitutes(filtered.blocked_ingredients)

    # Step 4: 골든타임 임박 재료(주의 이상)를 소비했을 때 탄소 절감 계산
    # - 점수 50점 이상(주의~기한초과) 재료만 대상으로 계산
    at_risk_ingredients = [
        gt.ingredient for gt in golden_time_ranked
        if gt.priority_score >= 50
    ]
    carbon_saving = calculate_carbon_saving(at_risk_ingredients) if at_risk_ingredients else None

    # Step 5: 레시피 추천 (MVP에서는 빈 배열, 추후 Gemini AI 연동)
    recommended_recipes = []

    # 사용자 안내 메시지 생성
    if filtered.blocked_ingredients:
        blocked_names = [b.ingredient.name for b in filtered.blocked_ingredients]
        message = (
            f"분석 완료. {', '.join(blocked_names)} 은(는) "
            f"건강 프로필에 따라 제외되었고, 대체 식재료를 추천했습니다."
        )
    else:
        message = "분석이 완료되었습니다. 모든 식재료가 안전합니다."

    return RecipeRecommendationResponse(
        filtered=filtered,
        golden_time_ranked=golden_time_ranked,
        substitute_recommendations=substitute_recommendations,
        carbon_saving=carbon_saving,
        recommended_recipes=recommended_recipes,
        message=message,
    )
