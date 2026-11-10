from pathlib import Path
from xml.sax.saxutils import escape
import json
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
from PIL import Image
from pypdf import PdfReader, PdfWriter

ROOT=Path.cwd(); OUT=ROOT/'output/pdf/kimchistan-studio-company-introduction.pdf'
SITE=json.loads((ROOT/'content/site.json').read_text())
COMPANY_WEBSITE='https://'+SITE['domain']+'/'
PARTS=ROOT/'tmp/pdfs/kmong-portfolio'; PARTS.mkdir(parents=True,exist_ok=True)
W,H=A4; M=42; CW=W-2*M
# Pretendard is the studio website's Korean type family. These compatible
# TrueType editions are from the upstream project's official distribution.
FONT_DIR=ROOT/'tmp/pdfs/design-review/fonts'
for name,weight in [('Text','Regular'),('Medium','Medium'),('SemiBold','SemiBold'),('Bold','Bold')]:
 pdfmetrics.registerFont(TTFont(name,str(FONT_DIR/f'Pretendard-{weight}.ttf')))
BG=HexColor('#F6F4EF'); INK=HexColor('#18312F'); MUTED=HexColor('#62706A')
ACCENT=HexColor('#CB492C'); LINE=HexColor('#D1D6CD'); DARK=HexColor('#173431')
PALE=HexColor('#EAEDE6'); SOFT=HexColor('#EBDDD0'); LIGHT=HexColor('#C7D4CC')
P=[
 dict(slug='john4-24',title='John 4:24',label='웹 서비스 및 React Native 모바일 앱',start='2026-04',ongoing=True,role='웹 서비스 구축·모바일 앱 개발',share=100,tech='React Native / Android / iOS',url='https://john4-24.com/',visual='john',description='곡 관리, 가사·코드·조옮김, 예배 큐시트·콘티와 팀 협업을 지원하는 웹 서비스를 구축했습니다. 기존 웹 서비스를 바탕으로 React Native 기반 Android·iOS 앱을 개발하고 있습니다.',detail='2026년 4월 착수한 프로젝트로, 중단 기간을 거쳐 현재 모바일 확장을 진행 중입니다. 모바일 앱은 2027년 출시를 목표로 합니다.'),
 dict(slug='agricultural-order-ai',title='농산물 주문 관리 AI',label='카카오 대화 기반 업무 자동화',start='2026-11',ongoing=True,role='업무 흐름 설계·AI 자동화 개발',share=100,tech='Linux / 카카오 연동 / AI 업무 자동화',url=None,visual='automation',description='농가가 여러 고객과 개별 대화하는 부담을 줄이기 위한 주문 관리 AI 프로젝트입니다. 주문 접수부터 재고·배송 확인과 거래 정보 전달까지 하나의 AI 대화 흐름으로 연결합니다.',detail='2026년 11월 착수했습니다. Linux 환경에서 카카오 대화를 연동하여 농가와 고객 사이에 필요한 업무를 자동화하는 방향으로 개발하고 있습니다.'),
 dict(slug='code4rena-security',title='Code4rena Security Research',label='Olas·Jupiter Lend 경쟁형 스마트 컨트랙트 보안 감사',start='2026-01',end='2026-03',ongoing=False,role='스마트 컨트랙트 보안 분석·취약점 보고',share=100,tech='스마트 컨트랙트 / 보안 분석 / 경쟁형 감사',url='https://code4rena.com/@kimchiwarrior',visual='audit',description='Code4rena 경쟁형 감사 대회에 참가하여 Olas와 Jupiter Lend 코드베이스를 분석했습니다. 공개 프로필 kimchiwarrior 기준 두 대회에서 Medium 등급 유효 취약점이 각 1건 인정되었습니다.',detail='공개 결과: Jupiter Lend 22위, Olas 53위. 이 페이지의 기간은 Olas·Jupiter Lend 감사 참여 이력을 기준으로 정리했습니다. 본인 보안 분석 및 보고 작업을 소개합니다.'),
 dict(slug='orbit-foundry',title='Orbit Foundry',label='공장·증분 게임 및 브라우저 프로토타입',start='2026-09',ongoing=True,role='게임 기획·개발',share=100,tech='LÖVE / Lua / HTML5',url='https://kimchistan.itch.io/orbit-foundry',image='assets/games/orbit-foundry-screen-1.webp',description='별 주위에 공장을 건설하고 생산 시스템을 확장하는 공장·증분 게임입니다. 생산 배치, 자동화와 리포지 성장을 중심으로 게임 시스템과 사용성을 구현했습니다.',detail='2026년 9월 PC 브라우저 프로토타입을 공개했습니다. Steam 페이지를 공개했으며 정식 게임을 개발하고 있습니다.'),
 dict(slug='korean-kindergarten',title='Korean Kindergarten',label='1인칭 어린이집 3D 시뮬레이션',start='2026-10',end='2026-10',ongoing=False,role='게임·실내 공간·상호작용 개발',share=100,tech='Godot / Blender / HTML5 / Windows / macOS',url='https://kimchistan.itch.io/korean-kindergarten',image='assets/games/korean-kindergarten-cover.webp',description='한국 가정 어린이집을 1인칭으로 탐험하는 3D 시뮬레이션입니다. 실내 공간을 둘러보고 장난감과 생활 소품을 집거나 배치하는 상호작용을 구현했습니다.',detail='브라우저·Windows·macOS 버전 제작을 완료하고 2026년 10월 공개했습니다. Game Gauntlet SIM Jam에 출품했습니다.'),
 dict(slug='goblin-scrap-co',title='Goblin Scrap Co.',label='자동화·증분 시뮬레이션 게임',start='2026-09',end='2026-10',ongoing=False,role='게임 기획·개발',share=100,tech='LÖVE / Lua / HTML5',url='https://kimchistan.itch.io/goblin-scrap-co',image='assets/games/goblin-scrap-co-cover.webp',description='고블린 동료를 고용하고 고철 처리를 자동화하여 작업장을 확장하는 게임입니다. 고용, 설비 업그레이드, 영구 연구와 자동 저장 등 성장 시스템을 구현했습니다.',detail='2026년 9월 공개하고 10월까지 업데이트했습니다. 브라우저 게임 개발을 완료했습니다.'),
 dict(slug='daycare-3d-props',title='Daycare & Everyday Interiors',label='무료 CC0 3D 소품 360개 에셋 팩',start='2026-10',end='2026-10',ongoing=False,role='3D 소품 제작·GLB/Blender 배포',share=100,tech='Blender / GLB / glTF / CC0',url='https://kimchistan.itch.io/daycare-everyday-interiors-240',image='assets/games/daycare-props-cover.webp',description='한국 가정 어린이집과 일상 실내 공간에 활용할 수 있는 가구, 장난감과 생활용품 등 3D 소품 360개를 제작했습니다. GLB와 편집 가능한 Blender 형식으로 공개했습니다.',detail='2026년 10월 무료 CC0 에셋 팩으로 배포했습니다. 에셋별 메타데이터, 한·영 인덱스와 가져오기 안내를 포함하고 GLB를 Godot에서 확인했습니다.'),
 dict(slug='secrets-of-the-tomb',title='Secrets of the Tomb',label='GBJAM 14 협업 프로젝트',start='2026-09',end='2026-09',ongoing=False,role='코드·레벨 디자인·라이팅',share=50,tech='브라우저 게임 / 퍼즐 / 게임보이 스타일',url='https://poigratzashel.itch.io/secrets-of-the-tomb',image='tmp/pdfs/secrets-of-the-tomb.png',description='무덤을 탐험하며 보물을 찾고 탈출하는 게임보이 스타일 퍼즐 게임입니다. GBJAM 14 참가를 위해 PoigratZashel과 공동 제작했습니다.',detail='김치스탄 스튜디오는 코드, 레벨 디자인과 라이팅을 담당했습니다. PoigratZashel은 아트·음악과 레벨 디자인을 담당했으며, 공동 프로젝트 참여도는 50%입니다.'),
 dict(slug='stone-by-stone',title='Stone by Stone',label='Ludum Dare 60 Jam 협업 프로젝트',start='2026-10',end='2026-10',ongoing=False,role='코드·레벨 디자인',share=50,tech='Godot / HTML5 / 2D 퍼즐',url='https://poigratzashel.itch.io/stone-by-stone',image='tmp/pdfs/stone-by-stone.png',description='여러 장치를 활용해 피라미드를 건설하는 퍼즐 게임입니다. Ludum Dare 60 Jam 참가를 위해 PoigratZashel과 공동 제작했습니다.',detail='김치스탄 스튜디오는 코드와 레벨 디자인을 담당했습니다. PoigratZashel은 아트·음악과 레벨 디자인을 담당했으며, 공동 프로젝트 참여도는 50%입니다.'),
 dict(slug='animal-fighters-club',title='Animal Fighters Club',label='동물 캐릭터 아레나 대전 프로토타입',start='2026-05',end='2026-10',ongoing=False,role='게임 기획·개발',share=100,tech='Bevy Engine / Rust / HTML5',url='https://kimchistan.itch.io/afc',image='tmp/pdfs/afc-gameplay-current.png',description='동물 캐릭터가 등장하는 아레나 대전 브라우저 프로토타입입니다. 싱글 플레이와 로컬 1대1 대전, 약·강·특수 공격과 콤보, 음식 아이템을 구현했습니다.',detail='키보드와 컨트롤러 입력을 지원합니다. 2026년 5월 공개 후 업데이트를 진행하고 10월까지 공개 페이지를 정비했습니다. 프로토타입 제작을 완료했습니다.')
]

