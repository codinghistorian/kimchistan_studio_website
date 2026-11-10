from __future__ import annotations

import hashlib
import json
import re
from datetime import date
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph
from pypdf import PdfReader
import pdfplumber


ROOT = Path(__file__).resolve().parents[3]
WORK = ROOT / 'tmp/pdfs/kmong-227317'
OUT = ROOT / 'output/pdf/kmong-227317-proposal.pdf'
MESSAGE = ROOT / 'output/proposals/kmong-227317-submission.txt'
FONTS = ROOT / 'tmp/pdfs/design-review/fonts'
OUT.parent.mkdir(parents=True, exist_ok=True)

for name, filename in [('Regular', 'Pretendard-Regular.ttf'), ('Medium', 'Pretendard-Medium.ttf'),
                       ('SemiBold', 'Pretendard-SemiBold.ttf'), ('Bold', 'Pretendard-Bold.ttf')]:
    pdfmetrics.registerFont(TTFont(name, str(FONTS / filename)))
pdfmetrics.registerFontFamily('Regular', normal='Regular', bold='Bold', italic='Regular', boldItalic='Bold')
pdfmetrics.registerFontFamily('Medium', normal='Medium', bold='Bold', italic='Medium', boldItalic='Bold')

W, H = A4
M = 43
CW = W - 2 * M
BG = HexColor('#F7F5F0')
INK = HexColor('#18352F')
TEXT = HexColor('#263C37')
MUTED = HexColor('#586D65')
ACCENT = HexColor('#CB4828')
LINE = HexColor('#CCD6CE')
PALE = HexColor('#E9EEE7')
CREAM = HexColor('#F3DDD1')
LIGHT = HexColor('#D6E6DD')
BOTTOM = 62
PAGE = 0
DRAWN = []

c = canvas.Canvas(str(OUT), pagesize=A4, pageCompression=1)
c.setTitle('사내관리시스템 프론트엔드 리뉴얼 제안서')
c.setAuthor('주식회사 김치스탄스튜디오')
c.setSubject('PC 관리자 웹 UI/UX 개선, 기존 API 연동, MySQL-MariaDB 이전 및 스마트폰 선택 견적')
c.setCreator('KIMCHISTAN STUDIO')
c.setKeywords('프론트엔드, UI/UX, 관리자 시스템, 제안서, 227317')


def label(x, top, text, size=8, color=ACCENT, font='SemiBold'):
    txt(x, top, text, size, color, font)


def txt(x, top, text, size=10.5, color=TEXT, font='Regular'):
    width = pdfmetrics.stringWidth(text, font, size)
    assert x >= M - .1 and x + width <= W - M + .5, (PAGE, 'text width', text, x + width)
    assert top + size < H - 42, (PAGE, 'text bottom', text, top)
    c.setFillColor(color)
    c.setFont(font, size)
    c.drawString(x, H - top - size * .82, text)
    DRAWN.append({'page': PAGE, 'kind': 'text', 'top': top, 'bottom': top + size, 'text': text})


def style(size=10.5, leading=16, color=TEXT, font='Regular'):
    return ParagraphStyle('body', fontName=font, fontSize=size, leading=leading,
                          textColor=color, wordWrap=None, splitLongWords=False,
                          spaceBefore=0, spaceAfter=0, allowWidows=0, allowOrphans=0)


def measured(text, width, size=10.5, leading=16, color=TEXT, font='Regular'):
    p = Paragraph(text, style(size, leading, color, font))
    _, h = p.wrap(width, H)
    return p, h


def para(x, top, text, width=CW, size=10.5, leading=16, color=TEXT, font='Regular'):
    p, h = measured(text, width, size, leading, color, font)
    assert top + h <= H - BOTTOM + .1, (PAGE, 'paragraph bottom', top + h, text[:90])
    assert x >= M - .1 and x + width <= W - M + .1, (PAGE, 'paragraph width')
    p.drawOn(c, x, H - top - h)
    DRAWN.append({'page': PAGE, 'kind': 'paragraph', 'top': top, 'bottom': top + h,
                  'text': re.sub('<[^>]*>', '', text)})
    return top + h


def rule(top, x=M, width=CW, color=LINE):
    c.setStrokeColor(color)
    c.setLineWidth(.65)
    c.line(x, H - top, x + width, H - top)


