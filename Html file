<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<title>OMAD TOUR</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
<style>
:root {
  --bg:        #070c18;
  --surface:   #0d1526;
  --panel:     #111d33;
  --border:    rgba(148,175,220,0.12);
  --border2:   rgba(148,175,220,0.22);
  --navy:      #1a2d52;
  --blue:      #1e3a6e;
  --accent:    #4a7fd4;
  --silver:    #94afdc;
  --silver2:   #c8d8f0;
  --white:     #eef3fc;
  --dim:       #5a7399;
  --green:     #3dd68c;
  --mono:      'JetBrains Mono', monospace;
  --sans:      'Inter', sans-serif;
}

*, *::before, *::after { margin:0; padding:0; box-sizing:border-box; -webkit-tap-highlight-color:transparent; }
html, body { height:100%; overflow:hidden; }
body { background:var(--bg); color:var(--white); font-family:var(--sans); }

/* subtle grid */
body::after {
  content:''; position:fixed; inset:0; pointer-events:none; z-index:0;
  background-image:
    linear-gradient(rgba(74,127,212,.025) 1px, transparent 1px),
    linear-gradient(90deg, rgba(74,127,212,.025) 1px, transparent 1px);
  background-size:48px 48px;
}

/* ambient glow */
body::before {
  content:''; position:fixed; inset:0; pointer-events:none; z-index:0;
  background:
    radial-gradient(ellipse 60% 50% at 15% 20%, rgba(30,58,110,.35) 0%, transparent 70%),
    radial-gradient(ellipse 50% 60% at 85% 80%, rgba(74,127,212,.12) 0%, transparent 70%);
}

/* ══ SCREENS ══ */
.screen {
  position:fixed; inset:0; z-index:10;
  display:flex; flex-direction:column; align-items:center;
  transition:opacity .3s ease, transform .3s ease;
  overflow:hidden;
}
.screen.hidden { opacity:0; pointer-events:none; transform:translateY(16px); }

/* ══ HOME ══ */
#homeScreen { justify-content:center; }

.home-wrap {
  position:relative; z-index:2;
  width:100%; max-width:390px;
  padding:0 20px;
  display:flex; flex-direction:column; gap:14px;
}

/* Logo block */
.brand {
  display:flex; flex-direction:column; align-items:center;
  gap:6px; margin-bottom:20px;
}
.brand-tag {
  display:flex; align-items:center; gap:8px;
  background:rgba(74,127,212,.08);
  border:1px solid var(--border2);
  border-radius:20px; padding:5px 14px;
}
.brand-dot {
  width:6px; height:6px; border-radius:50%;
  background:var(--accent);
  box-shadow:0 0 8px var(--accent);
  animation:pulse 2.4s ease-in-out infinite;
}
@keyframes pulse { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:.4;transform:scale(.8)} }
.brand-tag-txt {
  font-family:var(--mono); font-size:9px; font-weight:700;
  letter-spacing:3px; color:var(--silver); text-transform:uppercase;
}
.brand-name {
  font-size:36px; font-weight:700; letter-spacing:-1px;
  color:var(--white);
  text-shadow:0 0 40px rgba(74,127,212,.3);
}
.brand-name span { color:var(--accent); }
.brand-sub {
  font-size:10px; letter-spacing:4px; color:var(--dim);
  text-transform:uppercase; font-weight:500;
}

/* Home cards */
.hcard {
  width:100%; background:none; border:none;
  cursor:pointer; outline:none; text-align:left;
}
.hcard-inner {
  position:relative; overflow:hidden;
  padding:20px 20px 20px 56px;
  background:var(--surface);
  border:1px solid var(--border);
  border-radius:16px;
  transition:border-color .2s, transform .15s, background .2s;
}
.hcard:active .hcard-inner {
  transform:scale(.975);
  border-color:var(--border2);
  background:var(--panel);
}
/* left accent */
.hcard-inner::before {
  content:'';
  position:absolute; left:0; top:0; bottom:0; width:3px;
  background:linear-gradient(180deg, var(--accent) 0%, transparent 100%);
  border-radius:3px 0 0 3px;
  opacity:.5; transition:opacity .2s;
}
.hcard:active .hcard-inner::before { opacity:1; }
/* shimmer */
.hcard-inner::after {
  content:'';
  position:absolute; top:0; left:-120%; width:60%; height:100%;
  background:linear-gradient(90deg,transparent,rgba(148,175,220,.04),transparent);
  transform:skewX(-15deg); transition:left .5s;
}
.hcard:active .hcard-inner::after { left:160%; }

