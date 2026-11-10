from pathlib import Path
from xml.sax.saxutils import escape
import json
import re
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
from PIL import Image, ImageOps
from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[3]
WORK = ROOT / 'tmp/pdfs/kmong-227330'
OUT = ROOT / 'output/pdf/kmong-227330-proposal-v1.pdf'
PROPOSALS = ROOT / 'output/proposals'
OUT.parent.mkdir(parents=True, exist_ok=True)
PROPOSALS.mkdir(parents=True, exist_ok=True)

FONT_DIR = ROOT / 'tmp/pdfs/design-review/fonts'
for name, weight in [('KR', 'Regular'), ('KRM', 'Medium'), ('KRS', 'SemiBold'), ('KRB', 'Bold')]:
    pdfmetrics.registerFont(TTFont(name, str(FONT_DIR / f'Pretendard-{weight}.ttf')))

W, H = landscape(A4)
M = 36
CW = W - 2 * M
BG = colors.HexColor('#F5F3EE')
INK = colors.HexColor('#192D36')
MUTED = colors.HexColor('#52666E')
TEAL = colors.HexColor('#087A78')
LIGHT = colors.HexColor('#E3EFEB')
LINE = colors.HexColor('#D6DEDA')
WHITE = colors.white
c = canvas.Canvas(str(OUT), pagesize=(W, H), pageCompression=1)
c.setTitle('프리캐스트 건물 조립 3D 애니메이션 제작 제안 | 초안 v1')
c.setAuthor('주식회사 김치스탄스튜디오')
c.setSubject('크몽 프로젝트 227330 제안 초안 / 2026.11.07')
LAYOUT = []


def txt(x, y, s, size=10, color=INK, font='KR'):
    c.setFont(font, size)
    c.setFillColor(color)
    c.drawString(x, y, s)


def para(x, top, s, width, size=10, leading=15, color=INK, font='KR', max_h=None):
    p = Paragraph(s, ParagraphStyle(
        'copy', fontName=font, fontSize=size, leading=leading,
        textColor=color, wordWrap='CJK', splitLongWords=False,
    ))
    _, h = p.wrap(width, 1000)
    if max_h is not None:
        assert h <= max_h, (s, h, max_h)
    assert top - h >= 38, (s, top - h)
    p.drawOn(c, x, top - h)
    LAYOUT.append({'page': c.getPageNumber(), 'text': re.sub('<[^>]+>', '', s), 'bottom': top-h, 'height': h})
    return h


def rect(x, y, w, h, fill=WHITE, radius=0, stroke=None):
    c.setFillColor(fill)
    c.setStrokeColor(stroke or fill)
    if radius:
        c.roundRect(x, y, w, h, radius, fill=1, stroke=bool(stroke))
    else:
        c.rect(x, y, w, h, fill=1, stroke=bool(stroke))


def image(path, x, y, w, h, fit='contain', background=None):
    p = Path(path)
    if not p.is_absolute():
        p = ROOT / p
    im = Image.open(p).convert('RGB')
    if background:
        rect(x, y, w, h, colors.HexColor(background))
    if fit == 'cover':
        im = ImageOps.fit(im, (round(w*3), round(h*3)), Image.Resampling.LANCZOS)
        c.drawImage(ImageReader(im), x, y, width=w, height=h)
    else:
        scale = min(w / im.width, h / im.height)
        iw, ih = im.width * scale, im.height * scale
        c.drawImage(ImageReader(im), x+(w-iw)/2, y+(h-ih)/2, width=iw, height=ih)


def base(page, section):
    rect(0, 0, W, H, BG)
    txt(M, H-28, 'KIMCHISTAN STUDIO', 9, INK, 'KRB')
    txt(W-237, H-28, '제안 초안 v1  /  2026.11.07', 8, MUTED)
    txt(M, H-59, section, 8.5, TEAL, 'KRS')
    c.setStrokeColor(LINE)
    c.setLineWidth(.6)
    c.line(M, 29, W-M, 29)
    txt(M, 16, '프리캐스트 건물 조립 3D 애니메이션 제작 제안  |  주식회사 김치스탄스튜디오', 7, MUTED)
    txt(W-M-17, 16, f'{page:02d}', 8, MUTED, 'KRS')


def heading(s, sub=None):
    txt(M, H-94, s, 24, INK, 'KRB')
    if sub:
        para(M, H-111, sub, CW, 10, 15, MUTED, max_h=32)


