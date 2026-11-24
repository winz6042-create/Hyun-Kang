import calendar, json, math, os, urllib.parse
from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo
import streamlit as st
from korean_lunar_calendar import KoreanLunarCalendar

# ───────── 기본 데이터 ─────────
STEM_K, STEM_H = list("갑을병정무기경신임계"), list("甲乙丙丁戊己庚辛壬癸")
BR_K, BR_H = list("자축인묘진사오미신유술해"), list("子丑寅卯辰巳午未申酉戌亥")
EL = ["목(木)", "화(火)", "토(土)", "금(金)", "수(水)"]
EL_COLOR = ["#3B7A57", "#B83A2E", "#C9A227", "#8A8A8A", "#1F2A44"]  # 오방색
STEM_EL = [0, 0, 1, 1, 2, 2, 3, 3, 4, 4]
BR_EL = [4, 2, 0, 0, 2, 1, 1, 2, 3, 3, 2, 4]
BR_MAIN = [9, 5, 0, 1, 4, 2, 3, 5, 6, 7, 4, 8]  # 지지 본기(천간 번호)
GROUP = ["비겁", "식상", "재성", "관성", "인성"]
DM_TEXT = [
    "갑목: 큰 나무. 곧고 진취적이며 리더십이 있습니다.",
    "을목: 풀과 덩굴. 유연하고 적응력이 좋으며 섬세합니다.",
    "병화: 태양. 밝고 열정적이며 표현력이 풍부합니다.",
    "정화: 촛불. 따뜻하고 세심하며 집중력이 뛰어납니다.",
    "무토: 큰 산. 믿음직하고 포용력이 크며 중후합니다.",
    "기토: 논밭의 흙. 온화하고 현실적이며 꼼꼼합니다.",
    "경금: 바위·쇠. 결단력이 강하고 의리가 있습니다.",
    "신금: 보석. 예민하고 깔끔하며 완성도를 중시합니다.",
    "임수: 큰 강·바다. 지혜롭고 스케일이 크며 자유롭습니다.",
    "계수: 이슬·비. 영리하고 감성적이며 직관이 좋습니다.",
]
GROUP_TEXT = [
    "비겁(비견·겁재): 자아, 독립심, 동료와 경쟁. 많으면 고집과 경쟁심, 적으면 주관 부족.",
    "식상(식신·상관): 표현력, 재능, 창의. 많으면 말과 아이디어가 풍부, 적으면 표현이 소극적.",
    "재성(편재·정재): 재물, 현실감각, 실행력. 많으면 현실적이고 활동적, 적으면 재물 관리에 신경.",
    "관성(편관·정관): 직업, 책임, 명예. 많으면 책임감과 압박, 적으면 자유로우나 조직 적응에 노력.",
    "인성(편인·정인): 학문, 보호, 자격. 많으면 사려 깊고 의존적, 적으면 독립적이나 후원 부족.",
]

