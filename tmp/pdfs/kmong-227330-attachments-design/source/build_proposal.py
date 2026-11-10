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
from PIL import Image
from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[4]
WORK = ROOT / 'tmp/pdfs/kmong-227330-attachments-design'
MEDIA = ROOT / 'tmp/pdfs/kmong-227330-v2/media'
SAMPLE = ROOT / 'tmp/pdfs/kmong-227330'
OUT = ROOT / 'output/pdf/kmong-227330-proposal.pdf'
ATTACHMENTS = [
    '01_프리캐스트_조립샘플.mp4',
    '02_어린이집_실내공간연출.mp4',
    '03_Orbit_Foundry_3D_연출.mp4',
]

OUT.parent.mkdir(parents=True, exist_ok=True)
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
c.setTitle('프리캐스트 건물 조립 3D 애니메이션 제작 제안')
c.setAuthor('주식회사 김치스탄스튜디오')
c.setSubject('크몽 프로젝트 227330 / 영상 포트폴리오와 제작 조건 반영 / 2026.11.07')
LAYOUT = []


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


def base(page,section):
    rect(0,0,W,H,BG)
    txt(M,H-28,'KIMCHISTAN STUDIO',9,INK,'KRB')
    txt(W-237,H-28,'제작 제안서  /  2026.11.07',8,MUTED)
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
para(M,437,'현장 관계자와 잠재 고객에게 부재 간 관계와 조립 순서를 설명하고,<br/>영업·고객 제안 자료로 활용할 수 있는 3D 영상을 제안합니다.',CW,11,16,MUTED,max_h=34)
picture(SAMPLE/'precast-overview.png',M,131,470,264.375)
txt(M,116,'본 제안을 위해 제작한 30초 배치 개념 샘플의 실제 화면',8.5,MUTED)
txt(M,102,'첨부 영상 01  |  01_프리캐스트_조립샘플.mp4',9,TEAL,'KRS')
x=531
txt(x,385,'30초 맞춤 샘플로',15,INK,'KRB')
txt(x,363,'설명 방식을 확인하세요.',15,INK,'KRB')
para(x,341,'함께 첨부한 MP4 파일을 열어<br/>배치 순서와 전체·근접 시점을 확인해 주세요.',272,11,17,max_h=55)
txt(x,272,'3-4분 · 한국어 자막',13.5,TEAL,'KRB')
txt(x,253,'4K/1080p MP4 · 썸네일',10,MUTED)
txt(x,224,'2026.11.30 최종 납품일',13.5,TEAL,'KRB')
txt(x,195,'편집 원본 제공 가능',12,TEAL,'KRS')
rect(x,131,272,48,INK,5)
txt(x+13,158,'제안 초안 700만 원 · 부가세 포함',13,WHITE,'KRB')
txt(x+13,141,'제공 모델 활용 기준 · 상세 범위는 7쪽',9,WHITE)
rect(M,53,CW,44,LIGHT,6)
txt(M+15,70,'전체 구도  →  부재 이동  →  접점 확대  →  전체 다시 보기',12,TEAL,'KRS')
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
rect(M,106,CW,104,WHITE,6)
txt(M+15,188,'샘플에서 확인하실 세 가지',11,TEAL,'KRS')
para(M+15,174,'① 기둥·보·슬래브가 놓이는 순서<br/>② 전체 구도와 받침부 근접 시점의 연결<br/>③ 자막·강조로 알리는 공정명·안착 관계·생략 단계',347,10.5,16,max_h=49)
para(M+15,120,'임시 지지와 받침부 등 장면 간 표현의 일관성을 점검했습니다.',347,8.8,13,MUTED,max_h=14)
txt(430,188,'실제 모델과 발주처 자료를 본편에 반영',11,TEAL,'KRS')
para(430,174,'본편에는 실제 부재 구성과 발주처가 확인한<br/>접합 상세·공정 설명을 반영합니다.<br/>접합·그라우팅·양생·지지 해체의 표현 범위는<br/>해당 자료에 따라 정합니다.',350,10.5,16,max_h=64)
txt(M,85,'첨부 영상 01  |  01_프리캐스트_조립샘플.mp4',11,TEAL,'KRS')
txt(M,65,'함께 첨부한 MP4 파일을 열어 재생해 주세요.  ·  30초 · 4K · 30fps · 무음',10,MUTED)
txt(M,44,'일반적인 부재 배치를 설명하는 개념 샘플이며, 구조 검토나 시공 절차 승인용은 아닙니다.',8.5,MUTED)
c.showPage()