def label(x, y, num, title):
    txt(x, y, num, 9, TEAL, 'KRB')
    txt(x+25, y, title, 11, INK, 'KRS')


# 1: solution and direct proof
base(1, '01 / 제작 방향')
txt(M, 496, '프리캐스트 건물 조립', 27, INK, 'KRB')
txt(M, 460, '3D 애니메이션 제작 제안', 27, INK, 'KRB')
para(M, 437, '완성 구조에서 접합부까지, 조립 흐름이 보이는 3분 30초를 제안합니다.', CW, 11, 16, MUTED)
image(WORK/'precast-overview.png', M, 131, 470, 264.375)
txt(M, 116, '본 제안을 위해 제작한 30초 배치 개념 샘플의 실제 화면', 8, MUTED)
x = 531
txt(x, 384, '발주처 제공 모델을 바탕으로', 15, INK, 'KRB')
txt(x, 362, '조립 순서를 읽기 쉽게.', 15, INK, 'KRB')
para(x, 340, '전체 배치와 부재 이동을 연결하고, 설명이 필요한 받침부·접합부는 가까이 보여드립니다.', 272, 11, 17, max_h=60)
for yy, a, b in [(267, '3-4분', '한국어 자막 중심'), (222, '4K + 1080p', 'MP4 · 썸네일 · 편집 원본'), (177, '2026.11.30', '최종 납품 목표')]:
    txt(x, yy, a, 15, TEAL, 'KRB')
    txt(x, yy-16, b, 9, MUTED)
rect(M, 53, CW, 44, LIGHT, 6)
txt(M+15, 70, '전체 관계  →  부재 이동  →  접점 확대  →  전체 회수', 12, TEAL, 'KRS')
txt(W-280, 70, '실제 공정은 발주처 승인 자료 기준', 9, MUTED)
c.showPage()


# 2: task-specific sample and its precise limits
base(2, '02 / 과업 맞춤 샘플')
heading('먼저, 이번 과업을 위한 샘플입니다.', '30초 영상으로 카메라 구성, 부재 이동, 받침부 안착과 자막 표현을 확인하실 수 있습니다.')
gap = 14
cardw = (CW-2*gap)/3
for i, (asset, title, body) in enumerate([
    ('precast-columns.png', '01  기둥과 임시 지지', '부재의 위치 변화와 임시 지지 상태를 함께 표현'),
    ('precast-bearing.png', '02  받침부 확대', '보와 받침 패드의 관계를 가까운 시점으로 설명'),
    ('precast-slabs.png', '03  슬래브 배치', '반복 부재의 순차 배치와 전체 구조의 관계 제시'),
]):
    xx = M+i*(cardw+gap)
    image(WORK/asset, xx, 287, cardw, cardw*9/16)
    txt(xx, 266, title, 11, INK, 'KRS')
    para(xx, 254, body, cardw, 9.5, 14, MUTED, max_h=35)
rect(M, 82, CW, 123, WHITE, 6)
label(M+15, 184, 'A', '현재 샘플에서 확인한 것')
para(M+15, 170, '지지부와 받침면의 접점, 기둥 이동 시 부속품의 동반 이동, 마지막 장면의 임시 지지 유지, 생략 공정을 알리는 자막을 점검·반영했습니다.', 347, 10, 15, max_h=65)
label(430, 184, 'B', '본편 제작 시 구체화할 것')
para(430, 170, '실제 기초·기둥·보·슬래브 구성과 접합·그라우팅·지지 해체 단계는 제공 모델과 승인 도면, 시공 순서에 맞춰 확정합니다.', 354, 10, 15, max_h=65)
txt(M, 57, '샘플: 3840×2160 / 1920×1080 · 30fps · 30초 · 무음  |  일반화한 배치 개념 예시이며 구조 검토 범위는 포함하지 않습니다.', 8, MUTED)
c.showPage()


# 3: Orbit Foundry 3D, using only supplied current remaster evidence
base(3, '03 / 관련 3D 작업 ①')
heading('Orbit Foundry - 3D 개발 버전', '자체 게임의 실제 개발 화면으로, 기계형 오브젝트의 형상·재질과 다양한 관찰 시점을 보여드립니다.')
image('remaster/evidence/flight-inspection.png', M, 189, 452, 254.25)
image('remaster/evidence/drone-readable.png', 506, 296, 299.89, 168.69)
image('remaster/evidence/connector-detail.png', 506, 115, 299.89, 168.69)
txt(M, 174, '외장 패널·체결 요소·기체 전체 형태', 8, MUTED)
for xx, title, body in [
    (M, '형상과 재질', '패널, 볼트, 배관과 금속 표면의 차이를 표현했습니다.'),
    (274, '부품과 공간', '설비 내부를 볼 수 있는 시점과 외부 근접 구도를 구성했습니다.'),
]:
    txt(xx, 141, title, 11, TEAL, 'KRS')
    para(xx, 128, body, 215, 10, 15, max_h=45)
