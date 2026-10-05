"""Rebuild the read-only GitHub Pages archive from captured public HTML."""
from pathlib import Path
from bs4 import BeautifulSoup, Comment
from urllib.parse import urljoin, urlsplit, parse_qs
from urllib.request import Request, urlopen
from concurrent.futures import ThreadPoolExecutor
import hashlib,re,json,time
ROOT=Path(__file__).resolve().parent.parent
SRC=ROOT/'source'; OUT=ROOT/'docs'; AS=OUT/'assets'; AS.mkdir(parents=True,exist_ok=True)
BASE='https://www.bvd-s.com/'
cache={}; failures=[]
def asset(url):
 url=urljoin(BASE,url)
 if url in cache:return cache[url]
 ext=Path(urlsplit(url).path).suffix
 if ext not in ['.css','.png','.jpg','.jpeg','.webp','.gif','.svg','.ico','.woff','.woff2','.ttf']:ext='.css' if 'css' in url else '.bin'
 name=hashlib.sha256(url.encode()).hexdigest()[:20]+ext
 cache[url]='assets/'+name
 path=AS/name
 if not path.exists():
  for attempt in range(3):
   try:
    data=urlopen(Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=40).read()
    if ext=='.css':
     text=data.decode('utf-8','replace')
     def sub(m):
      u=m.group(1).strip(' \"\'')
      if u.startswith('data:') or u.startswith('#'):return m.group(0)
      return 'url("'+asset(urljoin(url,u)).replace('assets/','')+'")'
     text=re.sub(r'url\(([^)]+)\)',sub,text)
     text=re.sub(r'@import\s+[\"\']([^\"\']+)[\"\']',lambda m:'@import "'+asset(urljoin(url,m.group(1))).replace('assets/','')+'"',text)
     data=text.encode()
    path.write_bytes(data);break
   except Exception as e:
    if attempt==2:failures.append((url,str(e)))
 return cache[url]
def link(h):
 if not h:return h
 u=urlsplit(urljoin(BASE,h));q=parse_qs(u.query)
 if u.netloc!='www.bvd-s.com':return h
 if 'idx' in q:return ('post-' if q.get('bmode')==['view'] else 'product-')+q['idx'][0]+'.html'
 if q.get('mode'):return q['mode'][0]+'.html'
 p=u.path.strip('/')
 return ('index' if p in ['','index'] else p)+'.html' if p in ['','index','store','lounge','concierge','hello','qna','24'] else '#'
