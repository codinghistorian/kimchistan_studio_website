from __future__ import annotations

import hashlib
import json
import runpy
import zipfile
from pathlib import Path

from PIL import Image
from pypdf import PdfReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor

ROOT=Path(__file__).resolve().parents[3]
WORK=ROOT/'tmp/pdfs/kmong-227326'
ASSETS=ROOT/'output/design/kmong-227326'
CONTENT=json.loads((WORK/'concept-content.json').read_text())
JPEG=WORK/'concept-images'
JPEG.mkdir(exist_ok=True)
for slide in CONTENT['slides']:
    source=ASSETS/slide['image']
    with Image.open(source) as image:
        image.convert('RGB').save(JPEG/(source.stem+'.jpg'),quality=95,subsampling=0,optimize=True)

# Landscape case presentation, with selectable native Korean text and the original
# generated mockups. Reuse the content and exact placements of the editable deck.
for weight in ['Regular','Bold']:
    pdfmetrics.registerFont(TTFont('Concept'+weight,str(ROOT/f'tmp/pdfs/design-review/fonts/Pretendard-{weight}.ttf')))
deck_path=ROOT/'output/pdf/고깃집예약주문-UIUX콘셉트.pdf'
deck=canvas.Canvas(str(deck_path),pagesize=(1200,675),pageCompression=1)
deck.setTitle(CONTENT['title'])
deck.setAuthor('주식회사 김치스탄스튜디오')
deck.setCreator('KIMCHISTAN STUDIO')
deck._doc.info.producer='ReportLab'

def deck_text(value,x,top,width,size,bold=False,color='#18352F',leading=None):
    font='ConceptBold' if bold else 'ConceptRegular'
    deck.setFont(font,size)
    deck.setFillColor(HexColor(color))
    leading=leading or size*1.22
    for index,line in enumerate(value.split('\n')):
        assert pdfmetrics.stringWidth(line,font,size)<=width+.5,(line,width)
        deck.drawString(x,900-top-size*.82-index*leading,line)

for data in CONTENT['slides']:
    deck.saveState()
    deck.scale(.75,.75)
    deck.setFillColor(HexColor('#F7F5F0'))
    deck.rect(0,0,1600,900,fill=1,stroke=0)
    deck_text(data['title'],70,44,1460,52,True)
    deck_text(data['subtitle'],70,126,1460,25,color='#586D65')
    y=235 if len(data['sections'])==3 else 265
    gap=166 if len(data['sections'])==3 else 202
    for section in data['sections']:
        deck_text(section['title'],70,y,370,28,True)
        deck_text(section['body'],70,y+52,370,24,color='#586D65')
        y+=gap
    with Image.open(ASSETS/data['image']) as image:
        scale=min(1060/image.width,650/image.height)
        width,height=image.width*scale,image.height*scale
    x=480+(1060-width)/2
    top=180+(650-height)/2
    deck.drawImage(str(JPEG/(Path(data['image']).stem+'.jpg')),x,900-top-height,width=width,height=height)
    deck_text(CONTENT['disclosure'],70,852,1460,17,color='#586D65')
    deck.restoreState()
    deck.showPage()
deck.save()
assert len(PdfReader(deck_path).pages)==3

# Retain the original eight-page proposal and its authoring source; create a
# reproducible ten-page revision with three concept pages replacing one wireframe.
source=(WORK/'archive-v1/create_proposal.py').read_text()
assert source.count('assert len(reader.pages) == 8')==1
source=source.replace('assert len(reader.pages) == 8','assert len(reader.pages) == 10')
source=source.replace('7페이지의 조건부 별도 예산','9페이지의 조건부 별도 예산')
source=source.replace('사용료는 6페이지에, 향후 PG 개발과 이용 비용은 7페이지에','사용료는 8페이지에, 향후 PG 개발과 이용 비용은 9페이지에')
for number in range(8,2,-1):
    needle=f'y = page({number},'
    assert source.count(needle)==1,(number,source.count(needle))
    source=source.replace(needle,f'y = page({number+2},')
    source=source.replace(f'# PAGE {number} -',f'# PAGE {number+2} -')

start=source.index('# PAGE 2 - Vector mockups')
end=source.index('# PAGE 5 - Capacity',start)
replacement=r'''# PAGES 2-4 - Proposal-specific UI/UX concept, not completed client work.
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


'''
source=source[:start]+replacement+source[end:]
target=WORK/'create_proposal_concept.py'
target.write_text(source)
runpy.run_path(str(target),run_name='__main__')

proposal=ROOT/'output/pdf/kmong-227326-proposal.pdf'
pdf=PdfReader(proposal)
assert len(pdf.pages)==10
for number in [1,2,3]:
    assert '콘셉트' in pdf.pages[number].extract_text()
    assert list(pdf.pages[number].images),number

# Source assets and the exact prompts remain local and reusable.
bundle=ROOT/'output/design/고깃집예약주문-목업원본.zip'
with zipfile.ZipFile(bundle,'w',zipfile.ZIP_DEFLATED) as archive:
    for source in sorted(ASSETS.iterdir()):
        if source.is_file():archive.write(source,source.name)
    stock=ASSETS/'stock'
    if (stock/'sources.json').exists():
        archive.write(stock/'sources.json','stock/sources.json')
        for item in json.loads((stock/'sources.json').read_text()):
            if item.get('used_in_current_mockups'):
                archive.write(stock/item['file'],'stock/'+item['file'])

record={
    'proposal':str(proposal),'proposal_pages':10,
    'presentation_pdf':str(deck_path),'presentation_pages':3,
    'presentation_pptx':str(ROOT/'output/presentations/고깃집예약주문-UIUX콘셉트.pptx'),
    'asset_bundle':str(bundle),'image_generation_mode':'UI/device concept with directly composited real stock food photography',
    'proposal_visual_review_complete':False,'presentation_visual_review_complete':False,
    'original_proposal_sha256':hashlib.sha256((ROOT/'output/pdf/kmong-227326-proposal-v1.pdf').read_bytes()).hexdigest(),
    'concept_pdf_sha256':hashlib.sha256(deck_path.read_bytes()).hexdigest(),
}
(WORK/'concept-bundle-qa.json').write_text(json.dumps(record,ensure_ascii=False,indent=2))
print(json.dumps(record,ensure_ascii=False,indent=2))