.hcard-num {
  position:absolute; left:18px; top:50%; transform:translateY(-50%);
  font-family:var(--mono); font-size:9px; color:var(--dim);
  writing-mode:vertical-rl; letter-spacing:2px;
}
.hcard-head { display:flex; align-items:center; gap:10px; margin-bottom:6px; }
.hcard-icon { font-size:20px; }
.hcard-title { font-size:15px; font-weight:600; color:var(--white); letter-spacing:.2px; }
.hcard-desc { font-size:12px; color:var(--dim); line-height:1.6; margin-bottom:10px; }
.hcard-pill {
  display:inline-flex; align-items:center; gap:5px;
  background:rgba(74,127,212,.1); border:1px solid rgba(74,127,212,.2);
  border-radius:20px; padding:3px 10px;
  font-family:var(--mono); font-size:9px; color:var(--silver);
  letter-spacing:1px;
}

/* ══ TOPBAR ══ */
.topbar {
  width:100%; flex-shrink:0;
  display:flex; align-items:center; gap:12px;
  padding:14px 16px;
  background:rgba(7,12,24,.94); backdrop-filter:blur(20px);
  border-bottom:1px solid var(--border);
  z-index:20; position:relative;
}
.back {
  width:36px; height:36px;
  display:flex; align-items:center; justify-content:center;
  background:var(--surface); border:1px solid var(--border2);
  border-radius:10px; cursor:pointer;
  font-size:15px; color:var(--silver);
  transition:transform .15s, background .15s; flex-shrink:0;
}
.back:active { transform:scale(.88); background:var(--panel); }
.topbar-title {
  font-family:var(--mono); font-size:11px; font-weight:700;
  letter-spacing:3px; color:var(--silver2); text-transform:uppercase;
}

/* ══ SCROLL ══ */
.scroll {
  flex:1; overflow-y:auto; overflow-x:hidden;
  -webkit-overflow-scrolling:touch;
  padding:20px 16px 80px;
  position:relative; z-index:2;
}
.inner { max-width:440px; margin:0 auto; display:flex; flex-direction:column; gap:18px; }

/* Section label */
.slbl {
  font-family:var(--mono); font-size:9px; letter-spacing:3px;
  color:var(--dim); text-transform:uppercase; margin-bottom:10px;
}

/* ══ COUNTRY GRID ══ */
.cgrid { display:grid; grid-template-columns:repeat(3,1fr); gap:8px; }
.cbtn {
  padding:10px 4px; text-align:center;
  background:var(--surface); border:1px solid var(--border);
  border-radius:10px; cursor:pointer;
  font-family:var(--sans); font-size:11px; font-weight:600;
  color:var(--dim); transition:all .18s;
}
.cbtn.on {
  background:rgba(74,127,212,.12);
  border-color:rgba(74,127,212,.4);
  color:var(--silver2);
}
.cbtn:active { transform:scale(.93); }
.cflag { font-size:16px; display:block; margin-bottom:3px; }

/* ══ UPLOAD ZONE ══ */
.upzone {
  border:1.5px dashed rgba(74,127,212,.3); border-radius:14px;
  padding:30px 20px; text-align:center;
  background:rgba(13,21,38,.6); cursor:pointer;
  transition:all .2s;
}
.upzone:active { border-color:var(--accent); background:rgba(74,127,212,.06); }
.upzone-ico { font-size:34px; display:block; margin-bottom:10px; animation:float 3s ease-in-out infinite; }
@keyframes float { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-5px)} }
.upzone-t { font-size:13px; font-weight:600; color:var(--silver); margin-bottom:3px; }
.upzone-h { font-size:11px; color:var(--dim); }
input[type=file] { display:none; }

/* Preview */
.prev { display:none; border-radius:12px; overflow:hidden; border:1px solid var(--border2); position:relative; }
.prev.on { display:block; }
.prev img { width:100%; max-height:190px; object-fit:cover; display:block; }
.prev-change {
  position:absolute; bottom:8px; right:8px;
  background:rgba(7,12,24,.9); border:1px solid var(--border2);
  border-radius:6px; padding:4px 12px;
  font-size:11px; color:var(--silver); cursor:pointer;
}