def txt(c,x,y,s,size=10,color=INK,font='Text'):
 c.setFillColor(color);c.setFont(font,size);c.drawString(x,y,s)

def tracked(c,x,y,s,size=8,color=MUTED,spacing=.9,font='SemiBold'):
 c.saveState();c.setFillColor(color);t=c.beginText(x,y);t.setFont(font,size);t.setCharSpace(spacing);t.textOut(s);t.setCharSpace(0);c.drawText(t);c.restoreState()

def para(c,x,top,s,w,size=10.5,leading=17,color=INK,font='Text'):
 # Wrap at Korean word boundaries as well as English spaces; this avoids
 # short trailing syllables stranded at the beginning of a new line.
 style=ParagraphStyle('body',fontName=font,fontSize=size,leading=leading,textColor=color,wordWrap=None,splitLongWords=False,spaceBefore=0,spaceAfter=0)
 p=Paragraph(s,style);_,height=p.wrap(w,1000);p.drawOn(c,x,top-height)
 return height

def rule(c,x,y,w,color=LINE,width=.65):
 c.setStrokeColor(color);c.setLineWidth(width);c.line(x,y,x+w,y)

def base(c,page,section):
 c.setFillColor(BG);c.rect(0,0,W,H,fill=1,stroke=0)
 txt(c,M,H-34,'KIMCHISTAN STUDIO',10.7,INK,'Bold')
 t_width=pdfmetrics.stringWidth(section,'Medium',7.6)
 txt(c,W-M-t_width,H-34,section,7.6,MUTED,'Medium')
 rule(c,M,H-49,CW)
 rule(c,M,42,CW)
 txt(c,M,26,'주식회사 김치스탄스튜디오  /  대한민국 경기도 고양시',7.1,MUTED)
 txt(c,W-M-12,26,f'{page:02d}',8.1,INK,'SemiBold')

