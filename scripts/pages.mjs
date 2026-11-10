import { e, t, arrow, brandMark, external, alt, label, localized, projectCard, resourceLink, community, contact, crafts, art, badge, tape, lettuceArt, leafTemplate, motionToggle, inquiryLink } from './render.mjs';

const kicker = (tag, text) => `<p class="kicker"><span class="tag">${tag}</span>${text}</p>`;

function noticeStrip(notices) {
  return `<section class="notice-strip" id="notices"><div class="container notice-strip-inner"><div><p class="mini-label">${t('Company information', '회사 안내')}</p><a class="notice-strip-title" href="notices/">${t('Official notices', '전자공고')}<span lang="ko" class="notice-ko">전자공고</span>${arrow}</a></div><div class="notice-strip-content">${notices.length
    ? notices.slice(0, 3).map((notice) => `<a class="notice-preview" href="notices/${e(notice.slug)}.html"><time datetime="${notice.date}">${notice.date.replaceAll('-', '.')}</time><span lang="ko">${e(notice.title)}</span>${arrow}</a>`).join('')
    : `<p>${t('There are currently no published notices.', '현재 등록된 공고가 없습니다.')}</p>`}</div></div></section>`;
}

function rotator(lang) {
  return `<span class="rotator" data-rotator>${crafts.map((craft, i) => `<span class="rotator-word${i === 0 ? ' is-active' : ''}" data-word="${craft.key}">${craft.word[lang === 'ko' ? 1 : 0]}</span>`).join('')}</span>`;
}

const flag = `<svg class="flag" viewBox="0 0 300 200" aria-hidden="true" focusable="false"><g stroke="#100f0d" stroke-width="5" stroke-linejoin="round"><rect x="3" y="3" width="294" height="194" rx="10" fill="#fffaf0"/><path d="M3 43h294M3 83h294M3 123h294M3 163h294" fill="none"/></g><path d="M5.5 5.5h289v35H5.5z" fill="#7c5cff"/><path d="M5.5 45.5h289v35H5.5z" fill="#2d5bff"/><path d="M5.5 85.5h289v35H5.5z" fill="#ffd23f"/><path d="M5.5 125.5h289v35H5.5z" fill="#ff5ca8"/><path d="M5.5 165.5h289v29H5.5z" fill="#bdf246"/><rect x="3" y="3" width="124" height="120" rx="10" fill="#ff4423" stroke="#100f0d" stroke-width="5"/><path d="M65 22 74.5 52.5 105 62 74.5 71.5 65 102 55.5 71.5 25 62 55.5 52.5Z" fill="#fffaf0" stroke="#100f0d" stroke-width="4" stroke-linejoin="round"/><rect x="3" y="3" width="294" height="194" rx="10" fill="none" stroke="#100f0d" stroke-width="6"/></svg>`;

