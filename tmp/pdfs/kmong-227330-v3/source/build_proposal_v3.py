from pathlib import Path
from io import BytesIO
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
from reportlab.graphics.shapes import Drawing
from reportlab.graphics import renderPDF
from reportlab.graphics.barcode.qr import QrCodeWidget
from PIL import Image
from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[4]
WORK = ROOT / 'tmp/pdfs/kmong-227330-v3'
MEDIA = ROOT / 'tmp/pdfs/kmong-227330-v2/media'
SAMPLE = ROOT / 'tmp/pdfs/kmong-227330'
OUT = ROOT / 'output/pdf/kmong-227330-proposal-v3.pdf'
SUBMISSION = ROOT / 'output/proposals/kmong-227330-submission-v3.txt'
KINDER_URL = 'https://www.youtube.com/watch?v=At6hzU6x3Y8'
ORBIT_URL = 'https://www.youtube.com/shorts/kOg6ybxZyqs'
ALLOWED_URLS = {KINDER_URL, ORBIT_URL}

OUT.parent.mkdir(parents=True, exist_ok=True)
SUBMISSION.parent.mkdir(parents=True, exist_ok=True)
FONT_DIR = ROOT / 'tmp/pdfs/design-review/fonts'
for name, weight in [('KR', 'Regular'), ('KRM', 'Medium'), ('KRS', 'SemiBold'), ('KRB', 'Bold')]:
    pdfmetrics.registerFont(TTFont(name, str(FONT_DIR / f'Pretendard-{weight}.ttf')))

W, H = landscape(A4)
M = 36
CW = W-2*M
BG = colors.HexColor('#F5F3EE')
INK = colors.HexColor('#192D36')
MUTED = colors.HexColor('#52666E')
TEAL = colors.HexColor('#087A78')
LIGHT = colors.HexColor('#E3EFEB')
LINE = colors.HexColor('#D6DEDA')
WHITE = colors.white
c = canvas.Canvas(str(OUT), pagesize=(W, H), pageCompression=1)
c.setTitle('프리캐스트 건물 조립 3D 애니메이션 제작 제안 | 초안 v3')
c.setAuthor('주식회사 김치스탄스튜디오')
c.setSubject('크몽 프로젝트 227330 / 영상 포트폴리오와 제작 조건 반영 / 2026.11.07')
LAYOUT = []
LINKS = []
QR_LAYOUT = []


def txt(x, y, s, size=10, color=INK, font='KR'):
    width = pdfmetrics.stringWidth(s, font, size)
    assert x >= 0 and x+width <= W-M+1, (c.getPageNumber(), s, x+width)
    c.setFont(font, size)
    c.setFillColor(color)
    c.drawString(x, y, s)
    LAYOUT.append({'page':c.getPageNumber(), 'type':'line', 'text':s, 'x':x, 'y':y, 'width':width, 'size':size})


def para(x, top, s, width, size=10.5, leading=16, color=INK, font='KR', max_h=None):
    p = Paragraph(s, ParagraphStyle('copy',fontName=font,fontSize=size,leading=leading,textColor=color,wordWrap='CJK',splitLongWords=False))
    _, h = p.wrap(width, 1000)
    if max_h is not None:
        assert h <= max_h, (c.getPageNumber(), s, h, max_h)
    assert top-h >= 43, (c.getPageNumber(), s, top-h)
    p.drawOn(c, x, top-h)
    LAYOUT.append({'page':c.getPageNumber(),'type':'paragraph','text':re.sub('<[^>]+>','',s),'x':x,'top':top,'bottom':top-h,'width':width,'height':h,'size':size})
    return h


def rect(x, y, w, h, fill=WHITE, radius=0, stroke=None):
    c.setFillColor(fill)
    c.setStrokeColor(stroke or fill)
    if radius:
        c.roundRect(x,y,w,h,radius,fill=1,stroke=bool(stroke))
    else:
        c.rect(x,y,w,h,fill=1,stroke=bool(stroke))