def draw_image(c,path,x,top,w):
 """Use the complete source image at its native aspect ratio, without crops."""
 im=Image.open(ROOT/path).convert('RGB')
 h=w*im.height/im.width
 c.drawImage(ImageReader(im),x,top-h,width=w,height=h,mask='auto')
 return h

def project_header(c,p,index,page):
 categories={
  'john4-24':'WEB & MOBILE', 'agricultural-order-ai':'AI AUTOMATION',
  'code4rena-security':'SMART CONTRACT SECURITY', 'orbit-foundry':'FACTORY & INCREMENTAL GAME',
  'korean-kindergarten':'3D SIMULATION', 'goblin-scrap-co':'AUTOMATION & INCREMENTAL GAME',
  'daycare-3d-props':'3D ASSET PACK', 'secrets-of-the-tomb':'GAME JAM COLLABORATION',
  'stone-by-stone':'GAME JAM COLLABORATION', 'animal-fighters-club':'ARENA PROTOTYPE'
 }
 base(c,page,'회사 포트폴리오 / SELECTED WORKS')
 tracked(c,M,H-78,f'{index:02d}  /  '+categories[p['slug']],8.4,ACCENT,.65)
 title_size=30
 while pdfmetrics.stringWidth(p['title'],'Bold',title_size)>CW and title_size>23:
  title_size-=.25
 txt(c,M,H-115,p['title'],title_size,INK,'Bold')
 txt(c,M,H-139,p['label'],11.6,MUTED,'Medium')
 rule(c,M,H-158,CW)
 period=p['start'].replace('-','.')+' - '+('진행 중' if p['ongoing'] else p['end'].replace('-','.'))
 status='진행 중' if p['ongoing'] else ('프로토타입 완료' if p['slug']=='animal-fighters-club' else '완료')
 for x,label,value in [(M,'진행 기간',period),(M+238,'상태',status),(M+414,'참여도',str(p['share'])+'%')]:
  txt(c,x,H-174,label,7.7,MUTED,'Medium')
  txt(c,x,H-192,value,10.5,ACCENT if label=='상태' and p['ongoing'] else INK,'SemiBold')
 rule(c,M,H-205,CW)