txt(506, 96, '설비 내부와 커넥터 근접 화면', 8, MUTED)
para(M, 64, '본 과업에서는 이 제작 경험을 부재 식별, 접합부 가독성, 전체-상세 시점 전환에 적용하겠습니다.', CW, 10, 15, TEAL, 'KRS', max_h=20)
c.showPage()


# 4: complementary 3D portfolios
base(4, '04 / 관련 3D 작업 ②')
heading('공간 구성부터 개별 소품까지.', '실내 공간 구현과 3D 자산 제작 경험을 함께 제시합니다.')
col = (CW-22)/2
image('assets/games/korean-kindergarten-cover.webp', M, 259, col, 210, background='#E3E9E4')
image('assets/games/daycare-props-cover.webp', M+col+22, 259, col, 210, background='#14201E')
for xx, title, line, body, apply in [
    (M, 'Korean Kindergarten', '1인칭 어린이집 3D 시뮬레이션', '실내 공간, 조명과 생활 소품을 구성하고, 소품을 집거나 배치하는 상호작용을 구현했습니다.', '본 과업 적용: 공간 관계를 읽기 쉬운 시점과 빛으로 구성'),
    (M+col+22, 'Daycare & Everyday Interiors', '360개 3D 소품 · GLB + Blender · CC0', '가구·장난감·생활용품을 제작하고 편집 가능한 Blender 파일과 GLB 형식으로 배포했습니다.', '본 과업 적용: 부재별 자산 정리와 편집 가능한 원본 인계'),
]:
    txt(xx, 234, title, 17, INK, 'KRB')
    txt(xx, 214, line, 10, TEAL, 'KRS')
    para(xx, 195, body, col-8, 11, 16, max_h=55)
    para(xx, 120, apply, col-8, 9.5, 15, TEAL, 'KRS', max_h=35)
txt(M, 57, '회사소개서에 수록된 자체 3D 프로젝트를 과업 관련 역량 중심으로 발췌했습니다.', 8, MUTED)
c.showPage()


# 5: proposed 3m30s script, explicitly conditional on the supplied actual system
base(5, '05 / 본편 구성안')
heading('3분 30초의 설명 흐름', '아래 순서는 제안용 예시입니다. 실제 부재 구성과 공정 순서는 발주처 자료 확인 후 확정합니다.')
table_top = 445
rect(M, table_top-28, CW, 28, INK)
for xx, ss in [(M+12,'구간'), (M+128,'설명 주제'), (M+330,'화면 구성')]:
    txt(xx, table_top-18, ss, 10, WHITE, 'KRS')
rows = [
    ('00:00-00:20', '완성 구조와 설명 범위', '전체 구조 회전 또는 천천히 이동하는 시점으로 대상 소개'),
    ('00:20-00:45', '부재 종류와 위치', '주요 부재를 색·명칭으로 구분하고 조립 전 위치 관계 설명'),
    ('00:45-01:25', '기둥 배치와 지지', '이동·정렬·안착을 단계로 나누고 기초 접합과 임시 지지 설명'),
    ('01:25-02:10', '보 배치와 접합부', '전체 이동 장면에서 받침부·접합 상세로 전환'),
    ('02:10-02:55', '슬래브와 이음부', '순차 배치 후 승인된 이음·그라우팅 공정 표현'),
    ('02:55-03:30', '최종 상태와 핵심 정리', '승인된 단계의 전체 상태와 주요 공정 요약'),
]
for i, (time, subject, shot) in enumerate(rows):
    yy = table_top-28-(i+1)*44
    rect(M, yy, CW, 44, WHITE if i%2==0 else colors.HexColor('#ECF0EB'))
    txt(M+12, yy+17, time, 10, TEAL, 'KRS')
    txt(M+128, yy+17, subject, 10.5, INK, 'KRS')
    para(M+330, yy+34, shot, CW-346, 10, 15, max_h=32)
