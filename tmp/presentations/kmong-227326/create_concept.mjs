import fs from 'node:fs/promises';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { GlobalFonts } from '@napi-rs/canvas';

const ROOT = '/Users/techistudio/Documents/GitHub/kimchistan_studio_website';
const BUILD = path.join(ROOT, 'tmp/presentations/kmong-227326');
const ASSETS = path.join(ROOT, 'output/design/kmong-227326');
const SKILL = '/Users/techistudio/.codex/plugins/cache/openai-primary-runtime/presentations/26.1011.11113/skills/presentations';
const PYTHON = '/Users/techistudio/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3';
const FINAL = path.join(ROOT, 'output/presentations/kmong-227326-concept-v2.pptx');
const HUMAN = path.join(ROOT, 'output/presentations/고깃집예약주문-UIUX콘셉트.pptx');
const FONTS = path.join(ROOT, 'tmp/pdfs/design-review/fonts');
process.env.RUNTIME_NODE_MODULES = '/Users/techistudio/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules';
process.env.RUNTIME_NODE = '/Users/techistudio/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node';
process.env.RUNTIME_PYTHON = PYTHON;
process.env.RUNTIME_BIN_DIR = '/Users/techistudio/.cache/codex-runtimes/codex-primary-runtime/dependencies/bin/override';
for (const weight of ['Regular', 'Medium', 'SemiBold', 'Bold']) {
  GlobalFonts.registerFromPath(path.join(FONTS, `Pretendard-${weight}.ttf`), 'Pretendard');
}

const { Presentation, PresentationFile } = await import('@oai/artifact-tool');
const { finalizePresentation } = await import(pathToFileURL(path.join(SKILL, 'container_tools/artifact_tool_utils.mjs')).href);
const content = JSON.parse(await fs.readFile(path.join(ROOT, 'tmp/pdfs/kmong-227326/concept-content.json'), 'utf8'));
await fs.mkdir(BUILD, {recursive:true});
await fs.mkdir(path.dirname(FINAL), {recursive:true});

const presentation = Presentation.create({slideSize:{width:1600,height:900}});
const FONT = 'Pretendard';
const INK = '#18352F';
const MUTED = '#586D65';

function addText(slide, name, value, x, y, width, height, size, bold=false, color=INK) {
  const shape = slide.shapes.add({
    geometry:'textbox',name,
    position:{left:x,top:y,width,height},fill:'none',
    line:{fill:'none',width:0},
  });
  shape.text = [{run:value,style:{typeface:FONT,fontSize:`${size}px`,bold,color}}];
  shape.text.style = {fontSize:size,bold,color,insets:0,verticalAlignment:'top'};
  return shape;
}

for (let i=0;i<content.slides.length;i++) {
  const data=content.slides[i];
  const slide=presentation.slides.add();
  slide.background.fill='#F7F5F0';
  addText(slide,`title-${i+1}`,data.title,70,44,1460,78,52,true);
  addText(slide,`subtitle-${i+1}`,data.subtitle,70,126,1460,42,25,false,MUTED);
  const sections=data.sections;
  let y=sections.length===3?235:265;
  const gap=sections.length===3?166:202;
  for (let j=0;j<sections.length;j++) {
    addText(slide,`section-${i+1}-${j+1}`,sections[j].title,70,y,370,43,28,true);
    addText(slide,`body-${i+1}-${j+1}`,sections[j].body,70,y+52,370,112,24,false,MUTED);
    y+=gap;
  }
  const bytes=await fs.readFile(path.join(ASSETS,data.image));
  slide.images.add({
    blob:bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.byteLength),
    contentType:'image/png',fit:'contain',alt:`${data.title}. 제안용 가상 화면`,
    position:{left:480,top:180,width:1060,height:650},
  });
  addText(slide,`disclosure-${i+1}`,content.disclosure,70,852,1460,29,17,false,MUTED);
  slide.speakerNotes.text=data.notes;
}

for (let i=0;i<presentation.slides.items.length;i++) {
  const slide=presentation.slides.items[i];
  const png=await presentation.export({slide,format:'png',scale:1});
  await fs.writeFile(path.join(BUILD,`slide-${i+1}.png`),new Uint8Array(await png.arrayBuffer()));
  const layout=await slide.export({format:'layout'});
  await fs.writeFile(path.join(BUILD,`slide-${i+1}.layout.json`),await layout.text());
}

const candidate=path.join(BUILD,'candidate.pptx');
await (await PresentationFile.exportPptx(presentation)).save(candidate);
const requirements={explicitTotalSlideCount:3,requiredNativeTableOwnerSlides:[],requiredNativeChartOwnerSlides:[]};
const result=await finalizePresentation({
  ...requirements, workspaceDir:ROOT,candidatePath:candidate,finalPath:FINAL,
  pythonExecutable:PYTHON,
  integrityValidatorPath:path.join(SKILL,'container_tools/inspect_presentation_package_integrity.py'),
  layoutValidatorPath:path.join(SKILL,'container_tools/inspect_presentation_layout_geometry.py'),
  layoutArgs:['--expected-slide-size-emu','15240000,8572500','--validate-heading-fit'],
  fontPolicy:{basis:'design',families:[FONT]},
  verifyArtifactToolImport:true,
  receiptPath:path.join(BUILD,'validation-stock-v2.json'),
});
await fs.copyFile(FINAL,HUMAN);
await fs.writeFile(path.join(BUILD,'build-result.json'),JSON.stringify({finalPath:HUMAN,internalPath:FINAL,requirements,result},null,2));
console.log(JSON.stringify({finalPath:HUMAN,slides:3,renderedSlides:3,validationReceipt:path.join(BUILD,'validation-stock-v2.json')}));