export function homePage(site, games, notices) {
  const projects = [...games.filter((game) => game.detailPath), ...games.filter((game) => game.type !== 'asset' && !game.detailPath)];
  const resources = games.filter((game) => game.type === 'asset');
  const covers = projects.map((game) => game.image);
  return `<section class="hero" data-hero data-word="games">
    <div class="hero-bg" aria-hidden="true"><span class="blob blob-1"></span><span class="blob blob-2"></span><span class="blob blob-3"></span></div>
    <div class="container hero-inner">
      <div class="hero-topline"><p class="kicker kicker-live"><span class="live-dot" aria-hidden="true"></span>${t('Independent creative studio', '독립 크리에이티브 스튜디오')}</p><p class="hero-clock">${t('Goyang, KR', '대한민국 고양')} · <span data-clock>KST</span></p></div>
      <h1 class="hero-title"><span class="sr-only">${t('KIMCHISTAN STUDIO makes games, software, AI agents and videos, and distributes lettuce.', '김치스탄 스튜디오는 게임, 소프트웨어, AI 에이전트, 영상을 만들고 상추를 유통합니다.')}</span><span class="hero-title-visual" aria-hidden="true"><span class="locale" lang="en"><span class="ht-line">WE <span class="verb"><span class="verb-make">MAKE</span><span class="verb-swap">SHIP</span></span></span><span class="ht-line">${rotator('en')}</span></span><span class="locale" lang="ko"><span class="ht-line">${rotator('ko')}</span><span class="ht-line"><span class="verb"><span class="verb-make">만듭니다</span><span class="verb-swap">유통합니다</span></span></span></span></span></h1>
      <div class="hero-lower">
        <p class="hero-description">${t('KIMCHISTAN STUDIO is a small, independent studio in Goyang, South Korea. We build original games, custom software and AI agents, make videos — and distribute fresh smart-farm lettuce. Yes, really.', '김치스탄 스튜디오는 경기도 고양시의 작은 독립 스튜디오입니다. 오리지널 게임과 맞춤형 소프트웨어, AI 에이전트를 만들고, 영상을 제작하며, 신선한 스마트팜 상추를 유통합니다. 정말이에요.')}</p>
        <div class="hero-actions"><a class="button button-primary" href="#services">${t('See today’s menu', '오늘의 메뉴 보기')}${arrow}</a><a class="button button-ghost" href="#contact">${t('Start a project', '프로젝트 문의')}${arrow}</a></div>
      </div>
      <div class="sticker-board">
        <a class="sticker polaroid" data-sticker href="games/orbit-foundry/" style="--x:78%;--y:5%;--r:7deg"><img src="assets/games/orbit-foundry-orbit.webp" ${alt('Orbit Foundry: a luminous star surrounded by an orbital factory', 'Orbit Foundry: 빛나는 별을 둘러싼 궤도 공장')} width="2400" height="775" fetchpriority="high"><span>Orbit Foundry ${arrow}</span></a>
        <span class="sticker sticker-games" data-sticker aria-hidden="true" style="--x:62%;--y:0%;--r:-12deg">${art.games}</span>
        <span class="sticker sticker-software" data-sticker aria-hidden="true" style="--x:89%;--y:63%;--r:9deg">${art.software}</span>
        <span class="sticker sticker-agents" data-sticker aria-hidden="true" style="--x:62%;--y:58%;--r:-8deg">${art.agents}</span>
        <span class="sticker sticker-videos" data-sticker aria-hidden="true" style="--x:75%;--y:77%;--r:12deg">${art.videos}</span>
        <span class="sticker sticker-lettuce" data-sticker aria-hidden="true" style="--x:47%;--y:72%;--r:-6deg">${art.lettuce}</span>
        <span class="drag-hint" aria-hidden="true">${t('psst — drag the stickers', '쉿, 스티커를 끌어 보세요')}</span>
      </div>
      <div class="hero-bottom"><a class="scroll-cue" href="#services">${t('Scroll for the menu', '스크롤해서 메뉴 보기')}<span aria-hidden="true">↓</span></a>${motionToggle}</div>
    </div>
  </section>
  <div class="tapes" aria-hidden="true">${tape('tape-a', crafts.map((craft) => craft.word[0]))}${tape('tape-b', crafts.map((craft) => craft.word[1]))}<span class="tapes-badge">${badge()}</span></div>

  <section class="menu-section section" id="services"><div class="container">
    <div class="section-top">${kicker(t('Menu', '메뉴'), t('One studio, five crafts', '하나의 스튜디오, 다섯 가지 일'))}<h2 class="display">${t('On the menu <em>today.</em>', '오늘의 <em>메뉴.</em>')}</h2><p class="section-description">${t('Pick one dish or order the full course. Everything is served by the same small team in Goyang.', '한 가지만 골라도, 코스로 주문해도 좋아요. 모두 고양의 작은 팀이 정성껏 내어 드립니다.')}</p></div>
    <div class="menu-grid">
      <a class="menu-tile tile-games" href="games/" data-tilt data-reveal><span class="tile-no">01</span><h3 class="tile-title">${t('Games', '게임')}</h3><p>${t('Original worlds to explore, build and get lost in.', '탐험하고, 짓고, 빠져드는 오리지널 세계.')}</p>
        <span class="card-fan" aria-hidden="true">${covers.map((src) => `<img src="${e(src)}" alt="" width="400" height="250" loading="lazy">`).join('')}</span>
        <span class="tile-go">${t('Our games', '게임 보기')}${arrow}</span></a>
      <a class="menu-tile tile-software" href="services/" data-tilt data-reveal><span class="tile-no">02</span><h3 class="tile-title">${t('Software', '소프트웨어')}</h3><p>${t('Custom apps and internal tools shaped around how your team works.', '팀이 일하는 방식에 꼭 맞춘 애플리케이션과 업무 도구.')}</p>
        <span class="terminal" aria-hidden="true"><span class="term-bar"><i></i><i></i><i></i></span><code><span class="tl" style="--n:34;--d:0s">$ kimchistan build --for=your-team</span><span class="tl ok" style="--n:30;--d:1.4s">✓ spreadsheets → one dashboard</span><span class="tl ok" style="--n:18;--d:2.6s">✓ requests tracked</span><span class="tl ok" style="--n:24;--d:3.5s">✓ shipped. coffee break.</span></code></span>
        <span class="tile-go">${t('Software & AI', '소프트웨어 & AI')}${arrow}</span></a>
      <a class="menu-tile tile-agents" href="services/#ai-agents" data-tilt data-reveal><span class="tile-no">03</span><h3 class="tile-title">${t('AI Agents', 'AI 에이전트')}</h3><p>${t('Agents that find, draft and hand off to a person for the final call.', '찾고, 초안을 쓰고, 마지막 판단은 사람에게 넘기는 에이전트.')}</p>
        <span class="agent-flow" aria-hidden="true"><span class="node">${t('Find', '찾기')}</span><span class="wire"><i></i></span><span class="node">${t('Draft', '초안')}</span><span class="wire"><i></i></span><span class="node node-human">${t('You review', '사람이 검토')}</span></span>
        <span class="tile-go">${t('Put AI to work', 'AI 도입하기')}${arrow}</span></a>
      <a class="menu-tile tile-videos" href="#videos" data-tilt data-reveal><span class="tile-no">04</span><h3 class="tile-title">${t('Videos', '영상')}</h3><p>${t('3D animation, explainers, trailers and cinematics.', '3D 애니메이션, 설명 영상, 트레일러와 시네마틱.')}</p>
        <span class="mini-viewfinder" aria-hidden="true"><span class="bars"></span><span class="rec">REC</span><span class="tc" data-timecode>00:00:00:00</span><span class="play"></span></span>
        <span class="tile-go">${t('Roll camera', '촬영 시작')}${arrow}</span></a>
      <a class="menu-tile tile-lettuce" href="#lettuce" data-tilt data-reveal><span class="tile-no">05</span><h3 class="tile-title">${t('Lettuce', '상추')}</h3><p>${t('Crisp, fresh smart-farm lettuce, distributed by us. Truly.', '스마트팜에서 자란 아삭하고 신선한 상추를 유통합니다. 진짜로요.')}</p>
        <span class="tile-lettuce-art" aria-hidden="true">${lettuceArt('lettuce-art')}<span class="price-tag">${t('FRESH!', '신선!')}</span></span>
        <span class="tile-go">${t('Get some', '주문하기')}${arrow}</span></a>
    </div>
  </div></section>

  <section class="work-section section" id="work"><div class="container"><span class="anchor-alias" id="games"></span>
    <div class="section-top">${kicker('01', t('Games', '게임'))}<h2 class="display">${t('Worlds we’ve <em>built.</em>', '우리가 만든 <em>세계.</em>')}</h2><p class="section-description">${t('Worlds to explore, systems to figure out, and a little something for fellow makers.', '탐험할 세계와 풀어 갈 시스템, 그리고 동료 창작자들을 위한 작은 선물까지.')}</p></div>
    <div class="selected-grid">${projects.map((game, i) => projectCard(game, '', { featured: i === 0 })).join('')}</div>
    ${resources.map((game) => resourceLink(game, '')).join('')}
    <a class="button button-light more-link" href="games/">${t('All games & experiments', '게임과 실험 모두 보기')}${arrow}</a>
  </div></section>

  <section class="video-section section" id="videos"><div class="container video-grid">
    <div class="video-copy">${kicker('04', t('Videos', '영상'))}<h2 class="display">${t('Lights. Camera. <em>Kimchi.</em>', '조명, 카메라, <em>김치!</em>')}</h2>
      <p class="lead">${t('3D animation, product and process explainers, game trailers and cinematics. The craft we pour into our games, pointed at your story.', '3D 애니메이션, 제품과 공정을 설명하는 영상, 게임 트레일러와 시네마틱. 게임을 만들며 쌓은 감각을 여러분의 이야기에 담습니다.')}</p>
      <ul class="chip-list">${[['3D animation', '3D 애니메이션'], ['Explainer videos', '설명 영상'], ['Trailers & cinematics', '트레일러 & 시네마틱'], ['Subtitles & callouts', '자막 & 강조 그래픽']].map(([en, ko]) => `<li>${t(en, ko)}</li>`).join('')}</ul>
      <div class="actions">${inquiryLink(site, 'button button-primary', 'Commission a video', '영상 제작 문의', 'videos')}<a class="text-link" ${external(site.links.youtube)}>${t('Watch on YouTube', 'YouTube에서 보기')}${arrow}</a></div>
    </div>
    <figure class="viewfinder" data-reveal><div class="vf-screen"><img src="assets/games/orbit-foundry-screen-2.webp" ${alt('Orbit Foundry gameplay: factory progression and orbital production', 'Orbit Foundry 게임 화면: 공장의 성장과 궤도 생산 시스템')} width="1920" height="1080" loading="lazy"><span class="vf-overlay" aria-hidden="true"><span class="vf-scan"></span><span class="vf-corner vf-tl"></span><span class="vf-corner vf-tr"></span><span class="vf-corner vf-bl"></span><span class="vf-corner vf-br"></span><span class="vf-hud vf-top"><span class="rec">REC</span><span data-timecode>00:00:00:00</span></span><span class="vf-hud vf-bottom"><span>4K</span><span>24 FPS</span><span class="vf-battery"><i></i><i></i><i></i><i></i></span></span><span class="vf-focus"></span></span></div>
      <figcaption>${t('Still from our game, Orbit Foundry', '자체 게임 Orbit Foundry의 한 장면')}</figcaption></figure>
  </div></section>

  <section class="lettuce-section section" id="lettuce"><div class="container lettuce-grid">
    <div class="lettuce-stage" data-reveal>
      <button class="lettuce-button" type="button" data-harvest ${label('Pick a lettuce leaf', '상추 잎 하나 따기')}>${lettuceArt('lettuce-art lettuce-hero')}</button>
      <span class="price-tag price-tag-big" aria-hidden="true">${t('FRESH<br>FROM THE<br>SMART FARM', '스마트팜<br>직송<br>신선 상추')}</span>
      <span class="leaf-fall" data-leaf-fall aria-hidden="true"></span>${leafTemplate}
      <span class="tap-hint" aria-hidden="true">${t('tap to pick a leaf', '눌러서 잎 따기')}</span>
    </div>
    <div class="lettuce-copy">${kicker('05', t('Lettuce', '상추'))}<h2 class="display">${t('Yes, we also distribute <em>lettuce.</em>', '네, 상추도 <em>유통합니다.</em>')}</h2>
      <p class="lead">${t('Alongside games and software, we distribute lettuce: crisp, fresh leaves grown in smart farms, where light, water and temperature are carefully controlled. It’s the one thing we ship that’s meant to be green.', '게임과 소프트웨어를 만드는 한편, 우리는 상추를 유통합니다. 빛과 물, 온도를 세심하게 관리하는 스마트팜에서 자란 아삭하고 신선한 상추. 우리가 출시하는 것 중 유일하게 초록색이어야 하는 제품이죠.')}</p>
      <div class="release-notes"><p class="rn-title"><code>lettuce v1.0</code> — ${t('release notes', '릴리스 노트')}</p><ul>
        <li><b>+</b>${t('Smart-farm grown, distributed by us', '스마트팜 재배, 김치스탄 유통')}</li>
        <li><b>+</b>${t('Crisp, fresh leaves, ready for ssam', '쌈 싸 먹기 좋은 아삭하고 신선한 잎')}</li>
        <li><b>+</b>${t('Ask us about quantities and availability', '수량과 공급 일정은 문의해 주세요')}</li>
      </ul><p class="rn-meta">${t('Leaves picked on this page', '이 페이지에서 딴 잎')}: <output data-harvest-count>0</output></p></div>
      <div class="actions">${inquiryLink(site, 'button button-primary', 'Order fresh lettuce', '상추 주문 문의', 'lettuce')}</div>
    </div>
  </div></section>

  <section class="studio-section section" id="studio"><div class="container studio-grid">
    <figure class="flag-figure" data-reveal><span class="flag-pole" aria-hidden="true"></span>${flag}<figcaption>${t('The flag of Kimchistan: five crafts, one star.', '김치스탄의 깃발: 다섯 가지 일, 하나의 별.')}</figcaption></figure>
    <div class="studio-copy">${kicker(t('About', '소개'), t('A little about us', '우리를 소개합니다'))}<h2 class="display">${t('Welcome to <em>Kimchistan.</em>', '김치스탄에 <em>어서 오세요.</em>')}</h2>
      <p class="studio-intro">${t('We’re KIMCHISTAN STUDIO, an independent creative studio based in Goyang, South Korea.', '김치스탄 스튜디오는 경기도 고양시에 자리한 독립 크리에이티브 스튜디오입니다.')}</p>
      <p>${t('Five crafts might sound like a lot. To us it’s one habit: bring people real, useful things, with care for whoever is on the other side — of the screen, or of the salad bowl.', '다섯 가지 일이 많아 보일 수도 있지만, 우리에게는 하나의 습관입니다. 화면 너머의 사람, 그리고 식탁 앞의 사람을 생각하며 진짜 쓸모 있는 것을 정성껏 전하는 것.')}</p>
      <dl class="fact-sheet">
        <div><dt>${t('Capital', '수도')}</dt><dd>${t('Goyang, South Korea', '대한민국 경기도 고양시')}</dd></div>
        <div><dt>${t('Local time', '현지 시각')}</dt><dd><span data-clock>KST</span></dd></div>
        <div><dt>${t('Languages', '공용어')}</dt><dd>English, <span lang="ko">한국어</span></dd></div>
        <div><dt>${t('Exports', '주요 수출품')}</dt><dd>${t('Games, software, AI agents, videos, lettuce', '게임, 소프트웨어, AI 에이전트, 영상, 상추')}</dd></div>
        <div><dt>${t('Currency', '통화')}</dt><dd>${t('Curiosity', '호기심')}</dd></div>
      </dl>
    </div>
  </div></section>
  ${contact(site)}
  ${noticeStrip(notices)}`;
}