def picture(path, x, y, w, h, background=None):
    p = Path(path)
    if not p.is_absolute():
        p = ROOT/p
    im = Image.open(p).convert('RGB')
    scale = min(w/im.width,h/im.height)
    iw, ih = im.width*scale, im.height*scale
    if background:
        rect(x,y,w,h,colors.HexColor(background))
    # Compress photographic/video evidence while retaining the original framing.
    buffer = BytesIO()
    im.save(buffer,format='JPEG',quality=94,subsampling=0)
    buffer.seek(0)
    c.drawImage(ImageReader(buffer),x+(w-iw)/2,y+(h-ih)/2,width=iw,height=ih)
    return (x+(w-iw)/2,y+(h-ih)/2,iw,ih)


def link_box(url, x, y, w, h, label):
    assert url in ALLOWED_URLS
    c.linkURL(url,(x,y,x+w,y+h),relative=0,thickness=0)
    LINKS.append({'page':c.getPageNumber(),'url':url,'kind':label,'rect':[x,y,x+w,y+h]})


def play_icon(x,y,r=19):
    c.setFillColor(TEAL)
    c.setStrokeColor(WHITE)
    c.setLineWidth(1.2)
    c.circle(x,y,r,fill=1,stroke=1)
    p=c.beginPath()
    p.moveTo(x-4,y-8)
    p.lineTo(x+9,y)
    p.lineTo(x-4,y+8)
    p.close()
    c.setFillColor(WHITE)
    c.drawPath(p,fill=1,stroke=0)


def video_poster(path,x,y,w,h,url):
    ix,iy,iw,ih=picture(path,x,y,w,h)
    play_icon(ix+iw/2,iy+ih/2)
    link_box(url,ix,iy,iw,ih,'poster')


def video_button(x,y,w,label,url):
    rect(x,y,w,32,TEAL,5)
    txt(x+14,y+11,label,10.5,WHITE,'KRS')
    link_box(url,x,y,w,32,'button')


def qr_card(x,y,url,size=72):
    rect(x,y,size,size,WHITE)
    widget=QrCodeWidget(url,barLevel='M')
    x0,y0,x1,y1=widget.getBounds()
    inner=size-12
    drawing=Drawing(inner,inner,transform=[inner/(x1-x0),0,0,inner/(y1-y0),-x0*inner/(x1-x0),-y0*inner/(y1-y0)])
    drawing.add(widget)
    renderPDF.draw(drawing,c,x+6,y+6)
    link_box(url,x,y,size,size,'qr')
    QR_LAYOUT.append({'page':c.getPageNumber(),'url':url,'rect_pdf_points':[x,y,x+size,y+size]})


def base(page,section):
    rect(0,0,W,H,BG)
    txt(M,H-28,'KIMCHISTAN STUDIO',9,INK,'KRB')
    txt(W-237,H-28,'제안 초안 v3  /  2026.11.07',8,MUTED)
    txt(M,H-59,section,8.5,TEAL,'KRS')
    c.setStrokeColor(LINE)
    c.setLineWidth(.6)
    c.line(M,29,W-M,29)
    txt(M,16,'프리캐스트 건물 조립 3D 애니메이션 제작 제안  |  주식회사 김치스탄스튜디오',7,MUTED)
    txt(W-M-17,16,f'{page:02d}',8,MUTED,'KRS')


def heading(title,subtitle):
    txt(M,H-94,title,24,INK,'KRB')
    para(M,H-111,subtitle,CW,10.5,16,MUTED,max_h=32)