rect(M, 67, CW, 61, LIGHT, 6)
para(M+15, 115, '공정명과 핵심 메시지 중심의 자막, 필요한 구간의 화살표·강조 표시로 설명을 보완합니다.<br/>접합·양생·임시 지지 해체는 발주처가 승인한 자료와 순서에 맞춰 표현합니다.', CW-30, 10, 16, TEAL, max_h=40)
c.showPage()


# 6: concrete scope, delivery dates, a proposed price rather than an assumed tender VAT rule
base(6, '06 / 제작 범위와 일정')
heading('검토 시점을 먼저 정하고, 납기를 관리합니다.', '착수 시 모델·도면을 수령하고, 단계별 검토일에 일괄 의견을 받는 기준으로 구성한 초안입니다.')
leftw = 424
txt(M, 439, '2026.11.10 착수 → 11.30 최종 납품', 13, INK, 'KRB')
schedule = [
    ('11.10-11.12', '모델 반입·축척·부재 분리 상태 확인'),
    ('11.13-11.16', '콘티·카메라·저해상도 동작안 검토'),
    ('11.17-11.22', '애니메이션 제작·1080p 초안 검토'),
    ('11.23-11.25', '접합 표현·자막 수정, 장면 내용 확정'),
    ('11.26-11.28', '4K 렌더링·편집·파일 재생 확인'),
    ('11.29', '최종 오류 점검 및 재출력 예비일'),
    ('11.30', '영상·썸네일·원본 파일 납품'),
]
for i, (date, desc) in enumerate(schedule):
    y = 410-i*29
    txt(M, y, date, 10, TEAL, 'KRS')
    txt(M+100, y, desc, 10, INK)
rect(M, 75, leftw, 113, WHITE, 6)
txt(M+14, 167, '포함 범위 및 수정 기준', 11, INK, 'KRS')
para(M+14, 153, '제공 모델의 장면 정리, 애니메이션, 렌더링, CG·편집, 한국어 자막을 포함합니다. 수정은 콘티 1회·본편 1회의 일괄 의견 기준으로 제안하며, 제작 오류는 별도로 바로잡습니다.', leftw-28, 10, 15, max_h=65)
x = 487
rightw = W-M-x
rect(x, 330, rightw, 128, INK, 6)
txt(x+17, 435, '제안 금액 · 초안', 10, colors.HexColor('#C5E4DE'), 'KRS')
txt(x+17, 397, '7,000,000원', 28, WHITE, 'KRB')
txt(x+17, 373, 'VAT 포함 기준 · 제공 모델 활용', 10, WHITE)
txt(x+17, 351, '세금계산서 및 산출물 목록 제공', 9, colors.HexColor('#C5E4DE'))
txt(x, 310, '납품물 / 원본 파일 제공 가능', 12, TEAL, 'KRB')
deliver = [
    '3-4분 메인 영상: 4K MP4 (16:9)',
    '동일 본편: 1080p MP4 (16:9)',
    '썸네일: PNG 1종',
    '편집 가능한 Blender 프로젝트',
    '사용 자산·자막·편집 구성 및 파일 목록',
]
for i, s in enumerate(deliver):
    txt(x, 286-i*20, '• '+s, 10)
para(x, 167, '고객 제공 모델은 인계 범위에 맞춰 포함하며, 외부 자산 사용 시 라이선스와 원본 제공 범위를 함께 정리합니다.', rightw, 9, 13, MUTED, max_h=42)
para(x, 109, '신규 상세 모델링·구조 검토·성우 녹음·번역·현장 촬영은 별도 협의 항목입니다.', rightw, 9, 13, MUTED, max_h=32)
txt(M, 50, '초안 협의 사항: 모델 형식·상태, 실제 공정·접합 도면, 검토 담당자·회신일, 음향 요구를 착수 전에 확정합니다.', 8, MUTED)
c.showPage()
c.save()


