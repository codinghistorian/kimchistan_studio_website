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
from PIL import Image, ImageOps
from pypdf import PdfReader, PdfWriter

ROOT=Path.cwd(); OUT=ROOT/'output/pdf/kimchistan-studio-company-introduction.pdf'
SITE=json.loads((ROOT/'content/site.json').read_text())
COMPANY_WEBSITE='https://'+SITE['domain']+'/'
PARTS=ROOT/'tmp/pdfs/kmong-portfolio'; PARTS.mkdir(parents=True,exist_ok=True)
W,H=A4; M=42; CW=W-2*M
BG=HexColor('#F4F1EB'); INK=HexColor('#192B34'); MUTED=HexColor('#596870'); ACCENT=HexColor('#D84C2B'); LINE=HexColor('#D9DDD8'); DARK=HexColor('#10242C')
pdfmetrics.registerFont(TTFont('Gothic','/System/Library/Fonts/Supplemental/Arial Unicode.ttf'))
pdfmetrics.registerFont(TTFont('ArialBold','/System/Library/Fonts/Supplemental/Arial Bold.ttf'))
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

def txt(c,x,y,s,size=10,color=INK,font='Gothic'):
 c.setFillColor(color);c.setFont(font,size);c.drawString(x,y,s)
def para(c,x,y,s,w,size=10,leading=16,color=INK):
 p=Paragraph(s,ParagraphStyle('p',fontName='Gothic',fontSize=size,leading=leading,textColor=color,wordWrap='CJK',splitLongWords=False));_,h=p.wrap(w,1000);p.drawOn(c,x,y-h);return h
def base(c,page,section):
 c.setFillColor(BG);c.rect(0,0,W,H,fill=1,stroke=0);txt(c,M,H-37,'KIMCHISTAN STUDIO',11,INK,'ArialBold');txt(c,W-M-116,H-37,section,7.5,MUTED)
 c.setStrokeColor(LINE);c.setLineWidth(.6);c.line(M,42,W-M,42);txt(c,M,27,'주식회사 김치스탄스튜디오  |  대한민국 경기도 고양시',7.5,MUTED);txt(c,W-M-13,27,f'{page:02d}',8,MUTED,'ArialBold')
def image(c,path,x,y,w,h,cover=False):
 im=Image.open(ROOT/path).convert('RGB')
 if cover:im=ImageOps.fit(im,(round(w*3),round(h*3)),method=Image.Resampling.LANCZOS);dw,dh=w,h
 else:
  ratio=min(w/im.width,h/im.height);dw,dh=im.width*ratio,im.height*ratio
 c.setFillColor(DARK);c.roundRect(x,y,w,h,6,fill=1,stroke=0);c.drawImage(ImageReader(im),x+(w-dw)/2,y+(h-dh)/2,width=dw,height=dh,mask='auto')