/* ══ ACTION BUTTON ══ */
.act-btn {
  width:100%; padding:15px;
  background:linear-gradient(135deg, #163266 0%, #1e4080 50%, #1a3570 100%);
  border:1px solid rgba(74,127,212,.3); border-radius:13px;
  color:var(--white); font-family:var(--mono); font-size:11px; font-weight:700;
  letter-spacing:3px; cursor:pointer; position:relative; overflow:hidden;
  transition:transform .15s; box-shadow:0 4px 20px rgba(22,50,102,.5);
}
.act-btn::after {
  content:''; position:absolute; top:0; left:-100%; width:50%; height:100%;
  background:linear-gradient(90deg,transparent,rgba(255,255,255,.06),transparent);
  transform:skewX(-20deg); transition:left .5s;
}
.act-btn:active::after { left:160%; }
.act-btn:active { transform:scale(.97); }
.act-btn:disabled { opacity:.4; cursor:not-allowed; }

/* ══ SPINNER ══ */
.spin-row { display:none; align-items:center; justify-content:center; gap:12px; padding:14px; }
.spin-row.on { display:flex; }
.spin { width:24px; height:24px; border:2px solid rgba(74,127,212,.15); border-top-color:var(--accent); border-radius:50%; animation:rot .7s linear infinite; }
@keyframes rot { to{transform:rotate(360deg)} }
.spin-t { font-family:var(--mono); font-size:9px; letter-spacing:2px; color:var(--dim); }

/* ══ RESULT BOX ══ */
.rbox { display:none; border-radius:14px; overflow:hidden; border:1px solid rgba(74,127,212,.25); }
.rbox.on { display:block; }
.rbox-head {
  display:flex; align-items:center; justify-content:space-between;
  padding:11px 14px;
  background:rgba(22,50,102,.25); border-bottom:1px solid var(--border);
}
.rbox-lbl { font-family:var(--mono); font-size:9px; letter-spacing:3px; color:var(--accent); }
.copy-btn {
  display:flex; align-items:center; gap:5px;
  background:rgba(74,127,212,.12); border:1px solid rgba(74,127,212,.25);
  border-radius:7px; padding:6px 14px;
  font-family:var(--mono); font-size:9px; font-weight:700;
  letter-spacing:2px; color:var(--silver2); cursor:pointer; transition:all .15s;
}
.copy-btn:active { background:rgba(74,127,212,.25); transform:scale(.93); }
.copy-btn.ok { color:var(--green); border-color:rgba(61,214,140,.3); }
.rbox-body { padding:16px 14px; background:rgba(5,10,20,.8); }
.rbox-text {
  font-family:var(--mono); font-size:clamp(10px,2.5vw,12.5px);
  color:#6ee7b7; line-height:2.1; word-break:break-all; white-space:pre-wrap; letter-spacing:.3px;
}

/* ══ SIZE BUTTONS ══ */
.sgrid { display:grid; grid-template-columns:1fr 1fr; gap:10px; }
.sbtn {
  padding:18px 10px; text-align:center;
  background:var(--surface); border:1px solid var(--border);
  border-radius:14px; cursor:pointer; transition:all .18s;
}
.sbtn.on { border-color:rgba(74,127,212,.5); background:rgba(74,127,212,.1); }
.sbtn:active { transform:scale(.95); }
.sbtn-ico { font-size:20px; display:block; margin-bottom:7px; }
.sbtn-dim { font-family:var(--mono); font-size:15px; font-weight:700; color:var(--silver2); display:block; margin-bottom:3px; }
.sbtn-sub { font-size:10px; color:var(--dim); }

/* ══ PHOTO CANVAS ══ */
.canvas-sec { display:none; flex-direction:column; gap:10px; }
.canvas-sec.on { display:flex; }
.canvas-meta { display:flex; align-items:center; justify-content:space-between; }
.canvas-lbl { font-family:var(--mono); font-size:9px; letter-spacing:2px; color:var(--dim); }
.canvas-ok { font-family:var(--mono); font-size:9px; letter-spacing:2px; color:var(--green); }
.canvas-frame {
  background:#fff; border-radius:12px;
  border:1px solid rgba(255,255,255,.1);
  display:flex; align-items:center; justify-content:center; min-height:160px;
  overflow:hidden;
}
#pCanvas { display:block; max-width:100%; height:auto; }

/* progress */
.prog { display:none; flex-direction:column; gap:8px; padding:4px 0; }
.prog.on { display:flex; }
.prog-bar-bg { height:3px; background:rgba(74,127,212,.15); border-radius:2px; overflow:hidden; }
.prog-fill { height:100%; background:linear-gradient(90deg, var(--accent), #90caf9); border-radius:2px; width:0%; transition:width .25s; }
.prog-t { font-family:var(--mono); font-size:9px; letter-spacing:2px; color:var(--dim); text-align:center; }

/* save btn */
.save-btn {
  width:100%; padding:15px;
  background:linear-gradient(135deg, #0d3320, #145228, #1a6633);
  border:1px solid rgba(61,214,140,.2); border-radius:13px;
  color:var(--white); font-family:var(--mono); font-size:11px; font-weight:700;
  letter-spacing:3px; cursor:pointer; transition:transform .15s;
  box-shadow:0 4px 18px rgba(13,51,32,.5); display:none;
}
.save-btn.on { display:block; }
.save-btn:active { transform:scale(.97); }

/* ══ TOAST ══ */
.toast {
  position:fixed; bottom:24px; left:50%;
  transform:translateX(-50%) translateY(60px);
  background:rgba(13,21,38,.97); border:1px solid var(--border2);
  border-radius:24px; padding:10px 22px;
  font-family:var(--mono); font-size:10px; letter-spacing:2px;
  color:var(--silver2); z-index:999;
  transition:transform .3s cubic-bezier(.175,.885,.32,1.275);
  white-space:nowrap; backdrop-filter:blur(16px);
}
.toast.on { transform:translateX(-50%) translateY(0); }
</style>
</head>
<body>

<!-- HOME -->
<div class="screen" id="homeScreen">
  <div class="home-wrap">
    <div class="brand">
      <div class="brand-tag">
        <div class="brand-dot"></div>
        <div class="brand-tag-txt">Professional Suite</div>
      </div>
      <div class="brand-name">OMAD <span>TOUR</span></div>
      <div class="brand-sub">Travel Tools</div>
    </div>

    <button class="hcard" onclick="go('docsScreen')">
      <div class="hcard-inner">
        <div class="hcard-num">01</div>
        <div class="hcard-head">
          <span class="hcard-icon">🛂</span>
          <div class="hcard-title">SSR DOCS Generator</div>
        </div>
        <div class="hcard-desc">Pasport rasmini yuklang — AI avtomatik o'qib Amadeus GDS SSR DOCS formatini chiqaradi</div>
        <div class="hcard-pill">⚡ AI · AVTOMATIK</div>
      </div>
    </button>

    <button class="hcard" onclick="go('photoScreen')">
      <div class="hcard-inner">
        <div class="hcard-num">02</div>
        <div class="hcard-head">
          <span class="hcard-icon">📷</span>
          <div class="hcard-title">Foto Razmer</div>
        </div>
        <div class="hcard-desc">Rasmni yuklang — orqa fon oq bo'ladi, 3.5×4.5 yoki 2×3 sm razmerlaydi va saqlaydi</div>
        <div class="hcard-pill">📐 35×45 · 20×30</div>
      </div>
    </button>
  </div>
</div>

<!-- DOCS -->
<div class="screen hidden" id="docsScreen">
  <div class="topbar">
    <div class="back" onclick="go('homeScreen')">←</div>
    <div class="topbar-title">SSR DOCS Generator</div>
  </div>
  <div class="scroll">
    <div class="inner">

      <div>
        <div class="slbl">Davlat tanlang</div>
        <div class="cgrid">
          <button class="cbtn on" data-c="UZB" onclick="pickC(this)"><span class="cflag">🇺🇿</span>UZB</button>
          <button class="cbtn" data-c="RUS" onclick="pickC(this)"><span class="cflag">🇷🇺</span>RUS</button>
          <button class="cbtn" data-c="TKM" onclick="pickC(this)"><span class="cflag">🇹🇲</span>TKM</button>
          <button class="cbtn" data-c="TJK" onclick="pickC(this)"><span class="cflag">🇹🇯</span>TJK</button>
          <button class="cbtn" data-c="KGZ" onclick="pickC(this)"><span class="cflag">🇰🇬</span>KGZ</button>
          <button class="cbtn" data-c="KAZ" onclick="pickC(this)"><span class="cflag">🇰🇿</span>KAZ</button>
        </div>
      </div>

      <div>
        <div class="slbl">Pasport rasmi</div>
        <div class="upzone" id="dZone" onclick="document.getElementById('dFile').click()">
          <span class="upzone-ico">📄</span>
          <div class="upzone-t">Pasport rasmini yuklang</div>
          <div class="upzone-h">JPG · PNG · HEIC · Istalgan format</div>
        </div>
        <input type="file" id="dFile" accept="image/*" onchange="onDocImg(this)">
        <div class="prev" id="dPrev">
          <img id="dPrevImg" src="" alt="">
          <div class="prev-change" onclick="document.getElementById('dFile').click()">↺ Almashtirish</div>
        </div>
      </div>

      <button class="act-btn" id="dBtn" onclick="runDocs()" style="display:none">
        ⚡ &nbsp; SSR DOCS YARATISH
      </button>

      <div class="spin-row" id="dSpin">
        <div class="spin"></div>
        <div class="spin-t">PASPORT O'QILMOQDA...</div>
      </div>

      <div class="rbox" id="dBox">
        <div class="rbox-head">
          <div class="rbox-lbl">✈ SSR DOCS FORMAT</div>
          <button class="copy-btn" id="dCopyBtn" onclick="copyIt()">
            <span>📋</span><span id="dCopyTxt">COPY</span>
          </button>
        </div>
        <div class="rbox-body">
          <div class="rbox-text" id="dOut"></div>
        </div>
      </div>

    </div>
  </div>
</div>

<!-- PHOTO -->
<div class="screen hidden" id="photoScreen">
  <div class="topbar">
    <div class="back" onclick="go('homeScreen')">←</div>
    <div class="topbar-title">Foto Razmer</div>
  </div>
  <div class="scroll">
    <div class="inner">

      <div>
        <div class="slbl">Razmer tanlang</div>
        <div class="sgrid">
          <button class="sbtn on" data-sz="35x45" onclick="pickSz(this)">
            <span class="sbtn-ico">🪪</span>
            <span class="sbtn-dim">3.5 × 4.5</span>
            <span class="sbtn-sub">35 × 45 мм</span>
          </button>
          <button class="sbtn" data-sz="20x30" onclick="pickSz(this)">
            <span class="sbtn-ico">🖼️</span>
            <span class="sbtn-dim">2 × 3</span>
            <span class="sbtn-sub">20 × 30 мм</span>
          </button>
        </div>
      </div>

      <div>
        <div class="slbl">Rasm yuklang</div>
        <div class="upzone" id="pZone" onclick="document.getElementById('pFile').click()">
          <span class="upzone-ico">🖼️</span>
          <div class="upzone-t">Fotosuratni tanlang</div>
          <div class="upzone-h">Barcha formatlar · Har qanday o'lcham</div>
        </div>
        <input type="file" id="pFile" accept="image/*" onchange="onPhotoImg(this)">
      </div>

      <div class="prog" id="pProg">
        <div class="prog-bar-bg"><div class="prog-fill" id="pFill"></div></div>
        <div class="prog-t" id="pProgT">TAYYORLANMOQDA...</div>
      </div>

      <div class="canvas-sec" id="cSec">
        <div class="canvas-meta">
          <div class="canvas-lbl" id="cLbl">TAYYOR RASM</div>
          <div class="canvas-ok">✓ ORQ FON OQ</div>
        </div>
        <div class="canvas-frame">
          <canvas id="pCanvas"></canvas>
        </div>
      </div>

      <button class="save-btn" id="saveBtn" onclick="savePhoto()">
        💾 &nbsp; СОХРАНИТЬ В ГАЛЕРЕЮ
      </button>

    </div>
  </div>
</div>

<div class="toast" id="toast"></div>

<script>
// NAV
function go(id) {
  document.querySelectorAll('.screen').forEach(s => s.classList.toggle('hidden', s.id !== id));
}
function toast(msg, dur=2500) {
  const t = document.getElementById('toast');
  t.textContent = msg; t.classList.add('on');
  setTimeout(() => t.classList.remove('on'), dur);
}

// ── DOCS ──
let dC = 'UZB', dB64 = null, dMime = 'image/jpeg';

function pickC(btn) {
  document.querySelectorAll('.cbtn').forEach(b => b.classList.remove('on'));
  btn.classList.add('on'); dC = btn.dataset.c;
}

function onDocImg(inp) {
  if (!inp.files[0]) return;
  dMime = inp.files[0].type || 'image/jpeg';
  const r = new FileReader();
  r.onload = e => {
    dB64 = e.target.result.split(',')[1];
    document.getElementById('dPrevImg').src = e.target.result;
    document.getElementById('dPrev').classList.add('on');
    document.getElementById('dZone').style.display = 'none';
    document.getElementById('dBtn').style.display = 'block';
    document.getElementById('dBox').classList.remove('on');
  };
  r.readAsDataURL(inp.files[0]);
}

async function runDocs() {
  if (!dB64) return;
  document.getElementById('dBtn').disabled = true;
  document.getElementById('dSpin').classList.add('on');
  document.getElementById('dBox').classList.remove('on');

  try {
    const res = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model: 'claude-sonnet-4-20250514',
        max_tokens: 300,
        messages: [{
          role: 'user',
          content: [
            { type: 'image', source: { type: 'base64', media_type: dMime, data: dB64 } },
            { type: 'text', text: `You are an airline GDS passport OCR expert.
Read this passport carefully. Use the MRZ lines at the bottom for accuracy.
Output ONLY these 2 lines, nothing else:
SSR DOCS HK1 -P/[NAT]/[PASSNO]/P/[DOB]/[SEX]/[EXP]/[SURNAME]/[GIVENNAMES]
SSR DOCO HK1 -////[EXP]/[PASSNO]
Rules: dates DDMMMYY (e.g. 20JUL90), SEX=M or F, names ALL CAPS, NAT=3-letter code.` }
          ]
        }]
      })
    });
    const j = await res.json();
    if (j.error) throw new Error(j.error.message);
    const txt = j.content.map(x => x.text || '').join('').trim();
    document.getElementById('dOut').textContent = txt;
    document.getElementById('dBox').classList.add('on');
    toast('✅ SSR DOCS tayyor!');
  } catch(e) {
    toast('❌ ' + (e.message || 'Xatolik yuz berdi'));
  } finally {
    document.getElementById('dSpin').classList.remove('on');
    document.getElementById('dBtn').disabled = false;
  }
}