# 01 / Solution overview.
base(1,'01 / 제작 방향')
txt(M,496,'프리캐스트 건물 조립',27,INK,'KRB')
txt(M,460,'3D 애니메이션 제작 제안',27,INK,'KRB')
para(M,437,'현장 관계자와 잠재 고객이 부재 관계와 조립 순서를 이해하고,<br/>영업·고객 제안에 활용할 수 있는 3D 설명 영상을 제안합니다.',CW,11,16,MUTED,max_h=34)
picture(SAMPLE/'precast-overview.png',M,131,470,264.375)
txt(M,116,'본 제안을 위해 제작한 30초 배치 개념 샘플의 실제 화면',8.5,MUTED)
x=531
txt(x,385,'30초 맞춤 샘플로',15,INK,'KRB')
txt(x,363,'설명 방식을 확인하세요.',15,INK,'KRB')
para(x,341,'이번 과업을 위해 제작한 샘플로 배치 순서와 전체·근접 시점을 먼저 확인하실 수 있습니다.',272,11,17,max_h=55)
txt(x,272,'3-4분 · 한국어 자막',13.5,TEAL,'KRB')
txt(x,253,'4K/1080p MP4 · 썸네일',10,MUTED)
txt(x,224,'2026.11.30 최종 납품일',13.5,TEAL,'KRB')
txt(x,195,'편집 원본 제공 가능',12,TEAL,'KRS')
rect(x,131,272,48,INK,5)
txt(x+13,158,'제안 초안 700만원 · VAT 포함',13,WHITE,'KRB')
txt(x+13,141,'제공 모델 활용 기준 · 상세 범위는 7쪽',9,WHITE)
rect(M,53,CW,44,LIGHT,6)
txt(M+15,70,'전체 관계  →  부재 이동  →  접점 확대  →  전체 회수',12,TEAL,'KRS')
txt(W-280,70,'실제 공정은 발주처 확인 자료 기준',9,MUTED)
c.showPage()


# 02 / Direct task sample.
base(2,'02 / 과업 맞춤 샘플')
heading('30초로 확인하는 본편의 제작 방향','기둥·보·슬래브의 배치 흐름과 상세 시점, 자막 표현을 보여주는 개념 예시입니다.')
gap=14
cardw=(CW-2*gap)/3
for i,(asset,title,body) in enumerate([
    ('precast-columns.png','01  기둥과 임시 지지','부재 이동과 임시 지지 상태를 함께 표현'),
    ('precast-bearing.png','02  받침부 확대','보와 받침 패드의 안착 관계를 근접 시점으로 설명'),
    ('precast-slabs.png','03  슬래브 배치','반복 부재와 전체 구조의 위치 관계를 순서대로 제시'),
]):
    xx=M+i*(cardw+gap)
    picture(SAMPLE/asset,xx,287,cardw,cardw*9/16)
    txt(xx,266,title,11,INK,'KRS')
    para(xx,252,body,cardw,10,15,MUTED,max_h=35)
rect(M,102,CW,104,WHITE,6)
txt(M+15,184,'샘플에서 확인하실 세 가지',11,TEAL,'KRS')
para(M+15,170,'① 기둥·보·슬래브가 놓이는 순서<br/>② 전체 구도와 받침부 근접 시점의 연결<br/>③ 공정명·안착 관계·생략 단계의 자막·강조',347,10.5,16,max_h=49)
para(M+15,116,'임시 지지와 받침부 등 장면 간 표현의 일관성을 점검했습니다.',347,8.8,13,MUTED,max_h=14)
txt(430,184,'실제 모델과 확인 자료로 확장',11,TEAL,'KRS')
para(430,170,'본편은 실제 부재 구성과 발주처가 확인한 접합 상세·공정 설명으로 확장합니다. 접합·그라우팅·양생·지지 해체는 자료에 맞춰 표현 범위를 정합니다.',354,10.5,16,max_h=64)
txt(M,82,'별도 첨부 · precast-assembly-30s-1080p.mp4',9.5,INK,'KRS')
txt(M,65,'30초 · 30fps · 무음 · 1080p / 4K  |  일반화한 배치 개념이며 구조 검토와 시공 절차 승인 범위는 포함하지 않습니다.',8.5,MUTED)
c.showPage()


