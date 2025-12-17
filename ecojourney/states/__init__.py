"""
State 모듈들을 통합하는 패키지
각 기능별 State 클래스를 import하여 사용

최종 AppState는 ChallengeState를 사용 (모든 기능 포함)
"""

from .base import BaseState
from .auth import AuthState
from .carbon import CarbonState
from .battle import BattleState
from .mileage import MileageState
from .challenge import ChallengeState

# 최종 AppState는 ChallengeState (모든 기능 포함)
AppState = ChallengeState

__all__ = [
    "BaseState",
    "AuthState", 
    "CarbonState",
    "BattleState",
    "MileageState",
    "ChallengeState",
    "AppState",
]

