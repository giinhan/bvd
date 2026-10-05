# 비버댐 · GitHub Pages

https://www.bvd-s.com 의 공개 콘텐츠를 보존한 정적 사이트입니다.

- Welcome / Store / Lounge / Concierge / Hello / May I help you
- 상품 12개의 사진, 가격, 소개와 상세 본문
- Hello의 기존 게시글 4개 및 글 사이 이동
- 결제·장바구니·회원가입·글쓰기 제거
- 원본 Quicksand(Google Fonts), SUITE 및 이미지와 스타일 로컬 보관
- PC 사진 갤러리, 모바일 사진 전환, 사진 확대

## 미리보기

VS Code에서 이 폴더를 열고 **Go Live**를 누르면 사이트가 바로 열립니다. 루트의 `index.html`이 `docs/index.html`로 연결합니다.

```sh
python3 -m http.server 8765 --directory docs
```

http://localhost:8765 에서 확인하세요. `docs/index.html`을 직접 열어도 볼 수 있습니다.

## GitHub에 배포

현재 연결된 저장소는 [giinhan/bvd](https://github.com/giinhan/bvd)이며, `main` 브랜치를 사용합니다. GitHub Pages는 **GitHub Actions** 방식으로 활성화되어 있습니다. 이후 `main`에 푸시하면 `docs` 폴더가 자동 배포됩니다. [배포 상태](https://github.com/giinhan/bvd/actions)에서 결과를 확인할 수 있습니다.

다른 저장소에 새로 배포하려면:

1. GitHub 저장소를 만들고 이 폴더의 파일을 업로드합니다.
2. 저장소 Settings → Pages → Source에서 **GitHub Actions**를 선택합니다.
3. 포함된 `.github/workflows/pages.yml`이 `docs` 폴더를 배포합니다.

빌드 서버, 데이터베이스, API 키는 필요하지 않습니다. 프로젝트 저장소의 하위 경로에서도 모든 내부 링크가 동작합니다.

기존 `www.bvd-s.com` 도메인 연결은 Pages 배포 확인 후 Settings → Pages → Custom domain에서 설정하고 DNS를 바꾸세요. 현재 원본 호스팅의 도메인 설정은 변경하지 않았습니다.

## 파일

- `docs/`: 그대로 배포할 사이트
- `source/`: 가져온 원본 HTML, 게시글·상품 상세·약관
- `scripts/build.py`: 원본에서 정적 사이트를 다시 생성하는 스크립트
- `docs/assets/archive.css`, `archive.js`: 호스팅 기능을 대체한 표시·갤러리 코드

재생성에는 Python과 BeautifulSoup가 필요합니다.

```sh
python3 -m pip install beautifulsoup4
python3 scripts/build.py
```

스냅샷 날짜: 2026-10-05. 원본의 상품·배송 안내 및 약관 본문은 보존했습니다. 현재 버전에서는 주문과 개인정보 입력을 받지 않습니다.
