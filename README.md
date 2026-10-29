# KIMCHISTAN STUDIO

The English/Korean studio and Orbit Foundry launch website for **KIMCHISTANSTUDIO Inc. (주식회사 김치스탄스튜디오)**, published at **kimchistan.kr** through GitHub Pages.

The site includes company information, a games section, a dedicated **전자공고** archive, permanent notice pages, optional document downloads, and print styles. It uses static HTML, CSS, and a little JavaScript. There are no runtime dependencies, tracking scripts, forms, or backend services. Fonts and optimized game images are self-hosted. The homepage features the upcoming Orbit Foundry release, a keyboard-accessible screenshot gallery, playable projects, studio information, and community links.

## Preview locally

Use Node.js 22 or newer. No `npm install` is necessary.

```sh
npm run dev
```

Open **http://localhost:8000**. Restart the preview after editing source files, or run `npm run build` in another terminal and refresh the page. To choose another port, use `PORT=8080 npm run dev`.

```sh
npm run build
```

This generates the deployable website in `dist/`, including `CNAME`, a sitemap, and `robots.txt`. `dist/` is generated output and is not committed.

## Publish on GitHub Pages

1. Create your GitHub repository and push this project's files to its `main` branch.
2. In the repository, open **Settings → Pages → Build and deployment → Source**, then select **GitHub Actions**.
3. Under **Custom domain**, enter **kimchistan.kr** and save it. The generated `CNAME` is not a substitute for configuring this setting.
4. In **Actions**, run **Publish studio website**, or push a new commit to `main`. Once deployment succeeds and the domain points to GitHub Pages, enable **Enforce HTTPS** when GitHub makes it available.
5. Check **https://kimchistan.kr/** and **https://kimchistan.kr/notices/** before using the website address for your incorporation paperwork.

The included [GitHub Actions workflow](.github/workflows/pages.yml) builds and uploads only `dist/`; content source, documentation, and development files are not part of the published site. GitHub's [publishing-source documentation](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site) explains the Pages setting, and its [custom-domain documentation](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site) explains domain configuration.

If you prefer to deploy from a branch without GitHub Actions, build locally and publish **the contents of `dist/`** from your selected Pages branch. Keep `.nojekyll` and `CNAME` in that publishing folder.

## Update company information

Edit [content/site.json](content/site.json):

| Field | Used for |
| --- | --- |
| `legalName` | Exact English legal name, company information, and footer |
| `legalNameKo` | Korean legal name, displayed alongside the English name |
| `links` | Steam, itch.io, prototype, Discord, X, and YouTube destinations |
| `domain` | Hostname without `https://`, `CNAME`, canonical URLs, and sitemap |
| `email` | Public contact section and contact links; omitted until supplied |
| `representative` | Company representative; omitted until supplied |
| `registrationNumber` | Business registration number; omitted until supplied |
| `address.en`, `address.ko` | Public company address; omitted until supplied |
| `description.en`, `description.ko` | Search and sharing descriptions |

Both legal names and both address translations appear in the footer in either language mode. The supplied address is normalized to remove the repeated city/district prefix. Unspecified registration and representative fields remain hidden. Launch and project copy is translated through the EN / KO switch.

## Add games

Edit [content/games.json](content/games.json) to maintain the portfolio, using this structure for each project:

```json
[
  {
    "title": { "en": "Your game title", "ko": "게임 이름" },
    "summary": { "en": "A short description of your game.", "ko": "게임 소개를 입력하세요." },
    "status": { "en": "In development", "ko": "개발 중" },
    "image": "assets/games/your-screenshot.webp",
    "url": "https://your-game-store-page.example"
  }
]
```

`image` and `url` are required. Put real optimized screenshots in `assets/games/`. The build validates asset paths and HTTP(S) destinations. Add `"type": "asset"` to present an asset pack as a compact resource link below the games. Orbit Foundry has its own launch section in `scripts/build.mjs`; update that section and its screenshots when release information changes. Image provenance is recorded in [docs/image-sources.md](docs/image-sources.md).

The itch.io studio profile is edited separately on itch.io. Its published theme and copy are backed up in [docs/itch-profile.md](docs/itch-profile.md).

## Publish an official notice

1. Copy [docs/notice.example.json](docs/notice.example.json) to `content/notices/` under a unique filename.
2. Enter the final Korean title, publication date (`YYYY-MM-DD`), text paragraphs, and signatory. Use a stable, unique `slug` containing lowercase English letters, digits, and hyphens.
3. For attachments, place your document in `assets/notices/` and add an entry such as `{ "label": "공고문 PDF", "path": "assets/notices/your-notice.pdf" }` to `attachments`.
4. Keep `"draft": true` while preparing it. When the notice is ready to publish, change it to `false`. The date field is displayed metadata, not a publication scheduler: every non-draft notice goes live on the next successful deployment.
5. Preview with `npm run dev`, review the notice and its print layout, and push to `main` to publish.

The notice appears on the homepage and archive, with a permanent URL such as `https://kimchistan.kr/notices/your-notice-slug.html`. Notice text is included in the HTML and remains readable without JavaScript. The language switch translates navigation, while original Korean notice text stays intact. Search and year filters appear once there are notices.

Do not rename a published notice's slug or remove its files while the notice needs to remain available. Preserve the approved original documents and evidence of publication separately; Git history and a working webpage alone should not be treated as a complete legal record.

### Before registering the 공고 홈페이지

This website supplies the technical publishing mechanism. Confirm your articles of incorporation specify electronic publication and that the website address matches your registration. Also confirm the fallback publication method and retention requirements with the person handling your incorporation. [상법 시행령 제6조](https://law.go.kr/lumLsLinkPop.do?lspttninfSeq=75741) addresses registration of the homepage address, easy access from the homepage, fallback publication, and notice periods.

## Files

```text
assets/                  Styles, browser behavior, and local font
content/site.json        Company information
content/games.json       Game listings
content/notices/         Approved notice sources (JSON)
scripts/build.mjs        Static page generator
scripts/serve.mjs        Local preview server
docs/notice.example.json Unpublished notice template
.github/workflows/       Automatic GitHub Pages deployment
dist/                    Generated website; ignored by Git
```

Space Grotesk is distributed under the SIL Open Font License included in [assets/FONT-LICENSE.txt](assets/FONT-LICENSE.txt).