# 03 / A real interior tour, with linked poster and print QR.
base(3,'03 / 관련 3D 작업 ①')
heading('실내 공간·조명·카메라 동선','Korean Kindergarten  |  자체 3D 시뮬레이션의 실제 공간을 시네마틱으로 구성했습니다.')
video_poster(MEDIA/'kindergarten-14.png',M,178,490,275.625,KINDER_URL)
picture(MEDIA/'kindergarten-29.png',548,309,257.89,145.063)
txt(548,293,'욕실 장면 · 설비의 배치와 공간 관계',8.5,MUTED)
txt(548,271,'공간을 이해시키는 관찰 시점',12,TEAL,'KRS')
para(548,254,'실내 동선과 채광, 가구·설비의 위치 관계를 읽기 쉬운 구도로 보여드립니다.',257.89,11,17,max_h=58)
txt(M,158,'Korean Kindergarten',16,INK,'KRB')
para(M,143,'본 과업에서는 부재와 주변 공간의 관계를 먼저 보여주고,<br/>설명이 필요한 지점으로 자연스럽게 시선을 연결하겠습니다.',490,11,17,max_h=40)
txt(M,97,'확인 포인트 · 00:14-00:35 실내 동선과 설비 배치',9,MUTED)
video_button(548,129,169,'영상 보기 · 1분 3초',KINDER_URL)
qr_card(733,113,KINDER_URL,72)
txt(739,100,'같은 영상 열기',7.5,MUTED)
rect(M,55,CW,34,LIGHT,5)
txt(M+14,67,'본 과업 적용  |  공간 관계가 읽히는 카메라 · 부재를 구분하는 빛 · 전체와 상세의 연결',10.5,TEAL,'KRS')
c.showPage()


# 04 / Cinematic and current detail imagery are clearly separated.
base(4,'04 / 관련 3D 작업 ②')
heading('기계형 오브젝트와 전체-상세 시점','Orbit Foundry - 3D 개발 시네마틱  |  자체 게임의 영상과 현재 개발 상세 화면입니다.')
video_poster(MEDIA/'orbit-short-12.png',M,139,180,320,ORBIT_URL)
video_button(M,96,180,'영상 보기 · 약 23초',ORBIT_URL)
txt(M,80,'확인 포인트 · 00:06-00:16',8.5,MUTED)
para(M,68,'기체 배치 관계와 시점 변화',180,9,13,MUTED,max_h=14)
txt(236,451,'현재 개발 상세 화면',12,TEAL,'KRS')
para(236,434,'공개 시네마틱과 별도로, 기계형 오브젝트의 부품과 재질을 가까이 확인한 화면입니다.',569.89,10.5,16,max_h=32)
picture('remaster/evidence/drone-readable.png',236,250,270,151.875)
picture('remaster/evidence/connector-detail.png',522,250,283.89,151.875)
txt(236,234,'설비 내부의 공간과 구성 요소',8.5,MUTED)
txt(522,234,'패널·커넥터의 근접 표현',8.5,MUTED)
para(236,215,'기계형 오브젝트의 재질·부품 표현과 시점 구성 경험을<br/>부재 식별, 접합부 가독성, 전체-상세 전환에 적용하겠습니다.',470,11,17,max_h=45)
qr_card(733,162,ORBIT_URL,72)
txt(739,150,'같은 영상 열기',7.5,MUTED)
rect(236,57,569.89,83,WHITE,5)
picture('assets/games/daycare-props-cover.webp',246,65,81,64.3)
txt(342,119,'함께 제시하는 자산 제작 경험',11,TEAL,'KRS')
para(342,104,'Daycare & Everyday Interiors · 360개 소품<br/>GLB와 편집 가능한 Blender 형식으로 제작·배포한 경험을 원본 정리에 연결합니다.',446,10,15,max_h=45)
c.showPage()


# 05 / A script that explains what the buyer will understand.
base(5,'05 / 본편 구성안')
heading('3분 30초의 설명 흐름','실제 부재 구성과 공정 순서를 확인한 뒤 확정할 제안용 예시입니다. 총 210초로 구성했습니다.')
table_top=445
rect(M,table_top-28,CW,28,INK)
for xx,label in [(M+12,'구간'),(M+128,'설명 주제'),(M+330,'시청자가 이해할 내용')]:
    txt(xx,table_top-18,label,10,WHITE,'KRS')
