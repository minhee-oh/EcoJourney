# info.py - 정보 글 & OX 퀴즈 페이지

import reflex as rx
from ..states import AppState
from .common_header import header

# --------------------------
# 아티클 데이터
# --------------------------
ARTICLES = [
    {
        "title": "탄소 발자국이란?",
        "full_text": (
            "‘탄소 발자국(Carbon Footprint)’은 개인, 기업, 국가가 생활이나 생산 활동 과정에서 "
            "직접·간접적으로 발생시키는 온실가스를 전부 합산한 값을 말합니다. 이 값은 대부분 이산화탄소로 "
            "환산되어 표기되며, 우리가 사용하는 전기, 교통수단, 소비하는 제품 등 거의 모든 활동과 연결되어 있습니다. "
            "탄소 발자국이 높을수록 기후변화에 미치는 영향이 커지기 때문에 일상 속에서 줄이는 실천이 필요합니다. "
            "탄소 발자국을 이해하는 것은 지속가능한 생활을 위한 첫걸음입니다.\n\n"
            "탄소 발자국을 줄이는 방법에는 대중교통 이용, 에너지 효율이 높은 제품 사용, 재활용 확대 등이 있습니다. "
            "식생활에서도 육류 섭취를 줄이고 채식 비중을 높이는 것이 효과적이며, 지역 농산물을 구매해 운송 거리를 "
            "줄이는 것도 중요한 실천입니다. 작은 행동이라도 꾸준히 실천하면 개인의 배출량을 상당히 줄일 수 있습니다. "
            "나아가 많은 사람들이 이러한 노력을 함께할 때, 사회 전체의 탄소 배출량 감소에 큰 영향을 미칠 수 있습니다. "
            "탄소 발자국 감축은 환경 보호뿐 아니라 건강한 미래를 만드는 데 중요한 역할을 합니다."
        ),
        "image": "/article1.jpg",
        "on_read": AppState.complete_daily_info,
    }, 
    {
        "title": "제로웨이스트 실천",
        "full_text": (
            "제로웨이스트(Zero Waste)는 ‘쓰레기를 가능한 한 만들지 않는 것’을 목표로 하는 생활 방식입니다. "
            "우리가 일상 속에서 사용하는 물건들은 대부분 포장재와 일회용품을 동반하고 있으며, 이들이 결국 환경오염의 "
            "주요 원인이 됩니다. 제로웨이스트는 이러한 소비 구조를 바꾸기 위해 재사용 가능한 물건을 선택하고, "
            "불필요한 소비를 줄이는 것에서 출발합니다. 이는 자원을 효율적으로 사용하고 폐기물을 최소화하는 중요한 실천입니다.\n\n"
            "제로웨이스트 생활 방식은 다회용 컵, 장바구니, 리필 스테이션 이용처럼 비교적 간단한 실천에서 시작할 수 있습니다. "
            "또한 음식을 필요한 만큼만 구매하여 음식물 쓰레기를 줄이고, 오래 사용할 수 있는 제품을 선택하는 것도 핵심입니다. "
            "한 사람의 실천은 작아 보일 수 있지만, 많은 사람들이 동참하면 생산·유통 구조 전체가 변화하는 데 큰 힘이 됩니다. "
            "제로웨이스트는 환경 보호뿐 아니라 건강한 소비 습관을 만드는 데도 도움이 됩니다. "
            "지속 가능한 미래를 위한 중요한 실천입니다."
        ),
        "image": "/article2.jpg",
        "on_read": AppState.complete_daily_info,
    },
    {
        "title": "미세먼지의 원인",
        "full_text": (
            "미세먼지는 공기 중에 떠다니는 매우 작은 입자로, 자동차 배기가스, 공장·발전소 배출물, 난방 연료 사용 등에서 "
            "주로 생성됩니다. 이러한 미세먼지는 지름이 매우 작아 눈에 보이지 않지만 호흡기를 통해 쉽게 체내로 유입될 수 있어 "
            "건강에 큰 영향을 줄 수 있습니다. 특히 초미세먼지(PM2.5)는 폐 깊숙이 침투해 다양한 질병을 유발할 가능성이 큽니다. "
            "도시화와 산업화가 진행될수록 미세먼지 문제가 심화되고 있어 사회적 관심이 커지고 있습니다.\n\n"
            "미세먼지를 줄이기 위해서는 수송, 산업, 난방 부문에서의 배출 저감 노력이 필요합니다. "
            "대중교통 이용, 자동차 공회전 줄이기, 친환경 연료 보급 확대 등이 효과적인 방법입니다. "
            "정부와 기업의 정책도 중요하지만 개인의 작은 습관 변화도 미세먼지 개선에 도움을 줄 수 있습니다. "
            "예를 들어 에너지 절약, 분리배출 실천, 실내 공기질 관리 등이 해당됩니다. "
            "미세먼지는 개인 건강뿐 아니라 사회 전체의 환경 문제이므로 함께 해결해야 할 과제입니다."
        ),
        "image": "/article3.jpg",
        "on_read": AppState.complete_daily_info,
    },
    {
        "title": "재활용의 중요성",
        "full_text": (
            "재활용은 한 번 사용된 자원을 다시 사용 가능한 형태로 전환하여 새로운 자원 투입을 줄이는 활동입니다. "
            "플라스틱, 종이, 유리, 금속 등 우리가 매일 사용하는 물건들은 올바른 분리배출만 이루어지면 대부분 재활용이 가능합니다. "
            "그러나 분리배출이 잘 이루어지지 않으면 재활용률이 떨어지고, 결국 쓰레기 매립과 소각으로 이어져 환경오염을 악화시킵니다. "
            "재활용은 단순한 쓰레기 관리가 아니라 자원 순환의 핵심 요소입니다.\n\n"
            "재활용을 활성화하기 위해서는 분리배출 규칙을 준수하는 것이 가장 중요합니다. "
            "라벨 제거, 내용물 비우기, 비닐과 플라스틱의 구분 등 기본적인 수칙만 잘 지켜도 재활용 품질이 크게 향상됩니다. "
            "또한 재활용 제품을 선택하는 소비 습관은 친환경 제품 생산을 촉진해 시장 구조까지 변화시킬 수 있습니다. "
            "환경 보호는 개인의 작은 실천에서 시작되며, 재활용은 모든 사람이 쉽게 참여할 수 있는 첫 단계입니다. "
            "지속 가능한 미래를 위해 재활용 문화 확산이 필수적입니다."
        ),
        "image": "/article4.jpg",
        "on_read": AppState.complete_daily_info,
    },
    {
        "title": "에너지 절약의 효과",
        "full_text": (
            "전기 생산 과정에서는 많은 양의 온실가스가 배출되기 때문에, 전력 사용량을 줄이는 것은 탄소 배출을 감소시키는 "
            "가장 직접적인 방법입니다. 가정이나 학교, 회사에서 사용하는 냉난방, 조명, 가전제품은 모두 전력 소비와 연결되어 있으며 "
            "효율적인 사용만으로도 큰 절약 효과를 거둘 수 있습니다. 에너지 절약은 경제적 비용을 줄일 뿐만 아니라 기후위기 대응에도 "
            "중요한 역할을 합니다.\n\n"
            "에너지 절약 실천은 매우 간단한 행동에서 시작할 수 있습니다. 냉난방 온도를 적정 수준으로 유지하고, 사용하지 않는 조명과 "
            "전자기기를 끄는 것은 기본입니다. 또한 고효율 가전제품 사용, 대기전력 차단, 공공교통 이용 역시 에너지 사용을 줄이는 데 "
            "효과적입니다. 이러한 실천은 개개인뿐 아니라 사회 전체의 전력 수요를 줄여 환경에 긍정적인 영향을 미칩니다. "
            "작은 습관의 변화가 모이면 큰 변화를 만들 수 있습니다."
        ),
        "image": "/article5.jpg",
        "on_read": AppState.complete_daily_info,
    },
    {
        "title": "해양 플라스틱 문제",
        "full_text": (
            "전 세계 바다에는 매년 수백만 톤의 플라스틱 쓰레기가 유입되고 있으며, 이는 해양 생태계에 큰 피해를 주고 있습니다. "
            "플라스틱은 분해되는 데 수백 년이 걸려 바다 속에서 계속 축적되며, 해양 생물들이 이를 먹이로 착각해 섭취하는 일이 "
            "빈번하게 발생합니다. 이러한 플라스틱 오염은 생태계뿐 아니라 관광, 어업 등 인간의 삶에도 부정적인 영향을 미칩니다. "
            "해양 플라스틱 문제는 이미 전 세계적인 환경 위기로 자리 잡았습니다.\n\n"
            "해양 플라스틱을 줄이기 위해서는 플라스틱 사용량 자체를 감소시키는 것이 핵심입니다. "
            "일회용품 사용 줄이기, 재사용 가능한 물품 선택, 올바른 분리배출은 누구나 할 수 있는 대표적인 실천입니다. "
            "기업과 정부 역시 생분해성 재료 개발, 플라스틱 회수 시스템 구축 등 다양한 해결책을 모색하고 있습니다. "
            "지속적인 관심과 실천이 이루어진다면 바다의 건강을 되찾는 데 큰 도움이 될 것입니다. "
            "미래 세대를 위해 지금 행동하는 것이 중요합니다."
        ),
        "image": "/article6.jpg",
        "on_read": AppState.complete_daily_info,
    },
    {
        "title": "순환경제란?",
        "full_text": (
            "순환경제(Circular Economy)는 기존의 ‘사용 후 폐기’ 중심의 선형 경제에서 벗어나 "
            "자원을 가능한 한 오래 사용하고, 폐기물을 최소화하며, 다시 자원으로 순환시키는 경제 구조를 말합니다. "
            "이 모델에서는 제품 설계 단계부터 재사용과 재활용을 고려하여 자원 낭비를 줄이고 환경오염을 방지하는 것이 중요합니다. "
            "순환경제는 환경적·경제적 효율성을 동시에 추구하는 미래형 경제 모델로 주목받고 있습니다.\n\n"
            "순환경제 실현을 위해서는 소비자가 재사용 가능한 제품을 선택하고, 기업이 재활용이 쉬운 소재를 사용하며, "
            "정부가 순환 시스템 구축을 지원해야 합니다. 또한 중고 거래 활성화, 공유 경제 서비스 이용, 수리 문화 확산 등도 "
            "순환경제의 중요한 요소입니다. 이러한 변화는 자원 고갈 문제를 완화하고 기후변화 대응에도 기여합니다. "
            "순환경제는 지속 가능한 사회를 만드는 핵심 전략 중 하나입니다."
        ),
        "image": "/article7.jpg",
        "on_read": AppState.complete_daily_info,
    },
    {
        "title": "기후위기와 폭염",
        "full_text": (
            "지구 평균 기온은 산업화 이후 계속 상승하고 있으며, 이는 전 세계적으로 폭염과 가뭄, 집중호우 같은 극단적 기후 현상을 "
            "더 자주, 더 강하게 발생시키고 있습니다. 폭염은 인간의 건강뿐 아니라 농업 생산성에도 큰 피해를 주며, 전력 수요 증가로 "
            "또 다른 환경 문제를 야기할 수 있습니다. 이러한 변화는 단순한 날씨 변화가 아니라 장기적인 기후위기의 징후로 "
            "전문가들은 경고하고 있습니다.\n\n"
            "기후위기에 대응하기 위해서는 탄소 배출량을 줄이고 재생에너지 사용을 확대하는 것이 필수적입니다. "
            "개인적으로는 에너지 절약, 친환경 교통수단 이용, 소비 습관 변화 등을 통해 기여할 수 있습니다. "
            "정부와 기업은 탄소중립 전략을 수립하고 관련 정책을 시행하여 구조적인 변화를 만들어야 합니다. "
            "폭염과 이상 기후는 더 이상 먼 미래의 일이 아니라 현재 진행 중인 위기이며, 지금 행동해야 피해를 줄일 수 있습니다. "
            "지속 가능한 미래를 위해 모두의 노력이 필요합니다."
        ),
        "image": "/article8.jpg",
        "on_read": AppState.complete_daily_info,
    },
]