export function gamesPage(site, games) {
  const orbit = games.find((game) => game.detailPath);
  return `<section class="page-intro intro-games section"><div class="container">${kicker('01', t('Games & experiments', '게임과 실험'))}<div class="intro-grid"><h1 class="display">${t('Small studio.<br><em>Many worlds.</em>', '작은 스튜디오의<br><em>다양한 세계.</em>')}</h1><div class="intro-copy"><p>${t('A star-powered factory. A familiar Korean daycare. A crew of ambitious goblins. Follow your curiosity.', '별을 중심으로 돌아가는 공장, 익숙한 한국의 어린이집, 꿈 많은 고블린들. 호기심이 이끄는 곳으로 떠나보세요.')}</p><a class="button button-light" ${external(site.links.itch)}>${t('All projects on itch.io', 'itch.io에서 전체 프로젝트 보기')}${arrow}</a></div></div><span class="intro-sticker" aria-hidden="true">${art.games}</span></div></section>
  <section class="games-portfolio"><div class="container"><article class="game-spotlight" id="orbit-foundry" data-reveal><a class="spotlight-image" href="orbit-foundry/"><img src="../assets/games/orbit-foundry-orbit.webp" ${alt('Orbit Foundry’s colorful orbital factory', 'Orbit Foundry의 다채로운 궤도 공장')} width="2400" height="775" fetchpriority="high"></a><div class="spotlight-copy"><p class="kicker"><span class="tag">${t('In development', '개발 중')}</span></p><h2 class="display">Orbit<br><em>Foundry.</em></h2><p>${localized(orbit.summary)}</p><a class="button button-primary" href="orbit-foundry/">${t('Discover the game', '게임 자세히 보기')}${arrow}</a><a class="text-link" ${external(site.links.prototype)}>${t('Play the desktop-browser prototype', 'PC 브라우저 프로토타입 플레이')}${arrow}</a></div></article>
    <div class="game-grid">${games.filter((game) => game.type !== 'asset' && !game.detailPath).map((game) => projectCard(game, '../')).join('')}</div>
    ${games.filter((game) => game.type === 'asset').map((game) => resourceLink(game, '../')).join('')}
  </div></section>
  <section class="community-section section"><div class="container">${kicker(t('Community', '커뮤니티'), t('Come along for the next chapter', '다음 이야기도 함께해요'))}<div class="community-grid"><h2 class="display">${t('Better with<br><em>company.</em>', '함께하면<br><em>더 즐거워요.</em>')}</h2>${community(site)}</div></div></section>`;
}

