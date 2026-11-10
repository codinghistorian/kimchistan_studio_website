from __future__ import annotations

import hashlib
import json
import re
import shutil
from datetime import date
from pathlib import Path
from xml.sax.saxutils import escape

import pdfplumber
from PIL import Image
from pypdf import PdfReader
from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph


ROOT = Path(__file__).resolve().parents[3]
WORK = ROOT / 'tmp/pdfs/kmong-227326'
OUT = ROOT / 'output/pdf/kmong-227326-proposal.pdf'
ATTACHMENT = ROOT / 'output/pdf/고깃집홈페이지-예약포장주문시스템-제안서.pdf'
MESSAGE = ROOT / 'output/proposals/kmong-227326-submission.txt'
FONTS = ROOT / 'tmp/pdfs/design-review/fonts'
WORK.mkdir(parents=True, exist_ok=True)
OUT.parent.mkdir(parents=True, exist_ok=True)

PRESERVED = {
    'output/pdf/kimchistan-studio-company-introduction.pdf':
        '76758b55ba6986dc396eb697f6494cd21d92a7b5ed5aab01b327f2a2dcff567e',
    'output/pdf/kmong-227317-proposal.pdf':
        '77a6be9893f3d0f173ab6a7d23d6a2f521f429f4b07ffd9438cc9a90b1967a98',
    'output/proposals/kmong-227317-submission.txt':
        'd97af6c8c397982386c7552e9f28b68eaa46d38b9dac57789c8db984c8f8d12a',
}
for path, expected in PRESERVED.items():
    assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == expected, path

for name in ['Regular', 'Medium', 'SemiBold', 'Bold']:
    pdfmetrics.registerFont(TTFont(name, str(FONTS / f'Pretendard-{name}.ttf')))
for name in ['Regular', 'Medium', 'SemiBold']:
    pdfmetrics.registerFontFamily(name, normal=name, bold='Bold', italic=name, boldItalic='Bold')

# This is a literal crop of a browser screenshot. Only this cropped pixel region is
# embedded, so browser chrome, contact navigation and source URLs are absent even
# from the PDF image stream. No generative image transformation is used.
source_image = WORK / 'john-songbook-source.png'
with Image.open(source_image) as image:
    assert image.size == (2296, 1486)
    evidence_crop = (65, 431, 2231, 1423)
    image.crop(evidence_crop).convert('RGB').save(WORK / 'john-songbook-evidence.png')

W, H = A4
M = 43
CW = W - M * 2
BOTTOM = 61
BG = HexColor('#F7F5F0')
INK = HexColor('#18352F')
TEXT = HexColor('#263C37')
MUTED = HexColor('#586D65')
ACCENT = HexColor('#CB4828')
LINE = HexColor('#CCD6CE')
PALE = HexColor('#E9EEE7')
LIGHT = HexColor('#D6E6DD')
CREAM = HexColor('#F3DDD1')
PAGE = 0
DRAWN: list[dict] = []

c = canvas.Canvas(str(OUT), pagesize=A4, pageCompression=1)
c.setTitle('고깃집 홈페이지 및 예약·포장 주문 시스템 구축 제안서')
c.setAuthor('주식회사 김치스탄스튜디오')
c.setSubject('두 매장 반응형 홈페이지·단체 예약·포장 주문·알림톡 및 향후 온라인 결제 확장')
c.setCreator('KIMCHISTAN STUDIO')
c._doc.info.producer = 'ReportLab'
c.setKeywords('반응형 홈페이지, 단체 예약, 포장 주문, 알림톡, PG 확장')


def text(x, top, value, size=10.2, color=TEXT, font='Regular'):
    width = pdfmetrics.stringWidth(value, font, size)
    assert x >= M - .2 and x + width <= W - M + .6, (PAGE, 'text width', value, x + width)
    assert top >= 19 and top + size < H - 20, (PAGE, 'text vertical', value, top)
    c.setFillColor(color)
    c.setFont(font, size)
    c.drawString(x, H - top - size * .82, value)
    DRAWN.append({'page': PAGE, 'kind': 'text', 'x': x, 'top': top,
                  'bottom': top + size, 'text': value})


def label(x, top, value, size=8.1, color=ACCENT):
    text(x, top, value, size, color, 'SemiBold')


def measured(value, width, size=10.2, leading=15.7, color=TEXT, font='Regular'):
    style = ParagraphStyle('body', fontName=font, fontSize=size, leading=leading,
                           textColor=color, wordWrap=None, splitLongWords=False,
                           spaceBefore=0, spaceAfter=0, allowWidows=0, allowOrphans=0)
    p = Paragraph(value, style)
    _, height = p.wrap(width, H)
    for line in p.blPara.lines:
        if isinstance(line, tuple):
            assert line[0] >= -.7, (PAGE, 'unbreakable paragraph', value, width)
    return p, height


def para(x, top, value, width=CW, size=10.2, leading=15.7, color=TEXT, font='Regular'):
    p, height = measured(value, width, size, leading, color, font)
    assert x >= M - .2 and x + width <= W - M + .2
    assert top + height <= H - BOTTOM + .2, (PAGE, 'paragraph bottom', top + height, value[:120])
    p.drawOn(c, x, H - top - height)
    DRAWN.append({'page': PAGE, 'kind': 'paragraph', 'x': x, 'top': top,
                  'bottom': top + height, 'text': re.sub('<[^>]*>', '', value)})
    return top + height


