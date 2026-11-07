크몽 227330 프리캐스트 건물 조립 3D 애니메이션 제안

제출 자료
output/proposals/kmong-227330-submission-package 폴더의 PDF 1개와 MP4 3개를 첨부합니다.
폼에는 kmong-227330-form-submission.txt 내용을 붙여 넣습니다.
영상 링크, QR, 외부 연락처 및 버전 표시는 제출 PDF에 없습니다.
MP4 3개는 각각 30초, 30초, 12초 분량의 무음 영상입니다.
어린이집 및 Orbit Foundry 영상은 외부 홍보 엔딩을 제외한 발췌본입니다.

제안 내용
제안 금액은 부가세 포함 7,000,000원, 진행 기간은 20일입니다.
착수 예정일은 2026년 11월 10일이며 최종 납품일은 11월 30일입니다.
제출용 요약은 이모티콘 입력 제한에 대응하여 한글, 영문, 숫자, 공백, 마침표와 쉼표로 작성했습니다.

PDF 제작 소스
scripts/proposals/kmong_227330.py
assets/proposals/kmong-227330
assets/fonts/pretendard-pdf
폰트 라이선스는 해당 폰트 디렉터리에 포함되어 있습니다.

재생성 명령
uv run --with reportlab --with pillow --with pypdf python scripts/proposals/kmong_227330.py

재생성 결과는 output/pdf/kmong-227330-proposal.pdf에 기록됩니다.
구조 검사와 레이아웃 기록은 tmp/pdfs/kmong-227330-attachments-design에 생성됩니다.
내용을 수정한 경우 전체 페이지를 다시 렌더링하고 확인한 후 제출 폴더의 PDF도 교체해야 합니다.

샘플 제작 소스
scripts/prototypes/kmong_227330.py
scripts/prototypes/audit_kmong_227330.py
output/prototypes/kmong-227330-v2
Blender 프로젝트와 원본 생성 및 검수 스크립트, 폰트, 영상, 검수 결과를 보관합니다.
샘플은 부재 배치 설명용 개념 영상이며 구조 성능 또는 시공 절차를 승인하는 자료가 아닙니다.

검수
최종 PDF 7페이지의 이미지와 문구, 링크와 QR 제거, 파일명 일치를 확인했습니다.
MP4 3개의 전체 디코드, 길이, 프레임 수, 해상도와 무음 여부를 확인했습니다.
최종 검수 기록은 kmong-227330-qa.json, PDF 입력 자산 해시는 kmong-227330-build-inputs.json에 있습니다.
이 저장은 로컬 제출 자료의 보관이며 외부 제출 또는 업로드를 수행하지 않습니다.
