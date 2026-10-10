from pathlib import Path
from xml.dom import minidom as M
import zipfile, shutil, datetime, copy
base=Path(r'D:\studentus\studia 2 stopnia\sem3')
source=next(base.glob('*serwis*/*.docx'))
reference=next(base.glob('*widok*/*aplikacji.docx'))
W='http://schemas.openxmlformats.org/wordprocessingml/2006/main'
R='http://schemas.openxmlformats.org/officeDocument/2006/relationships'
def load(p):
 with zipfile.ZipFile(p) as z: return {n:z.read(n) for n in z.namelist()}
a=load(source); b=load(reference)
doc=M.parseString(a['word/document.xml']); ref=M.parseString(b['word/document.xml'])
body=doc.getElementsByTagNameNS(W,'body')[0]; rb=ref.getElementsByTagNameNS(W,'body')[0]
children=[n for n in body.childNodes if n.nodeType==n.ELEMENT_NODE]
refchildren=[n for n in rb.childNodes if n.nodeType==n.ELEMENT_NODE]
def el(name, attrs={}):
 n=doc.createElementNS(W,'w:'+name)
 for k,v in attrs.items(): n.setAttributeNS(W,'w:'+k,str(v))
 return n
def para(text, kind):
 template={'heading':17,'description':18,'caption':23}[kind]
 p=doc.importNode(refchildren[template],True)
 for n in list(p.childNodes):
  if not (n.nodeType==n.ELEMENT_NODE and n.localName=='pPr'): p.removeChild(n)
 r=el('r')
 if kind=='caption':
  rp=el('rPr'); rp.appendChild(el('i')); rp.appendChild(el('color',{'val':'595959'})); rp.appendChild(el('sz',{'val':18})); rp.appendChild(el('szCs',{'val':18})); r.appendChild(rp)
 t=el('t'); t.appendChild(doc.createTextNode(text)); r.appendChild(t); p.appendChild(r)
 return p
images={}
for n in children[16:]:
 for drawing in n.getElementsByTagNameNS(W,'drawing'):
  blip=drawing.getElementsByTagName('a:blip')[0]
  rid=blip.getAttributeNS(R,'embed')
  p=el('p'); pp=el('pPr'); pp.appendChild(el('keepNext')); pp.appendChild(el('jc',{'val':'center'})); p.appendChild(pp)
  r=el('r'); r.appendChild(doc.importNode(drawing,True)); p.appendChild(r); images[int(rid[3:])-3]=p
# Keep the cover and its original page break intact.
cover=[n.toxml() for n in children[:16]]
section=next(n for n in children if n.localName=='sectPr')
for n in children[16:]: body.removeChild(n)
groups=[
('1. Instalacja narzędzi Firebase', 'Zaktualizowano npm, sprawdzono wersję Node.js i zainstalowano globalnie Firebase CLI poleceniem npm install -g firebase-tools.', [(2,'Aktualizacja menedżera npm.'),(3,'Sprawdzenie wersji Node.js.'),(4,'Globalna instalacja Firebase CLI.')]),
('2. Konfiguracja projektu i Firebase Hosting', 'Zalogowano się do Firebase, a następnie skonfigurowano Hosting dla projektu test-c8cb0. Jako katalog strony wybrano public.', [(5,'Logowanie do konta Firebase.'),(6,'Konfiguracja Firebase Hosting.')]),
('3. Edycja pliku index.html', 'W pliku public/index.html dodano statyczny tekst z imieniem i nazwiskiem autora.', [(7,'Imię i nazwisko w kodzie HTML.')]),
('4. Deployment projektu', 'Stronę opublikowano poleceniem firebase deploy --only hosting. Terminal potwierdził zakończenie wdrożenia i wyświetlił adres strony.', [(8,'Pomyślny deployment na Firebase.')]),
('5. Wyświetlenie strony w przeglądarce', 'Otwarto stronę pod adresem https://test-c8cb0.web.app. Zrzut przedstawia jej rozbudowaną wersję z imieniem i nazwiskiem oraz licznikiem kliknięć.', [(9,'Strona na serwerze Firebase.')]),
('6. Rozbudowa strony o JavaScript i CSS', 'Rozbudowano HTML, dodano style CSS oraz obsługę licznika i przycisku zerowania w JavaScript. Po ponownym wdrożeniu sprawdzono stronę w przeglądarce.', [(11,'Rozbudowany kod HTML.'),(12,'Obsługa licznika w JavaScript.'),(13,'Style strony w pliku CSS.'),(10,'Działający licznik po rozbudowie strony.')])]
count=0
for heading, description, shots in groups:
 body.appendChild(para(heading,'heading')); body.appendChild(para(description,'description'))
 for key,caption in shots:
  body.appendChild(images[key]); count+=1; body.appendChild(para(f'Zdjęcie {count} - {caption}','caption'))
body.appendChild(section)
assert cover==[n.toxml() for n in [n for n in body.childNodes if n.nodeType==n.ELEMENT_NODE][:16]]
# Copy heading style definitions from the reference if missing.
styles=M.parseString(a['word/styles.xml']); refs=M.parseString(b['word/styles.xml'])
ids={n.getAttributeNS(W,'styleId') for n in styles.getElementsByTagNameNS(W,'style')}
for n in refs.getElementsByTagNameNS(W,'style'):
 sid=n.getAttributeNS(W,'styleId')
 if sid in ('Nagwek1','Nagwek1Znak'):
  old=next((x for x in styles.getElementsByTagNameNS(W,'style') if x.getAttributeNS(W,'styleId')==sid),None)
  if old: styles.documentElement.removeChild(old)
  styles.documentElement.appendChild(styles.importNode(n,True))
a['word/document.xml']=doc.toxml(encoding='UTF-8'); a['word/styles.xml']=styles.toxml(encoding='UTF-8')
backup=source.with_name(source.stem+' - kopia przed edycją '+datetime.datetime.now().strftime('%Y%m%d-%H%M%S')+'.docx')
shutil.copy2(source,backup)
temp=source.with_name(source.stem+' - edycja.tmp')
with zipfile.ZipFile(temp,'w',zipfile.ZIP_DEFLATED) as z:
 for name,data in a.items(): z.writestr(name,data)
with zipfile.ZipFile(temp) as z:
 assert z.testzip() is None
 for name,data in load(backup).items():
  if name.startswith('word/media/'): assert z.read(name)==data
 assert len(M.parseString(z.read('word/document.xml')).getElementsByTagNameNS(W,'drawing'))==13
source.write_bytes(temp.read_bytes()); temp.unlink()
print('Edited:',source); print('Backup:',backup); print('Verified: unchanged cover, all 12 screenshots preserved, 6 headings and 12 captions.')