def info_card(title: str, body: str, on_click) -> rx.Component:
    """단일 정보 카드 컴포넌트."""
    return rx.vstack(
        rx.heading(title, size="5", color="#333333", margin_bottom="8px"),
        rx.text(body, size="5", color="gray.700", font_weight="normal", line_height="1.7", white_space="pre-wrap"),
        rx.button(
            "읽었어요",
            on_click=on_click,
            margin_top="12px",
            color_scheme="green",
            variant="solid",
            size="2",
        ),
        spacing="3",
        align="start",
        width="100%",
        padding="20px",
    )


# --------------------------
# 모달 컴포넌트
# --------------------------
def article_modal(article: dict):
    return rx.dialog.root(
        rx.dialog.trigger(
            rx.box(
                rx.vstack(
                    rx.heading(article["title"], size="5", color="#333333"),
                    spacing="2",
                    align="start",
                    justify="end",
                    height="100%",
                ),
                width="250px",
                height="300px",
                border_radius="20px",
                padding="20px",
                cursor="pointer",
                
                background=f"url('{article['image']}') no-repeat top",
                background_size="100% 80%",
                background_position="top",
                
                box_shadow="0 6px 16px rgba(0,0,0,0.25)",
                position="relative",
                class_name="article-card",
            )
        ),

        rx.dialog.content(
            rx.vstack(
                # 이미지
                rx.box(
                    background=f"url('{article['image']}')",
                    background_size="cover",
                    background_position="center",
                    width="100%",
                    height="400px",
                    border_radius="12px",
                ),

                # 제목 & 본문
                rx.heading(article["title"], size="6", margin_top="15px"),
                rx.text(article["full_text"], size="4", color="gray.700"),

                rx.dialog.close(
                    rx.button(
                        rx.cond(
                            AppState.article_read_today,
                            "오늘 이미 보상 받았어요!",
                            "보상 받기"
                        ),
                        on_click=[article["on_read"]],
                        color_scheme=rx.cond(
                            AppState.article_read_today,
                            "gray",
                            "green"
                        ),
                        disabled=AppState.article_read_today,
                        width="100%",
                        margin_top="20px",
                    ),
                ),
                align="center",
                spacing="4",
            ),
            padding="25px",
            border_radius="16px",
            max_width="600px",
            background="white",
        )
    )