def role_rail(c,p,x,top,w):
 txt(c,x,top,'담당 역할',8.1,ACCENT,'SemiBold')
 role_text=escape(p['role'])
 if p['slug']=='code4rena-security':
  role_text='스마트 컨트랙트 보안 분석·<br/>취약점 보고'
 rh=para(c,x,top-15,role_text,w,11,17.5,INK,'SemiBold')
 ty=top-15-rh-24
 txt(c,x,ty,'관련 기술',8.1,ACCENT,'SemiBold')
 th=para(c,x,ty-15,escape(p['tech']),w,9.5,15.4,MUTED,'Medium')
 return ty-15-th


def project_story(c,p,top):
 left_w=320;right_x=M+348;right_w=CW-348
 txt(c,M,top,'프로젝트 소개',9,ACCENT,'SemiBold')
 desc_h=para(c,M,top-18,escape(p['description']),left_w,10.7,17.4)
 detail_top=top-18-desc_h-15
 detail_h=para(c,M,detail_top,escape(p['detail']),left_w,9.7,15.7,MUTED)
 rule(c,right_x-14,top+3,0)
 c.setStrokeColor(LINE);c.setLineWidth(.65);c.line(right_x-14,top+3,right_x-14,min(top-147,detail_top-detail_h))
 rail_bottom=role_rail(c,p,right_x,top,right_w)
 bottom=min(detail_top-detail_h,rail_bottom)
 assert bottom>103,(p['slug'],'story too long',bottom)
 return bottom


def link_footer(c,p):
 if p['url']:
  rule(c,M,105,CW)
  txt(c,M,87,'공개 프로젝트 / 결과',7.7,ACCENT,'SemiBold')
  txt(c,M,69,p['url'],8.9,INK,'Medium')
  # The visible URL and its full row are clickable in the combined and
  # extracted individual project PDFs.
  c.linkURL(p['url'],(M,58,W-M,98),relative=0,thickness=0)


def service_visual(c,p,top):
 h=278;y=top-h
 if p['visual']=='john':
  c.setFillColor(DARK);c.rect(M,y,CW,h,fill=1,stroke=0)
  tracked(c,M+22,top-25,'WEB SERVICE',8.3,LIGHT,.9)
  txt(c,M+22,top-67,'예배 준비와',25,white,'Bold')
  txt(c,M+22,top-101,'팀 협업을 연결',25,white,'Bold')
  rows=[('곡 관리','가사·코드·조옮김'),('예배 기획','큐시트·콘티'),('팀 협업','역할·소통')]
  rx=M+304
  for i,(title,subtitle) in enumerate(rows):
   yy=top-41-i*48
   txt(c,rx,yy,f'0{i+1}',8.3,HexColor('#F39270'),'SemiBold')
   txt(c,rx+25,yy,title,11.7,white,'SemiBold')
   txt(c,rx+25,yy-17,subtitle,9.2,LIGHT)
  rule(c,M+22,y+73,CW-44,HexColor('#4B6460'),.55)
  tracked(c,M+22,y+47,'MOBILE EXPANSION',8.1,HexColor('#F39270'),.8)
  txt(c,M+22,y+24,'React Native  /  Android · iOS',15,white,'SemiBold')
 elif p['visual']=='automation':
  c.setFillColor(SOFT);c.rect(M,y,CW,h,fill=1,stroke=0)
  tracked(c,M+22,top-26,'ORDER WORKFLOW',8.3,ACCENT,.8)
  txt(c,M+22,top-69,'주문부터 전달까지,',22,INK,'Bold')
  txt(c,M+22,top-99,'하나의 AI 대화 흐름',22,INK,'Bold')
  para(c,M+22,top-129,'Linux 환경에서<br/>카카오 대화를 연동하는<br/>농가 주문 관리 자동화',205,11,18,MUTED,'Medium')
  rx=M+284
  labels=['주문 접수','농가 재고·배송 확인','고객에게 입금 계좌 안내','농가에 수령 정보 전달']
  for i,label in enumerate(labels):
   yy=top-42-i*53
   txt(c,rx,yy,f'0{i+1}',8.4,ACCENT,'SemiBold')
   para(c,rx+29,yy+10,escape(label),CW-284-47,11.3,17.2,INK,'SemiBold')
   if i<3:rule(c,rx,yy-17,CW-306,HexColor('#CEBCAB'),.5)
 elif p['visual']=='audit':
  c.setFillColor(DARK);c.rect(M,y,CW,h,fill=1,stroke=0)
  tracked(c,M+22,top-25,'CODE4RENA  /  PUBLIC RESULTS',8.3,LIGHT,.8)
  for i,(name,rank) in enumerate([('Jupiter Lend','#22'),('Olas','#53')]):
   xx=M+22+i*251
   txt(c,xx,top-61,name,15,white,'SemiBold')
   txt(c,xx,top-131,rank,55,white,'Bold')
   txt(c,xx,top-156,'공개 순위',8.3,LIGHT,'Medium')
   txt(c,xx,top-196,'Medium 등급 유효 취약점 1건',10.1,white,'Medium')
  c.setStrokeColor(HexColor('#4B6460'));c.setLineWidth(.55);c.line(M+CW/2,top-48,M+CW/2,y+67)
  rule(c,M+22,y+50,CW-44,HexColor('#4B6460'),.55)
  txt(c,M+22,y+24,'Olas · Jupiter Lend 경쟁형 스마트 컨트랙트 보안 감사',10.1,LIGHT,'Medium')
 return h