# 03 / Interior cinematic and its separate MP4 attachment.
base(3,'03 / 관련 3D 작업 ①')
heading('실내 공간·조명·카메라 동선','Korean Kindergarten  |  자체 3D 시뮬레이션 속 실내 공간을 시네마틱 영상으로 구성했습니다.')
picture(MEDIA/'kindergarten-14.png',M,178,490,275.625)
picture(MEDIA/'kindergarten-29.png',548,309,257.89,145.063)
txt(548,293,'욕실 장면 · 설비의 배치와 공간 관계',8.5,MUTED)
txt(548,271,'공간 관계가 드러나는 카메라 구도',12,TEAL,'KRS')
para(548,254,'실내 동선과 채광, 가구·설비의 위치 관계를 읽기 쉬운 구도로 보여드립니다.',257.89,11,17,max_h=58)
txt(M,158,'Korean Kindergarten',16,INK,'KRB')
para(M,143,'본 과업에서는 부재와 주변 공간의 관계를 먼저 보여주고,<br/>설명이 필요한 지점으로 시선을 자연스럽게 이끌겠습니다.',490,11,17,max_h=40)
txt(548,193,'첨부 영상 02  |  30초 · 무음',10.5,TEAL,'KRS')
para(548,178,'02_어린이집_실내공간연출.mp4',257.89,10,14,INK,'KRS',max_h=28)
para(548,152,'함께 첨부한 MP4 파일을 열어<br/>실내 동선·채광·설비 배치를 확인해 주세요.',257.89,10,15,MUTED,max_h=45)
txt(548,105,'1280 × 720 · 시네마틱 발췌',9,MUTED)
rect(M,55,CW,34,LIGHT,5)
txt(M+14,67,'본 과업 적용  |  공간 관계가 읽히는 카메라 · 부재를 구분하는 빛 · 전체와 상세의 연결',10.5,TEAL,'KRS')
c.showPage()


# 04 / Cinematic and current detail imagery are clearly separated.
base(4,'04 / 관련 3D 작업 ②')
heading('기계형 3D 모델과 전체·상세 구도','Orbit Foundry  |  개발 중인 3D 게임의 시네마틱과 현재 개발 상세 화면입니다.')
picture(MEDIA/'orbit-short-12.png',M,139,180,320)
txt(M,120,'첨부 영상 03  |  12초 · 무음',10,TEAL,'KRS')
para(M,105,'03_Orbit_Foundry_3D_연출.mp4',180,9.2,13,INK,'KRS',max_h=27)
para(M,80,'함께 첨부한 MP4 파일을<br/>열어 재생해 주세요.',180,9.5,13,MUTED,max_h=27)
txt(236,451,'현재 개발 상세 화면',12,TEAL,'KRS')
para(236,434,'첨부 시네마틱과 별도로, 기계형 3D 모델의 부품과 재질을 가까이 확인한 화면입니다.',569.89,10.5,16,max_h=32)
picture('remaster/evidence/drone-readable.png',236,250,270,151.875)
picture('remaster/evidence/connector-detail.png',522,250,283.89,151.875)
txt(236,234,'설비 내부의 공간과 구성 요소',8.5,MUTED)
txt(522,234,'패널·커넥터의 근접 표현',8.5,MUTED)
para(236,215,'기계형 3D 모델의 재질·부품 표현과 구도 구성 경험을<br/>부재 식별, 접합부 가독성, 전체 화면과 상세 화면의 전환에 적용하겠습니다.',470,11,17,max_h=45)
rect(236,57,569.89,83,WHITE,5)
picture('assets/games/daycare-props-cover.webp',246,65,81,64.3)
txt(342,119,'함께 제시하는 자산 제작 경험',11,TEAL,'KRS')
para(342,104,'Daycare & Everyday Interiors · 360개 소품<br/>GLB와 편집 가능한 Blender 파일을 제작·배포한 경험을 바탕으로, 본 과업의 자산과 원본을 정리하겠습니다.',446,10,15,max_h=45)
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
    ('02:10-02:55','슬래브와 이음부','슬래브 배치 순서와 발주처 자료에 따른 이음·그라우팅 단계'),
    ('02:55-03:30','최종 상태와 고객 설명용 핵심 정리','전체 구조·조립 흐름과 발주처가 확인한 핵심 설명 내용'),
]
for i,(time,subject,message) in enumerate(rows):
    yy=table_top-28-(i+1)*44
    rect(M,yy,CW,44,WHITE if i%2==0 else colors.HexColor('#ECF0EB'))
    txt(M+12,yy+17,time,10,TEAL,'KRS')
    txt(M+128,yy+17,subject,10.5,INK,'KRS')
    para(M+330,yy+33,message,CW-346,10.5,16,max_h=32)