def box(x, top, width, height, fill=PALE, stroke=None):
    assert top + height <= H - BOTTOM + .2, (PAGE, 'box bottom', top + height)
    c.setFillColor(fill)
    c.setStrokeColor(stroke or fill)
    c.roundRect(x, H - top - height, width, height, 5, fill=1, stroke=int(stroke is not None))


def section(top, number, title):
    label(M, top + 3, number, 8.2)
    txt(M + 29, top, title, 13.3, INK, 'Bold')
    return top + 28


def callout(top, title, body, fill=INK, width=CW, x=M):
    dark = fill == INK
    p, h = measured(body, width - 32, 10.4, 16, LIGHT if dark else TEXT)
    height = h + 55
    box(x, top, width, height, fill)
    txt(x + 16, top + 14, title, 11.3, white if dark else INK, 'SemiBold')
    para(x + 16, top + 37, body, width - 32, 10.4, 16, LIGHT if dark else TEXT)
    return top + height


def table(top, widths, headers, rows, size=10.1, leading=15.3, min_height=0, padding=20):
    header_h = 28
    box(M, top, CW, header_h, INK)
    xx = M
    for width, header in zip(widths, headers):
        txt(xx + 10, top + 9, header, 9, white, 'SemiBold')
        xx += width
    yy = top + header_h
    for i, row in enumerate(rows):
        ps = [measured(cell, width - 20, size, leading, TEXT) for cell, width in zip(row, widths)]
        height = max(max(h for _, h in ps) + padding, min_height)
        assert yy + height <= H - BOTTOM, (PAGE, 'table overflow', yy + height)
        if i % 2 == 0:
            box(M, yy, CW, height, white)
        xx = M
        for width, cell in zip(widths, row):
            para(xx + 10, yy + padding / 2, cell, width - 20, size, leading)
            xx += width
        rule(yy + height)
        yy += height
    return yy


def page(number, section_name, title, subtitle):
    global PAGE
    PAGE = number
    c.setFillColor(BG)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    txt(M, 24, 'KIMCHISTAN STUDIO', 10.2, INK, 'Bold')
    right = 'PROJECT 227317 / ' + section_name
    ww = pdfmetrics.stringWidth(right, 'Medium', 7.4)
    txt(W - M - ww, 27, right, 7.4, MUTED, 'Medium')
    rule(47)
    label(M, 67, f'0{number} / {section_name}', 8)
    txt(M, 88, title, 25, INK, 'Bold')
    bottom = para(M, 125, subtitle, CW, 10.6, 16.5, MUTED)
    rule(H - 44)
    c.setFillColor(MUTED)
    c.setFont('Regular', 7.4)
    c.drawString(M, 27, '주식회사 김치스탄스튜디오  |  크몽 엔터프라이즈 제안')
    c.setFont('Medium', 7.4)
    c.drawRightString(W - M, 27, f'2026.11.06   /   {number:02d}')
    return bottom + 23


# PAGE 1: A substantive executive summary rather than a cover-only page.
y = page(1, 'PROPOSAL', '사내관리시스템 FE 리뉴얼',
         '기존 기능과 업무 흐름을 유지하면서,<br/>사용하기 쉽고 유지보수 가능한 관리자 시스템으로 전환하겠습니다.')
y = callout(y, '매일 쓰는 업무를 더 명확하게',
            'PC 관리자 웹의 화면과 코드를 정비하고, 기존 API와 업무 규칙을 이어갑니다. '
            '로그인부터 조회·보고·결재까지, 현재 사용 중인 기능이 새 화면에서도 동일하게 동작하는지를 기준으로 완성도를 확인합니다.') + 22