rows=[
    ('00:00-00:20','완성 구조와 설명 범위','전체 구조의 형태와 이번 영상에서 설명할 범위'),
    ('00:20-00:45','부재 종류와 위치','주요 부재의 역할, 명칭과 조립 전 위치 관계'),
    ('00:45-01:25','기둥 배치와 지지','이동·정렬·안착의 순서, 기초 접합과 임시 지지'),
    ('01:25-02:10','보 배치와 접합부','보가 놓이는 위치와 받침부·접합 상세의 관계'),
    ('02:10-02:55','슬래브와 이음부','슬래브의 배치 순서와 발주처 확인 자료의 이음·그라우팅 단계'),
    ('02:55-03:30','최종 상태와 고객 설명용 핵심 정리','전체 구조·조립 흐름과 발주처가 확인한 주요 설명 포인트 정리'),
]
for i,(time,subject,message) in enumerate(rows):
    yy=table_top-28-(i+1)*44
    rect(M,yy,CW,44,WHITE if i%2==0 else colors.HexColor('#ECF0EB'))
    txt(M+12,yy+17,time,10,TEAL,'KRS')
    txt(M+128,yy+17,subject,10.5,INK,'KRS')
    para(M+330,yy+33,message,CW-346,10.5,16,max_h=32)
rect(M,57,CW,75,LIGHT,6)
para(M+15,120,'마지막 구간은 고객 제안·프레젠테이션에서 설명할 부재 역할·조립 순서·접합 관계를 정리합니다.<br/>공정명 자막과 필요한 화살표·강조 표시로 이해를 돕습니다.<br/>접합·그라우팅·양생·임시 지지 해체의 표현과 생략 안내는 발주처 확인 자료에 따라 정합니다.',CW-30,10.5,16,TEAL,max_h=56)
c.showPage()


# 06 / Schedule, early render verification, communication and acceptance.
base(6,'06 / 일정과 검토')
heading('11월 30일 납품을 기준으로 단계별로 확인합니다.','2026.11.10 착수 · 2026.11.30 최종 납품  |  착수 후 전체 모델·공정 자료를 검수합니다.')
leftw=424
para(M,460,'확인 자료 · 모델 형식·단위·부재 분리 상태<br/>조립 순서·접합 참고 자료·부재 명칭·주요 설명 문구',leftw,9.5,14,MUTED,max_h=30)
schedule=[
    ('11.10-11.12','전체 모델·공정·자산 검수와 대표 장면 4K 시험 렌더'),
    ('11.13-11.16','콘티·카메라·저해상도 동작안 검토'),
    ('11.17-11.22','애니메이션 제작과 1080p 본편 초안 검토'),
    ('11.23-11.25','접합 표현·자막 반영, 장면 내용 확정'),
    ('11.26-11.28','4K 렌더링·편집과 납품 파일 검수'),
    ('11.29','최종 오류 점검과 재출력 예비일'),
    ('11.30','영상·썸네일·편집 원본 납품'),
]
for i,(date,body) in enumerate(schedule):
    top=422-i*43
    if i==6:
        rect(M-7,top-29,leftw+7,38,LIGHT,4)
    txt(M,top-13,date,10.5,TEAL,'KRS')
    para(M+101,top,body,leftw-101,10.5,16,max_h=35)
x=493
txt(x,440,'검토일마다 확인할 내용',13,INK,'KRB')
for yy,date,body in [
    (415,'11.16  콘티·동작안','설명 범위·공정 순서·전체/상세 시점'),
    (361,'11.22  본편 초안','부재·접합 표현과 명칭·자막'),
    (307,'11.25  내용 확정','수정 반영과 최종 설명 문구'),
]:
    txt(x,yy,date,10.5,TEAL,'KRS')
    para(x,yy-14,body,W-M-x,10.5,16,max_h=35)