DM_DETAIL = [
    "곧게 뻗는 큰 나무처럼 자존심이 강하고 정직하며, 새로운 일을 시작하고 이끄는 힘이 있습니다. 굽히기 싫어하는 고집이 약점이라 유연함을 더하면 좋습니다. 교육, 기획, 경영, 개척형 분야에 어울립니다.",
    "풀과 덩굴처럼 환경에 잘 적응하고 사람을 부드럽게 끄는 힘이 있습니다. 겉은 순해도 속은 끈질깁니다. 눈치를 너무 보다 결정을 미루는 점을 조심하세요. 상담, 디자인, 서비스, 예술 분야에 어울립니다.",
    "태양처럼 밝고 공명정대하며 사람을 모으는 매력이 있습니다. 시작은 화끈하지만 급한 면이 있어 마무리를 챙기는 것이 중요합니다. 방송, 영업, 교육, 대외 활동 분야에 어울립니다.",
    "촛불처럼 따뜻하고 섬세하며 한 가지에 깊이 몰입합니다. 예의 바르고 배려심이 있으나 마음의 상처를 오래 담아 두기 쉽습니다. 연구, 교육, 문화예술, 의료·상담 분야에 어울립니다.",
    "큰 산처럼 묵직하고 신뢰감이 있으며 중심을 잡아 주는 사람입니다. 변화에 느리고 고집스러워 보일 수 있습니다. 조직 운영, 부동산, 금융, 관리직 분야에 어울립니다.",
    "논밭의 흙처럼 포용력이 있고 실속 있게 사람과 일을 키웁니다. 겉으로 드러내지 않고 속으로 걱정을 많이 하는 편입니다. 교육, 농·식품, 서비스, 상담·행정 분야에 어울립니다.",
    "바위와 쇠처럼 결단력과 추진력이 강하고 의리를 중시합니다. 직설적이어서 차갑게 보일 수 있으니 말의 온도를 살피면 좋습니다. 군·경, 법률, 기계·기술, 운동 분야에 어울립니다.",
    "보석처럼 섬세하고 깔끔하며 미적 감각과 완벽주의 성향이 있습니다. 예민하고 자존심이 강해 상처를 잘 받을 수 있습니다. 전문직, 금융, 패션·디자인, 정밀 기술 분야에 어울립니다.",
    "큰 강과 바다처럼 포용력이 크고 생각의 스케일이 넓으며 자유를 사랑합니다. 계획 없이 흘러가거나 한 곳에 머물기 어려운 면이 있습니다. 무역, 유통, 학문, 연구, 기획 분야에 어울립니다.",
    "이슬과 빗물처럼 영리하고 감수성이 풍부하며 직관과 눈치가 빠릅니다. 생각이 많고 걱정을 쌓아 두기 쉬워 마음을 쉬게 하는 시간이 필요합니다. 연구, 기획, 글쓰기, 상담·의료 분야에 어울립니다.",
]
TEN_DAE = {
    "비견": "나와 비슷한 사람(동료·형제·친구)과 어울리고 독립심과 자존심이 커지는 시기입니다. 협력도 늘지만 경쟁과 재물 분산에 주의하세요.",
    "겁재": "경쟁과 승부욕이 강해지고 사람 관계로 얻고 잃는 일이 생기는 시기입니다. 동업·보증·투자는 신중하게 하세요.",
    "식신": "먹고 즐기고 만들어 내는 여유의 시기입니다. 재능과 취미가 꽃피고 몸과 마음이 편해지기 쉽습니다. 안주하지 않는 것이 포인트입니다.",
    "상관": "표현력과 창의성이 커지고 기존 틀을 깨고 싶어지는 시기입니다. 말실수와 윗사람과의 마찰에 주의하세요.",
    "편재": "활동 범위가 넓어지고 큰 돈과 사업 기회를 만나기 쉬운 시기입니다. 들어오는 만큼 나가기 쉬우니 관리가 중요합니다.",
    "정재": "꾸준한 수입과 안정, 성실한 재물 관리의 시기입니다. 가정과 현실 기반을 다지기 좋습니다.",
    "편관": "책임과 압박이 커지고 도전과 시험이 따르는 시기입니다. 버티며 실력을 쌓으면 큰 성장이 됩니다. 건강 관리에 신경 쓰세요.",
    "정관": "직장·명예·질서가 따르는 시기로 승진이나 자격, 사회적 인정을 얻기 좋습니다. 규칙을 지키는 자세가 도움이 됩니다.",
    "편인": "특이한 공부, 기술, 종교·철학 등 남다른 분야에 관심이 생기는 시기입니다. 생각이 많아져 변덕이 생기지 않게 주의하세요.",
    "정인": "학업, 자격, 문서, 윗사람의 도움이 따르는 안정의 시기입니다. 배우고 준비하기 좋으나 의존적이 되지 않도록 하세요.",
}
EL_LACK = [
    "목이 부족: 추진력과 성장 에너지, 계획성이 약해질 수 있습니다. 간·눈·근육 건강을 챙기고 새로운 시작을 의식적으로 해 보세요.",
    "화가 부족: 열정과 표현이 소극적일 수 있습니다. 밝은 활동과 사람과의 교류를 늘려 보세요.",
    "토가 부족: 안정감과 중심, 신뢰를 쌓는 힘이 약할 수 있습니다. 규칙적인 생활과 소화기 건강에 신경 쓰세요.",
    "금이 부족: 결단력과 마무리가 약할 수 있습니다. 원칙과 기준을 정해 두면 좋습니다.",
    "수가 부족: 유연함과 지혜, 휴식이 부족할 수 있습니다. 충분한 수면과 배우는 습관이 도움이 됩니다.",
]
EL_EXCESS = [
    "목이 과다: 생각과 계획이 많고 고집이 세질 수 있습니다. 하나에 집중하고 유연함을 기르세요.",
    "화가 과다: 급하고 감정 기복이 클 수 있습니다. 쉬어 가는 시간과 호흡 조절이 필요합니다.",
    "토가 과다: 고집과 걱정이 많고 변화에 둔할 수 있습니다. 새로운 시도를 조금씩 해 보세요.",
    "금이 과다: 냉정하고 비판적으로 보일 수 있습니다. 말의 온도와 여유를 챙기세요.",
    "수가 과다: 생각이 많고 불안·우유부단해지기 쉽습니다. 계획을 정해 행동으로 옮기세요.",
]
STRENGTH_TEXT = {
    "신강": "일간의 힘이 강한 편입니다. 주관과 추진력이 크고 스스로 일어서는 힘이 좋습니다. 에너지를 밖으로 쓰는 식상·재성·관성의 흐름(표현, 재물, 직업 활동)이 잘 맞고, 고집과 독선을 경계하세요.",
    "신약": "일간의 힘이 상대적으로 약한 편입니다. 주변 환경과 사람의 영향을 많이 받아 도움과 협력이 중요합니다. 나를 돕는 비겁·인성(동료, 공부, 휴식, 윗사람의 도움)이 들어오는 시기에 힘이 나며, 무리한 확장은 조심하세요.",
    "균형": "일간의 힘이 크게 치우치지 않은 균형형입니다. 상황에 따라 유연하게 대응할 수 있고, 운의 흐름에 따라 강점이 달라집니다.",
}