gap = 15
col = (CW - gap) / 2
box(M, y, col, 100, white)
box(M + col + gap, y, col, 100, white)
label(M + 15, y + 13, '기본 제안 금액', 8.3)
txt(M + 15, y + 34, '6,000,000원', 23, INK, 'Bold')
txt(M + 15, y + 69, 'VAT 포함 / 세금계산서 발행 가능', 9.2, MUTED, 'Medium')
label(M + col + gap + 15, y + 13, '기본 수행 일정', 8.3)
txt(M + col + gap + 15, y + 35, '50일', 23, INK, 'Bold')
txt(M + col + gap + 15, y + 69, '2026.11.11 - 2026.12.31', 9.8, MUTED, 'Medium')
y += 122
y = section(y, '01', '고객님이 확인하실 세 가지 결과')
for number, title, body in [
    ('1', '일관된 업무 화면', '표·필터·입력폼·상태 안내를 공통화해 화면마다 다른 조작 방식과 피드백을 정리합니다.'),
    ('2', '기존 기능과 데이터의 연속성', '화면·권한·API 대응표로 누락을 점검하고, 통계 결과와 결재 흐름, 이전 데이터를 대조합니다.'),
    ('3', '개발 중 확인하고 인수할 수 있는 결과물', '대표 화면을 먼저 시연하고 주간 단위로 공유합니다. 소스·배포 안내·검수 결과·복귀 절차까지 전달합니다.'),
]:
    rule(y)
    label(M, y + 15, '0' + number, 9)
    txt(M + 30, y + 13, title, 11.7, INK, 'SemiBold')
    end = para(M + 30, y + 34, body, CW - 30, 10.4, 16)
    y = end + 14
y += 3
para(M, y, '<b>제안 기준</b>  PC 프론트엔드 전환·UI/UX 개선 + 합의한 소량 DB 이전. '
     '스마트폰 대응은 추가 1,200,000원(VAT 포함)의 선택 견적이며, 최종 과업·금액은 화상 미팅 및 요구명세 합의 후 확정합니다.',
     CW, 9.8, 15, MUTED)
c.showPage()


# PAGE 2: Feature coverage and intentional UX decisions.
y = page(2, 'SCOPE & UX', '현재 기능을 빠짐없이 연결합니다',
         '기존 메뉴 구조와 업무 규칙을 기준으로 화면을 전환하고,<br/>실제 업무에 필요한 가독성·조작 일관성·처리 피드백을 개선합니다.')
rows = [
    ('로그인·인증', '기존 인증·세션 흐름 유지', '로그인·로그아웃, 만료·접근 제한 시 안내'),
    ('권한별 대시보드', '기존 역할별 정보와 접근 범위 유지', '역할별 노출·이동·API 접근 결과'),
    ('통계·리포트', '기존 조회 조건과 결과 구조 유지', '동일 조건의 수치·합계·기존 출력 결과'),
    ('알림·공지사항', '기존 조회·관리 흐름 전환', '목록·상세·등록 등 현행 제공 기능'),
    ('사용자·권한 관리', '기존 설정 화면 전환', '설정 결과·접근 범위; 고도화는 별도 합의'),
    ('파일 업로드·다운로드', '기존 파일 처리 방식 연동', '허용 형식·용량·권한·실패 안내'),
    ('내부 결재·승인', '기존 결재 단계·상태 전환 유지', '역할별 처리·중복 조작·상태 표시'),
]
y = table(y, [105, 192, CW - 297], ['기능 영역', '유지·전환 기준', '주요 확인 항목'], rows, 9.8, 15) + 21
y = section(y, '02', 'UI/UX 개선의 적용 기준')
for title, body in [
    ('정보를 읽기 쉽게', '표의 열·숫자 정렬, 상태 표시, 검색·필터 위치와 정보 위계를 정리합니다. 기존 메뉴 구조는 유지합니다.'),
    ('처리 결과를 알기 쉽게', '필수 입력·유효성 검사·로딩·빈 결과·실패 안내를 통일하고, 처리 중 중복 조작을 줄입니다.'),
    ('대표 화면으로 먼저 검증', '미팅에서 우선순위를 정한 대시보드·목록/상세·입력/결재 유형 중 대표 화면을 먼저 구현해 방향을 합의합니다.'),
]:
    txt(M, y, title, 10.7, INK, 'SemiBold')
    end = para(M + 128, y - 1, body, CW - 128, 10.1, 15.5)
    y = end + 13
para(M, y + 2, '표의 확인 항목은 현행 제공 기능에 한해 적용합니다. 화면·팝업·역할별 변형을 포함한 목록과 필수 시나리오를 '
     '착수 시 대조하며, 신규 기능과 메뉴 구조 재설계는 기본 범위에 포함하지 않습니다.', CW, 9.4, 14.5, MUTED)
c.showPage()


# PAGE 3: Technical integration and safe migration.
y = page(3, 'TECH & MIGRATION', '기존 API와 데이터를 이어갑니다',
         'JavaScript 생태계로 프론트엔드를 전환하고,<br/>API 계약과 데이터의 일관성을 유지하는 방식으로 통합합니다.')