def rule(top, x=M, width=CW, color=LINE):
    c.setStrokeColor(color)
    c.setLineWidth(.65)
    c.line(x, H - top, x + width, H - top)


def box(x, top, width, height, fill=PALE, stroke=None, radius=5):
    assert top + height <= H - BOTTOM + .2, (PAGE, 'box bottom', top + height)
    c.setFillColor(fill)
    c.setStrokeColor(stroke or fill)
    c.roundRect(x, H - top - height, width, height, radius, fill=1, stroke=int(stroke is not None))


def section(top, number, title):
    label(M, top + 3, number, 8.2)
    text(M + 29, top, title, 12.9, INK, 'Bold')
    return top + 27


def callout(top, title, body, fill=INK, size=10.2, leading=15.7):
    dark = fill == INK
    _, height = measured(body, CW - 32, size, leading, LIGHT if dark else TEXT)
    box(M, top, CW, height + 55, fill)
    text(M + 16, top + 14, title, 11.2, white if dark else INK, 'SemiBold')
    para(M + 16, top + 37, body, CW - 32, size, leading, LIGHT if dark else TEXT)
    return top + height + 55


def table(top, widths, headers, rows, size=9.8, leading=14.8, padding=15):
    assert abs(sum(widths) - CW) < .1
    box(M, top, CW, 28, INK)
    x = M
    for width, header in zip(widths, headers):
        text(x + 10, top + 9, header, 8.7, white, 'SemiBold')
        x += width
    y = top + 28
    for index, row in enumerate(rows):
        ps = [measured(cell, width - 20, size, leading) for cell, width in zip(row, widths)]
        height = max(h for _, h in ps) + padding
        assert y + height <= H - BOTTOM, (PAGE, 'table bottom', y + height)
        if index % 2 == 0:
            box(M, y, CW, height, white)
        x = M
        for cell, width in zip(row, widths):
            para(x + 10, y + padding / 2, cell, width - 20, size, leading)
            x += width
        rule(y + height)
        y += height
    return y


def page(number, name, title, subtitle):
    global PAGE
    PAGE = number
    c.setFillColor(BG)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    text(M, 24, 'KIMCHISTAN STUDIO', 10.2, INK, 'Bold')
    right = 'PROJECT 227326 / ' + name
    width = pdfmetrics.stringWidth(right, 'Medium', 7.4)
    text(W - M - width, 27, right, 7.4, MUTED, 'Medium')
    rule(47)
    label(M, 67, f'{number:02d} / {name}', 8)
    titles = title if isinstance(title, list) else [title]
    for index, title_line in enumerate(titles):
        text(M, 88 + index * 33, title_line, 25, INK, 'Bold')
    subtitle_top = 125 + (len(titles) - 1) * 33
    bottom = para(M, subtitle_top, subtitle, CW, 10.5, 16.4, MUTED)
    rule(H - 44)
    text(M, H - 32, '주식회사 김치스탄스튜디오  |  크몽 엔터프라이즈 제안', 7.3, MUTED)
    right = f'2026.11.06   /   {number:02d}'
    width = pdfmetrics.stringWidth(right, 'Medium', 7.3)
    text(W - M - width, H - 32, right, 7.3, MUTED, 'Medium')
    return bottom + 22


def step_cards(top, items, height=91, size=9.5):
    gap = 9
    width = (CW - gap * (len(items) - 1)) / len(items)
    for index, (title, body) in enumerate(items):
        x = M + index * (width + gap)
        box(x, top, width, height, white)
        label(x + 12, top + 11, f'0{index + 1}', 8)
        text(x + 12, top + 29, title, 11, INK, 'SemiBold')
        para(x + 12, top + 50, body, width - 24, size, 14.4, MUTED)
    return top + height


# PAGE 1 - Start with the operating problem and a reviewable commercial offer.
y = page(1, 'PROPOSAL', ['두 매장의 예약과 주문,', '한곳에서 관리합니다'],
         '고깃집 매장 반응형 홈페이지 및 예약·포장 주문 시스템 구축<br/>'
         '예약 누락·중복을 줄이고, 바쁜 직원의 전화 응대와 가격 수정 부담을 덜겠습니다.')
y = callout(y, '고객은 간편하게 접수하고, 직원은 오늘 할 일을 확인합니다',
            '매장 선택부터 단체 예약·포장 주문까지 연결합니다. 두 매장의 데이터와 권한은 구분하고, '
            '직원은 휴대폰에서 예약 달력·주문 상태·메뉴 가격을 관리합니다.') + 19
gap = 10
card_w = (CW - gap * 2) / 3
for index, (caption, amount, detail, fill) in enumerate([
    ('기본 홈페이지·단체 예약', '800만원', '두 매장 / 모바일 관리자 포함', white),
    ('포장 주문 선택 옵션', '+200만원', '픽업 관리·준비 완료 알림', white),
    ('전체 선택 시', '1,000만원', 'VAT 포함 / 세금계산서 발행', CREAM),
]):
    x = M + index * (card_w + gap)
    box(x, y, card_w, 93, fill)
    label(x + 12, y + 12, caption, 8)
    text(x + 12, y + 34, amount, 22, INK, 'Bold')
    text(x + 12, y + 71, detail, 8.1, MUTED, 'Medium')