def visual(c,p,x,y,w,h):
 if p.get('image'):image(c,p['image'],x,y,w,h);return
 c.setFillColor(DARK);c.roundRect(x,y,w,h,6,fill=1,stroke=0)
 typ=p['visual']
 if typ=='john':
  txt(c,x+21,y+h-33,'WEB + MOBILE',13,white,'ArialBold');txt(c,x+21,y+h-56,'예배 준비와 팀 협업을 연결하는 서비스 구성',11,white)
  labels=[('곡 관리','가사·코드·조옮김'),('예배 기획','큐시트·콘티'),('팀 협업','역할·소통'),('모바일 확장','React Native')]
  cw=(w-56)/2
  for i,(a,b) in enumerate(labels):
   xx=x+20+(i%2)*(cw+16);yy=y+22+(1-i//2)*68;c.setFillColor(HexColor('#24404B'));c.roundRect(xx,yy,cw,57,5,fill=1,stroke=0);txt(c,xx+12,yy+32,a,11,white);txt(c,xx+12,yy+13,b,8.5,HexColor('#C9D7DA'))
 elif typ=='automation':
  txt(c,x+21,y+h-32,'ORDER WORKFLOW',13,white,'ArialBold');txt(c,x+21,y+h-55,'Linux·카카오·AI 기반 업무 흐름 설계',10,white)
  labels=['주문 접수','농가 재고·배송 확인','고객에게 입금 계좌 안내','농가에 수령 정보 전달']
  for i,l in enumerate(labels):
   yy=y+h-96-i*36;c.setFillColor(HexColor('#24404B'));c.roundRect(x+20,yy,w-40,27,4,fill=1,stroke=0);txt(c,x+32,yy+9,f'0{i+1}  {l}',10,white)
 elif typ=='audit':
  txt(c,x+21,y+h-32,'VALIDATED MEDIUM FINDINGS',12,white,'ArialBold');txt(c,x+21,y+h-55,'Code4rena 공개 경쟁형 감사 결과',10,white)
  for i,(name,rank) in enumerate([('Jupiter Lend','#22'),('Olas','#53')]):
   xx=x+20+i*((w-54)/2+14);cw=(w-54)/2;c.setFillColor(HexColor('#24404B'));c.roundRect(xx,y+30,cw,123,5,fill=1,stroke=0);txt(c,xx+14,y+126,name,12,white,'ArialBold');txt(c,xx+14,y+85,rank,30,white,'ArialBold');txt(c,xx+14,y+50,'유효 Medium 1건',10,white)
 else:
  txt(c,x+21,y+h-35,'ARENA BRAWLER',20,white,'ArialBold');txt(c,x+21,y+h-64,'프로토타입 기능 구성',10,white)
  labels=['싱글 플레이','로컬 1대1 대전','콤보·특수 공격','음식 아이템','키보드 입력','컨트롤러 입력'];cw=(w-54)/2
  for i,l in enumerate(labels):
   xx=x+20+(i%2)*(cw+14);yy=y+25+(2-i//2)*44;c.setFillColor(HexColor('#24404B'));c.roundRect(xx,yy,cw,33,4,fill=1,stroke=0);txt(c,xx+12,yy+12,l,10,white)

c=canvas.Canvas(str(OUT),pagesize=A4,pageCompression=1);c.setTitle('김치스탄 스튜디오 | 회사소개 및 포트폴리오');c.setAuthor('KIMCHISTAN STUDIO');c.setSubject('웹·모바일, AI 자동화, Web3·보안 감사, 게임 개발')
base(c,1,'회사소개 / COMPANY')
txt(c,M,H-89,'게임과 서비스를 만들고,',28);txt(c,M,H-128,'일의 흐름을 연결합니다.',28,ACCENT)
para(c,M,H-153,'웹·모바일 서비스, AI 업무 자동화, Web3와 게임 개발 경험을<br/>하나의 크리에이티브 테크 스튜디오에 담았습니다.',CW,11.5,19)
image(c,'assets/games/orbit-foundry-orbit.webp',M,493,CW,130,cover=True)
txt(c,M,465,'함께 만들 수 있는 것',15)
services=[('웹·모바일 서비스','React·React Native, Django와 JavaScript·TypeScript를 활용한 맞춤형 서비스 개발'),('AI 업무 자동화','기존 도구와 AI를 연결하는 업무 흐름 설계, Linux 환경 연동과 카카오 기반 주문 관리'),('Web3·보안 분석','Rust·Solidity, Ethereum·Solana, 블록체인과 스마트 컨트랙트 개발 및 경쟁형 보안 감사'),('게임·3D 콘텐츠','Godot·LÖVE·Bevy, Lua·Rust, Blender를 활용한 게임과 프로토타입, 3D 소품 제작')]
col=(CW-14)/2
for i,(a,b) in enumerate(services):
 x=M+(i%2)*(col+14);top=443-(i//2)*100;c.setFillColor(white);c.roundRect(x,top-88,col,88,6,fill=1,stroke=0);txt(c,x+13,top-24,a,11);para(c,x+13,top-37,b,col-26,9,14,MUTED)
txt(c,M,218,'공개 결과로 확인하는 보안 감사 경험',13)
para(c,M,199,'Code4rena: 유효 High 2건 · Medium 3건<br/>Rujira 13위 · Jupiter Lend 22위 · Olas 53위',CW,10,17,MUTED)
para(c,M,154,'문제와 도구를 이해하고, 필요한 범위를 함께 정합니다.<br/>개발 과정과 결과를 공유하며 실제 도입과 운영을 돕습니다.',CW,9.5,14)
c.setFillColor(white);c.roundRect(M,54,CW,65,6,fill=1,stroke=0)
txt(c,M+12,102,'이메일',8,MUTED);txt(c,M+57,102,SITE['email'],9.5)
txt(c,M+278,102,'전화',8,MUTED);txt(c,M+314,102,SITE['phone']['ko'],9.5)
txt(c,M+12,84,'웹사이트',8,MUTED);txt(c,M+57,84,COMPANY_WEBSITE,9.5)
txt(c,M+12,66,'주소',8,MUTED);txt(c,M+57,66,SITE['address']['ko'],9)
c.linkURL('mailto:'+SITE['email'],(M+57,99,M+244,113),relative=0,thickness=0)
c.linkURL('tel:+82319118190',(M+314,99,W-M-12,113),relative=0,thickness=0)
c.linkURL(COMPANY_WEBSITE,(M+57,81,M+244,95),relative=0,thickness=0)
c.showPage()
for n,p in enumerate(P,2):
 base(c,n,'프로젝트 / PORTFOLIO');txt(c,M,H-76,'SELECTED WORK',9,ACCENT,'ArialBold')
 titlefont='ArialBold' if p['title'].isascii() else 'Gothic';titleSize=24 if len(p['title'])<28 else 22
 txt(c,M,H-112,p['title'],titleSize,INK,titlefont);txt(c,M,H-137,p['label'],11,MUTED)
 c.setFillColor(white);c.roundRect(M,H-214,CW,54,6,fill=1,stroke=0)
 period=p['start'].replace('-','.')+' - '+('진행 중' if p['ongoing'] else p['end'].replace('-','.'))
 for i,(a,b) in enumerate([('진행 기간',period),('상태','진행 중' if p['ongoing'] else ('프로토타입 완료' if p['slug']=='animal-fighters-club' else '완료')),('참여도',str(p['share'])+'%')]):
  x=M+13+i*(CW/3);txt(c,x,H-178,a,8,MUTED);txt(c,x,H-199,b,9.5)
 visual(c,p,M,374,CW,239)
 txt(c,M,349,'프로젝트 소개',13);bh=para(c,M,331,escape(p['description']),CW,10.5,17)
 yy=331-bh-20;txt(c,M,yy,'담당 역할',10,ACCENT);para(c,M+77,yy+3,escape(p['role']),CW-77,10,15)
 yy-=29;txt(c,M,yy,'관련 기술',10,ACCENT);para(c,M+77,yy+3,escape(p['tech']),CW-77,9.5,15)
 yy-=30;dh=para(c,M,yy,escape(p['detail']),CW,9.6,15,MUTED)
 assert yy-dh>104,(p['slug'],yy,dh)
 if p['url']:
  txt(c,M,84,'공개 프로젝트 / 결과',8,ACCENT);para(c,M,70,escape(p['url']),CW,8.5,11,MUTED);c.linkURL(p['url'],(M,54,W-M,94),relative=0,thickness=0)
 c.showPage()
c.save()
r=PdfReader(OUT);assert len(r.pages)==11
text='\n'.join(p.extract_text() for p in r.pages)
assert 'Unity' not in text and '대표가' not in text
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
