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

# The archived eight-page proposal is retained. The active eleven-page source
# contains the integrated UI/UX narrative and is the canonical editable source.
target=WORK/'create_proposal_concept.py'
assert target.exists()
assert 'assert len(reader.pages) == 11' in target.read_text()
runpy.run_path(str(target),run_name='__main__')

proposal=ROOT/'output/pdf/kmong-227326-proposal.pdf'
pdf=PdfReader(proposal)
assert len(pdf.pages)==11
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
    'proposal':str(proposal),'proposal_pages':11,
    'presentation_pdf':str(deck_path),'presentation_pages':3,
    'presentation_pptx':str(ROOT/'output/presentations/고깃집예약주문-UIUX콘셉트.pptx'),
    'asset_bundle':str(bundle),'image_generation_mode':'UI/device concept with directly composited real stock food photography',
    'proposal_visual_review_complete':False,'presentation_visual_review_complete':False,
    'original_proposal_sha256':hashlib.sha256((ROOT/'output/pdf/kmong-227326-proposal-v1.pdf').read_bytes()).hexdigest(),
    'concept_pdf_sha256':hashlib.sha256(deck_path.read_bytes()).hexdigest(),
}
(WORK/'concept-bundle-qa.json').write_text(json.dumps(record,ensure_ascii=False,indent=2))
print(json.dumps(record,ensure_ascii=False,indent=2))