y += 111
box(M, y, CW, 52, PALE)
text(M + 14, y + 12, '구축 일정', 8.8, MUTED, 'Medium')
text(M + 14, y + 28, '2026.11.13 - 2026.12.20', 12.2, INK, 'Bold')
text(M + 290, y + 12, '수행 계획', 8.8, MUTED, 'Medium')
text(M + 290, y + 28, 'PM 겸 개발자 + 웹 전문 인력', 10.2, INK, 'SemiBold')
y += 73
y = section(y, '01', '이 프로젝트에서 바꿀 세 가지 업무')
for index, (title, body) in enumerate([
    ('단체 예약의 기준을 한곳으로', '룸·단체석·시간을 기준으로 확정하고, 전화·외부 예약도 같은 달력에 등록합니다.'),
    ('바쁜 시간의 포장 주문을 목록으로', '픽업 시간을 받아 접수·준비·수령 상태를 관리하고, 준비 완료를 알림톡으로 안내합니다.'),
    ('가격 변경을 직원의 손으로', '외주 요청을 기다리지 않고, 매장별 메뉴·가격·품절 상태를 휴대폰에서 수정합니다.'),
]):
    rule(y)
    label(M, y + 12, f'0{index + 1}', 8.8)
    text(M + 29, y + 10, title, 11, INK, 'SemiBold')
    y = para(M + 29, y + 29, body, CW - 29, 9.8, 14.8) + 11
para(M, y + 2, '제안 기준: 공통 플랫폼 1개·도메인 1개·매장 2개. 이번 오픈은 현장 결제 방식이며, '
     '향후 PG 실연동은 9페이지의 조건부 별도 예산입니다.', CW, 8.8, 13.2, MUTED)
c.showPage()


# PAGES 2-4 - Proposal-specific UI/UX concept, not completed client work.
def concept_image(top, filename):
    image_path = ROOT / 'tmp/pdfs/kmong-227326/concept-images' / filename
    with Image.open(image_path) as image:
        height = CW * image.height / image.width
    assert top + height < H - BOTTOM
    c.drawImage(str(image_path), M, H - top - height, width=CW, height=height)
    DRAWN.append({'page': PAGE, 'kind': 'concept_image', 'top': top,
                  'bottom': top + height, 'text': '제안용 가상 UI/UX 콘셉트'})
    return top + height


y = page(2, 'UI/UX CONCEPT', '두 매장에 맞춘 반응형 웹 경험',
         '고객의 매장 선택과 예약·포장 접수, 직원의 매장 관리를 연결한 디자인 방향입니다.<br/>'
         '홈페이지·태블릿·휴대폰에서 필요한 업무가 이어지는 모습을 제안합니다.')
label(M, y, '제안 단계 UI/UX 콘셉트 / 가상 매장·메뉴·가격·데이터 / 음식 사진: 무료 스톡', 8.1)
y = concept_image(y + 21, '01-responsive-overview.jpg') + 8
y = para(M, y, '음식 사진은 무료 스톡 촬영본입니다. 실제 매장 사진·브랜드·메뉴와 최종 화면은 착수 후 확정합니다.',
         CW, 8.5, 12.8, MUTED) + 16
y = section(y, '01', '공고의 운영 문제를 화면 설계에 연결합니다')
y = table(y, [115, CW - 115], ['운영 상황', '제안하는 화면 설계'], [
    ('두 매장 접수 구분', '고객이 매장을 먼저 선택하고 예약·주문 중에도 선택 매장을 확인합니다.<br/>직원은 해당 매장의 오늘 업무를 중심으로 처리합니다.'),
    ('고객·직원의 다른 목적', '고객에게는 예약·포장 접수를, 직원에게는 요청 확인·상태 변경을<br/>먼저 배치합니다. 메뉴·가격 수정은 직원이 직접 처리합니다.'),
], 9.6, 14.6, 12) + 13
para(M, y, '화면은 디자인 방향을 보여주는 예시이며, 실제 과업 범위는 견적과 운영 정책에 따릅니다. '
     '포장 주문은 선택 옵션, 이번 오픈의 결제 방식은 현장 결제입니다.', CW, 9.1, 13.9, MUTED)
c.showPage()


y = page(3, 'CUSTOMER EXPERIENCE', '고객의 예약·포장 접수 흐름',
         '첫 화면에서 단체 예약 또는 포장 주문을 선택하고, 필요한 정보만 입력합니다.<br/>'
         '세 화면은 시작 화면과 두 가지 접수 경로를 보여줍니다.')
label(M, y, '제안 단계 UI/UX 콘셉트 / 가상 화면·메뉴·가격·데이터 / 음식 사진: 무료 스톡', 8.1)
y = concept_image(y + 21, '02-customer-flows.jpg') + 8
y = para(M, y, '무료 스톡 촬영본을 사용했습니다. 메뉴·가격은 예시이며 실제 정보는 고객 제공 자료로 확정합니다.',
         CW, 8.5, 12.8, MUTED) + 16
y = section(y, '01', '고객이 접수 전에 확인할 정보')
y = table(y, [115, CW - 115], ['설계 포인트', '화면에 반영한 내용'], [
    ('매장 선택 유지', '예약·포장 화면 상단에 매장을 표시해 어느 매장에 접수하는지<br/>계속 확인할 수 있게 합니다.'),
    ('요청과 확정 구분', '날짜·시간·인원·공간 선택 후 예약을 요청합니다.<br/>직원 확인 후 확정되는 다음 단계를 안내합니다.'),
    ('픽업·금액·결제', '픽업 시간과 주문 금액을 확인하고 현장 결제 방식으로 접수합니다.<br/>주문 당시 금액을 보관하고, 준비 완료는 알림톡으로 안내합니다.'),
], 9.6, 14.6, 11) + 13
para(M, y, '회원가입 없는 접수를 기본으로 하고 개인정보 수집 동의와 안전한 확인 동선을 구성합니다. '
     '실제 휴대폰에서 입력·오류 안내·접수 상태를 검수합니다.', CW, 9.1, 13.9, MUTED)