function copyIt() {
  const txt = document.getElementById('dOut').textContent;
  if (!txt) return;
  const done = () => {
    document.getElementById('dCopyTxt').textContent = 'COPIED!';
    document.getElementById('dCopyBtn').classList.add('ok');
    setTimeout(() => {
      document.getElementById('dCopyTxt').textContent = 'COPY';
      document.getElementById('dCopyBtn').classList.remove('ok');
    }, 2200);
    toast('📋 Nusxalandi!');
  };
  navigator.clipboard.writeText(txt).then(done).catch(() => {
    const ta = document.createElement('textarea');
    ta.value = txt; ta.style.cssText = 'position:fixed;opacity:0';
    document.body.appendChild(ta); ta.focus(); ta.select();
    try { document.execCommand('copy'); done(); } catch {}
    document.body.removeChild(ta);
  });
}

// ── PHOTO ──
let selSz = '35x45', origSrc = null;
const SZ = {
  '35x45': { w:413, h:531, label:'3.5×4.5 sm' },
  '20x30': { w:236, h:354, label:'2×3 sm' }
};

function pickSz(btn) {
  document.querySelectorAll('.sbtn').forEach(b => b.classList.remove('on'));
  btn.classList.add('on'); selSz = btn.dataset.sz;
  if (origSrc) doPhoto();
}