y = section(y, '01', '제안 기술과 적용 이유')
rows = [
    ('React + TypeScript', '화면을 컴포넌트로 분리하고 데이터 타입을 명확히 해 연결 오류와 변경 영향을 줄입니다.'),
    ('Vite + Node.js', '개발·빌드 환경으로 활용합니다. 신규 Node.js 백엔드 구축은 포함하지 않습니다.'),
    ('Material UI', '표·폼·대화상자·상태 표시를 공통화합니다. 무료 구성요소를 우선 활용하고 유료 기능은 사전 협의합니다.'),
]
y = table(y, [139, CW - 139], ['구성', '역할'], rows, 10.1, 15.4) + 18
y = section(y, '02', '인증·권한과 API 연결')
y = para(M, y, '기존 인증 방식, 요청·응답 구조와 업무 규칙을 유지합니다. 화면의 노출 제어와 함께 서버의 권한 판정 결과를 '
         '확인합니다. DB 접근은 기존 백엔드를 통해 처리하며, 프론트엔드에 DB 자격증명을 두지 않습니다.', CW, 10.3, 16) + 10
y = para(M, y, '소스 확인 시 PHP 내부 업무 로직과 API 미제공 기능을 구분합니다. 기존 API만으로 전환이 어려운 항목은 '
         '확인 즉시 처리안·담당·비용·일정 영향을 제시하고, 추가 개발 여부를 사전 합의합니다.', CW, 10.1, 15.5, MUTED) + 18
y = section(y, '03', 'MySQL → MariaDB 이전 절차')
step_gap = 8
step_w = (CW - step_gap * 3) / 4
for i, (title, body) in enumerate([
    ('호환성 점검', '버전·문자셋·쿼리\n연결 설정 확인'),
    ('시험 이전', '백업·복구 확인\n시험 환경에 복원'),
    ('결과 대조', '테이블 건수·핵심 값\n통계·API 회귀 확인'),
    ('승인 후 전환', '쓰기 중지·최종 백업\n이전·검증·재개'),
]):
    x = M + i * (step_w + step_gap)
    box(x, y, step_w, 88, PALE)
    label(x + 10, y + 10, f'0{i+1}', 8)
    txt(x + 10, y + 27, title, 10.5, INK, 'SemiBold')
    para(x + 10, y + 46, escape(body).replace('\n', '<br/>'), step_w - 20, 8.8, 13, MUTED)
y += 104
y = para(M, y, '대상 버전, 소량 데이터의 범위, 뷰·트리거·저장 로직 및 타 시스템 의존성을 먼저 확인합니다. '
         '연결 설정과 합의한 호환성 보완을 포함하며, 소요 중지 시간은 시험 이전 결과를 기준으로 협의합니다.', CW, 10.1, 15.5) + 12
callout(y, '복귀 기준까지 준비합니다',
        '쓰기 재개 전 검증에 실패하면 기존 환경으로 복귀합니다. 재개 후 문제가 발생하면 추가 쓰기를 중지하고 변경분을 보존한 뒤 '
        '복구 방안을 합의합니다. 원본 백업과 시험 복구 결과, 운영 전환·복귀 절차를 인수 자료에 포함합니다.', fill=PALE)
c.showPage()


# PAGE 4: Honest staffing, dated delivery, and review cadence.
y = page(4, 'TEAM & SCHEDULE', '책임과 진행 상황이 보이는 개발',
         'PM이 개발에도 직접 참여하고, 웹 개발 전문 인력을 더해 수행합니다.<br/>대표 화면 시연부터 운영 전환까지 검토 시점을 명확히 하겠습니다.')
