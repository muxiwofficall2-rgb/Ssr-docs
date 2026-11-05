// Omad Tour — Rossiya ichidagi serverda ishlaydigan yagona fayl (sayt + chat + Telegram + push).
// Redis, Vercel, VPN kerak emas. Xabarlar server xotirasida saqlanadi (4 kundan keyin o'chadi).
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import zlib from 'node:zlib';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';

const ROOT=path.dirname(fileURLToPath(import.meta.url)),E=process.env,PORT=+E.PORT||3000;
const TG=(E.TG_API_BASE||'https://api.telegram.org').replace(/\/$/,''); // Telegram bloklansa: proksi manzili
const DATA=E.DATA_DIR||(fs.existsSync('/data')?'/data':path.join(ROOT,'data'));
const sleep=ms=>new Promise(r=>setTimeout(r,ms));

// ---------- kichik baza (Redis o'rniga) ----------
fs.mkdirSync(DATA,{recursive:true});
const DB_FILE=path.join(DATA,'db.json');
let db={v:{},e:{}};try{db=JSON.parse(fs.readFileSync(DB_FILE,'utf8'))}catch{}
const alive=k=>{if(db.e[k]&&db.e[k]<Date.now()){delete db.v[k];delete db.e[k]}return k in db.v};
const rng=(l,a,b)=>{const n=l.length;a=a<0?Math.max(n+a,0):a;b=b<0?n+b:b;return l.slice(a,b+1)};
const kv={
  GET:k=>alive(k)?db.v[k]:null,
  SET:(k,v,ex,s)=>{db.v[k]=String(v);if(ex==='EX')db.e[k]=Date.now()+s*1000;else delete db.e[k];return 'OK'},
  DEL:k=>{delete db.v[k];delete db.e[k];return 1},
  INCR:k=>{const n=(alive(k)?+db.v[k]:0)+1;db.v[k]=String(n);return n},
  EXPIRE:(k,s)=>{if(!alive(k))return 0;db.e[k]=Date.now()+s*1000;return 1},
  RPUSH:(k,x)=>{alive(k);const l=Array.isArray(db.v[k])?db.v[k]:(db.v[k]=[]);l.push(x);return l.length},
  LRANGE:(k,a,b)=>alive(k)?rng(db.v[k],a,b):[],
  LTRIM:(k,a,b)=>{if(alive(k))db.v[k]=rng(db.v[k],a,b);return 'OK'},
  SADD:(k,x)=>{alive(k);const l=Array.isArray(db.v[k])?db.v[k]:(db.v[k]=[]);if(!l.includes(x))l.push(x);return 1},
  SMEMBERS:k=>alive(k)?db.v[k]:[],
  SREM:(k,x)=>{if(alive(k))db.v[k]=db.v[k].filter(y=>y!==x);return 1}
};
const r=(c,...a)=>kv[c](...a);
const save=()=>{try{fs.writeFileSync(DB_FILE+'.tmp',JSON.stringify(db));fs.renameSync(DB_FILE+'.tmp',DB_FILE)}catch(e){console.error('save',e.message)}};
setInterval(save,20000);
setInterval(()=>{for(const k of Object.keys(db.v))alive(k)},600000); // eski kalitlarni tozalash
for(const s of ['SIGTERM','SIGINT'])process.on(s,()=>{save();process.exit(0)});