c.showPage()


y = page(4, 'STAFF EXPERIENCE', '직원이 오늘 처리할 일을 먼저',
         '선택 매장의 예약 상태와 픽업 시간을 중심으로 업무를 정리합니다.<br/>'
         '예약 확정·포장 준비 완료·가격 수정을 휴대폰에서도 처리하도록 구성합니다.')
label(M, y, '제안 단계 UI/UX 콘셉트 / 예약·주문·메뉴·가격은 가상 데이터', 8.1)
y = concept_image(y + 21, '03-staff-operations.jpg') + 8
y = para(M, y, '직원용 웹 화면의 디자인 방향입니다. 매장별 직원 권한과 업무 정책은 착수 시 확정합니다.',
         CW, 8.5, 12.8, MUTED) + 16
y = section(y, '01', '직원의 실제 처리 순서에 맞춥니다')
y = table(y, [115, CW - 115], ['업무', '제안하는 처리 방식'], [
    ('예약 요청 확인', '매장·날짜별로 요청과 확정을 구분하고, 전화 예약도 같은 달력에<br/>등록합니다. 확정 단계에서 공간·시간을 재검증합니다.'),
    ('포장 준비 완료', '픽업 시간과 준비 상태를 함께 표시합니다.<br/>준비 완료 처리와 고객 알림톡을 연결합니다.'),
    ('메뉴·가격·마감', '메뉴 가격·품절·공간 마감을 직원이 직접 관리합니다.<br/>가격을 바꿔도 이미 접수한 주문의 금액은 유지합니다.'),
], 9.6, 14.6, 11) + 13
para(M, y, '사용성 검수에서는 두 매장 직원이 실제 휴대폰으로 예약 확정·상태 변경·가격 수정을 확인합니다. '
     '화면 시연과 피드백을 개발 중 주간 단위로 공유합니다.', CW, 9.1, 13.9, MUTED)
c.showPage()


# PAGE 5 - Capacity, channel operations and approved informational notifications.
y = page(5, 'BOOKING & NAVER', '단체석 재고의 기준을 한곳으로',
         '예약 요청과 확정을 구분하고, 공간·시간·정원으로 중복 확정을 방지합니다.<br/>'
         '네이버 병행 운영과 전화 예약까지 포함해 직원이 지킬 수 있는 운영 기준을 만듭니다.')
y = section(y, '01', '예약 확정에 필요한 세 가지 기준')
y = table(y, [110, CW - 110], ['관리 기준', '구현·운영 방식'], [
    ('공간·이용 시간', '매장별 룸/단체석 정원·이용 시간·휴무·차단을 설정합니다.<br/>동일 공간·시간의 예약이 겹치는지 확인합니다.'),
    ('확정 시 재검증', '직원이 확정할 때 서버에서 가용 공간을 다시 검사합니다.<br/>직원 두 명이 동시에 처리해도 중복 확정을 막습니다.'),
    ('같은 예약 달력', '전화·외부 예약도 수기 등록하고 변경·취소를 반영합니다.<br/>오픈 전 기존 확정 예약과 채널별 접수 설정을 대조합니다.'),
], 10, 15.1, 15) + 18
y = section(y, '02', '네이버는 검색 유입, 단체석은 재고 일원화 권장')
y = callout(y, '네이버 자동 동기화는 공식 연동 확인 후 별도 협의합니다',
            '네이버 플레이스의 유입은 유지하면서 단체룸·단체석 접수를 자체 홈페이지로 모으는 방향을 제안합니다. '
            '네이버 예약을 계속 받는다면 판매 재고를 분리하거나 직원이 즉시 등록·차단해야 합니다. '
            '같은 재고의 양방향 자동 동기화는 현재 계정의 공식 연동 자격과 지원 범위 확인 후 별도 협의합니다.',
            PALE, 9.9, 15.1) + 18