txt(x,263,'납품 전 확인할 항목',12,TEAL,'KRB')
para(x,246,'영상 · 4K/1080p, 길이·프레임·재생 오류<br/>표현 · 반영 내용, 자막·가독성·화면 전환<br/>원본 · 프로젝트 열기, 사용 자산·누락 미디어',W-M-x,10,15,MUTED,max_h=61)
para(x,168,'검토 의견은 한 창구로 일괄 취합해<br/>반영 범위를 함께 확인합니다.',W-M-x,10,15,max_h=32)
rect(M,57,CW,70,LIGHT,6)
para(M+15,113,'자료·검토 회신이 지연될 것으로 예상되면 즉시 영향을 공유하고, 11월 30일 납품을 기준으로 반영 우선순위와 가능한 대안을 협의합니다. 초기 시험 렌더로 모델 처리와 출력 규모를 먼저 확인합니다.',CW-30,10.5,16,TEAL,max_h=50)
c.showPage()


# 07 / Price, model scope, revisions, delivery and editable handoff.
base(7,'07 / 견적·범위·원본 인계')
heading('작업 범위와 인계 내용을 먼저 정합니다.','대표 모델을 확인해 계약 전에 포함 작업과 금액을 확정하는 기준의 제안 초안입니다.')
col=370.945
right=434.945
rect(M,369,col,87,INK,6)
txt(M+15,436,'제안 금액 · 초안',10,colors.HexColor('#C5E4DE'),'KRS')
txt(M+15,400,'7,000,000원',29,WHITE,'KRB')
txt(M+15,383,'VAT 포함 기준 · 발주처 제공 모델 활용',10,WHITE)
txt(M,345,'기본 포함',11.5,TEAL,'KRB')
para(M,330,'모델 불러오기·단위 확인, 기존 부재의 장면 배치·명명 정리와 애니메이션·렌더링·CG·편집·한국어 자막을 포함합니다.',col,10.5,16,max_h=55)
txt(M,265,'계약 전 대표 모델 확인',11.5,TEAL,'KRB')
para(M,250,'불러오기와 가공 필요 범위를 확인하고, 객체 분리·형상 복원·누락 상세의 신규 제작을 포함할지 정해 견적 범위와 금액을 확정합니다.',col,10.5,16,max_h=50)
txt(M,190,'수정과 변경',11.5,TEAL,'KRB')
para(M,175,'콘티 1회·본편 1회의 일괄 의견을 기준으로 합니다. 승인된 콘티 안의 위치·타이밍·자막·표현 조정은 기본 수정에 포함합니다. 승인 후 부재·공정·상세 추가나 시나리오 변경은 비용과 납기 내 반영 가능성을 사전에 협의합니다. 제작 오류는 수정 횟수에서 차감하지 않습니다.',col,10.2,15,max_h=98)
para(M,68,'성우·번역·현장 촬영·구조 검토는 별도 협의합니다.',col,9.5,14,MUTED,max_h=20)
txt(right,440,'납품물 / 원본 파일 제공 가능',12,TEAL,'KRB')
deliver=[
    (414,'01  최종 영상','3-4분 4K MP4 + 동일 본편 1080p MP4 (16:9)'),
    (358,'02  썸네일','PNG 1종'),
    (310,'03  편집 원본','Blender 장면·카메라·애니메이션·자막·편집 구성'),
    (254,'04  인계 자료','제공 가능한 사용 자산, 버전·열기 안내, 파일 목록'),
]
for yy,title,body in deliver:
    txt(right,yy,title,10.5,INK,'KRS')
    para(right,yy-14,body,col,10.5,16,max_h=35)
para(right,183,'고객 제공 모델과 외부 자산은 사용·인계 권한에 맞춰 포함하고, 라이선스와 원본 제공 범위를 함께 정리합니다.',col,10.2,15,MUTED,max_h=50)
rect(right,61,col,60,WHITE,5)
txt(right+13,100,'세금계산서 · 산출물 목록 제공',10.5,INK,'KRS')
para(right+13,87,'정부지원 과제의 지정 정산 양식은 착수 전에 확인합니다.',col-26,9.5,14,MUTED,max_h=20)
c.showPage()
c.save()