// ---------- yordamchilar ----------
const cidOk=c=>/^[a-f0-9]{24}$/.test(c||'');
const admins=()=>(E.ADMIN_CHAT_ID||'').split(',').map(x=>x.trim()).filter(Boolean);
const token=()=>((E.BOT_TOKEN||'').match(/\d{6,}:[A-Za-z0-9_-]{30,}/)||[''])[0];
const tg=(m,x)=>fetch(`${TG}/bot${token()}/${m}`,{method:'POST',...(x instanceof FormData?{body:x}:{headers:{'content-type':'application/json'},body:JSON.stringify(x)})}).then(a=>a.json());
const rate=(k,max,sec)=>{const n=r('INCR',k);if(n===1)r('EXPIRE',k,sec);return n<=max};
const kb=cid=>({inline_keyboard:[[{text:'✉️ Ответить',callback_data:'r:'+cid}]]});
let wpLib;
async function wp(){
  if(wpLib)return wpLib;
  const w=(await import('web-push')).default;let sj=(E.VAPID_SUBJECT||'').trim();
  if(!/^(mailto:|https?:\/\/)/.test(sj))sj='mailto:'+(sj||'admin@example.com');
  w.setVapidDetails(sj,(E.VAPID_PUBLIC||'').trim(),(E.VAPID_PRIVATE||'').trim());return wpLib=w;
}
const vapidCheck=async()=>{if(!E.VAPID_PUBLIC||!E.VAPID_PRIVATE)return 'kiritilmagan';try{await wp();return 'ok'}catch(e){return 'XATO: '+String(e.message).slice(0,90)}};
async function push(cid,payload){ // xato bo'lsa ham javob yo'qolmaydi
  try{const w=await wp();
    for(const s of r('SMEMBERS','p:'+cid)){
      try{await w.sendNotification(JSON.parse(s),JSON.stringify(payload),{urgency:'high',TTL:86400})}
      catch(e){if(e.statusCode===404||e.statusCode===410)r('SREM','p:'+cid,s)}}
  }catch(e){console.error('push',e.message)}
}
const touch=cid=>{r('LTRIM','c:'+cid,-100,-1);r('EXPIRE','c:'+cid,345600);r('SET','rd:'+cid,String(Date.now()),'EX',604800)};

// ---------- /api/chat ----------
async function chat(b,h){
  if(b.action==='reply'){ // admin javobi (faqat maxfiy kalit bilan)
    if(h['x-secret']!==E.ADMIN_SECRET||!cidOk(b.cid))return[403,{}];
    const text=String(b.text||'').slice(0,2000);
    r('RPUSH','c:'+b.cid,JSON.stringify({from:'ad',text,t:Date.now()}));touch(b.cid);
    await push(b.cid,{title:'Omad Tour',body:text});return[200,{ok:1}];
  }
  if(!cidOk(b.cid))return[400,{error:'cid'}];
  if(b.action==='submit'){ // Виза / Копи-центр: fayl + telefon -> Telegram
    if(!rate('rl:'+b.cid,12,3600))return[429,{error:'rate'}];
    const phone=String(b.phone||'').replace(/[^\d+]/g,'').slice(0,16);
    if(phone.replace(/\D/g,'').length<10)return[400,{error:'phone'}];
    const m=/^data:([\w\/+.-]+);base64,(.+)$/.exec(b.data||'');if(!m)return[400,{error:'file'}];
    const buf=Buffer.from(m[2],'base64');if(buf.length>3.2e6)return[413,{error:'big'}];
    const kind=b.kind==='print'?'print':'visa',img=m[1].startsWith('image/');
    const name=String(b.name||'file').replace(/[^\w.\- ]/g,'_').slice(0,60);
    const cap=`${kind==='visa'?'🛂 Виза':'🖨 Копи-центр'}\n📞 ${phone}\nID: ${b.cid.slice(0,6)}`;let sent=0;
    for(const a of admins()){
      const f=new FormData();f.append('chat_id',a);f.append('caption',cap);f.append('reply_markup',JSON.stringify(kb(b.cid)));
      f.append(img?'photo':'document',new Blob([buf],{type:m[1]}),img?'photo.jpg':name);
      try{const t=await tg(img?'sendPhoto':'sendDocument',f);if(t.ok)sent++;else console.error('tg',t.description)}catch(e){console.error('tg',e.message)}
    }
    r('SET','ph:'+b.cid,phone,'EX',2592000);
    return sent?[200,{ok:1}]:[502,{error:'telegram'}];
  }
  if(b.action==='sub'){if(b.sub&&b.sub.endpoint){r('SADD','p:'+b.cid,JSON.stringify(b.sub));r('EXPIRE','p:'+b.cid,2592000)}return[200,{ok:1}]}
  if(b.action==='send'&&(b.text||b.img)){ // chatdan matn / rasm -> Telegram
    if(!rate('rl:'+b.cid,60,3600))return[429,{}];
    const ph=r('GET','ph:'+b.cid),text=String(b.text||'').slice(0,800);
    const cap=`💬 Чат${ph?'\n📞 '+ph:''}\nID: ${b.cid.slice(0,6)}\n${text}`;
    const ok=typeof b.img==='string'&&b.img.startsWith('data:image/jpeg;base64,')&&b.img.length<4e6;let sent=0;
    for(const a of admins()){
      try{let m;
        if(ok){const f=new FormData();f.append('chat_id',a);f.append('caption',cap);f.append('reply_markup',JSON.stringify(kb(b.cid)));
          f.append('photo',new Blob([Buffer.from(b.img.split(',')[1],'base64')],{type:'image/jpeg'}),'photo.jpg');m=await tg('sendPhoto',f)}
        else m=await tg('sendMessage',{chat_id:a,text:cap,reply_markup:kb(b.cid)});
        if(m.ok)sent++;else console.error('tg',m.description)}catch(e){console.error('tg',e.message)}
    }
    return sent?[200,{ok:1}]:[502,{error:'telegram'}];
  }
  return[200,{msgs:r('LRANGE','c:'+b.cid,-50,-1).map(x=>JSON.parse(x)),read:Number(r('GET','rd:'+b.cid))||0}];
}