y = section(y, '01', '2인 수행 계획')
y = table(y, [148, CW - 148], ['역할', '책임'], [
    ('PM 겸 개발자 1명', '고객 소통, 요구사항·설계, 개발, API 통합, DB 이전 조정, QA·검수 및 인수인계 총괄'),
    ('웹 전문 프리랜서 1명', '계약 체결 후 합류 예정. 공통 UI·기능별 화면 구현과 연동, 테스트 및 이슈 수정 분담'),
], 10.1, 15.4) + 19
y = section(y, '02', '기본 일정: 2026.11.11 - 2026.12.31 / 50일')
y = table(y, [97, 244, CW - 341], ['기간', '주요 작업', '확인·산출물'], [
    ('11.11 - 11.17', '화면·API·권한·DB 점검<br/>과업 기준과 UI 방향 합의', '범위·대응표<br/>필수 시나리오'),
    ('11.18 - 11.24', '공통 구조·UI 구성요소<br/>대표 화면 구현 및 API 연결', '대표 화면 시연<br/>UI 방향 확인'),
    ('11.25 - 12.15', '기능별 화면 전환과 API 연동<br/>완료 흐름별 점검·보완', '주간 시연<br/>기능 점검 기록'),
    ('12.16 - 12.24', '통합 테스트·DB 시험 이전<br/>데이터 대조·사용자 검수', '검수 결과<br/>전환 계획'),
    ('12.28 - 12.31', '중대 이슈 해소·승인 후 운영 전환<br/>배포 확인·인수인계', '소스·문서<br/>인수 확인'),
], 10, 15.2, padding=14) + 19
y = section(y, '03', '검토와 의사결정 방식')
y = para(M, y, '<b>매주 시연과 진행 보고</b>  완료 범위·다음 작업·확인할 이슈를 공유합니다. 공통 이슈 목록에 담당과 상태를 '
         '기록하고, 결정 사항을 문서로 남깁니다.', CW, 10.3, 16) + 10
y = para(M, y, '<b>합의한 범위 안에서 완성</b>  미팅에서 화면 목록과 필수 업무를 정리하고, 계약 후 소스·API와 대조합니다. '
         '합의 범위의 과업은 견적 내 수행하며, 추가 요구는 영향 설명과 사전 합의를 거칩니다.', CW, 10.3, 16) + 12
para(M, y, '의뢰인 측 업무 설명·검수 담당자, 역할별 시험 계정, 소스/API 명세, DB·배포 환경 접근과 검토 일정을 '
     '착수 시 합의합니다. 자료·의사결정 지연 또는 추가 과업이 있으면 영향과 조정안을 즉시 공유합니다.', CW, 9.6, 14.7, MUTED)
c.showPage()


# PAGE 5: Commercial clarity, acceptance, and complete handover.
y = page(5, 'OFFER & ACCEPTANCE', '범위·견적·검수 기준을 명확하게',
         'PC 기본 과업과 스마트폰 선택 과업을 구분했습니다.<br/>견적은 VAT 포함이며 세금계산서 발행이 가능합니다.')
y = table(y, [103, 260, CW - 363], ['구분', '범위', '금액 / VAT 포함'], [
    ('기본 과업', 'PC 프론트엔드 전환·UI/UX 개선<br/>+ 합의한 소량 MySQL → MariaDB 이전', '<b>6,000,000원</b>'),
    ('스마트폰 선택', '합의 화면의 스마트폰 조회·입력·결재 대응<br/>태블릿·네이티브 앱 제외 / 잠정 견적', '<b>+1,200,000원</b>'),
    ('선택 시 합계', '기본 과업 + 스마트폰 선택 과업', '<b>7,200,000원</b>'),
], 9.9, 15.2) + 11
y = para(M, y, '기본 완료 목표는 2026.12.31입니다. 스마트폰 옵션은 화면 목록·표 밀도·파일 처리·시험 단말을 검토한 뒤 '
         '최종 범위와 최대 7일의 추가 일정을 합의합니다. 위 금액은 공고 기준의 제안 견적으로, 화상 미팅과 요구명세 합의 후 확정합니다.',
         CW, 9.7, 14.8, MUTED) + 17
y = section(y, '01', '최종 검수 기준')
y = para(M, y, '합의한 필수 업무 시나리오를 모두 통과하고, 전환으로 발생한 중대 결함을 해소한 뒤 운영 전환합니다. '
         '중대 결함에는 핵심 업무 중단, 권한 오류, 데이터 누락·불일치가 포함됩니다.', CW, 10.3, 16) + 10
y = para(M, y, '권한별 접근·세션 만료, 동일 조건의 통계 결과, 기존 결재 상태 전환, 파일 송수신, API 실패 안내, '
         '이전 데이터 건수와 핵심 값을 확인합니다. 의뢰인 검수 결과와 운영 전환 승인을 기록합니다.', CW, 10.1, 15.5) + 17
y = section(y, '02', '인수 산출물과 납품 후 지원')
y = para(M, y, '<b>소스·개발 자료</b>  소스코드, 의존성·라이선스 목록, 화면/API 대응표<br/>'
         '<b>배포·운영 자료</b>  빌드·배포·설정 안내, 운영자 안내<br/>'
         '<b>검증·이전 자료</b>  테스트·검수 결과, DB 이전·복귀 절차와 점검 기록', CW, 10.2, 17) + 11