export function servicesPage(site) {
  const services = [
    { id: 'custom-applications', color: 'software', title: ['Custom applications', '맞춤형 애플리케이션'], description: ['A web application or dashboard shaped around your business, your customers, and the way your team actually works.', '비즈니스와 고객, 팀이 실제로 일하는 방식에 맞춘 웹 애플리케이션과 대시보드를 개발합니다.'], example: ['A shared place to receive, track, and follow up on customer requests.', '고객 요청을 접수하고, 진행 상황을 확인하고, 후속 업무를 관리하는 공간.'], steps: [['Receive', '접수'], ['Track', '관리'], ['Follow up', '후속 업무']] },
    { id: 'internal-tools', color: 'lettuce', title: ['Internal tools', '팀을 위한 업무 도구'], description: ['Give repetitive tasks a simpler home. Connect information and turn a scattered process into a tool your team can use.', '반복되는 업무를 더 간단하게 처리하세요. 흩어진 정보를 연결하고, 복잡한 절차를 팀이 쓰기 편한 도구로 만듭니다.'], example: ['Turn information from separate spreadsheets into one useful team view.', '여러 스프레드시트에 흩어진 정보를 팀이 함께 보는 하나의 화면으로.'], steps: [['Gather', '모으기'], ['Organize', '정리'], ['Share', '공유']] },
    { id: 'ai-agents', color: 'agents', title: ['AI agents & workflow integration', 'AI 에이전트 & 업무 연동'], description: ['Find a useful role for AI agents, connect them to your existing tools, and build human review into the workflow.', 'AI 에이전트가 도움이 될 업무를 찾고, 기존 도구에 연결하며, 사람이 검토하는 단계를 업무 흐름에 함께 설계합니다.'], example: ['Find relevant information, prepare a first draft, and send it to a person for review.', '필요한 정보를 찾고 초안을 준비한 뒤, 담당자가 검토하는 흐름.'], steps: [['Find', '찾기'], ['Draft', '초안'], ['Review', '검토']] }
  ];
  return `<section class="page-intro intro-services section"><div class="container">${kicker('02 + 03', t('Software & AI agents / For small businesses and teams', '소프트웨어 & AI 에이전트 / 작은 비즈니스와 팀을 위해'))}<div class="intro-grid"><h1 class="display">${t('Good software.<br><em>Less busywork.</em>', '더 나은 도구.<br><em>더 편해진 일.</em>')}</h1><div class="intro-copy"><p>${t('Your team has things to do. We build applications, internal tools, and AI agents that fit the work in front of you.', '해야 할 일이 많은 팀을 위해, 지금의 업무에 맞는 애플리케이션과 내부 도구, AI 에이전트를 만듭니다.')}</p><a class="button button-light" href="#contact">${t('Discuss your project', '프로젝트 이야기하기')}${arrow}</a></div></div><span class="intro-sticker" aria-hidden="true">${art.software}</span><span class="intro-sticker intro-sticker-2" aria-hidden="true">${art.agents}</span></div></section>
  <section class="capabilities-section section"><div class="container"><div class="section-top">${kicker(t('Menu', '메뉴'), t('What we can build together', '함께 만들 수 있는 것'))}<h2 class="display">${t('Practical tools. <em>Thoughtful</em> build.', '필요한 도구를, <em>세심하게.</em>')}</h2></div>
    ${services.map((service, i) => `<article class="capability" id="${service.id}" style="--accent:var(--c-${service.color})" data-reveal><div class="capability-title"><span class="capability-number">0${i + 1}</span><h3>${t(...service.title)}</h3></div><div class="capability-copy"><p>${t(...service.description)}</p><div class="application-example"><p class="mini-label">${t('Possible application', '이런 곳에 활용할 수 있어요')}</p><p>${t(...service.example)}</p><ol class="workflow">${service.steps.map((step) => `<li>${t(...step)}</li>`).join('')}</ol></div></div></article>`).join('')}
  </div></section>
  <section class="process-section section"><div class="container"><div class="section-top">${kicker(t('Recipe', '레시피'), t('How we work', '함께 일하는 방식'))}<h2 class="display">${t('From the first question<br>to a <em>working</em> solution.', '첫 질문에서<br>실제로 <em>쓰는 도구까지.</em>')}</h2></div><ol class="process-grid">
    <li data-reveal><span class="process-number">01</span><h3>${t('Discover', '이해하기')}</h3><p>${t('Start with the people, the problem, and the tools you already use. Work out what is worth building.', '사람과 문제, 현재 사용하는 도구부터 살펴보고 무엇을 만들면 좋을지 함께 정합니다.')}</p></li>
    <li data-reveal><span class="process-number">02</span><h3>${t('Build & integrate', '만들고 연결하기')}</h3><p>${t('Design the workflow, build the software, and connect the pieces. Review progress together as it takes shape.', '업무 흐름을 설계하고 소프트웨어와 필요한 도구를 연결합니다. 만드는 과정에서 함께 확인합니다.')}</p></li>
    <li data-reveal><span class="process-number">03</span><h3>${t('Launch & support', '도입하고 다듬기')}</h3><p>${t('Put it into everyday use, help your team get started, and agree on the support it needs.', '실제 업무에 도입하고 팀의 사용을 도우며, 필요한 운영 지원을 함께 정합니다.')}</p></li>
  </ol></div></section>
  ${contact(site, { compact: true })}`;
}