// ---------- Telegram: tugma va admin javobi ----------
async function onUpdate(u){
  const ids=admins(),cb=u.callback_query;
  if(cb){
    const uid=String(cb.from.id),d=cb.data||'',cid=d.slice(2);
    if(!d.startsWith('r:')||!cidOk(cid))return;
    if(!ids.includes(uid))return void await tg('answerCallbackQuery',{callback_query_id:cb.id,text:`⛔ Ruxsat yo'q. Sizning ID: ${uid}. ADMIN_CHAT_ID shu bo'lishi kerak.`,show_alert:true});
    r('SET','adm:'+uid,cid,'EX',1800);r('SET','rd:'+cid,String(Date.now()),'EX',604800);
    await tg('answerCallbackQuery',{callback_query_id:cb.id});
    return void await tg('sendMessage',{chat_id:cb.message.chat.id,text:'✍️ Напишите ответ клиенту. Отмена: /cancel',reply_markup:{force_reply:true,input_field_placeholder:'Ответ клиенту…'}});
  }
  const m=u.message;if(!m||!m.text)return;
  const uid=String(m.from.id),t=m.text.trim();
  if(/^\/(start|ping|id)\b/.test(t))return void await tg('sendMessage',{chat_id:m.chat.id,text:`✅ Support bot ishlayapti.\nSizning ID: ${uid}`});
  if(!ids.includes(uid))return;
  const cid=r('GET','adm:'+uid);
  if(/^\/cancel\b/.test(t)){r('DEL','adm:'+uid);return void await tg('sendMessage',{chat_id:m.chat.id,text:'Отменено'})}
  if(!cid||t[0]==='/')return;
  r('DEL','adm:'+uid);
  r('RPUSH','c:'+cid,JSON.stringify({from:'ad',text:t.slice(0,2000),t:Date.now()}));touch(cid);
  await push(cid,{title:'Omad Tour',body:t.slice(0,200)});
  await tg('sendMessage',{chat_id:m.chat.id,text:'✅ Отправлено клиенту',reply_markup:{inline_keyboard:[[{text:'✉️ Ответить ещё',callback_data:'r:'+cid}]]}});
}
const poll={running:false,last:null,error:null};
async function pollLoop(){
  if(!token()){poll.error='BOT_TOKEN yo\'q';return}
  poll.running=true;
  while(true){try{const j=await tg('deleteWebhook',{});if(j.ok)break;poll.error=j.description}catch(e){poll.error=String(e.message).slice(0,80)}await sleep(5000)}
  let off=0;
  while(true){
    try{
      const j=await tg('getUpdates',{offset:off,timeout:25,allowed_updates:['message','callback_query']});
      if(!j.ok){poll.error=j.description;await sleep(5000);continue}
      poll.error=null;poll.last=Date.now();
      for(const u of j.result){off=u.update_id+1;try{await onUpdate(u)}catch(e){console.error('update',e.message)}}
    }catch(e){poll.error=String(e.message).slice(0,80);await sleep(5000)}
  }
}