SEOUL = ZoneInfo("Asia/Seoul")      # 연도별 표준시 변경·서머타임 규칙 내장
SOLAR = timedelta(hours=8, minutes=28)  # 서울(127°E) 진태양시 = UTC+8:28

# ───────── 천문 계산 (태양 황경으로 절기 정밀 계산) ─────────
def to_jd(utc):
    return (utc - datetime(1970, 1, 1)).total_seconds() / 86400 + 2440587.5

def sun_lon(jd):
    t = (jd - 2451545) / 36525
    l0 = 280.46646 + 36000.76983 * t
    m = math.radians(357.52911 + 35999.05029 * t)
    c = ((1.914602 - 0.004817 * t) * math.sin(m) + 0.019993 * math.sin(2 * m)
         + 0.000289 * math.sin(3 * m))
    om = math.radians(125.04 - 1934.136 * t)
    return (l0 + c - 0.00569 - 0.00478 * math.sin(om)) % 360

def cross(target, a, b):
    """[a,b](JD) 안에서 태양 황경이 target이 되는 시각을 이분법으로 찾음"""
    diff = lambda j: ((sun_lon(j) - target + 540) % 360) - 180
    for _ in range(40):
        m = (a + b) / 2
        if diff(m) < 0:
            a = m
        else:
            b = m
    return (a + b) / 2

def jdn(y, m, d):
    a = (14 - m) // 12
    yy, mm = y + 4800 - a, m + 12 * a - 3
    return d + (153 * mm + 2) // 5 + 365 * yy + yy // 4 - yy // 100 + yy // 400 - 32045

def idx60(s, b):
    return next(i for i in range(60) if i % 10 == s and i % 12 == b)

def ten(ds, os_):
    same = ds % 2 == os_ % 2
    return [("비견", "겁재"), ("식신", "상관"), ("편재", "정재"), ("편관", "정관"),
            ("편인", "정인")][(STEM_EL[os_] - STEM_EL[ds]) % 5][0 if same else 1]

def group_of(ds, os_):
    return (STEM_EL[os_] - STEM_EL[ds]) % 5