y = para(M, y, '검수 완료 후 <b>30일간 납품 범위의 결함 보정</b>을 제안합니다. 지속적인 운영 대행, 기능 추가와 '
         '외부 환경 변경에 따른 대응은 별도 협의합니다.', CW, 10.2, 15.8) + 16
callout(y, '견적의 기준과 변경 관리',
        '기존 기능·메뉴·API 활용과 소량 DB 이전을 전제로 합니다. 신규 기능, 메뉴 구조 재설계, 권한 고도화와 대규모 백엔드 개편은 '
        '별도 합의 대상입니다. 인프라·유료 라이선스 비용은 필요 시 사전 협의하며, 추가 작업을 임의로 진행하거나 청구하지 않습니다.', fill=PALE)
c.showPage()


# PAGE 6: Specific, supported work and a productive next meeting.
y = page(6, 'EXPERIENCE & NEXT STEP', '업무 흐름을 서비스로 구현한 경험',
         '주식회사 김치스탄스튜디오는 웹·모바일 서비스와 맞춤형 소프트웨어를 만듭니다.<br/>관련 경험과 이번 과업에 적용할 방식을 함께 소개합니다.')
label(M, y, 'RELATED WEB SERVICE', 8.2)
txt(M, y + 20, 'John 4:24', 29, INK, 'Bold')
txt(M, y + 60, '웹 서비스 구축 / 2026.04 착수 / 당사 참여도 100%', 10.1, MUTED, 'Medium')
y += 81
box(M, y, CW, 105, INK)
ref_cols = [
    ('곡 관리', '가사·코드·조옮김'),
    ('예배 기획', '큐시트·콘티'),
    ('팀 협업', '협업을 위한 업무 흐름'),
]
ref_w = CW / 3
for i, (title, body) in enumerate(ref_cols):
    x = M + i * ref_w + 15
    label(x, y + 15, f'0{i+1}', 8, LIGHT)
    txt(x, y + 37, title, 14, white, 'SemiBold')
    para(x, y + 65, body, ref_w - 28, 9.6, 14, LIGHT)
y += 122
y = para(M, y, '곡 관리, 가사·코드·조옮김, 예배 큐시트·콘티와 팀 협업을 지원하는 웹 서비스를 구축했습니다. '
         '구조화된 데이터와 여러 업무 흐름을 화면으로 연결한 경험을 바탕으로, 이번 과업에서도 업무의 순서와 화면 간 일관성을 함께 살피겠습니다.',
         CW, 10.4, 16) + 11
y = para(M, y, '<b>현재는 모바일 앱으로 확장하고 있습니다.</b> 기존 웹 서비스를 바탕으로 React Native 기반 '
         'Android·iOS 앱을 개발 중이며, 모바일 앱은 2027년 출시를 목표로 합니다. 이번 제안의 스마트폰 옵션은 웹 반응형 대응입니다.',
         CW, 9.9, 15.5, MUTED) + 20
y = section(y, '01', '화상 미팅에서 함께 확정할 항목')
questions = [
    ('화면과 업무', '화면·팝업·역할별 변형 수, 자주 쓰는 업무, 대표 화면과 필수 검수 시나리오'),
    ('API와 권한', '인증·세션 방식, 역할별 권한표, 기존 API 제공 범위와 PHP 내부 업무 로직'),
    ('DB와 운영', 'MySQL·MariaDB 버전, 데이터 규모·연계 시스템, 중지 가능 시간과 배포 환경'),
    ('선택 과업·검수', '스마트폰 대상 화면·단말, 검수 담당자와 일정, 최종 범위·금액'),
]
for i, (title, body) in enumerate(questions):
    rule(y)
    txt(M, y + 12, title, 10.5, INK, 'SemiBold')
    end = para(M + 111, y + 10, body, CW - 111, 10.1, 15.5)
    y = end + 9
y += 12
y = callout(y, '현재 화면과 우선 확인할 업무부터 함께 살펴보겠습니다',
            '크몽 화상 미팅에서 화면 목록과 의사결정 기준을 정리하고, 검토 가능한 대표 화면부터 개발하겠습니다. '
            '논의 내용은 과업·일정·검수 기준으로 문서화해 공유하겠습니다.') + 12