y = section(y, '03', '예약 상태와 연결되는 알림톡')
gap = 10
width = (CW - gap) / 2
for index, (title, body) in enumerate([
    ('예약 확정', '확정된 매장·시간·인원·공간 안내'),
    ('예약 변경', '변경 후 정보를 기준으로 안내'),
    ('방문 전날', '취소·변경된 예약을 재확인해 안내'),
    ('포장 준비 완료 / 옵션', '선택한 매장과 픽업 안내'),
]):
    x = M + (index % 2) * (width + gap)
    top = y + (index // 2) * 65
    box(x, top, width, 55, white)
    text(x + 12, top + 11, title, 10.1, INK, 'SemiBold')
    para(x + 12, top + 30, body, width - 24, 9.1, 13.5, MUTED)
y += 133
para(M, y, '알림 실패가 예약을 누락시키지 않도록 발송 처리를 분리하고, 중복 발송 방지·실패 기록·재처리를 구성합니다. '
     '비즈니스 채널 연결과 템플릿 승인을 일정 초기에 준비하며, 승인 일정은 외부 심사에 따릅니다.',
     CW, 9.3, 14.4, MUTED)
c.showPage()


# PAGE 6 - Transparent scope-based quote; platform costs and future PG are separate.
y = page(6, 'SCOPE & QUOTATION', '기본 800만원 + 포장 주문 200만원',
         '모든 개발비는 VAT 포함이며 세금계산서를 발행합니다.<br/>'
         '기본 홈페이지·단체 예약과 포장 주문 옵션을 구분해 선택하실 수 있습니다.')
y = table(y, [114, 284, CW - 398], ['항목', '포함 범위', 'VAT 포함'], [
    ('기획·디자인·홈페이지', '고객·직원 동선 설계, 두 매장 반응형 화면<br/>소개·사진·메뉴 안내·위치·주차', '<b>200만원</b>'),
    ('콘텐츠 관리', '매장별 메뉴·가격·사진·공지 수정<br/>품절 표시', '<b>120만원</b>'),
    ('단체 예약', '인원·시간·룸/단체석 선택, 직원 확정<br/>외부 예약 등록, 중복 확정 방지', '<b>200만원</b>'),
    ('모바일 관리자', '예약 달력·오늘 예약·마감·차단<br/>매장별 데이터·직원 권한', '<b>140만원</b>'),
    ('예약 알림톡', '확정·변경·전날 안내<br/>발송 이력·실패 확인', '<b>60만원</b>'),
    ('검수·배포·교육', '통합 검수, 오픈, 직원 사용 안내<br/>소스·운영 자료 인수인계', '<b>80만원</b>'),
    ('<b>기본 합계</b>', '<b>홈페이지 + 단체 예약 + 관리 기능</b>', '<b>800만원</b>'),
    ('<b>포장 주문 옵션</b>', '메뉴·수량·픽업 시간, 주문 상태 관리<br/>준비 완료 알림톡 / 현장 결제', '<b>+200만원</b>'),
    ('<b>전체 선택 시</b>', '<b>기본 + 포장 주문 옵션</b>', '<b>1,000만원</b>'),
], 9.6, 14.5, 13) + 19
y = section(y, '01', '견적의 전제와 추가 과업 처리')
y = para(M, y, '<b>공통 플랫폼 1개·도메인 1개·매장 2개</b>를 기준으로 합니다. 로고·사진·메뉴·가격·매장 정보는 '
         '고객 제공 자료를 활용하고, 화면 구성과 반응형 디자인은 포함합니다.', CW, 10, 15.3) + 10
y = para(M, y, '별도 촬영, 로고 신규 제작, 네이티브 앱, POS·배달 플랫폼 연동, 네이버 자동 동기화, 실제 PG 연동은 '
         '추가 협의 대상입니다. 신규 요구는 비용·일정 영향을 설명하고 사전 합의합니다.', CW, 9.7, 14.9, MUTED) + 12
para(M, y, '서버·도메인·알림톡 사용료는 8페이지에, 향후 PG 개발과 이용 비용은 9페이지에 구분했습니다. '
     '공고 기준 제안이며, 계약 시 운영 정책·화면·검수 기준을 문서로 확정합니다.', CW, 9.2, 14.1, MUTED)
c.showPage()


# PAGE 7 - Staffing is a plan, not a claim that a freelancer is already hired.
y = page(7, 'TEAM & SCHEDULE', '담당자와 결과물이 보이는 진행',
         'PM이 개발에도 직접 참여해 요구사항부터 인수인계까지 책임집니다.<br/>'
         '2026.11.13 착수, 2026.12.20 초기 안정화 완료를 기준으로 제안합니다.')
y = section(y, '01', '2인 수행 계획')
y = table(y, [142, CW - 142], ['역할', '책임'], [
    ('PM 겸 개발자 1명', '고객 소통, 정책·설계, 개발·API·DB 통합<br/>검수·배포·교육·인수인계 총괄'),
    ('웹 전문 프리랜서 1명', '계약 체결 후 합류 예정. 고객·관리자 화면 구현<br/>기능 연동·테스트·수정 분담'),
], 9.8, 14.7, 13) + 18
y = section(y, '02', '상세 일정과 단계별 확인')
y = table(y, [95, 258, CW - 353], ['기간', '주요 작업', '확인할 결과'], [
    ('11.13 - 11.17', '매장·공간·예약·취소·픽업 정책, 자료 수집<br/>화면 구성, 알림톡 채널·템플릿 준비', '운영 정책·화면 목록<br/>검수 기준'),
    ('11.18 - 11.24', '디자인 시안, 반응형 홈페이지<br/>메뉴·가격·사진·공지 관리', '고객 화면 시안<br/>관리자 시연'),
    ('11.25 - 12.02', '단체 예약·공간·마감·예약 달력<br/>수기 예약 등록과 동시 확정 방지', '예약 흐름 시연<br/>중복 처리 확인'),
    ('12.03 - 12.09', '포장 주문 옵션·픽업·상태 관리<br/>예약·포장 알림톡 통합', '주문·알림 시연<br/>실패 처리 확인'),
    ('12.10 - 12.16', '두 매장 직원 참여 검수·수정<br/>실제 휴대폰에서 주요 업무 점검', '검수 결과<br/>오픈 준비 확인'),
    ('12.17 - 12.20', '배포·운영 확인·직원 교육<br/>초기 안정화·인수인계', '소스·운영 문서<br/>인수 확인'),
], 9.4, 14.1, 12) + 17
y = para(M, y, '<b>소통</b>  크몽 메시지와 주 1회 시연·진행 보고로 완료 범위·다음 작업·확인할 이슈를 공유합니다. '
         'PM을 단일 소통 담당자로 두고 결정 사항·담당·상태를 기록합니다.', CW, 9.8, 15) + 9
y = para(M, y, '<b>기술 기준</b>  React·TypeScript / Django / PostgreSQL. HTTPS, 관리자 권한 구분, '
         '개인정보 접근 최소화와 백업·복구 확인을 포함합니다.', CW, 9.5, 14.5) + 9
para(M, y, '고객 측 검수 담당자와 자료·계정·피드백 일정을 착수 시 합의합니다. 자료나 외부 승인 지연 시 영향과 조정안을 공유합니다. '
     '포장 옵션을 선택하지 않으면 해당 기간에 기본 기능 검수·보완을 진행합니다.', CW, 8.9, 13.5, MUTED)
c.showPage()


# PAGE 8 - Usage charges are distinct from development and maintenance.
y = page(8, 'OPERATIONS & SUPPORT', '오픈 후 비용과 인수 범위까지',
         '개발비, 외부 서비스 사용료, 유지보수를 나누어 안내합니다.<br/>'
         '계정과 소스·운영 자료를 고객에게 인계해 이후 운영과 확장의 기반을 남깁니다.')
y = section(y, '01', '초기 규모의 운영 예산')
y = table(y, [112, 137, CW - 249], ['항목', '계획 예산', '산정·과금 기준'], [
    ('서버·DB·백업', '<b>월 6-10만원</b>', 'AWS Lightsail 앱 서버 + 암호화 지원 DB 기준<br/>저장·백업·환율·사용량에 따라 변동'),
    ('도메인 1개', '<b>연 2-4만원</b>', '선택한 확장자·등록 업체·갱신 요금에 따름<br/>서버 비용과 별도'),
    ('알림톡 / SOLAPI', '<b>1,000건 14,300원</b><br/><b>3,000건 42,900원</b>', '표준 단가 13원 + VAT / 메시지 발송 건수 기준<br/>대체 문자·별도 유료 상품은 추가'),
], 9.6, 14.7, 12) + 12
y = para(M, y, '서버·도메인은 VAT 등을 고려한 계획 예산이며 고정 청구액이 아닙니다. 알림톡 예시는 VAT 포함입니다. '
         '초기 API 기본 이용 조건을 기준으로 하며, 실제 과금은 가입 시점의 업체 정책·사용량에 따릅니다.',
         CW, 9.1, 14, MUTED) + 16
y = callout(y, '알림 비용은 예약 건수와 다릅니다',
            '예약 확정 1건과 전날 안내 1건은 메시지 2건입니다. 변경 안내와 포장 준비 완료가 추가되면 발송량도 늘어납니다. '
            '발송 이력·실패 상태와 충전 잔액을 확인할 수 있도록 운영 절차를 안내합니다.', PALE, 9.7, 14.8) + 14
y = section(y, '02', '최종 검수 후 30일 무상 지원')
y = para(M, y, '최종 검수 완료 후 <b>30일간 합의된 기능의 오류 수정과 사용 안내</b>를 제공합니다. 이후 유지보수·신규 기능·'
         '외부 환경 변경 대응은 건별로 견적을 안내합니다. 월 유지보수 계약은 필수가 아닙니다.', CW, 10, 15.3) + 11
y = para(M, y, '도메인·서버·알림톡 계정은 <b>고객 소유</b>를 원칙으로 합니다. 외부 서비스 가입·심사에 필요한 사업자 자료는 '
         '고객이 준비하고, 개발사는 연동 설정과 필요한 화면·자료 준비를 지원합니다.', CW, 9.8, 15) + 14
y = section(y, '03', '인수 자료')
y = step_cards(y, [
    ('소스·개발', '소스코드, 의존성·설정 안내<br/>매장·예약·주문 데이터 구조'),
    ('배포·운영', '배포·백업·복구 방법<br/>메뉴·예약·주문 사용 매뉴얼'),
    ('검수·교육', '검수 결과·미해결 사항 기록<br/>직원 사용 교육·인수 확인'),
], 86, 9) + 12
para(M, y, '요금 확인: 2026.11.06 / AWS Lightsail 공식 요금·SOLAPI 공식 가격 정책. '
     '도메인은 등록·갱신 조건에 따른 예산 범위입니다. 향후 PG 이용 비용은 별도입니다.', CW, 8.2, 12.4, MUTED)
c.showPage()


# PAGE 9 - Conditional PG budget with explicit seller, channel and workflow bounds.
y = page(9, 'FUTURE ONLINE PAYMENT', '온라인 결제는 조건을 정해 확장합니다',
         '이번 오픈은 현장 결제입니다. 포장 옵션 구축 시 매장·판매 사업자 매핑,<br/>'
         '주문번호·주문 당시 금액 보관, 주문 상태와 결제 상태 분리를 준비합니다.')
y = callout(y, '향후 PG 추가 개발: 300-500만원 / VAT 포함',
            '<b>포장 주문 기능 구축 완료 + 판매 사업자 1개 + PG 1사 + 상점 계정 1개</b> 기준의 조건부 계획 예산입니다. '
            '공식 시세나 확정 견적이 아니며, 운영 정책·심사 조건을 확인해 정식 견적을 확정합니다.', INK, 9.8, 14.9) + 16
y = table(y, [105, CW - 105], ['기본 확장 범위', '산정 조건과 처리 방식'], [
    ('결제 대상·수단', '한 주문에 한 매장의 포장 음식 선결제. 국내 카드와<br/>동일 PG 통합결제창에서 계약·승인된 간편결제를 기준으로 합니다.'),
    ('매장 접수·취소', '결제 후 매장 접수, 거절·접수 기한 초과 시 전액 취소.<br/>고객 취소 요청은 직원 확인 후 전액 취소하며 기준·기한을 합의합니다.'),
    ('운영·오류 복구', '결제 내역·상태·영수증·권한·취소 이력, 서버 금액 검증,<br/>중복 처리 방지, 상태 조회·복구, 취소 실패 확인·재처리를 포함합니다.'),
], 9.6, 14.7, 14) + 13
y = para(M, y, '성공 화면만으로 결제 완료 처리하지 않습니다. 서버에서 승인과 금액을 확인하고, 응답 유실·중복 통보에 대비합니다. '
         '취소 요청 중·실패·완료를 구분해 실제 PG 결과와 주문 상태를 대조합니다.', CW, 9.6, 14.7) + 16
y = section(y, '01', '개발 일정과 가맹 심사를 구분합니다')
y = para(M, y, '<b>개발·검수 약 3-4주 / 내부 계획 공수 12-18인일.</b> 가맹 계약·카드사 심사는 외부 일정이며 일부 병행합니다. '
         '토스 최근 안내상 계약 완료 후 카드사 심사에 최대 10-14영업일이 소요될 수 있고, 보완 시 지연될 수 있습니다.',
         CW, 9.5, 14.7) + 10
y = para(M, y, 'PG는 판매 사업자 명의로 계약하고 해당 사업자에게 정산되는 구조를 우선 검토합니다. '
         '사업자가 다르면 신규 계약이 필요합니다. <b>PG 가입·연관리비·거래 수수료·필요한 보증보험·추가 서비스 이용료는 개발비와 별도</b>입니다.',
         CW, 9.4, 14.5) + 15
y = section(y, '02', '추가 산정할 조건')
y = para(M, y, '다사업자·여러 상점 계정 / 부분 취소·주문 금액 변경 / 단체 예약금·노쇼 자동 청구 / '
         'PG 다중화·POS·회계 연동·판매자 간 대금 배분 / 주류 온라인 판매 요건은 별도 검토·산정합니다.',
         CW, 9.4, 14.5) + 12
para(M, y, '확인: 2026.11.06 / 토스페이먼츠 공식 카드사 심사·사업자 계약 안내 및 개발자 문서. '
     '기간·개발비는 제안사의 조건부 추정이며 실제 결제 오픈일은 가맹 심사 완료와 검수 통과 후 확정합니다.',
     CW, 8.1, 12.3, MUTED)
c.showPage()


# PAGE 10 - A real screenshot, a correctly labeled ongoing case, concrete acceptance.
y = page(10, 'EXPERIENCE & ACCEPTANCE', '업무 흐름을 화면과 운영으로 연결합니다',
         '주식회사 김치스탄스튜디오는 웹·모바일 서비스와 맞춤형 소프트웨어를 만듭니다.<br/>'
         '관련 경험과 이번 과업의 검수 기준을 함께 제시합니다.')
text(M, y, 'John 4:24', 20, INK, 'Bold')
text(M + 167, y + 7, '웹 서비스 구축 / 2026.04 착수 / 당사 참여도 100%', 9.1, MUTED, 'Medium')
y += 32
im = Image.open(WORK / 'john-songbook-evidence.png')
image_h = CW * im.height / im.width
assert y + image_h <= H - BOTTOM
c.drawImage(str(WORK / 'john-songbook-evidence.png'), M, H - y - image_h, width=CW, height=image_h, mask='auto')
c.setStrokeColor(LINE)
c.setLineWidth(.6)
c.rect(M, H - y - image_h, CW, image_h, fill=0, stroke=1)
DRAWN.append({'page': PAGE, 'kind': 'evidence_image', 'top': y, 'bottom': y + image_h,
              'text': '실제 공개 서비스 검색·목록 화면 / 브라우저 UI·주소 제외'})
y += image_h + 7
y = para(M, y, '실제 공개 서비스의 검색·목록 화면 일부 / 2026.11.06 확인 / 제안 화면 예시와 구분',
         CW, 8.2, 12.4, MUTED) + 11
y = para(M, y, '곡 관리·가사·코드·조옮김, 예배 큐시트·콘티와 팀 협업을 지원하는 웹 서비스를 구축했습니다. '
         '콘텐츠와 여러 업무 흐름을 연결한 경험을 메뉴 관리·예약·직원 화면 구성에 적용합니다. '
         'React Native 기반 모바일 확장은 개발 중입니다.', CW, 9.5, 14.6) + 15
y = callout(y, '농산물 주문 관리 AI / 2026.11 착수·개발 중',
            '고객 주문 접수, 농가 재고·배송 확인, 거래·수령 정보 전달을 연결하는 대화 기반 자동화 프로젝트입니다. '
            'Linux 환경에서 카카오 대화를 연결하는 방식으로 개발 중이며, 주문 처리 순서와 담당자 간 정보 전달을 설계하고 있습니다.',
            PALE, 9.3, 14.3) + 17
y = section(y, '01', '이번 과업의 검수·착수 확인')
y = para(M, y, '<b>검수</b>  동시 예약 확정·매장별 권한·주문 당시 가격·품절/픽업 마감·변경/취소 후 알림 정정·'
         '발송 실패 대응·직원 휴대폰 업무·백업 복구를 확인합니다. 향후 PG는 승인 응답 유실·중복 통보·거절·환불 실패를 별도 검수합니다.',
         CW, 9.2, 14.1) + 9
y = para(M, y, '<b>착수 확인</b>  두 매장의 사업자 구조, 공간 정원·이용 시간, 예약·주문 취소 규칙, '
         '네이버 운영 방식, 포장 가능 메뉴, 자료·검수 담당자를 확정합니다.', CW, 9.2, 14.1) + 10
para(M, y, '실적 근거: 당사 회사소개서 및 공개 서비스 확인. 두 사례의 수행 내용·진행 상태를 구분해 작성했습니다.',
     CW, 8.1, 12.3, MUTED)
c.showPage()
c.save()


# Deliverable checks: actual rendered document content, not merely source strings.
message = MESSAGE.read_text(encoding='utf-8')
utf16_units = len(message.encode('utf-16-le')) // 2
assert len(message) <= 2900 and utf16_units <= 2900
assert all(ch not in message for ch in ['\u2011', '\u2013', '\u2014', '\u2192'])
assert not re.search('[\U0001F000-\U0001FAFF\u2600-\u27BF]', message)
reader = PdfReader(OUT)
assert len(reader.pages) == 10, len(reader.pages)
pdf_text = '\n'.join(p.extract_text() for p in reader.pages)
contact_patterns = [
    r'https?://', r'www\.', r'\bmailto:', r'\btel:',
    r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b',
    r'0\d{1,2}[- ]\d{3,4}[- ]\d{4}', r'kimchistan\.kr', r'john4-24\.com',
    r'오픈채팅', r'직접 연락', r'031[- ]?911[- ]?8190',
]
for pattern in contact_patterns:
    for label_, value in [('message', message), ('PDF', pdf_text), ('metadata', str(reader.metadata))]:
        assert not re.search(pattern, value, re.I), (label_, pattern)
assert not any(ch in pdf_text for ch in ['\u2011', '\u2013', '\u2014'])
assert all(not page.get('/Annots') for page in reader.pages)
assert not reader.trailer['/Root'].get('/Names')
assert not reader.trailer['/Root'].get('/OpenAction')
for required in ['800만원', '200만원', '1,000만원', '300-500만원', 'VAT', '30일',
                 '2026.11.13', '2026.12.20', '14,300원', '42,900원', '6-10만원', '2-4만원',
                 '3-4주', '10-14영업일', 'React', 'TypeScript', 'Django', 'PostgreSQL',
                 'John 4:24', '개발 중', '사업자 1개', 'PG 1사', '상점 계정 1개',
                 '현장 결제', '전액 취소', '부분 취소', '노쇼', '수기 등록']:
    assert required in pdf_text, ('missing PDF', required)
    assert required in message, ('missing message', required)
for stale in ['200-300만원', '7-10영업일', '13.2%', 'PROJECT 227317', '화상 미팅 필수']:
    assert stale not in pdf_text and stale not in message, stale
base_fees = [2000000, 1200000, 2000000, 1400000, 600000, 800000]
assert sum(base_fees) == 8000000
assert sum(base_fees) + 2000000 == 10000000
assert 13 * 1.1 * 1000 == 14300
assert round(13 * 1.1 * 3000) == 42900

edge_violations = []
glyphs = 0
with pdfplumber.open(OUT) as pdf:
    for index, p in enumerate(pdf.pages, 1):
        for ch in p.chars:
            glyphs += 1
            if ch['x0'] < M - 1 or ch['x1'] > W - M + 1 or ch['top'] < 19 or ch['bottom'] > H - 18:
                edge_violations.append({'page': index, 'text': ch['text'],
                                        'bbox': [ch['x0'], ch['top'], ch['x1'], ch['bottom']]})
assert not edge_violations, edge_violations[:10]
for path, expected in PRESERVED.items():
    assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == expected, path

shutil.copyfile(OUT, ATTACHMENT)
digest = hashlib.sha256(OUT.read_bytes()).hexdigest()
assert hashlib.sha256(ATTACHMENT.read_bytes()).hexdigest() == digest

qa = {
    'internal_pdf': str(OUT), 'attachment_pdf': str(ATTACHMENT), 'submission': str(MESSAGE),
    'pages': len(reader.pages), 'pdf_bytes': OUT.stat().st_size,
    'submission_characters': len(message), 'submission_utf16_units': utf16_units,
    'submission_limit': 3000, 'submission_target': 2900,
    'base_fees_vat_included': base_fees, 'base_total': sum(base_fees),
    'takeout_option': 2000000, 'combined_total': 10000000,
    'future_pg_conditional_budget_vat_included': [3000000, 5000000],
    'start_date': '2026-11-13', 'end_date': '2026-12-20',
    'elapsed_calendar_days': (date(2026, 12, 20) - date(2026, 11, 13)).days,
    'warranty_calendar_days_after_acceptance': 30,
    'glyphs_checked': glyphs, 'edge_violations': edge_violations,
    'contact_detail_scan': 'passed', 'external_annotations': 0,
    'embedded_files': 0, 'source_screenshot_crop': evidence_crop,
    'source_screenshot_sha256': hashlib.sha256(source_image.read_bytes()).hexdigest(),
    'attachment_matches_internal_pdf': True, 'preserved_source_sha256': PRESERVED,
    'pdf_sha256': digest, 'submission_sha256': hashlib.sha256(MESSAGE.read_bytes()).hexdigest(),
    'visual_review_complete': False,
}
(WORK / 'qa.json').write_text(json.dumps(qa, ensure_ascii=False, indent=2), encoding='utf-8')
(WORK / 'layout-records.json').write_text(json.dumps(DRAWN, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(qa, ensure_ascii=False, indent=2))
