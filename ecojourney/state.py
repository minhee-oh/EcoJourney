"""
EcoJourney 앱의 메인 State 클래스

기능별로 분리된 State 클래스들을 통합하여 사용합니다.
각 기능은 states/ 디렉토리의 별도 파일로 관리됩니다.

구조:
- states/base.py: 기본 UI 상태 및 공통 기능
- states/auth.py: 사용자 인증 (BaseState 상속)
- states/carbon.py: 탄소 배출량 입력 및 저장 (AuthState 상속)
- states/battle.py: 대항전 시스템 (CarbonState 상속)
- states/mileage.py: 마일리지 환산 (BattleState 상속)
- states/challenge.py: 챌린지 시스템 (MileageState 상속)

최종 AppState는 ChallengeState를 사용하여 모든 기능을 포함합니다.
"""

from .states import AppState

# AppState는 states/__init__.py에서 ChallengeState로 정의됨
# 모든 기능이 포함된 최종 State 클래스
__all__ = ["AppState"]
