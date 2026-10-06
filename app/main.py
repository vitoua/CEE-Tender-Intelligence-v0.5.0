from datetime import date
from urllib.parse import unquote
from fastapi import FastAPI,Form,Request,HTTPException
from fastapi.responses import HTMLResponse,RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from itsdangerous import URLSafeSerializer,BadSignature
from app.core import store,active,analytics
app=FastAPI(title='CEE Tender Intelligence',version='0.5.0');app.mount('/static',StaticFiles(directory='app/static'),name='static');tpl=Jinja2Templates(directory='app/templates');sign=URLSafeSerializer('change-me','session')
def auth(r):
 try:return sign.loads(r.cookies.get('session',''))=='admin'
 except BadSignature:return False
@app.get('/health')
def health():return {'status':'ok','version':'0.5.0','tenders':len(store.data)}
@app.get('/login',response_class=HTMLResponse)
def lp(request:Request):return tpl.TemplateResponse('login.html',{'request':request})
@app.post('/login')
def login(email:str=Form(),password:str=Form()):
 if email!='admin@example.com' or password!='ChangeMe123!':return HTMLResponse('Invalid credentials',400)
 r=RedirectResponse('/',303);r.set_cookie('session',sign.dumps('admin'),httponly=True,samesite='lax');return r
@app.get('/',response_class=HTMLResponse)
def home(request:Request,country:str='',active_only:int=1):
 if not auth(request):return RedirectResponse('/login',303)
 rows=list(store.data.values());rows=[x for x in rows if (not active_only or active(x)) and (not country or x.country==country)]
 return tpl.TemplateResponse('index.html',{'request':request,'rows':rows,'runs':store.runs,'countries':store.countries(),'country':country,'active_only':active_only})
@app.post('/refresh/{src}')
async def refresh(src:str,request:Request):
 if not auth(request):raise HTTPException(401)
 try:
  if src=='ted':from app.connectors.ted import fetch
  elif src=='prozorro':from app.connectors.prozorro import fetch
  else:raise HTTPException(404)
  store.add(src,await fetch())
 except Exception as e:store.error(src,e)
 return RedirectResponse('/',303)
@app.get('/analytics',response_class=HTMLResponse)
def report(request:Request,countries:list[str]|None=None,date_from:str='',date_to:str='',sort_by:str='wins',order:str='desc'):
 if not auth(request):raise HTTPException(401)
 rows=analytics(store.data.values(),countries,date.fromisoformat(date_from) if date_from else None,date.fromisoformat(date_to) if date_to else None);key={'wins':'wins','value':'total'}.get(sort_by,'wins');rows.sort(key=lambda r:(r[key],r['winner'].lower()),reverse=order!='asc')
 return tpl.TemplateResponse('analytics.html',{'request':request,'rows':rows,'countries':store.countries(),'selected':countries or [],'date_from':date_from,'date_to':date_to,'sort_by':sort_by,'order':order})
@app.get('/tenders/{tid:path}',response_class=HTMLResponse)
def detail(tid:str,request:Request):
 if not auth(request):raise HTTPException(401)
 x=store.data.get(tid)
 if not x:raise HTTPException(404)
 return tpl.TemplateResponse('detail.html',{'request':request,'x':x})