submission = '''프리캐스트 건물 조립 3D 애니메이션 제작 제안

안녕하세요. 게임과 3D 콘텐츠를 제작하는 주식회사 김치스탄스튜디오입니다.

제공하시는 3D 모델을 바탕으로 프리캐스트 건물의 조립 과정을 3~4분 영상으로 제작하는 방안을 제안드립니다. 전체 구조에서 부재 이동, 받침부·접합부 확대, 전체 상태 확인으로 이어지는 흐름을 구성하고 한국어 자막과 필요한 강조 그래픽으로 이해를 돕겠습니다.

이번 과업을 위해 기둥·보·슬래브의 배치 과정을 표현한 30초 샘플을 제작했습니다. 지지부와 받침면의 접점, 임시 지지 유지, 생략 공정 안내 자막을 점검·반영했습니다. 샘플은 일반화한 배치 개념 예시이며, 본편은 실제 제공 모델과 승인 도면·공정 순서에 따라 구체화하겠습니다.

관련 3D 제작 역량은 자체 게임 Orbit Foundry의 3D 개발 화면으로 함께 제시합니다. 기계형 오브젝트의 패널·체결 요소·배관·금속 재질과 전체/근접 시점을 확인하실 수 있습니다. 실내 공간과 상호작용을 구현한 Korean Kindergarten, Blender·GLB 형식으로 배포한 360개 3D 소품 작업도 제안서에 담았습니다.

[제작 범위]
제공 모델 확인 및 장면 정리, 애니메이션, 렌더링, CG·편집, 한국어 자막.
신규 상세 모델링·구조 검토·성우 녹음·번역·현장 촬영은 별도 협의합니다.

[일정]
2026.11.10 착수, 2026.11.30 최종 납품을 기준으로 제안합니다.
11.16 콘티·동작안 검토 → 11.22 본편 초안 검토 → 11.25 장면 내용 확정 → 11.26~28 4K 렌더링 및 검수 → 11.29 최종 점검 → 11.30 납품.
착수 시 모델·도면 수령과 각 검토일의 일괄 회신을 기준으로 하며, 세부 일정은 착수 전 확정하겠습니다.

[납품물 / 원본 제공 가능]
- 3~4분 4K MP4 메인 영상
- 동일 본편 1080p MP4 (16:9)
- PNG 썸네일 1종
- 편집 가능한 Blender 프로젝트와 사용 자산·자막·편집 구성, 파일 목록
고객 제공 모델 및 외부 자산은 사용·인계 권한에 맞춰 포함합니다.

[제안 금액]
7,000,000원, VAT 포함 기준의 초안입니다. 제공 모델 활용 및 위 제작 범위를 기준으로 하며, 모델 상태와 확정 콘티를 확인한 후 견적을 확정하겠습니다. 수정은 콘티 1회·본편 1회의 일괄 의견 기준으로 제안하며, 제작 오류는 별도로 바로잡습니다. 세금계산서와 산출물 목록을 제공합니다.

첨부한 맞춤 샘플과 3D 작업 사례를 통해 화면 구성과 표현 수준을 검토해 주시면 감사하겠습니다.
'''
(PROPOSALS/'kmong-227330-submission-v1.txt').write_text(submission, encoding='utf-8')

