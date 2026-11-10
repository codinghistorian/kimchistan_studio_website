"""Literal stock-photo compositing requested by the user; no image generation.

The existing UI/device raster remains the base. Real source photographs replace
every food-image area, with cropping and a readability gradient. UI text/actions
and the phone occlusion remain above the photo layer.
"""
from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT=Path(__file__).resolve().parents[3]
ASSETS=ROOT/'output/design/kmong-227326'
STOCK=ASSETS/'stock'
WORK=ROOT/'tmp/pdfs/kmong-227326'
ARCHIVE=WORK/'archive-ai-food'
ARCHIVE.mkdir(exist_ok=True)

for path in [ASSETS/'01-responsive-overview.png',ASSETS/'02-customer-flows.png',
             ASSETS/'03-staff-operations.png',ASSETS/'manifest.json',
             WORK/'concept-content.json',WORK/'build_concept_bundle.py',
             ROOT/'output/pdf/kmong-227326-proposal.pdf',
             ROOT/'output/pdf/고깃집예약주문-UIUX콘셉트.pdf',
             ROOT/'output/presentations/고깃집예약주문-UIUX콘셉트.pptx']:
    target=ARCHIVE/path.name
    if not target.exists():shutil.copyfile(path,target)

def rounded_mask(size,bounds,radius):
    scale=4
    mask=Image.new('L',(size[0]*scale,size[1]*scale),0)
    d=ImageDraw.Draw(mask)
    d.rounded_rectangle(tuple(round(x*scale) for x in bounds),radius=radius*scale,fill=255)
    return mask.resize(size,Image.Resampling.LANCZOS)

def crop_photo(name,size,center=(.5,.5),source_box=None):
    im=Image.open(STOCK/name).convert('RGB')
    if source_box:im=im.crop(source_box)
    return ImageOps.fit(im,size,method=Image.Resampling.LANCZOS,centering=center)

def photo_layer(base,name,bounds,radius=0,center=(.5,.5),source_box=None,gradient=None,exclude=None):
    x0,y0,x1,y1=bounds
    patch=crop_photo(name,(x1-x0,y1-y0),center,source_box)
    if gradient:
        axis,start,end=gradient
        w,h=patch.size
        values=np.linspace(start,end,w if axis=='x' else h)
        alpha=np.tile(values,(h,1)) if axis=='x' else np.tile(values[:,None],(1,w))
        rgba=Image.new('RGBA',patch.size,(0,0,0,0))
        rgba.putalpha(Image.fromarray(np.round(alpha*255).astype(np.uint8)))
        patch=Image.alpha_composite(patch.convert('RGBA'),rgba).convert('RGB')
    whole=Image.new('RGB',base.size)
    whole.paste(patch,(x0,y0))
    mask=rounded_mask(base.size,(x0,y0,x1-1,y1-1),radius)
    if exclude:
        exclusion=rounded_mask(base.size,exclude[:4],exclude[4])
        mask=Image.fromarray(np.minimum(np.asarray(mask),255-np.asarray(exclusion)).astype(np.uint8))
    base.paste(whole,(0,0),mask)
    return mask

def preserve_ui(base,original,bounds,radius):
    mask=rounded_mask(base.size,bounds,radius)
    base.paste(original,(0,0),mask)

def preserve_white_text(base,original,bounds):
    x0,y0,x1,y1=bounds
    # Re-typeset the existing short headline instead of retaining fragments of
    # the old photograph in its antialias pixels.
    size=50 if x1-x0>400 else 44
    font=ImageFont.truetype(str(ROOT/'tmp/pdfs/design-review/fonts/Pretendard-Bold.ttf'),size)
    ImageDraw.Draw(base).text((x0,y0),'함께 모이는 자리',font=font,fill=(248,245,238),anchor='lt')

original=Image.open(ARCHIVE/'01-responsive-overview.png').convert('RGB')
overview=original.copy()
# Desktop hero: protect the foreground phone, and restore existing UI above it.
photo_layer(overview,'grill-tommao-2025.jpg',(75,214,913,570),
            source_box=(0,1400,2400,2420),gradient=('x',.57,.04),
            exclude=(811,460,1035,919,41))
preserve_white_text(overview,original,(129,316,554,374))
preserve_ui(overview,original,(132,385,185,392),2)
preserve_ui(overview,original,(129,420,307,482),20)
preserve_ui(overview,original,(318,420,502,482),20)
# All three menu previews use real photography too.
photo_layer(overview,'beef-kyle-mackie.jpg',(221,607,410,735),10,
            source_box=(300,950,1750,2250))
photo_layer(overview,'grill-tommao-2025.jpg',(419,607,607,735),10,
            source_box=(250,1600,2300,2700))
photo_layer(overview,'soup-makafood.jpg',(618,607,814,735),10,
            source_box=(300,150,2150,1500),exclude=(811,460,1035,919,41))
overview.save(ASSETS/'01-responsive-overview.png',optimize=True)

original=Image.open(ARCHIVE/'02-customer-flows.png').convert('RGB')
customer=original.copy()
photo_layer(customer,'grill-tommao-2025.jpg',(105,205,487,661),
            center=(.55,.64),gradient=('y',.65,.06))
preserve_white_text(customer,original,(137,278,462,329))
preserve_ui(customer,original,(144,345,197,352),2)
photo_layer(customer,'beef-kyle-mackie.jpg',(1118,315,1246,416),10,
            source_box=(300,950,1750,2250))
customer.save(ASSETS/'02-customer-flows.png',optimize=True)

# Verify unchanged UI areas outside the photo edit bounds; staff mockup has no
# food imagery and remains byte-identical.
assert (ASSETS/'03-staff-operations.png').read_bytes()==(ARCHIVE/'03-staff-operations.png').read_bytes()
sources=json.loads((STOCK/'sources.json').read_text())
used={'grill-tommao-2025.jpg','beef-kyle-mackie.jpg','soup-makafood.jpg'}
for row in sources:row['used_in_current_mockups']=row['file'] in used
(STOCK/'sources.json').write_text(json.dumps(sources,ensure_ascii=False,indent=2))

manifest=json.loads((ASSETS/'manifest.json').read_text())
manifest['classification']='공고 기반 UI/UX 제안 콘셉트. 음식 사진은 실제 무료 스톡 촬영본이며 매장·메뉴·가격·데이터는 예시입니다.'
manifest['food_photo_method']='Literal source-photo compositing with crop/readability gradients; no AI food generation or regeneration.'
manifest['stock_sources']='stock/sources.json'
for asset in manifest['assets']:
    p=ASSETS/asset['file']
    asset['bytes']=p.stat().st_size
    asset['sha256']=hashlib.sha256(p.read_bytes()).hexdigest()
(ASSETS/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))

credits=['Food photographs used in the current concept mockups',
         'Downloaded and license checked on 2026-11-06.',
         'Photos are illustrative stock photographs, not photos of the client restaurant.',
         'Food pixels are composited from the source images without generative redrawing.',
         'Cropping and dark readability gradients are applied.',
         'The UI/device framework remains a proposal concept.', '']
for row in sources:
    if row['file'] in used:
        credits += [f"{row['photographer']} / {row['provider']}",row['source_page'],
                    f"License: {row['license']}",f"File: stock/{row['file']}",f"SHA256: {row['sha256']}",'']
(ASSETS/'photo-credits.txt').write_text('\n'.join(credits))
print(json.dumps({'updated':['01-responsive-overview.png','02-customer-flows.png'],
                  'staff_image_unchanged':True,'real_stock_photos_used':len(used),
                  'source_record':str(STOCK/'sources.json')},ensure_ascii=False))