def portrait_visual(c,p,top):
 # Compact artwork gets its own asymmetric composition rather than the
 # letterboxing used in the previous document. The entire image is visible.
 image_w=360
 h=draw_image(c,p['image'],M,top,image_w)
 x=M+385;w=CW-385
 tracked(c,x,top-11,'PROJECT NOTES',7.7,ACCENT,.6)
 if p['slug']=='daycare-3d-props':
  txt(c,x,top-68,'360',47,INK,'Bold')
  txt(c,x,top-92,'3D 소품',12,INK,'SemiBold')
  rule(c,x,top-117,w)
  txt(c,x,top-151,'CC0',25,INK,'Bold')
  para(c,x,top-171,'무료 에셋 팩<br/>GLB + Blender',w,10.2,16.5,MUTED,'Medium')
 elif p['slug']=='goblin-scrap-co':
  for i,s in enumerate(['고용','자동화','성장']):txt(c,x,top-55-i*38,s,24,INK,'Bold')
  rule(c,x,top-156,w)
  para(c,x,top-174,'브라우저 게임<br/>개발 완료',w,10.6,17.5,MUTED,'Medium')
 else:
  txt(c,x,top-56,'GBJAM',21,INK,'Bold')
  txt(c,x,top-101,'14',43,INK,'Bold')
  rule(c,x,top-125,w)
  para(c,x,top-143,'PoigratZashel과<br/>공동 제작',w,10.2,17,MUTED,'Medium')
  txt(c,x,top-218,'50%',28,INK,'Bold')
  txt(c,x,top-238,'공동 프로젝트 참여도',8.5,MUTED,'Medium')
 return h