submission='''프리캐스트 건물 조립 3D 애니메이션 제작 제안

안녕하세요. 게임과 3D 콘텐츠를 제작하는 주식회사 김치스탄스튜디오입니다.

제공하시는 모델과 발주처가 확인한 공정 자료를 바탕으로, 프리캐스트 건물의 조립 과정을 이해하기 쉬운 3~4분 영상으로 제작하겠습니다. 현장 관계자는 부재 관계와 조립 순서를, 잠재 고객은 전체 구조가 구성되는 흐름을 이해하도록 설명하겠습니다. 한국어 자막과 강조 그래픽을 더해 영업·고객 제안에 활용할 수 있도록 구성합니다. 3분 30초 구성안의 마지막 35초에는 부재 역할·조립 순서·접합 관계 등 고객 설명용 핵심 포인트를 정리합니다.

[맞춤 샘플과 관련 3D 작업]
이번 과업을 위해 제작한 30초 맞춤 샘플에서 세 가지를 확인하실 수 있습니다. ① 기둥·보·슬래브가 놓이는 순서 ② 전체 구도와 받침부 근접 시점의 연결 ③ 공정명·안착 관계·생략 단계를 알리는 자막·강조 표현입니다. 임시 지지와 받침부 등 장면 간 표현의 일관성을 점검했습니다. 본편은 실제 모델과 발주처가 확인한 접합 상세·공정 설명으로 확장합니다. 샘플은 일반화한 배치 개념이며 구조 검토나 시공 절차 승인용은 아닙니다. 접합·그라우팅·양생·지지 해체의 표현 범위는 발주처 자료에 맞춰 정합니다.
별도 첨부: precast-assembly-30s-1080p.mp4 (30초, 무음 / 4K 버전도 제공 가능)

Korean Kindergarten은 자체 3D 시뮬레이션의 실내 공간을 시네마틱으로 보여주는 작업입니다. 카메라 동선, 채광과 설비 배치를 확인하실 수 있습니다.
확인 포인트 · 00:14~00:35 실내 동선과 설비 배치
영상 보기 · 1분 3초: https://www.youtube.com/watch?v=At6hzU6x3Y8

Orbit Foundry는 자체 게임의 3D 개발 시네마틱입니다. 별과 기체의 배치 관계·시점 변화를 보여주며, 제안서에는 공개 시네마틱과 구분한 현재 개발 상세 화면도 함께 제시했습니다. 기계형 오브젝트의 부품·재질 표현과 전체/상세 시점 구성 경험을 본 과업에 적용하겠습니다. GLB·Blender 형식으로 제작·배포한 360개 소품 작업도 보조 사례로 담았습니다.
확인 포인트 · 00:06~00:16 기체 배치 관계와 시점 변화
영상 보기 · 약 23초: https://www.youtube.com/shorts/kOg6ybxZyqs

[일정과 검토]
2026.11.10 착수, 최종 납품일은 2026.11.30입니다.
계약 전에는 대표 모델로 불러오기와 가공 필요 범위를 확인해 견적 범위를 정합니다. 착수 후 11.10~12에는 전체 모델·공정·자산을 검수하고 대표 장면 4K 시험 렌더를 진행합니다. 확인할 자료는 모델 형식·단위·부재 분리 상태, 조립 순서·접합 참고 자료, 부재 명칭·주요 설명 문구입니다.
11.16 콘티·동작안: 설명 범위·공정 순서·전체/상세 시점 확인 → 11.22 본편 초안: 부재·접합 표현과 명칭·자막 확인 → 11.25 내용 확정: 수정 반영과 최종 설명 문구 확인 → 11.26~28 출력·검수 → 11.29 최종 점검·재출력 예비일 → 11.30 납품.
발주처의 검토 의견은 한 창구로 모아 일괄 취합하고 승인 시점과 반영 범위를 확인합니다. 자료·회신 지연이 예상되면 즉시 영향을 공유하고, 11월 30일 납품을 기준으로 반영 우선순위와 가능한 대안을 협의합니다.

[제안 금액과 모델 범위]
7,000,000원, VAT 포함 기준의 제안 초안입니다.
제공 모델 불러오기·단위 확인, 기존 부재의 장면 배치·명명 정리, 애니메이션·렌더링·CG·편집·한국어 자막을 포함합니다. 계약 전 대표 모델 확인에서 불러오기와 가공 필요 범위를 확인하고, 객체 분리·형상 복원·누락 상세의 신규 제작을 포함할지 정해 견적 범위와 금액을 확정합니다. 성우·번역·현장 촬영·구조 검토는 별도 협의합니다.

[수정과 변경]
콘티 1회·본편 1회의 일괄 의견을 기준으로 합니다. 기본 수정은 승인된 콘티 범위 내의 위치·타이밍·자막·표현 조정입니다. 승인 후 부재·공정·상세 장면 추가나 시나리오 변경은 비용과 납기 내 반영 가능성을 사전에 협의합니다. 제작 오류 수정은 수정 횟수에서 차감하지 않습니다.

[납품물 / 원본 파일 제공 가능]
- 3~4분 4K MP4 메인 영상 및 동일 본편 1080p MP4 (16:9)
- PNG 썸네일 1종
- 편집 가능한 Blender 장면·카메라·애니메이션·자막·편집 구성
- 제공 가능한 사용 자산, 버전·열기 안내와 파일 목록
고객 제공 모델과 외부 자산은 사용·인계 권한에 맞춰 포함하고 라이선스와 원본 제공 범위를 함께 정리합니다. 최종 납품 전에 해상도·길이·프레임·재생 오류·자막과 원본 열기·누락 미디어를 확인합니다. 세금계산서와 산출물 목록을 제공하며, 정부지원 과제의 지정 정산 양식은 착수 전에 확인합니다.

맞춤 샘플과 실제 3D 작업 사례를 통해 화면 구성과 표현 수준을 검토해 주시면 감사하겠습니다.
'''
SUBMISSION.write_text(submission,encoding='utf-8')

