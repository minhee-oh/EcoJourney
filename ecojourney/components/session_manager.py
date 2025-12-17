"""
세션 복원을 위한 글로벌 스크립트 컴포넌트
"""
import reflex as rx


def session_restoration_component() -> rx.Component:
    """
    페이지 로드 시 localStorage에서 세션을 확인하고 복원하는 컴포넌트
    """
    return rx.fragment(
        # HTML에 숨겨진 데이터 저장소
        rx.html('<div id="session-check" style="display:none;"></div>'),

        # 세션 복원 스크립트
        rx.script(
            """
            (function() {
                // localStorage에서 세션 정보 확인
                const userId = localStorage.getItem('eco_user_id');
                const isLoggedIn = localStorage.getItem('eco_is_logged_in');
                const userCollege = localStorage.getItem('eco_user_college');
                const userPoints = localStorage.getItem('eco_user_points');

                // 로그인 상태이고 세션 정보가 있으면 복원
                if (isLoggedIn === 'true' && userId && userId !== 'null') {
                    // 세션 데이터를 숨겨진 input에 저장 (Reflex가 읽을 수 있도록)
                    const sessionDiv = document.getElementById('session-check');
                    if (sessionDiv) {
                        sessionDiv.setAttribute('data-user-id', userId);
                        sessionDiv.setAttribute('data-user-college', userCollege || '');
                        sessionDiv.setAttribute('data-user-points', userPoints || '0');
                        sessionDiv.setAttribute('data-restore', 'true');
                    }
                }
            })();
            """
        )
    )
