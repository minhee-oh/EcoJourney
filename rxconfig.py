import reflex as rx

config = rx.Config(
    app_name="ecojourney",
    
    # 중요: Reflex는 자체 서버를 포트 3000에서 실행합니다
    # 백엔드 API는 별도로 포트 8000에서 실행됩니다
    # WebSocket은 Reflex 서버 자체(포트 3000)에 연결되어야 합니다
    
    # backend_url을 설정하지 않으면 Reflex가 자동으로 현재 서버를 사용합니다
    # 만약 backend_url을 설정하면 WebSocket이 그 URL로 연결을 시도하므로 주의!
    # backend_url=None  # 명시적으로 None으로 설정하여 자동 감지 방지
    
    # SitemapPlugin 경고 해결: 플러그인 비활성화
    disable_plugins=["reflex.plugins.sitemap.SitemapPlugin"],
    
    # 환경 친화적인 테마 설정
    theme=rx.theme(
        appearance="light",
        has_background=True,
        radius="large",
        accent_color="green",
        scaling="100%",
    )
)