notes = '''크몽 227330 제안 초안 - 내부 검토 메모 (제출용 아님)
작성일: 2026-11-07

추천 포지셔닝
"제공 모델과 승인 공정 자료를 이해하기 쉬운 3D 설명 영상으로 만드는 게임·3D 제작 스튜디오".
과업 맞춤 프리캐스트 샘플을 첫 번째 증거로, Orbit Foundry의 3D 개발 버전을 두 번째 증거로 제시한다.

권장 제출 순서
1. kmong-227330-submission-v1.txt를 검토·조정한 제안 본문
2. kmong-227330-proposal-v1.pdf (6페이지)
3. precast-assembly-30s-1080p.mp4 (30초 / 맞춤 샘플 v2)
4. Orbit Foundry 3D 소개 영상 (추가 편집 권장, 아래 구성)
4K 맞춤 샘플은 요청 시 추가 제공한다. 소스 ZIP은 요청 또는 선정 후 전달용으로 보관한다.

Orbit Foundry 소개 방식
remaster에는 evidence 이미지와 preview.mp4가 있으며 소스 프로젝트는 없다.
preview.mp4는 1920x1080, 30fps, 38초이고 게임 UI가 상당 부분 보인다.
현재 클립은 개발 상태를 확인하는 보조 자료로 활용할 수 있다. 별도 20~25초 소개 편집을 권장한다.
권장 구성: 전체 배치 3초 → 기체 전체·금속 패널 6초 → 커넥터 4초 → 설비 내부 6초 → 전체/측면 마무리 4초.
도입/마무리 외 구간은 UI가 적은 실제 개발 화면을 사용하고, 화면 전환은 단정하게 구성한다.
제안서에는 flight-inspection.png, drone-readable.png, connector-detail.png를 우선 사용했다.
추가 후보: refinery-readable.png, solar-readable-side.png, extractor-readable-side.png.
위 이미지 기반 장면 구성안은 아직 새 영상으로 제작하지 않았다. 정지 이미지를 움직인 영상은 실시간 조작 녹화와 구별해서 표기해야 한다.
포트폴리오 명칭은 "Orbit Foundry - 3D 개발 버전"으로 유지한다.
기존 공개 2D 프로토타입 또는 Steam 자료가 이 3D 버전과 동일하다고 설명하지 않는다.
소스가 없으므로 이 3D 버전의 엔진·툴체인·성능 수치·출시 상태는 추가 확인 없이 기재하지 않는다.
건축 납품 실적이나 구조·시공 전문 검토 이력으로 표현하지 않는다.

다른 3D 작업
Korean Kindergarten: 실내 공간, 조명, 소품과 상호작용.
Daycare & Everyday Interiors: 360개 소품, GLB 및 편집 가능한 Blender 형식.
두 사례는 회사소개서와 보유 이미지에서 관련 내용만 발췌했다.

금액·범위 가정
공고 예산은 7,000,000원. VAT 포함 여부를 단정하지 않고, 제안 금액 자체를 VAT 포함 7,000,000원 기준으로 작성했다.
이는 검토용 견적 제안이며 사용자 확정 전 자동 제출하지 않는다.
고객이 본편용 3D 모델을 제공한다는 전제. 실제 모델 반입/변환·부재 분리·누락 상세 보완량은 미확정이다.
1개 본편과 해상도별 2종 출력이며 1080p는 동일 16:9 영상이다. 세로 SNS 재편집은 포함하지 않았다.
기본은 한국어 자막이며 성우·번역은 별도 협의. 음향 필요 여부는 미확정이다.
수정은 콘티 1회·본편 1회의 일괄 의견으로 제안했으며 제작 오류의 시정은 별도이다.
11.10 자료 수령, 11.16/11.22 일괄 검토, 11.25 장면 내용 확정 전제. 11.29 최종 점검 예비일 확보.

제출 전 확정할 항목
모델 형식·용량·부재 분리·좌표·축척, 공정 순서·접합 상세·임시 지지 해체 기준, 검토 담당자와 회신일, 음향 요구, 최종 금액과 수정 범위.
정부지원사업/연구과제로 표시되어 있으므로 정산 산출물·세금계산서의 지정 양식이 있는지 확인한다.

자료 취급
공고에 외부 연락처 기재 금지 안내가 있다. 기존 회사소개서 1페이지에는 이메일·전화·웹사이트·주소가 있으므로 원본을 그대로 첨부하지 않는다.
이번 제안 PDF와 제출 본문에는 이메일·전화·웹사이트·주소·외부 연락 링크를 넣지 않았다.
프리캐스트 샘플의 배치 개념 및 접합/그라우팅 생략 고지는 유지한다.
아키텍처 검토 에이전트의 검토를 건축사·구조기술사의 공식 검토로 기재하지 않는다.

출처
공고: https://kmong.com/enterprise/requests/227330 (2026-11-07 공개 페이지 본문 확인)
3D 개발 화면: remaster/evidence/
회사 보유 작업: output/pdf/kimchistan-studio-company-introduction.pdf 및 assets/games/
맞춤 샘플: output/prototypes/kmong-227330-v2/
'''
(PROPOSALS/'kmong-227330-showcase-notes-v1.txt').write_text(notes, encoding='utf-8')

reader = PdfReader(OUT)
assert len(reader.pages) == 6
all_text = '\n'.join(p.extract_text() for p in reader.pages)
for term in ['Orbit Foundry', '3D 개발 버전', '360개', 'Korean Kindergarten', '7,000,000원', '11.30', '원본 파일 제공 가능', 'VAT 포함']:
    assert term in all_text, term
for contact in ['kimmchistan@gmail.com', '031-911-8190', 'https://', 'kimchistan.kr', '경기도', '@']:
    assert contact not in all_text, contact
    assert contact not in submission, contact
assert sum([20,25,40,45,45,35]) == 210
annotations = sum(len(p.get('/Annots', [])) for p in reader.pages)
assert annotations == 0
qa = {'pdf': str(OUT), 'pages':len(reader.pages), 'bytes':OUT.stat().st_size, 'contact_check':'passed', 'external_links':annotations, 'proposed_duration_seconds':210, 'layout_checks':len(LAYOUT), 'visual_review':'pending'}
(WORK/'layout.json').write_text(json.dumps(LAYOUT, ensure_ascii=False, indent=2))
(WORK/'qa.json').write_text(json.dumps(qa, ensure_ascii=False, indent=2))
print(json.dumps(qa, ensure_ascii=False, indent=2))