files=[p for p in SRC.glob('*.html') if p.stem not in ['policy','privacy'] and not p.stem.endswith(('-rendered','-dialog'))]
# Fetch shared styles and Google Fonts first.
font='https://fonts.googleapis.com/css2?family=Quicksand:wght@300;400;500;600;700&display=swap'
fontpath=asset(font)
suitepath=asset('https://vendor-cdn.imweb.me/css/suite.css')
(AS/'suite.css').write_text('@import url("'+suitepath.replace('assets/','')+'");')
for p in files:
 if p.stem.startswith('product-') and (SRC/(p.stem+'-rendered.html')).exists():p=SRC/(p.stem+'-rendered.html')
 s=BeautifulSoup(p.read_text(),'html.parser');name=p.stem.replace('-rendered','')
 for x in s.select('script, iframe, noscript, #loader, #site_alarm_slidemenu_container, #mobile_slide_menu_wrap, #cocoaModal, #cocoaSubModal, #member_profile, .alpha_instagram_feed, footer, [data-widget-type=inline_login_btn], [data-widget-type=inline_search_btn], [data-widget-type=inline_hr]'):x.decompose()
 for x in s.find_all(string=lambda t:isinstance(t,Comment)):x.extract()
 for x in s.select('link'):
  if 'stylesheet' in x.get('rel',[]):
   h=x.get('href','')
   if h.startswith('/') or any(v in h for v in ['alarm_menu','chosen','pretendard','tailwind','emoji','font-awesome']):x.decompose()
   else:x['href']=asset(h)
  elif 'icon' in x.get('rel',[]):x['href']=asset(x['href'])
  else:x.decompose()
 for x in s.find_all(True):
  if x.attrs is None:continue
  for a in list(x.attrs):
   if a.startswith('on'):del x[a]
  if x.name=='a':
   h=x.get('href','')
   if h.startswith('javascript') or x.get_text(strip=True) in ['글쓰기','Login','Register','구매하기','장바구니','목록','상세정보 펼쳐보기','상세정보 접기']:
    if x.get_text(strip=True)=='목록':x['href']='hello.html'
    else:x.decompose();continue
   else:x['href']=link(h)
   if x.get('href')=='24.html':x['href']='store.html'
  if x.name=='img':
   x['src']=x.get('data-original',x.get('src',''))
   x['style']=x.get('style','').replace('visibility:hidden','visibility:visible')
   x['loading']='eager'
  if x.name=='style':
   x.string=re.sub(r'@import[^;]+;','',x.get_text())
 # Replace dynamic product UI with preserved static product content.
 if name.startswith('product-'):
  wrap=s.select_one('.goods_wrapper')
  if wrap:
   image=s.select_one('#main-image') or s.select_one('.prod-owl-list img')
   title=s.select_one('.view_tit');price=s.select_one('.pay_number');summary=s.select_one('.goods_summary');detail=s.select_one('#prodDetailPC') or s.select_one('._prod_detail_detail_lazy_load') or s.select_one('#prod_detail_body')
   if detail and detail.name=='template':detail=BeautifulSoup(detail.decode_contents(),'html.parser')
   html='<div class="archive-product"><div class="archive-product-top"><div class="product-photo">'+str(image)+'</div><div class="product-copy">'+str(title)+str(price)+str(summary or '')+'<p class="catalog-note">상품 소개 · 결제는 제공하지 않습니다.</p><a href="store.html">← Store</a></div></div><div class="product-detail fr-view">'+str(detail or '')+'</div></div>'
   section=wrap.find_parent(class_='section_wrap')
   if section:
    # Keep the original section styling, replace all interactive commerce contents.
    section.clear();section.append(BeautifulSoup(html,'html.parser'))
 for x in s.select('.board_view .board_summary .tools, .comment, .comment_section, .board_write, .comment_num_warp, .social-sticker'):x.decompose()
 for x in s.select('form'):
  if x.select_one('input'):x.decompose()
 for x in s.select('[style]'):
  x['style']=x['style'].replace('visibility: hidden','visibility: visible').replace('visibility:hidden','visibility:visible')
 for text in s.find_all(string=True):
  if "Hosting by I'MWEB" in text:text.replace_with(str(text).replace("Hosting by I'MWEB",'Hosting by GitHub Pages'))
 # Download every remaining image and CSS background; no live Imweb assets required.
 urls=set()
 raw=str(s)
 urls.update(re.findall(r'https?://[^\s\"\'<>\)]+',raw))
 urls={u.rstrip(';') for u in urls if any(v in urlsplit(u).path.lower() for v in ['.jpg','.jpeg','.png','.gif','.webp','.svg','.ico','.woff'])}
 with ThreadPoolExecutor(max_workers=10) as ex:list(ex.map(asset,urls))
 for u in sorted(urls,key=len,reverse=True):raw=raw.replace(u,cache[u])
 s=BeautifulSoup(raw,'html.parser')
 for x in s.select('meta[property="og:url"]'):x['content']=''
 for x in s.select('meta[property="og:image"]'):x.decompose()
 for x in s.select('[srcset]'):del x['srcset']
 l=s.new_tag('link',rel='stylesheet',href=fontpath);s.head.append(l)
 l=s.new_tag('link',rel='stylesheet',href='assets/archive.css');s.head.append(l)
 js=s.new_tag('script',src='assets/archive.js',defer='');s.body.append(js)
 (OUT/(name+'.html')).write_text(str(s))
 print('Built',name,flush=True)
for kind in ['policy','privacy']:
 s=BeautifulSoup((OUT/'index.html').read_text(),'html.parser')
 for x in s.select('body > .section_wrap'):x.decompose()
 body=BeautifulSoup((SRC/(kind+'-dialog.html')).read_text(),'html.parser').select_one('.modal-body')
 main=s.new_tag('main',attrs={'class':'archive-policy'});heading=s.new_tag('h1');heading.string='이용약관' if kind=='policy' else '개인정보처리방침';main.append(heading);main.append(body);s.select_one('#doz_header').insert_after(main)
 (OUT/(kind+'.html')).write_text(str(s))
(OUT/'asset-map.json').write_text(json.dumps(cache,ensure_ascii=False,indent=2))
(OUT/'.nojekyll').touch()
if failures:print('FAILED',failures);raise SystemExit(1)
print('Downloaded',len(cache),'assets')