function onPhotoImg(inp) {
  if (!inp.files[0]) return;
  const r = new FileReader();
  r.onload = e => {
    origSrc = e.target.result;
    document.getElementById('pZone').style.display = 'none';
    doPhoto();
  };
  r.readAsDataURL(inp.files[0]);
}

function setP(pct, txt) {
  document.getElementById('pFill').style.width = pct + '%';
  document.getElementById('pProgT').textContent = txt;
}

function doPhoto() {
  const sz = SZ[selSz];
  document.getElementById('cLbl').textContent = sz.label.toUpperCase();
  document.getElementById('cSec').classList.remove('on');
  document.getElementById('saveBtn').classList.remove('on');
  document.getElementById('pProg').classList.add('on');
  setP(10, 'RASM YUKLANMOQDA...');

  const img = new Image();
  img.onload = () => {
    const SC = 2;
    const CW = sz.w * SC, CH = sz.h * SC;

    // draw cover-fit
    const off = document.createElement('canvas');
    off.width = CW; off.height = CH;
    const oc = off.getContext('2d');
    const sf = Math.max(CW / img.width, CH / img.height);
    const dw = img.width * sf, dh = img.height * sf;
    oc.drawImage(img, (CW-dw)/2, (CH-dh)/2, dw, dh);

    setP(40, 'FONDO ANIQLANMOQDA...');

    const id = oc.getImageData(0, 0, CW, CH);
    const px = id.data;

    // sample edge pixels for background color
    const samples = [];
    const step = 3;
    for (let x = 0; x < CW; x += step) {
      push(x, 0); push(x, 1); push(x, CH-1); push(x, CH-2);
    }
    for (let y = 2; y < CH-2; y += step) {
      push(0, y); push(1, y); push(CW-1, y); push(CW-2, y);
    }
    function push(x, y) {
      const i = (y*CW+x)*4;
      samples.push([px[i], px[i+1], px[i+2]]);
    }

    let sr=0,sg=0,sb=0;
    samples.forEach(s=>{sr+=s[0];sg+=s[1];sb+=s[2]});
    const n = samples.length;
    const BR = sr/n, BG = sg/n, BB = sb/n;
    const bgLuma = BR*.299 + BG*.587 + BB*.114;

    setP(65, 'ORQ FON OLIB TASHLANMOQDA...');

    // Flood fill from edges
    const W = CW, H = CH;
    const marked = new Uint8Array(W*H);
    const THR = bgLuma > 150 ? 58 : 42;

    function dist(i) {
      const r=px[i],g=px[i+1],b=px[i+2];
      return Math.sqrt((r-BR)**2+(g-BG)**2+(b-BB)**2);
    }

    // seed edges
    const Q = [];
    for (let x=0;x<W;x++) { Q.push(x,0); Q.push(x,H-1); }
    for (let y=1;y<H-1;y++) { Q.push(0,y); Q.push(W-1,y); }

    let qi = 0;
    while (qi < Q.length) {
      const x=Q[qi++], y=Q[qi++];
      if (x<0||x>=W||y<0||y>=H) continue;
      const idx = y*W+x;
      if (marked[idx]) continue;
      if (dist(idx*4) > THR) continue;
      marked[idx] = 1;
      Q.push(x+1,y, x-1,y, x,y+1, x,y-1);
    }

    // also remove very bright isolated pixels
    for (let i=0;i<px.length;i+=4) {
      const luma = px[i]*.299+px[i+1]*.587+px[i+2]*.114;
      if (luma > 230) marked[i/4] = 1;
    }

    // apply white
    for (let i=0;i<px.length;i+=4) {
      if (marked[i/4]) { px[i]=255;px[i+1]=255;px[i+2]=255;px[i+3]=255; }
    }
    oc.putImageData(id, 0, 0);

    setP(90, 'TUGATILMOQDA...');

    // final canvas
    const canvas = document.getElementById('pCanvas');
    canvas.width=CW; canvas.height=CH;
    canvas.style.width=sz.w+'px'; canvas.style.height=sz.h+'px';
    const ctx = canvas.getContext('2d');
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(0,0,CW,CH);
    ctx.drawImage(off,0,0);

    setP(100,'TAYYOR!');
    setTimeout(()=>{
      document.getElementById('pProg').classList.remove('on');
      document.getElementById('cSec').classList.add('on');
      document.getElementById('saveBtn').classList.add('on');
      toast('✅ Rasm tayyor!');
    }, 300);
  };
  img.src = origSrc;
}

function savePhoto() {
  const canvas = document.getElementById('pCanvas');
  const sz = SZ[selSz];
  const fname = 'omadtour_' + sz.label.replace(/[^\w]/g,'_') + '.jpg';
  canvas.toBlob(blob => {
    if (navigator.share && navigator.canShare) {
      const f = new File([blob], fname, { type:'image/jpeg' });
      if (navigator.canShare({files:[f]})) {
        navigator.share({files:[f]})
          .then(()=>toast('✅ Saqlandi!'))
          .catch(()=>dl(canvas,fname));
        return;
      }
    }
    dl(canvas, fname);
  }, 'image/jpeg', 0.97);
}
function dl(canvas, fname) {
  const a = document.createElement('a');
  a.download=fname; a.href=canvas.toDataURL('image/jpeg',.97); a.click();
  toast('💾 Yuklab olindi!');
}
</script>
</body>
</html>