def strength(r):
    """일간을 돕는 힘(비겁·인성) 비율로 신강/신약 간이 판정. 월지 가중치 3."""
    dm = r["p"][2][0]
    w = {(0, "s"): 1, (0, "b"): 1, (1, "s"): 1, (1, "b"): 3, (2, "b"): 1.5, (3, "s"): 1, (3, "b"): 1}
    sup = tot = 0
    for (i, kind), wt in w.items():
        s_, b_ = r["p"][i]
        tot += wt
        if group_of(dm, s_ if kind == "s" else BR_MAIN[b_]) in (0, 4):
            sup += wt
    ratio = sup / tot
    return ("신강" if ratio >= 0.6 else "신약" if ratio <= 0.4 else "균형"), ratio

def calc(d, t, male, adj):
    # 입력 시각 = 그 당시 한국의 시계 시각 → 연도별 규칙으로 UTC 변환 (서머타임 자동 반영)
    wall = datetime(d.year, d.month, d.day, t.hour, t.minute, tzinfo=SEOUL)
    utc = wall.astimezone(timezone.utc).replace(tzinfo=None)
    # 일주·시주 기준 시각: 진태양시(보정 켬) 또는 입력한 시계 시각 그대로(보정 끔)
    kst = utc + SOLAR if adj else wall.replace(tzinfo=None)
    jd = to_jd(utc)  # 절기는 절대시각(UTC)으로 계산
    lon = sun_lon(jd)

    sy = kst.year  # 년주: 입춘(황경 315°) 기준
    if kst.month <= 2 and 270 <= lon < 315:
        sy -= 1
    ys, yb = (sy - 4) % 10, (sy - 4) % 12

    mi = int(((lon - 315) % 360) // 30)  # 월주: 인월부터 30°씩
    mb, ms = (2 + mi) % 12, ((ys % 5) * 2 + 2 + mi) % 10

    di = (jdn(kst.year, kst.month, kst.day) + 49) % 60  # 일주
    ds, db = di % 10, di % 12

    hb = ((kst.hour + 1) // 2) % 12  # 시주
    hs = ((ds % 5) * 2 + hb) % 10

    fwd = (ys % 2 == 0) == male  # 양남음녀 순행
    target = (315 + 30 * (mi + 1)) % 360 if fwd else (315 + 30 * mi) % 360
    tj = cross(target, jd, jd + 35) if fwd else cross(target, jd - 35, jd)
    age = max(1, int(abs(tj - jd) / 3 + 0.5))  # 3일 = 1년
    mi60 = idx60(ms, mb)
    dae = [((mi60 + (k if fwd else -k)) % 60) for k in range(1, 9)]
    return dict(p=[(ys, yb), (ms, mb), (ds, db), (hs, hb)],
                dae=[(i % 10, i % 12) for i in dae], age=age, fwd=fwd, by=sy,
                off=wall.utcoffset(), dst=bool(wall.dst()))

# ───────── 화면 ─────────
def glyph(ch, e):
    c = EL_COLOR[e]
    return (f"<div style='margin:3px auto;width:58px;height:58px;line-height:58px;"
            f"text-align:center;font-size:32px;font-weight:bold;color:{c};"
            f"background:{c}1f;border:1px solid {c};border-radius:4px'>{ch}</div>")

def ai_prompt(r):
    """사주 계산 결과만으로 AI에게 보낼 질문 문장 생성 (생년월일·이름 등 개인정보 미포함)"""
    p = lambda x: STEM_K[x[0]] + BR_K[x[1]]
    return ("아래 사주팔자는 이미 계산된 것이니 다시 계산하지 말고 풀이만 해 주세요. "
            "성격, 직업·재물, 연애·결혼, 건강, 대운별 흐름을 항목별로 쉽고 상세하게 설명해 주세요.\n\n"
            f"년주 {p(r['p'][0])} / 월주 {p(r['p'][1])} / 일주 {p(r['p'][2])} / 시주 {p(r['p'][3])}\n"
            f"대운({'순행' if r['fwd'] else '역행'}, {r['age']}세 시작): "
            + " ".join(p(x) for x in r["dae"]))

def share_text(r, name, when):
    p = lambda x: STEM_K[x[0]] + BR_K[x[1]]
    dm = r["p"][2][0]
    n = f"{name}님의 " if name else ""
    lab, ratio = strength(r)
    lines = [f"{n}사주팔자", when, "",
             f"년주 {p(r['p'][0])} / 월주 {p(r['p'][1])} / 일주 {p(r['p'][2])} / 시주 {p(r['p'][3])}",
             DM_TEXT[dm], DM_DETAIL[dm], "",
             f"[일간 강약] {lab} - {STRENGTH_TEXT[lab]}", "",
             f"[대운] {'순행' if r['fwd'] else '역행'}, {r['age']}세 시작"]
    for k, x in enumerate(r["dae"]):
        a0 = r["age"] + 10 * k
        lines.append(f"· {a0}~{a0 + 9}세 {p(x)}({ten(dm, x[0])}운): {TEN_DAE[ten(dm, x[0])]}")
    return "\n".join(lines)

SAVE = os.environ.get("SAJU_SAVE") == "1"  # 내 컴퓨터에서만 저장 기능 사용
FILE = "records.json"
load_recs = lambda: json.load(open(FILE, encoding="utf-8")) if os.path.exists(FILE) else []

def run(d, t, g, adj, label):
    """계산 + 화면에 보여줄 입력 정보(label, 양력 날짜 등)를 결과에 함께 저장"""
    r = calc(d, t, g == "남", adj)
    r.update(solar=d, h=t.hour, mi=t.minute, g=g, adj=adj,
             when=f"{label} {t.hour}시 {t.minute:02d}분 ({g})")
    return r

def load(rec):
    bd = date.fromisoformat(rec["d"])  # 저장된 날짜는 양력 기준
    st.session_state.update(name=rec["n"], cal="양력", y=bd.year, mo=bd.month, dd=bd.day,
                            t=time(rec["h"], rec["m"]), g=rec["g"], adj=rec["a"])
    st.session_state.r = run(bd, st.session_state.t, rec["g"], rec["a"],
                             f"{bd.year}년 {bd.month}월 {bd.day}일(양력)")

st.set_page_config(page_title="사주팔자", page_icon="命")
st.title("命 사주팔자")

if SAVE:
    with st.sidebar:
        st.subheader("저장된 사주")
        recs = load_recs()
        for i, rec in enumerate(recs):
            c1, c2 = st.columns([4, 1])
            c1.button(rec["n"] + " " + rec["d"], key=f"l{i}", on_click=load, args=(rec,))
            if c2.button("🗑", key=f"x{i}"):
                recs.pop(i)
                json.dump(recs, open(FILE, "w", encoding="utf-8"), ensure_ascii=False)
                st.rerun()

name = st.text_input("이름 (선택)", key="name")
MIN_YEAR = 1900  # 더 이전 출생까지 허용하려면 이 값을 낮추세요
years = list(range(MIN_YEAR, date.today().year + 1))
st.session_state.setdefault("y", 1990)
st.session_state.setdefault("mo", 1)
st.session_state.setdefault("dd", 1)
st.write("**생년월일**")
cal_type = st.radio("달력 구분", ["양력", "음력"], horizontal=True, key="cal")
c1, c2, c3 = st.columns([1.3, 1, 1])
y = c1.selectbox("년", years, key="y", format_func=lambda v: f"{v}년")
mo = c2.selectbox("월", list(range(1, 13)), key="mo", format_func=lambda v: f"{v}월")
leap = False
if cal_type == "음력":
    nd = 30  # 음력은 29일 또는 30일 (존재 여부는 아래에서 검증)
    leap = st.checkbox("윤달 (해당 월이 윤달이면 체크)", key="leap")
else:
    nd = calendar.monthrange(y, mo)[1]  # 해당 월의 마지막 날 (윤년 포함)
if st.session_state.dd > nd:
    st.session_state.dd = nd
dd = c3.selectbox("일", list(range(1, nd + 1)), key="dd", format_func=lambda v: f"{v}일")

d, label = None, ""  # d = 계산에 쓰는 양력 날짜
if cal_type == "음력":
    kc = KoreanLunarCalendar()
    if y <= 2050 and kc.setLunarDate(y, mo, dd, leap):
        d = date.fromisoformat(kc.SolarIsoFormat()[:10])
        label = f"음력 {y}년 {'윤' if leap else ''}{mo}월 {dd}일 (양력 {d.year}.{d.month}.{d.day})"
        st.caption(f"양력으로 변환: {d.year}년 {d.month}월 {d.day}일")
    else:
        st.error("존재하지 않는 음력 날짜입니다. 윤달 체크와 일(29일/30일)을 확인해 주세요.")
else:
    d = date(y, mo, dd)
    label = f"{y}년 {mo}월 {dd}일(양력)"
t = st.time_input("태어난 시간", value=time(12, 0), step=60, key="t")
g = st.radio("성별", ["남", "여"], horizontal=True, key="g")
adj = st.toggle("진태양시 보정 (서울 127°E 기준)", value=True, key="adj",
                help="켜면 서울의 지방 태양시(UTC+8:28)로 일주·시주를 계산합니다. 연도별 표준시 변경과 서머타임은 자동 반영됩니다.")
if st.button("사주 보기", type="primary"):
    if d is None:
        st.error("생년월일을 확인해 주세요.")
    elif d > date.today():
        st.error("오늘 이후의 날짜는 계산할 수 없습니다.")
    else:
        st.session_state.r = run(d, t, g, adj, label)

r = st.session_state.get("r")
if r:
    dm = r["p"][2][0]
    st.subheader("사주 원국")
    mins = int(r["off"].total_seconds() // 60)
    st.caption(f"입력 시각에 적용된 한국 시간대: UTC+{mins // 60}:{mins % 60:02d}"
               + (" · 서머타임 적용" if r["dst"] else ""))
    cols = st.columns(4)
    for col, (label, i) in zip(cols, [("시주", 3), ("일주", 2), ("월주", 1), ("년주", 0)]):
        s, b = r["p"][i]
        top = "일원(나)" if i == 2 else ten(dm, s)
        col.markdown(f"<div style='text-align:center;font-size:12px'><span style='color:#9E2A2B'>"
                     f"{label}</span><br>{top}{glyph(STEM_H[s], STEM_EL[s])}"
                     f"{glyph(BR_H[b], BR_EL[b])}{ten(dm, BR_MAIN[b])}</div>",
                     unsafe_allow_html=True)
    st.write(" ".join(f"{STEM_K[s]}{BR_K[b]}{x}" for (s, b), x in zip(r["p"], "년월일시")))

    el, gr = [0] * 5, [0] * 5
    for i, (s, b) in enumerate(r["p"]):
        el[STEM_EL[s]] += 1
        el[BR_EL[b]] += 1
        if i != 2:
            gr[group_of(dm, s)] += 1
        gr[group_of(dm, BR_MAIN[b])] += 1
    st.subheader("오행 분포")
    st.write("  ".join(f"**{EL[i]} {el[i]}**" for i in range(5)))
    for i in range(5):
        if el[i] == 0:
            st.write("▪ " + EL_LACK[i])
        elif el[i] >= 4:
            st.write("▪ " + EL_EXCESS[i])
    st.subheader("나의 일간")
    st.write(DM_TEXT[dm])
    st.write(DM_DETAIL[dm])
    st.subheader("십성 풀이")
    st.write("  ".join(f"**{GROUP[i]} {gr[i]}**" for i in range(5)))
    st.write("가장 강한 기운 ▶ " + GROUP_TEXT[gr.index(max(gr))])
    st.write("가장 약한 기운 ▶ " + GROUP_TEXT[gr.index(min(gr))])
    lab, ratio = strength(r)
    st.subheader("일간 강약 (신강·신약)")
    st.write(f"**{lab}** (일간을 돕는 힘 약 {ratio * 100:.0f}%)")
    st.write(STRENGTH_TEXT[lab])
    st.caption("월지의 영향을 크게 본 간이 판정이며, 명리가마다 기준이 다를 수 있습니다.")

    st.subheader(f"대운 ({'순행' if r['fwd'] else '역행'} · {r['age']}세 시작)")
    age_now = date.today().year - r["by"]
    cur = min(7, (age_now - r["age"]) // 10) if age_now >= r["age"] else -1
    boxes = ""
    for k, (s, b) in enumerate(r["dae"]):
        bd = "2px solid #9E2A2B" if k == cur else "1px solid #0004"
        bg = "#C9A22750" if k == cur else "#FBF6E9"
        boxes += (f"<div style='width:72px;text-align:center;font-size:11px;padding:4px;"
                  f"border:{bd};background:{bg};border-radius:4px'>"
                  f"<span style='color:#9E2A2B'>{r['age'] + 10 * k}세</span><br>{ten(dm, s)}"
                  f"<div style='font-size:24px;color:{EL_COLOR[STEM_EL[s]]}'>{STEM_H[s]}</div>"
                  f"<div style='font-size:24px;color:{EL_COLOR[BR_EL[b]]}'>{BR_H[b]}</div>"
                  f"{r['by'] + r['age'] + 10 * k}~</div>")
    st.markdown(f"<div style='display:flex;flex-wrap:wrap;gap:6px'>{boxes}</div>",
                unsafe_allow_html=True)
    if cur >= 0:
        s, b = r["dae"][cur]
        st.write(f"**현재 대운: {STEM_K[s]}{BR_K[b]} ({ten(dm, s)} 운)**")
    with st.expander("대운별 상세 풀이", expanded=True):
        for k, (s, b) in enumerate(r["dae"]):
            a0 = r["age"] + 10 * k
            mark = "▶ " if k == cur else ""
            st.markdown(f"{mark}**{a0}~{a0 + 9}세 · {STEM_K[s]}{BR_K[b]} 대운 ({ten(dm, s)}운)**  \n"
                        f"{TEN_DAE[ten(dm, s)]}")
        st.caption("대운의 천간 십성을 기준으로 한 간이 풀이입니다.")

    when = r["when"]
    txt = share_text(r, name, when)
    st.subheader("공유")
    st.code(txt, language=None)  # 오른쪽 위 복사 버튼 → 카톡 등에 붙여넣기
    st.download_button("텍스트 파일로 저장", txt, file_name="saju.txt")

    st.subheader("AI에게 더 자세히 풀이받기")
    q = ai_prompt(r)
    st.code(q, language=None)  # 오른쪽 위 복사 버튼
    enc = urllib.parse.quote(q)
    b1, b2, b3 = st.columns(3)
    b1.link_button("ChatGPT로 바로 보내기", f"https://chatgpt.com/?q={enc}")
    b2.link_button("Claude로 보내기", f"https://claude.ai/new?q={enc}")
    b3.link_button("Gemini 열기", "https://gemini.google.com/app")
    st.caption("위 문장을 복사한 뒤 사용하는 AI 앱에 붙여넣어도 됩니다. Gemini는 열린 뒤 붙여넣기만 하면 되고, "
               "ChatGPT·Claude 버튼은 입력칸에 문장이 비어 있으면 같은 방식으로 붙여넣으세요. "
               "이름과 생년월일은 포함되지 않고 사주 글자만 전달됩니다.")
    if SAVE and st.button("이 사주 저장"):
        recs = load_recs()
        recs.append(dict(n=name or "이름없음", d=r["solar"].isoformat(), h=r["h"], m=r["mi"], g=r["g"], a=r["adj"]))
        json.dump(recs, open(FILE, "w", encoding="utf-8"), ensure_ascii=False)
        st.success("저장했습니다")
    st.caption("※ 절기는 태양 황경 계산으로 구했으며 수 분 내외의 오차가 있을 수 있습니다. "
               "풀이는 일반적인 해설로, 재미와 참고용으로 봐주세요.")

# 화면 오른쪽 하단 제작자 표기
st.markdown(
    "<div style='text-align:right; font-size:12px; color:#7a6a4f;'>"
    "Made by 강현. 2026.11.20</div>",
    unsafe_allow_html=True,
)