para(M, y, '작성 기준: 크몽 프로젝트 공고 및 당사 회사소개서. 현행 소스코드·API 명세는 공고에 따라 계약 후 확인 예정입니다.',
     CW, 8.8, 13, MUTED)
c.showPage()
c.save()


# Validate the actual outputs, rather than assuming a successful render is sufficient.
message = MESSAGE.read_text(encoding='utf-8')
utf16_units = len(message.encode('utf-16-le')) // 2
assert len(message) <= 2900, ('Submission too long', len(message))
assert utf16_units <= 2900, ('Submission too long in UTF-16', utf16_units)
assert not any(ch in message for ch in ['\u2011', '\u2013', '\u2014'])
assert (date(2026, 12, 31) - date(2026, 11, 11)).days == 50

reader = PdfReader(OUT)
assert len(reader.pages) == 6
pdf_text = '\n'.join(p.extract_text() for p in reader.pages)
contact_patterns = [r'https?://', r'www\.', r'\bmailto:', r'\btel:', r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b',
                    r'0\d{1,2}[- ]\d{3,4}[- ]\d{4}', r'kimchistan\.kr', r'john4-24\.com', r'카카오톡', r'오픈채팅']
for pattern in contact_patterns:
    assert not re.search(pattern, message, re.I), ('Contact detail in message', pattern)
    assert not re.search(pattern, pdf_text, re.I), ('Contact detail in PDF', pattern)
    assert not re.search(pattern, str(reader.metadata), re.I), ('Contact detail in metadata', pattern)
for p in reader.pages:
    assert not p.get('/Annots'), 'Unexpected annotation or external link'
assert not reader.trailer['/Root'].get('/Names'), 'Unexpected embedded names or attachments'
assert not reader.trailer['/Root'].get('/OpenAction'), 'Unexpected PDF open action'
for expected in ['6,000,000', '1,200,000', '7,200,000', 'React', 'TypeScript', 'Vite', 'Material UI',
                 'MySQL', 'MariaDB', 'John 4:24', '30일', '2026.11.11', '2026.12.31']:
    assert expected in pdf_text, ('Missing PDF content', expected)
    assert expected in message, ('Missing message content', expected)
assert '13.2%' not in pdf_text and '13.2%' not in message

edge_violations = []
glyph_count = 0
with pdfplumber.open(OUT) as pdf:
    for index, p in enumerate(pdf.pages, 1):
        for ch in p.chars:
            glyph_count += 1
            if ch['x0'] < M - 1 or ch['x1'] > W - M + 1 or ch['top'] < 19 or ch['bottom'] > H - 18:
                edge_violations.append({'page': index, 'glyph': ch['text'], 'bbox': [ch['x0'], ch['top'], ch['x1'], ch['bottom']]})
assert not edge_violations, edge_violations[:12]

source_hash = hashlib.sha256((ROOT / 'output/pdf/kimchistan-studio-company-introduction.pdf').read_bytes()).hexdigest()
assert source_hash == '76758b55ba6986dc396eb697f6494cd21d92a7b5ed5aab01b327f2a2dcff567e', 'Original company profile changed'

qa = {
    'pdf_path': str(OUT), 'submission_path': str(MESSAGE), 'pages': len(reader.pages),
    'pdf_bytes': OUT.stat().st_size, 'submission_characters': len(message),
    'submission_utf16_units': utf16_units, 'submission_limit': 3000,
    'submission_safety_target': 2900, 'glyphs_checked': glyph_count,
    'edge_violations': edge_violations, 'contact_detail_scan': 'passed',
    'external_pdf_annotations': 0, 'original_company_profile_unchanged': True,
    'core_total_vat_included': 6000000, 'mobile_option_vat_included': 1200000,
    'combined_total_vat_included': 7200000, 'core_elapsed_calendar_days': 50,
    'mobile_extra_calendar_days': 7, 'visual_review_complete': False,
    'pdf_sha256': hashlib.sha256(OUT.read_bytes()).hexdigest(),
    'source_company_profile_sha256': source_hash,
    'internal_note': 'The observed form displays a 13.2% brokerage fee. Do not include this note in client-facing materials.',
}
(WORK / 'qa.json').write_text(json.dumps(qa, ensure_ascii=False, indent=2), encoding='utf-8')
(WORK / 'layout-records.json').write_text(json.dumps(DRAWN, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(qa, ensure_ascii=False, indent=2))