# --------------------------
# OX 퀴즈 카드
# --------------------------
def quiz_card():
    return rx.cond(
        AppState.quiz_answered,
        # 이미 답변한 경우 - 결과 표시
        rx.box(
            rx.vstack(
                rx.heading(
                    rx.cond(
                        AppState.quiz_is_correct,
                        "정답입니다 ",
                        "틀렸습니다 "
                    ),
                    size="7",
                    color="#333333",
                    margin_bottom="15px",
                ),
                rx.text(
                    rx.cond(
                        AppState.quiz_is_correct,
                        "OX 퀴즈를 완료하여 포인트가 적립되었습니다. 내일 다시 도전해주세요",
                        "아쉽게도 틀렸습니다. 다시 도전해주세요!"
                    ),
                    color="gray.700",
                    size="5",
                    text_align="center",
                ),
                spacing="3",
                align="center",
            ),
            background=rx.cond(
                AppState.quiz_is_correct,
                "rgba(77, 171, 117, 0.1)",
                "rgba(231, 76, 60, 0.1)"
            ),
            border=rx.cond(
                AppState.quiz_is_correct,
                "2px solid #4DAB75",
                "2px solid #E74C3C"
            ),
            padding="40px",
            border_radius="12px",
            width="100%",
            min_height="120px",
            display="flex",
            align_items="center",
            justify_content="center",
            box_shadow="0 4px 12px rgba(0,0,0,0.1)",
        ),

        # 아직 답변하지 않은 경우 - 퀴즈 표시
        rx.vstack(
            # 문제 박스
            rx.box(
                rx.text(
                    rx.cond(
                        AppState.daily_quiz_question != "",
                        AppState.daily_quiz_question,
                        "지구 온난화를 막기 위해서는 일회용품 사용을 줄여야 한다."
                    ),
                    color="#333333",
                    size="5",
                    font_weight="500",
                ),
                background="#F1F3F4",
                padding="40px",
                border_radius="12px",
                width="100%",
                min_height="120px",
                display="flex",
                align_items="center",
                margin_bottom="20px",
            ),

            # O/X 버튼 (텍스트 오른쪽에 와도 어색하지 않도록 크기 축소)
            rx.hstack(
                # O 버튼 (정답)
                rx.button(
                    "O",
                    on_click=lambda: AppState.answer_quiz(True),
                    background_color="#4DAB75",
                    color="white",
                    size="3",
                    width="72px",
                    height="72px",
                    border_radius="999px",
                    font_weight="bold",
                    font_size="1.6em",
                    box_shadow="0 4px 10px rgba(0,0,0,0.18)",
                    transition="all 0.25s ease",
                    _hover={
                        "background_color": "#3d9463",
                        "transform": "translateY(-3px)",
                        "box_shadow": "0 8px 18px rgba(0,0,0,0.25)"
                    },
                    is_disabled=AppState.quiz_is_correct,
                ),

                # X 버튼 (오답)
                rx.button(
                    "X",
                    on_click=lambda: AppState.answer_quiz(False),
                    background_color="#E74C3C",
                    color="white",
                    size="3",
                    width="72px",
                    height="72px",
                    border_radius="999px",
                    font_weight="bold",
                    font_size="1.6em",
                    box_shadow="0 4px 10px rgba(0,0,0,0.18)",
                    transition="all 0.25s ease",
                    _hover={
                        "background_color": "#c0392b",
                        "transform": "translateY(-3px)",
                        "box_shadow": "0 8px 18px rgba(0,0,0,0.25)"
                    },
                    is_disabled=AppState.quiz_is_correct,
                ),

                spacing="3",
                width="100%",
                justify="center",
            ),
            spacing="4",
            width="100%",
            align="center",
        ),
    )


