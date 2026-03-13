# =============================================================================
# Supabase 데이터베이스 연결 설정
# =============================================================================
# Supabase는 PostgreSQL 기반의 오픈소스 Firebase 대안입니다.
# 인증, 실시간 DB, 스토리지를 모두 제공하며 NutriLens의 주요 데이터를 저장합니다.
#
# 사용하는 테이블 구조:
# ┌─────────────────────────────────────────────────────────────────┐
# │ users                                                           │
# │  - id (uuid, PK)                                               │
# │  - email (text, unique)                                        │
# │  - created_at (timestamptz)                                    │
# ├─────────────────────────────────────────────────────────────────┤
# │ health_profiles                                                 │
# │  - id (uuid, PK)                                               │
# │  - user_id (uuid, FK → users.id)                               │
# │  - diseases (text[], 예: ["당뇨", "고혈압"])                    │
# │  - allergies (text[], 예: ["egg", "milk"])                     │
# │  - updated_at (timestamptz)                                    │
# ├─────────────────────────────────────────────────────────────────┤
# │ ingredients                                                     │
# │  - id (uuid, PK)                                               │
# │  - user_id (uuid, FK → users.id)                               │
# │  - name (text, 식재료명)                                       │
# │  - expiry_date (date, nullable)                                │
# │  - quantity (text, nullable, 예: "3개", "500g")                │
# │  - created_at (timestamptz)                                    │
# └─────────────────────────────────────────────────────────────────┘
# =============================================================================

import os
from supabase import create_client, Client


def get_supabase_client() -> Client:
    """
    환경변수에서 Supabase 접속 정보를 읽어 클라이언트를 반환합니다.

    필요한 환경변수 (.env 파일에 설정):
        SUPABASE_URL: Supabase 프로젝트 URL
                      예: https://abcdefgh.supabase.co
        SUPABASE_KEY: Supabase anon(공개) API 키
                      Supabase 대시보드 → Settings → API에서 확인 가능

    Returns:
        Supabase Client 인스턴스

    Raises:
        ValueError: 환경변수가 설정되지 않은 경우
    """
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")

    if not url:
        raise ValueError(
            "SUPABASE_URL 환경변수가 설정되지 않았습니다. "
            ".env 파일에 SUPABASE_URL=https://your-project.supabase.co 를 추가하세요."
        )

    if not key:
        raise ValueError(
            "SUPABASE_KEY 환경변수가 설정되지 않았습니다. "
            ".env 파일에 SUPABASE_KEY=your-anon-key 를 추가하세요."
        )

    return create_client(url, key)


# =============================================================================
# 개발/테스트 환경 가이드
# =============================================================================
# 1. 프로젝트 루트에 .env 파일 생성:
#    SUPABASE_URL=https://your-project-id.supabase.co
#    SUPABASE_KEY=your-anon-public-key
#
# 2. main.py에서 python-dotenv로 환경변수 로드:
#    from dotenv import load_dotenv
#    load_dotenv()
#
# 3. .gitignore에 .env 추가 필수! (API 키 노출 방지)
# =============================================================================