// ---------- /api/health ----------
async function health(q){
  const o={env:Object.fromEntries(['BOT_TOKEN','ADMIN_SECRET','VAPID_PUBLIC','VAPID_PRIVATE'].map(k=>[k,!!E[k]])),admins:admins().length,storage:'server xotirasi + '+DATA};
  const t=token();o.token=t?{botId:t.split(':')[0],secretLen:t.split(':')[1].length}:{found:false};
  o.vapid=await vapidCheck();
  try{const m=await tg('getMe',{});o.bot=m.ok?'@'+m.result.username:m.description}catch(e){o.bot='XATO: '+String(e.message).slice(0,80)}
  o.polling={running:poll.running,oxirgi:poll.last?new Date(poll.last).toISOString():null,xato:poll.error};
  if(E.ADMIN_SECRET&&q.test===E.ADMIN_SECRET){
    o.test=[];for(const a of admins()){try{const m=await tg('sendMessage',{chat_id:a,text:'✅ Omad Tour: server ↔ bot ishlayapti. Pastdagi tugmani bosib, javob berishni sinab ko\'ring.',reply_markup:{inline_keyboard:[[{text:'✉️ Ответить (test)',callback_data:'r:'+'0'.repeat(24)}]]}});o.test.push(m.ok?'yuborildi':m.description)}catch(e){o.test.push('XATO: '+e.message)}}
  }
  return o;
}

// ---------- HTTP ----------
const STATIC=new Set(['index.html','sw.js','manifest.json','icon-192.png','icon-512.png','icon-maskable-512.png','apple-touch-icon.png','logo.png','badge-96.png']);
const MIME={'.html':'text/html; charset=utf-8','.js':'text/javascript; charset=utf-8','.json':'application/manifest+json','.png':'image/png'};
const cache=new Map();
const readBody=req=>new Promise((ok,no)=>{let n=0;const c=[];req.on('data',d=>{n+=d.length;if(n>6e6){no(new Error('big'));req.destroy()}else c.push(d)});req.on('end',()=>ok(Buffer.concat(c).toString()));req.on('error',no)});
const send=(res,code,obj)=>{res.writeHead(code,{'content-type':'application/json; charset=utf-8','cache-control':'no-store'});res.end(JSON.stringify(obj))};
http.createServer(async(req,res)=>{
  try{
    const u=new URL(req.url,'http://x'),p=u.pathname;
    if(p==='/api/chat'){
      if(req.method!=='POST')return send(res,405,{});
      let b={};try{b=JSON.parse(await readBody(req)||'{}')}catch{return send(res,400,{error:'json'})}
      const [c,j]=await chat(b,req.headers);return send(res,c,j);
    }
    if(p==='/api/health')return send(res,200,await health(Object.fromEntries(u.searchParams)));
    const name=p==='/'?'index.html':p.slice(1);
    if(req.method!=='GET'&&req.method!=='HEAD'||!STATIC.has(name)){res.writeHead(404,{'content-type':'text/plain'});return res.end('Not found')}
    let f=cache.get(name);
    if(!f){const raw=fs.readFileSync(path.join(ROOT,name));const ext=path.extname(name);f={raw,gz:/\.(html|js|json)$/.test(name)?zlib.gzipSync(raw):null,type:MIME[ext]};cache.set(name,f)}
    const h={'content-type':f.type,'x-content-type-options':'nosniff','cache-control':/index|sw\.js|manifest/.test(name)?'no-cache':'public,max-age=86400'};
    if(name==='sw.js')h['service-worker-allowed']='/';
    const gz=f.gz&&/gzip/.test(req.headers['accept-encoding']||'');if(gz)h['content-encoding']='gzip';
    res.writeHead(200,h);res.end(req.method==='HEAD'?undefined:(gz?f.gz:f.raw));
  }catch(e){console.error(e);try{send(res,500,{error:String(e.message).slice(0,80)})}catch{}}
}).listen(PORT,()=>{console.log('Omad Tour server: port',PORT,'| data:',DATA);pollLoop()});