def info_page() -> rx.Component:
    """정보 글 & 챌린지 페이지"""
    return rx.cond(
        AppState.is_logged_in,
        rx.box(
            header(),
            # 헤더 공간 확보
            rx.box(height="100px"),
            # fade-in 애니메이션을 위한 CSS 삽입
            rx.html("""
            <style>
            @keyframes fadeInUp {
                0% {
                    opacity: 0;
                    transform: translateY(20px);
                }
                100% {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
            </style>
            """),

            # 배경 레이어 구성
            rx.box(
                # 상단 배경 + 텍스트 + fade-in animation
                rx.box(
                    rx.hstack(
                        rx.vstack(
                            rx.heading(
                                "챌린지",
                                size="9",
                                color="#333333",
                                margin_bottom="18px",
                                style={
                                    "opacity": 0,
                                    "transform": "translateY(20px)",
                                    "animation": "fadeInUp 0.8s ease forwards",
                                    "animation-delay": "0.1s",
                                },
                            ),
                            rx.text(
                                "정보 글을 읽고 OX 퀴즈를 풀어 일일 챌린지를 완료하세요!",
                                color="gray.200",
                                size="5",
                                font_weight="bold",
                                text_align="left",
                                width="100%",
                                style={
                                    "opacity": 0,
                                    "transform": "translateY(20px)",
                                    "animation": "fadeInUp 1s ease forwards",
                                    "animation-delay": "0.25s",
                                },
                            ),
                            spacing="2",
                            align="start",
                            justify="center",
                            height="100%",
                            padding_top="50px",
                            padding_left="100px",
                        ),

                        # 오른쪽: 이미지 영역
                        rx.box(
                            rx.image(
                                src="/challenge.png",
                                width="100%",
                                height="auto",
                                object_fit="contain",
                                style={
                                    "opacity": 0,
                                    "transform": "translateY(20px)",
                                    "animation": "fadeInUp 0.8s ease forwards",
                                    "animation-delay": "0.2s",
                                },
                            ),
                            width="50%",
                            display="flex",
                            align_items="center",
                            justify_content="center",
                            padding_left="50px",
                            padding_top="70px",
                        ),
                        width="100%",
                        height="100%",
                        align="center",
                        justify="between",
                    ),
                    width="100%",
                    height="80vh",
                    background="linear-gradient(135deg, rgba(77, 171, 117, 0.1) 0%, rgba(77, 171, 117, 0.15) 100%)",
                    position="absolute",
                    top="0",
                    left="0",
                    z_index="0",
                ),

                # 실제 콘텐츠
                rx.box(
                    rx.vstack(
                        # 정보 글 카드
                        rx.card(
                            info_card(
                                rx.cond(AppState.daily_info_title != "", AppState.daily_info_title, "탄소 중립이란?"),
                                rx.cond(
                                    AppState.daily_info_body != "",
                                    AppState.daily_info_body,
                                    "인류 활동으로 발생한 온실가스 배출량을 줄이고, 남은 부분은 흡수·제거하여 순 배출량을 0으로 만드는 것.",
                                ),
                                AppState.complete_daily_info,
                            ),
                            width="100%",
                            background="white",
                            border="1px solid rgba(0,0,0,0.1)",
                            box_shadow="0 4px 12px rgba(0,0,0,0.1)",
                            margin_bottom="30px",
                        ),

                        # 퀴즈 카드
                        rx.card(
                            quiz_card(),
                            width="100%",
                            background="white",
                            border="1px solid rgba(0,0,0,0.1)",
                            box_shadow="0 4px 12px rgba(0,0,0,0.1)",
                            margin_bottom="30px",
                        ),

                        # 챌린지 메시지
                        rx.cond(
                            AppState.challenge_message != "",
                            rx.card(
                                rx.callout(
                                    AppState.challenge_message,
                                    icon="info",
                                    color_scheme="green",
                                    width="100%",
                                ),
                                width="100%",
                                background="white",
                                border="1px solid rgba(0,0,0,0.1)",
                                box_shadow="0 4px 12px rgba(0,0,0,0.1)",
                                margin_bottom="30px",
                            ),
                        ),

                        spacing="6",
                        width="100%",
                        max_width="1200px",
                        align="center",
                    ),

                    width="100%",
                    z_index="2",
                    padding="40px 20px",
                    display="flex",
                    justify_content="center",
                    margin_top="66vh",
                ),
            ),
        ),
        rx.box(
            header(),
            rx.center(
                rx.vstack(
                    rx.heading("로그인이 필요합니다", size="6", color="white"),
                    rx.button(
                        "로그인하기",
                        on_click=rx.redirect("/auth"),
                        color_scheme="green",
                        size="3",
                        margin_top="20px",
                    ),
                    spacing="4",
                    align="center",
                ),
                width="100%",
                min_height="calc(100vh - 80px)",
            ),
            spacing="0",
            width="100%",
            min_height="100vh",
        ),
    )