rect(M,57,CW,75,LIGHT,6)
para(M+15,120,'마지막 구간에서는 고객 제안·프레젠테이션에 활용할 부재의 역할, 조립 순서와 접합 관계를 정리합니다.<br/>공정명 자막과 필요한 화살표·강조 표시로 이해를 돕습니다.<br/>접합·그라우팅·양생·임시 지지 해체의 표현과 생략 안내는 발주처 확인 자료에 따라 정합니다.',CW-30,10.5,16,TEAL,max_h=56)
c.showPage()


# 06 / Schedule, early render verification, communication and acceptance.
base(6,'06 / 일정과 검토')
heading('11월 30일 납품까지 단계별로 확인합니다.','2026.11.10 착수 · 2026.11.30 최종 납품  |  착수 후 전체 모델·공정 자료를 검수합니다.')
leftw=424
para(M,460,'확인 자료 · 모델 형식·단위·부재 분리 상태<br/>조립 순서·접합 참고 자료·부재 명칭·주요 설명 문구',leftw,9.5,14,MUTED,max_h=30)
schedule=[
    ('11.10-11.12','전체 모델·공정 자료·자산 검수와 대표 장면의 4K 시험 렌더링'),
    ('11.13-11.16','콘티(장면 구성안)·카메라·저해상도 동작안 검토'),
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
para(x,246,'영상 · 4K/1080p, 길이·프레임·재생 오류<br/>표현 · 반영 내용, 자막·가독성·화면 전환<br/>원본 · 프로젝트 열기, 자산·미디어 누락 여부',W-M-x,10,15,MUTED,max_h=61)
para(x,168,'검토 의견은 한 창구로 일괄 취합해<br/>반영 범위를 함께 확인합니다.',W-M-x,10,15,max_h=32)
rect(M,57,CW,70,LIGHT,6)
para(M+15,113,'자료 전달이나 검토 회신이 지연될 것으로 예상되면 일정에 미치는 영향을 즉시 공유합니다.<br/>11월 30일 납품을 기준으로 반영 우선순위와 대안을 협의합니다.<br/>초기 시험 렌더링으로 모델 처리와 출력 작업 규모를 확인합니다.',CW-30,10.5,16,TEAL,max_h=50)
c.showPage()


# 07 / Price, model scope, revisions, delivery and editable handoff.
base(7,'07 / 견적·범위·원본 인계')
heading('작업 범위와 인계 내용을 먼저 정합니다.','대표 모델을 확인한 뒤 계약 전에 작업 범위와 금액을 확정하는 제안 초안입니다.')
col=370.945
right=434.945
rect(M,369,col,87,INK,6)
txt(M+15,436,'제안 금액 · 초안',10,colors.HexColor('#C5E4DE'),'KRS')
txt(M+15,400,'7,000,000원',29,WHITE,'KRB')
txt(M+15,383,'부가세 포함 · 발주처 제공 모델 활용',10,WHITE)
txt(M,345,'기본 포함',11.5,TEAL,'KRB')
para(M,330,'모델 불러오기와 단위 확인, 기존 부재의 배치·명칭 정리를 포함합니다.<br/>애니메이션·렌더링·CG·편집·한국어 자막도 제작합니다.',col,10.5,16,max_h=55)
txt(M,265,'계약 전 대표 모델 확인',11.5,TEAL,'KRB')
para(M,250,'모델을 불러올 수 있는지와 추가 가공 범위를 확인합니다.<br/>객체 분리·형상 복원·누락 상세 제작의 포함 여부를 정해<br/>견적 범위와 금액을 확정합니다.',col,10.5,16,max_h=50)
txt(M,183,'수정과 변경',11.5,TEAL,'KRB')
para(M,168,'콘티와 본편 단계에서 각각 1회씩 검토 의견을 취합합니다.<br/>승인된 콘티 범위의 위치·타이밍·자막·표현 조정은 기본 수정에 포함합니다.<br/>콘티 승인 후 부재·공정·상세 장면 추가나 시나리오 변경은<br/>비용과 납기 내 반영 가능성을 사전에 협의합니다.<br/>제작 오류를 바로잡는 수정은 위 횟수에 포함하지 않습니다.',col,10.2,15,max_h=98)
para(M,68,'성우·번역·현장 촬영·구조 검토는 별도 협의합니다.',col,9.5,14,MUTED,max_h=20)
txt(right,440,'납품물 / 원본 파일 제공 가능',12,TEAL,'KRB')
deliver=[
    (414,'01  최종 영상','3-4분 4K MP4 + 동일 본편 1080p MP4 (16:9)'),
    (358,'02  썸네일','PNG 1종'),
    (310,'03  편집 원본','장면·카메라·애니메이션·자막·편집 구성이 포함된 Blender 프로젝트'),
    (254,'04  인계 자료','인계 가능한 자산, 제작 도구 버전·파일 열기 안내, 파일 목록'),
]
for yy,title,body in deliver:
    txt(right,yy,title,10.5,INK,'KRS')
    para(right,yy-14,body,col,10.5,16,max_h=35)
para(right,183,'발주처 제공 모델과 외부 자산은 사용·인계가 허용된 범위에서 포함하고, 라이선스와 원본 제공 범위를 함께 정리합니다.',col,10.2,15,MUTED,max_h=50)
rect(right,61,col,60,WHITE,5)
txt(right+13,100,'세금계산서 · 산출물 목록 제공',10.5,INK,'KRS')
para(right+13,87,'정부지원 과제의 지정 정산 양식은 착수 전에 확인합니다.',col-26,9.5,14,MUTED,max_h=20)
c.showPage()
c.save()


reader=PdfReader(OUT)
assert len(reader.pages)==7
fulltext='\n'.join(page.extract_text() for page in reader.pages)
annotations=[]
for i,page in enumerate(reader.pages,1):
    for ref in page.get('/Annots',[]):
        annotation=ref.get_object()
        annotations.append({'page':i,'subtype':str(annotation.get('/Subtype')),'action':str(annotation.get('/A'))})
assert len(annotations)==0,annotations
for bad in ['http://','https://','youtube','youtu.be','YouTube','QR','브라우저','클릭 시','휴대폰 카메라','스캔해','영상 보기','kimmchistan@gmail.com','031-911-8190','kimchistan.kr','discord.gg','store.steampowered.com','itch.io','/Users/','최종 납품 목표','PDF 자동 재생']:
    assert bad not in fulltext,bad
assert not re.search(r'[\w.+-]+@[\w.-]+\.[a-zA-Z]{2,}',fulltext)
for term in ['Korean Kindergarten','Orbit Foundry','4K 시험 렌더링','최종 납품일','계약 전에','각각 1회씩','제작 오류','원본 파일 제공 가능','7,000,000원','부가세 포함','360개',*ATTACHMENTS]:
    assert term in fulltext,term
assert sum([20,25,40,45,45,35])==210
assert not re.search(r'(?i)\bv[1-9]\d*\b',fulltext)
assert not re.search(r'(?i)\bv[1-9]\d*\b',str(reader.metadata))
(WORK/'designer-layout.json').write_text(json.dumps(LAYOUT,ensure_ascii=False,indent=2))
qa={'status':'structural_checks_passed','pdf':str(OUT),'pages':7,'pdf_bytes':OUT.stat().st_size,'attachments':ATTACHMENTS,'uri_annotations':0,'all_annotations':0,'video_links':0,'qr_codes':0,'play_icons':0,'browser_playback_controls':0,'contact_text_check':'passed','source_limits_and_draft_terms':'preserved','proposed_duration_seconds':210,'visual_review':'pending','korean_review_items':[f'K{i:02d}' for i in range(1,15)],'pm_improvements':['M1','M2','M3','M4','O1']}
(WORK/'designer-qa.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2))
print(json.dumps(qa,ensure_ascii=False,indent=2))