def cover(c):
 base(c,1,'회사소개 / COMPANY PROFILE')
 txt(c,M,H-100,'게임과 서비스를 만들고,',29,INK,'Bold')
 txt(c,M,H-140,'일의 흐름을 연결합니다.',29,ACCENT,'Bold')
 para(c,M,H-164,'웹·모바일 서비스, AI 업무 자동화, Web3와 게임 개발 경험을<br/>하나의 크리에이티브 테크 스튜디오에 담았습니다.',CW,11,18.3,INK,'Medium')
 draw_image(c,'assets/games/orbit-foundry-orbit.webp',M,627,CW)
 tracked(c,M,441,'CAPABILITIES',7.9,ACCENT,.9)
 txt(c,M+113,440,'함께 만들 수 있는 것',14.2,INK,'Bold')
 services=[
  ('웹·모바일 서비스','React·React Native, Django와 JavaScript·TypeScript를 활용한 맞춤형 서비스 개발'),
  ('AI 업무 자동화','기존 도구와 AI를 연결하는 업무 흐름 설계, Linux 환경 연동과 카카오 기반 주문 관리'),
  ('Web3·보안 분석','Rust·Solidity, Ethereum·Solana, 블록체인과 스마트 컨트랙트 개발 및 경쟁형 보안 감사'),
  ('게임·3D 콘텐츠','Godot·LÖVE·Bevy, Lua·Rust, Blender를 활용한 게임과 프로토타입, 3D 소품 제작')]
 col=(CW-26)/2
 for i,(title,body) in enumerate(services):
  x=M+(i%2)*(col+26);top=420-(i//2)*77
  rule(c,x,top,col)
  txt(c,x,top-22,f'0{i+1}',7.8,ACCENT,'SemiBold')
  txt(c,x+26,top-23,title,11.8,INK,'Bold')
  para(c,x+26,top-35,body,col-26,9.4,14.5,MUTED)
 c.setFillColor(DARK);c.rect(M,201,CW,60,fill=1,stroke=0)
 txt(c,M+14,238,'Code4rena',13.6,white,'Bold')
 txt(c,M+14,219,'공개 보안 감사 결과',8.1,LIGHT,'Medium')
 txt(c,M+181,237,'유효 High 2건 · Medium 3건',12.2,white,'SemiBold')
 txt(c,M+181,218,'Rujira 13위 · Jupiter Lend 22위 · Olas 53위',9.4,LIGHT,'Medium')
 para(c,M,182,'문제와 도구를 이해하고, 필요한 범위를 함께 정합니다.<br/>개발 과정과 결과를 공유하며 실제 도입과 운영을 돕습니다.',CW,10,16.3,INK,'Medium')
 rule(c,M,132,CW)
 tracked(c,M,115,'CONTACT',7.5,ACCENT,.85)
 txt(c,M,96,'이메일',7.7,MUTED,'Medium');txt(c,M+49,96,SITE['email'],9.6,INK,'Medium')
 txt(c,M+308,96,'전화',7.7,MUTED,'Medium');txt(c,M+342,96,SITE['phone']['ko'],9.6,INK,'Medium')
 txt(c,M,78,'웹사이트',7.7,MUTED,'Medium');txt(c,M+49,78,COMPANY_WEBSITE,9.6,INK,'Medium')
 txt(c,M,60,'주소',7.7,MUTED,'Medium');txt(c,M+49,60,SITE['address']['ko'],9.1,INK,'Medium')
 c.linkURL('mailto:'+SITE['email'],(M+49,92,M+278,107),relative=0,thickness=0)
 c.linkURL('tel:+82319118190',(M+342,92,W-M,107),relative=0,thickness=0)
 c.linkURL(COMPANY_WEBSITE,(M+49,74,M+278,89),relative=0,thickness=0)
 c.showPage()


c=canvas.Canvas(str(OUT),pagesize=A4,pageCompression=1)
c.setTitle('김치스탄 스튜디오 | 회사소개 및 포트폴리오');c.setAuthor('KIMCHISTAN STUDIO')
c.setSubject('웹·모바일, AI 자동화, Web3·보안 감사, 게임 개발')
cover(c)
for index,p in enumerate(P,1):
 project_header(c,p,index,index+1)
 image_top=H-223
 if p.get('visual'):
  hero_h=service_visual(c,p,image_top)
 elif p['slug'] in ['goblin-scrap-co','daycare-3d-props','secrets-of-the-tomb']:
  hero_h=portrait_visual(c,p,image_top)
 else:
  hero_h=draw_image(c,p['image'],M,image_top,CW)
 project_story(c,p,image_top-hero_h-25)
 link_footer(c,p)
 c.showPage()
c.save()

r=PdfReader(OUT);assert len(r.pages)==11
text='\n'.join(p.extract_text() for p in r.pages)
assert 'Unity' not in text and '대표가' not in text
assert '진행 중인 업무 자동화 프로젝트 · 고객·수령인·계좌의 실제 정보는 포함하지 않았습니다.' not in text
assert '공개 프로젝트와 제공된 회사 경험 기준 · 보안 감사 결과 확인: 2026.11.06' not in text
for item in P:assert item['title'] in text
for value in [SITE['email'],SITE['phone']['ko'],SITE['address']['ko'],COMPANY_WEBSITE]:assert value in r.pages[0].extract_text()
assert '01099838190' not in text
for i,p in enumerate(P,1):
 w=PdfWriter();w.add_page(r.pages[i]);w.add_metadata({'/Title':p['title']+' | KIMCHISTAN STUDIO','/Author':'KIMCHISTAN STUDIO'})
 target=PARTS/(p['slug']+'.pdf')
 with target.open('wb') as f:w.write(f)
 p['attachment']=str(target)
(ROOT/'tmp/pdfs/kmong-project-data.json').write_text(json.dumps(P,ensure_ascii=False,indent=2))
print(json.dumps({'company_pdf':str(OUT),'pages':len(r.pages),'portfolio_files':len(P),'bytes':OUT.stat().st_size},ensure_ascii=False))