reader=PdfReader(OUT)
assert len(reader.pages)==7
fulltext='\n'.join(page.extract_text() for page in reader.pages)
uri_records=[]
for i,page in enumerate(reader.pages,1):
    for ref in page.get('/Annots',[]):
        annotation=ref.get_object()
        action=annotation.get('/A',{})
        assert action.get('/S')=='/URI',(i,action)
        uri=str(action.get('/URI'))
        assert uri in ALLOWED_URLS,(i,uri)
        uri_records.append({'page':i,'uri':uri,'rect':[float(x) for x in annotation['/Rect']]})
assert len(uri_records)==6,uri_records
assert {x['uri'] for x in uri_records}==ALLOWED_URLS
for bad in ['kimmchistan@gmail.com','031-911-8190','kimchistan.kr','discord.gg','store.steampowered.com','itch.io','/Users/','최종 납품 목표','PDF 자동 재생']:
    assert bad not in fulltext,bad
    assert bad not in submission,bad
for text in [fulltext,submission]:
    assert not re.search(r'[\w.+-]+@[\w.-]+\.[a-zA-Z]{2,}',text)
for term in ['Korean Kindergarten','Orbit Foundry','4K 시험 렌더','최종 납품일','계약 전에','콘티 1회','제작 오류','원본 파일 제공 가능','7,000,000원','VAT 포함','360개']:
    assert term in fulltext,term
assert set(re.findall(r'https?://\S+',submission))==ALLOWED_URLS
assert sum([20,25,40,45,45,35])==210
(WORK/'designer-layout.json').write_text(json.dumps(LAYOUT,ensure_ascii=False,indent=2))
(WORK/'designer-links.json').write_text(json.dumps({'links':LINKS,'qr_layout':QR_LAYOUT,'pdf_annotations':uri_records},ensure_ascii=False,indent=2))
qa={'status':'structural_checks_passed','pdf':str(OUT),'submission':str(SUBMISSION),'pages':7,'pdf_bytes':OUT.stat().st_size,'allowed_video_urls':sorted(ALLOWED_URLS),'uri_annotations':len(uri_records),'contact_text_check':'passed','source_limits_and_draft_terms':'preserved','proposed_duration_seconds':210,'visual_review':'pending','qr_pixel_decode':'pending','pm_improvements':['M1','M2','M3','M4','O1']}
(WORK/'designer-qa.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2))
print(json.dumps(qa,ensure_ascii=False,indent=2))
