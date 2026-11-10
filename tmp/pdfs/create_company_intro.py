from pathlib import Path
from xml.sax.saxutils import escape
import json
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, Color, white
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
from PIL import Image, ImageOps
from pypdf import PdfReader

ROOT=Path.cwd()
OUT=ROOT/'output/pdf/kimchistan-studio-company-introduction.pdf'
FONT='/System/Library/Fonts/Supplemental/Arial Unicode.ttf'
pdfmetrics.registerFont(TTFont('Gothic', FONT))
pdfmetrics.registerFont(TTFont('ArialBold', '/System/Library/Fonts/Supplemental/Arial Bold.ttf'))
W,H=A4
BG=HexColor('#F4F1EB'); INK=HexColor('#192B34'); MUTED=HexColor('#596870'); ACCENT=HexColor('#D84C2B'); LINE=HexColor('#D9DDD8')
M=42; CW=W-2*M
c=canvas.Canvas(str(OUT),pagesize=A4,pageCompression=1)
c.setTitle('김치스탄 스튜디오 | 회사소개서')
c.setAuthor('KIMCHISTAN STUDIO')
c.setSubject('게임, 맞춤형 소프트웨어, AI 업무 연동 및 공개 프로젝트 소개')

def text(x,y,s,size=10,color=INK,font='Gothic'):
    c.setFillColor(color); c.setFont(font,size); c.drawString(x,y,s)

def para(x,y,s,width,size=10,leading=15,color=INK):
    p=Paragraph(s, ParagraphStyle('p',fontName='Gothic',fontSize=size,leading=leading,textColor=color,wordWrap='CJK',splitLongWords=False))
    _,h=p.wrap(width,1000); p.drawOn(c,x,y-h); return h

def base(page,label):
    c.setFillColor(BG);c.rect(0,0,W,H,fill=1,stroke=0)
    text(M,H-39,'KIMCHISTAN STUDIO',11,INK,'ArialBold')
    text(W-M-104,H-39,label,8,MUTED)
    c.setStrokeColor(LINE);c.setLineWidth(.6);c.line(M,42,W-M,42)
    text(M,27,'주식회사 김치스탄스튜디오  |  대한민국 경기도 고양시',7.5,MUTED)
    text(W-M-10,27,f'{page:02d}',8,MUTED,'ArialBold')

def image_card(path,x,y,w,h):
    im=Image.open(ROOT/path).convert('RGB')
    im=ImageOps.fit(im,(round(w*3),round(h*3)),method=Image.Resampling.LANCZOS)
    c.drawImage(ImageReader(im),x,y,width=w,height=h,mask='auto')

base(1,'회사소개 / COMPANY')
text(M,H-88,'게임은 즐겁게.',31)
text(M,H-128,'일은 더 편하게.',31,ACCENT)
para(M,H-154,'오리지널 게임과 맞춤형 소프트웨어를 만들고,<br/>팀의 실제 업무에 AI를 연결합니다.',CW,12,19)
image_card('assets/games/orbit-foundry-orbit.webp',M,459,CW,162)
text(M+13,472,'ORBIT FOUNDRY',10,white,'ArialBold')
text(M,434,'함께 만들 수 있는 것',16)
services=[
('01  게임 개발','독창적인 게임과 플레이 가능한 프로토타입을 제작합니다.'),
('02  맞춤형 애플리케이션','비즈니스와 고객, 팀의 업무에 맞춘 웹 애플리케이션과 대시보드를 개발합니다.'),
('03  내부 업무 도구','흩어진 정보를 연결하고 반복 업무를 간단하게 처리하는 도구를 만듭니다.'),
('04  AI 업무 연동','기존 도구에 AI 에이전트를 연결하고 담당자 검토를 포함한 업무 흐름을 설계합니다.')]
gap=14; col=(CW-gap)/2
for i,(title,body) in enumerate(services):
    x=M+(i%2)*(col+gap); top=410-(i//2)*107
    c.setFillColor(white);c.roundRect(x,top-94,col,94,6,fill=1,stroke=0)
    text(x+13,top-24,title,11)
    para(x+13,top-37,body,col-26,9.3,14,MUTED)
text(M,167,'함께 일하는 방식',15)
steps=[('이해하기','현재의 도구와 해결할 문제를 살펴보고 필요한 범위를 정합니다.'),('만들고 연결하기','업무 흐름과 소프트웨어를 구현하며 진행 내용을 함께 확인합니다.'),('도입하고 다듬기','실제 사용을 돕고 필요한 운영 지원 범위를 협의합니다.')]
sc=(CW-24)/3
for i,(title,body) in enumerate(steps):
    x=M+i*(sc+12);text(x,140,f'0{i+1}  {title}',10,ACCENT)
    para(x,126,body,sc,8.6,13,MUTED)
c.showPage()

base(2,'공개 작업 / SELECTED WORK')
text(M,H-86,'우리의 생각이',27)
text(M,H-121,'현실이 된 모습.',27)
para(M,H-146,'직접 만드는 게임과 창작 도구를 통해 아이디어를 구현합니다.',CW,11,17,MUTED)
projects=json.loads((ROOT/'content/games.json').read_text())
descs=[
('공장 · 증분 게임 / 개발 중','별 주위에 공장을 만들고 생산 시스템을 확장합니다. PC 브라우저 프로토타입과 Steam 페이지를 공개하고 있습니다.'),
('탐험 · 시뮬레이션','한국의 가정 어린이집을 1인칭으로 둘러보며 익숙한 공간의 세부를 발견하는 시뮬레이션입니다.'),
('자동화 · 시뮬레이션','고블린 동료를 고용하고 고철 처리를 자동화하며 걸어 다니는 고물상을 만드는 게임입니다.'),
('무료 CC0 3D 에셋 팩','가구와 장난감 등 일상 공간의 3D 소품 360개. GLB와 편집 가능한 Blender 형식으로 공개했습니다.')]
for i,(p,(kind,body)) in enumerate(zip(projects,descs)):
    x=M+(i%2)*(col+gap); top=645-(i//2)*279
    c.setFillColor(white);c.roundRect(x,top-260,col,260,6,fill=1,stroke=0)
    image_card(p['image'],x+10,top-135,col-20,125)
    title=p['title']['en']
    if len(title)>24:
        text(x+12,top-155,'Daycare & Everyday',12,INK,'ArialBold')
        text(x+12,top-171,'Interiors',12,INK,'ArialBold')
        yy=top-189
    else:
        text(x+12,top-158,title,12,INK,'ArialBold'); yy=top-178
    text(x+12,yy,kind,8.2,ACCENT)
    para(x+12,yy-12,body,col-24,9.1,14,MUTED)
    c.linkURL(p['url'],(x+10,top-135,x+col-10,top-10),relative=0,thickness=0)
text(M,63,'공개 프로젝트를 기반으로 작성했습니다. 프로젝트 이미지를 클릭하면 해당 공개 페이지로 이동합니다.',7.2,MUTED)
c.save()
reader=PdfReader(OUT)
assert len(reader.pages)==2
all_text='\n'.join(page.extract_text() for page in reader.pages)
for expected in ['주식회사 김치스탄스튜디오','AI 업무 연동','Orbit Foundry','Korean Kindergarten','Goblin Scrap Co.','360개']:
    assert expected in all_text, expected
assert 'kimmchistan@gmail.com' not in all_text
print(json.dumps({'path':str(OUT),'pages':len(reader.pages),'bytes':OUT.stat().st_size,'text_characters':len(all_text)},ensure_ascii=False))