export const screenshots = [
  { path: 'assets/games/orbit-foundry-screen-1.webp', en: 'An orbital factory in the Prism Belt', ko: '프리즘 벨트의 궤도 공장', altEn: 'Orbit Foundry gameplay: orbital machinery around a star in the Prism Belt', altKo: 'Orbit Foundry 게임 화면: 프리즘 벨트의 별 주위에 배치된 궤도 기계' },
  { path: 'assets/games/orbit-foundry-screen-2.webp', en: 'Build your production. Find your rhythm.', ko: '생산을 확장하고 나만의 리듬을 찾아보세요.', altEn: 'Orbit Foundry gameplay: factory progression and orbital production', altKo: 'Orbit Foundry 게임 화면: 공장의 성장과 궤도 생산 시스템' },
  { path: 'assets/games/orbit-foundry-screen-3.webp', en: 'A growing, interconnected cosmic factory', ko: '서로 연결되며 성장하는 우주 공장', altEn: 'Orbit Foundry gameplay: building an interconnected cosmic factory', altKo: 'Orbit Foundry 게임 화면: 서로 연결된 우주 공장 건설' }
];

export function orbitPage(site) {
  return `<section class="orbit-hero section"><div class="orbit-stars" aria-hidden="true"></div><div class="container"><a class="breadcrumb" href="../">${t('Our games', '우리의 게임')}<span> / Orbit Foundry</span></a><div class="orbit-intro"><div><p class="kicker"><span class="tag">${t('In development', '개발 중')}</span>${t('A cosmic factory incremental', '우주 공장 증분 게임')}</p><h1 class="display">ORBIT<br><em>FOUNDRY.</em></h1></div><div class="orbit-intro-copy"><p>${t('Start with a star.<br>Build something astronomical.', '하나의 별에서 시작해<br>우주 규모의 공장을 만드세요.')}</p><a class="button button-accent" ${external(site.links.steam)}>${t('Wishlist on Steam', 'Steam 위시리스트에 추가')}${arrow}</a><a class="orbit-prototype" ${external(site.links.prototype)}>${t('Play the free 2D prototype', '무료 2D 프로토타입 플레이')}${arrow}</a><small>${t('Prototype: desktop browser · Full game: Windows + macOS', '프로토타입: PC 브라우저 · 정식 게임: Windows + macOS')}</small></div></div><div class="orbit-panorama"><img src="../../assets/games/orbit-foundry-orbit.webp" ${alt('A colorful orbital factory surrounds a luminous star in Orbit Foundry', 'Orbit Foundry에서 빛나는 별 주위를 둘러싼 다채로운 궤도 공장')} width="2400" height="775" fetchpriority="high"></div></div></section>
  <section class="gameplay-section section"><div class="container"><div class="section-top">${kicker(t('Inside', '게임 속'), t('A look inside', '게임 속으로'))}<h2 class="display">${t('One star.<br>Endless <em>possibilities.</em>', '하나의 별.<br><em>끝없는 가능성.</em>')}</h2><p class="section-description">${t('Arrange machines, find your production rhythm, and make every Reforge the start of something bigger.', '기계를 배치하고 생산 리듬을 찾으세요. 리포지할 때마다 더 큰 가능성이 열립니다.')}</p></div>
    <figure class="gameplay-gallery" data-gallery><div class="gameplay-frame"><img id="gameplay-image" src="../../${screenshots[0].path}" ${alt(screenshots[0].altEn, screenshots[0].altKo)} width="1920" height="1080" loading="lazy"></div><div class="gallery-bottom"><figcaption data-gallery-caption data-text-en="${e(screenshots[0].en)}" data-text-ko="${e(screenshots[0].ko)}">${e(screenshots[0].en)}</figcaption><div class="gallery-controls js-only" role="group" ${label('Gameplay screenshots', '게임 스크린샷')}>${screenshots.map((screen, i) => `<button type="button" data-screenshot="../../${screen.path}" data-screen-alt-en="${e(screen.altEn)}" data-screen-alt-ko="${e(screen.altKo)}" data-caption-en="${e(screen.en)}" data-caption-ko="${e(screen.ko)}" ${label('Screenshot ' + (i + 1), '스크린샷 ' + (i + 1))} aria-pressed="${i === 0}">0${i + 1}</button>`).join('')}</div></div><span class="sr-only" data-gallery-status role="status" aria-live="polite"></span></figure>
    <div class="game-features"><article data-reveal><span>01</span><h3>${t('Build your orbit.', '나만의 궤도를 설계하세요.')}</h3><p>${t('Turn a single star into the heart of a factory. Arrange machines and connect your production line.', '하나의 별을 공장의 중심으로 삼아 기계를 배치하고 생산 라인을 연결하세요.')}</p></article><article data-reveal><span>02</span><h3>${t('Find your rhythm.', '생산의 리듬을 찾으세요.')}</h3><p>${t('Time your pulses, grow your output, and discover how the pieces work together.', '펄스 타이밍을 맞추고 생산량을 늘리며 기계들이 함께 작동하는 방식을 알아가세요.')}</p></article><article data-reveal><span>03</span><h3>${t('Reforge. Go further.', '리포지하고, 더 멀리.')}</h3><p>${t('Make each Reforge count. Build on lasting progress and open up the next possibility.', '리포지를 통해 영구적인 성장을 쌓고 다음 가능성을 열어 가세요.')}</p></article></div>
  </div></section>
  <section class="orbit-cta section"><div class="container"><p class="kicker"><span class="tag">${t('Launch pad', '발사대')}</span>${t('Your factory is waiting', '나만의 공장이 기다리고 있어요')}</p><h2 class="display">${t('See you<br><em>in orbit.</em>', '궤도에서<br><em>만나요.</em>')}</h2><div class="orbit-cta-actions"><a class="button button-accent" ${external(site.links.steam)}>${t('Wishlist on Steam', 'Steam 위시리스트에 추가')}${arrow}</a><a class="text-link" ${external(site.links.prototype)}>${t('Try the desktop-browser prototype', 'PC 브라우저 프로토타입 체험')}${arrow}</a></div><a class="text-link orbit-community" ${external(site.links.discord)}>${t('Join the conversation on Discord', 'Discord에서 이야기 나누기')}${arrow}</a></div></section>`;
}
