from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import httpx
import asyncio

app = FastAPI()

# ======================== API কনফিগারেশন ========================
# 🔴 PANEL B (NEXAOTP - ডান কলাম)
NEXA_API_URL = "http://2.58.82.137:5000/api/v1/console/logs?limit=100"
NEXA_API_KEY = "nxa_b2101087b38e27f8f19f4cdd5963bc695808fbb8"

# 🟢 PANEL A (MNIT - বাম কলাম) 
MNIT_API_URL = "https://x.mnitnetwork.com/mapi/v1/mdashboard/console/info"
MNIT_MAUTH_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1aWQiOiJNX0k0VkE3RkU2UiIsInJvbGUiOiJ1c2VyIiwiYWNjZXNzX3BhdGgiOlsiL2Rhc2hib2FyZCJdLCJleHBpcnkiOjE3NzcxMTIyMjcsImNyZWF0ZWQiOjE3NzcwMjU4MjcsIjJvbzkiOiJNc0giLCJleHAiOjE3NzcxMTIyMjcsImlhdCI6MTc3NzAyNTgyNywic3ViIjoiTV9JNFZBN0ZFNlIifQ.U0a_fYHXwSDy3LlKKc9QPrYrZ-gyFobpal-aGZxS_jQ"
MNIT_COOKIE = "cf_clearance=.hi8mAX0mx3kwqp7HIjlGxIsdtXTvYtcOILvkJRjrH4-1777025822-1.2.1.1-PoM1woh2ALsl66iAo96cKKw5.7bMeeob4EoL7G7OSgKA7O.ErTnwJW1kMsC1P..bjxiWFHiiBN4ctveEqv8aXdsXQ.FjOiCS_1kCdBJ7gbcw3yapMVKIjlJGMlHsria2TKGxwZEX479I7dt3fbiWtf5i7vniph5Y7y69NdT7RN.prqogv_MmqJLBqR7LuJQaKbGkUF5CS6PVmcfchUDVhLU6727ZtmpKwRyCOIragIGYWyfb1TJwVmGJms72pusjgR71xh3LWRbow3Lqs.twsBbLW_a46yQvjDHw.tQjY3q7uvNUauII3.CGu2WL.pqlDynJBLuDUbkGyHFiIdbkVQ; mauthtoken=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1aWQiOiJNX0k0VkE3RkU2UiIsInJvbGUiOiJ1c2VyIiwiYWNjZXNzX3BhdGgiOlsiL2Rhc2hib2FyZCJdLCJleHBpcnkiOjE3NzcxMTIyMjcsImNyZWF0ZWQiOjE3NzcwMjU4MjcsIjJvbzkiOiJNc0giLCJleHAiOjE3NzcxMTIyMjcsImlhdCI6MTc3NzAyNTgyNywic3ViIjoiTV9JNFZBN0ZFNlIifQ.U0a_fYHXwSDy3LlKKc9QPrYrZ-gyFobpal-aGZxS_jQ; TawkConnectionTime=0; twk_uuid_681787a55d55ef191a9da720=%7B%22uuid%22%3A%221.Ws5fNn3B3jtPb5VwJIV72bULtbVrmIGVECkvIdlVtObmwTts0jfxpP7wOqftlRphv8hGSHEouYvyMG8KX6vsSezC5RRocZQO3z6AWCeEWJFEAETJ73gSnDcqX%22%2C%22version%22%3A3%2C%22domain%22%3A%22mnitnetwork.com%22%2C%22ts%22%3A1777038143512%7D"

# ======================== Data Fetching Logic ========================
async def fetch_nexa(client):
    headers = {"X-API-Key": NEXA_API_KEY, "Accept": "application/json"}
    try:
        response = await client.get(NEXA_API_URL, headers=headers, timeout=10.0)
        if response.status_code == 200:
            data = response.json()
            logs = data.get("data", []) if isinstance(data, dict) else data
            if logs:
                for l in logs: l['sys_node'] = "nexus"
                return logs[:50]
    except Exception:
        pass
    return []

async def fetch_mnit(client):
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "Mauthtoken": MNIT_MAUTH_TOKEN,
        "Cookie": MNIT_COOKIE,
        "Referer": "https://x.mnitnetwork.com/mdashboard/console"
    }
    try:
        response = await client.get(MNIT_API_URL, headers=headers, timeout=10.0)
        if response.status_code == 200:
            data = response.json()
            logs = data.get("data", {}).get("logs", [])
            if logs:
                for l in logs: l['sys_node'] = "alpha"
                return logs[:50]
    except Exception:
        pass
    return []

# ======================== API Endpoints ========================
@app.get("/api/logs")
async def get_logs():
    try:
        async with httpx.AsyncClient() as client:
            mnit_logs, nexa_logs = await asyncio.gather(
                fetch_mnit(client), 
                fetch_nexa(client),
                return_exceptions=True
            )
            
            # Error handling in case one fails
            if isinstance(mnit_logs, Exception): mnit_logs = []
            if isinstance(nexa_logs, Exception): nexa_logs = []
            
            return mnit_logs + nexa_logs
    except Exception:
        return []

@app.get("/")
def read_root():
    return HTMLResponse(content=INDEX_HTML)

# ======================== ULTIMATE PREMIUM UI ========================
INDEX_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SKY RANGE ⚡ - SUPREME DASHBOARD</title>
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&family=JetBrains+Mono:wght@700;800&display=swap" rel="stylesheet">
    <style>
        :root { 
            --bg-main: #030712; 
            --card-bg: rgba(17, 24, 39, 0.7); 
            --card-border: rgba(255, 255, 255, 0.1); 
            --text-main: #f8fafc; 
            --text-muted: #94a3b8; 
            --accent: #00f2fe; 
            --panel-a: #10b981; /* NEON GREEN */
            --panel-b: #8b5cf6; /* NEON PURPLE */
        }
        
        /* 🔴 সম্পূর্ণ বডি ক্যাপিটাল லெটার (ALL CAPS) 🔴 */
        body { 
            background-color: var(--bg-main); 
            color: var(--text-main); 
            font-family: 'Orbitron', sans-serif; /* Futuristic Font */
            text-transform: uppercase; /* ALL CAPS LOCK */
            margin: 0; 
            padding: 0; 
            background-image: 
                radial-gradient(circle at 50% 0%, rgba(0, 242, 254, 0.08) 0%, transparent 60%),
                linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px),
                linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px);
            background-size: 100% 100%, 30px 30px, 30px 30px;
            background-attachment: fixed; 
        }
        
        /* HEADER STYLES */
        .top-header { display: flex; justify-content: space-between; padding: 15px 25px; background: rgba(3, 7, 18, 0.9); backdrop-filter: blur(15px); position: sticky; top: 0; z-index: 50; border-bottom: 2px solid var(--accent); box-shadow: 0 5px 20px rgba(0, 242, 254, 0.15);}
        .brand-title { font-size: 1.4rem; font-weight: 900; color: white; letter-spacing: 2px; text-shadow: 0 0 10px var(--accent);}
        
        .logo-area { padding: 40px 20px 30px 20px; display: flex; flex-direction: column; align-items: center; gap: 15px; }
        .logo-text { font-size: 3.5rem; font-weight: 900; background: linear-gradient(to right, #4facfe, #00f2fe); -webkit-background-clip: text; -webkit-text-fill-color: transparent; letter-spacing: 4px; text-shadow: 0px 0px 20px rgba(0,242,254,0.4); text-align: center;}
        .logo-text span { background: linear-gradient(to right, #a18cd1, #fbc2eb); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .live-badge { background: rgba(0, 242, 254, 0.1); color: var(--accent); padding: 8px 25px; border-radius: 5px; font-weight: 900; letter-spacing: 2px; border: 1px solid var(--accent); box-shadow: 0 0 20px rgba(0, 242, 254, 0.4); animation: pulse 2s infinite;}
        
        @keyframes pulse { 0% { box-shadow: 0 0 10px rgba(0, 242, 254, 0.2); } 50% { box-shadow: 0 0 25px rgba(0, 242, 254, 0.6); } 100% { box-shadow: 0 0 10px rgba(0, 242, 254, 0.2); } }

        /* FILTER BUTTONS */
        .filters { display: flex; gap: 15px; padding: 0 20px; overflow-x: auto; margin-bottom: 40px; scrollbar-width: none; justify-content: center;}
        .filters::-webkit-scrollbar { display: none; }
        .filter-btn { background: var(--card-bg); border: 1px solid var(--card-border); color: var(--text-muted); padding: 12px 25px; border-radius: 4px; cursor: pointer; white-space: nowrap; font-weight: 700; font-family: 'Orbitron', sans-serif; text-transform: uppercase; letter-spacing: 1px; transition: all 0.3s; }
        .filter-btn.active { background: rgba(0, 242, 254, 0.15); color: var(--accent); border-color: var(--accent); box-shadow: 0 0 20px rgba(0, 242, 254, 0.3); }
        .btn-high-power { background: linear-gradient(135deg, #ff0844, #ffb199); color: white !important; border: none; font-weight: 900; box-shadow: 0 0 20px rgba(255, 8, 68, 0.5); }
        
        /* 🟢 🟣 SPLIT LAYOUT (PANEL A & PANEL B) */
        .split-container { display: grid; grid-template-columns: 1fr 1fr; gap: 30px; padding: 0 30px 60px 30px; max-width: 1600px; margin: 0 auto;}
        @media (max-width: 900px) { .split-container { grid-template-columns: 1fr; } } 
        
        /* PANEL HEADERS */
        .panel-box { background: rgba(0,0,0,0.4); border-radius: 12px; padding: 20px; border: 1px solid rgba(255,255,255,0.05); }
        
        .column-header { text-align: center; padding: 15px; margin-bottom: 25px; font-weight: 900; font-size: 1.4rem; letter-spacing: 3px; border-radius: 8px; backdrop-filter: blur(10px);}
        .header-alpha { background: rgba(16, 185, 129, 0.1); color: var(--panel-a); border: 2px solid var(--panel-a); box-shadow: 0 0 25px rgba(16, 185, 129, 0.2); text-shadow: 0 0 10px var(--panel-a);}
        .header-nexus { background: rgba(139, 92, 246, 0.1); color: var(--panel-b); border: 2px solid var(--panel-b); box-shadow: 0 0 25px rgba(139, 92, 246, 0.2); text-shadow: 0 0 10px var(--panel-b);}
        
        .column-content { display: flex; flex-direction: column; gap: 20px; }

        /* DATA CARDS */
        .range-card { background: var(--card-bg); border: 1px solid var(--card-border); border-radius: 8px; padding: 20px; transition: all 0.3s; position: relative; overflow: hidden; backdrop-filter: blur(10px); }
        .range-card:hover { transform: translateY(-5px) scale(1.02); z-index: 10; background: rgba(17, 24, 39, 0.9); }
        
        .card-alpha { border-left: 5px solid var(--panel-a); }
        .card-nexus { border-left: 5px solid var(--panel-b); }
        .card-alpha:hover { border-color: var(--panel-a); box-shadow: 0 10px 30px -5px rgba(16, 185, 129, 0.3); }
        .card-nexus:hover { border-color: var(--panel-b); box-shadow: 0 10px 30px -5px rgba(139, 92, 246, 0.3); }
        
        .high-power-card { background: linear-gradient(145deg, rgba(30, 10, 15, 0.9), rgba(67, 20, 30, 0.6)); border: 1px solid rgba(255, 8, 68, 0.4); border-left: 5px solid #ff0844;}
        
        .range-header { display: flex; justify-content: space-between; align-items: center; color: var(--text-muted); font-size: 0.9rem; margin-bottom: 15px; font-weight: 700; }
        .service-name { color: #fff; font-weight: 900; font-size: 1.2rem; letter-spacing: 1px; display: flex; align-items: center; gap: 10px;}
        
        /* 💬 GLOWING SMS BOX */
        .sms-box { background: rgba(0, 242, 254, 0.05); border: 1px dashed rgba(0, 242, 254, 0.4); border-radius: 4px; padding: 10px 15px; margin-bottom: 15px; font-size: 0.85rem; color: #e0f2fe; display: flex; align-items: center; gap: 10px; font-family: 'JetBrains Mono', monospace; font-weight: bold;}
        .high-power-card .sms-box { background: rgba(255, 8, 68, 0.05); border-color: rgba(255, 8, 68, 0.4); color: #ffe4e6;}
        .sms-icon { font-size: 1.2rem; }
        
        /* NUMBER COPY AREA */
        .copy-area { background: #000; border-radius: 6px; padding: 15px 20px; display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; border: 1px solid rgba(255,255,255,0.1); }
        .range-number { font-size: 1.6rem; font-family: 'JetBrains Mono', monospace; color: var(--accent); font-weight: 800; letter-spacing: 3px; text-shadow: 0 0 10px rgba(0,242,254,0.3);}
        .high-power-card .range-number { color: #ffb199; text-shadow: 0 0 10px rgba(255,177,153,0.3); }
        
        .copy-btn { background: var(--accent); color: #000; border: none; padding: 8px 18px; border-radius: 4px; cursor: pointer; font-weight: 900; font-size: 0.9rem; transition: all 0.2s; font-family: 'Orbitron', sans-serif; text-transform: uppercase;}
        .copy-btn:hover { background: #fff; box-shadow: 0 0 15px #fff; }
        .copy-btn:active { transform: scale(0.9); }
        
        .hit-badge { background: linear-gradient(45deg, #ff0844, #ffb199); color: white; padding: 5px 12px; border-radius: 4px; font-weight: 900; font-size: 0.8rem; letter-spacing: 1px; box-shadow: 0 0 15px rgba(255,8,68,0.4);}
        
        .footer-brand { text-align: center; color: rgba(255,255,255,0.3); font-size: 1rem; margin: 50px 0; font-weight: 700; letter-spacing: 2px;}
        .footer-brand span { color: var(--accent); font-weight: 900;}

        /* TOAST NOTIFICATION */
        #toast { visibility: hidden; min-width: 300px; background: rgba(0, 242, 254, 0.9); backdrop-filter: blur(10px); color: #000; text-align: center; border-radius: 8px; padding: 18px; position: fixed; z-index: 1000; bottom: 40px; left: 50%; transform: translateX(-50%); font-weight: 900; font-size: 1.1rem; letter-spacing: 1px; box-shadow: 0 0 30px rgba(0,242,254,0.6);}
        #toast.show { visibility: visible; animation: popUp 0.3s forwards, fadeOut 0.4s ease-in 2.5s forwards; }
        @keyframes popUp { 0% { bottom: 0; opacity: 0; transform: translateX(-50%) scale(0.8); } 100% { bottom: 40px; opacity: 1; transform: translateX(-50%) scale(1); } }
        @keyframes fadeOut { from { opacity: 1; } to { opacity: 0; visibility: hidden;} }
    </style>
</head>
<body>
    <div class="top-header"><div class="brand-title">☁️ SKY RANGE SYSTEM</div></div>
    
    <div class="logo-area">
        <div class="live-badge">⚡ SECURE CONNECTION</div>
        <div class="logo-text">SKY<span>·RANGE</span></div>
    </div>
    
    <div class="filters">
        <button class="filter-btn active" onclick="switchTab('all')">◉ ALL TRAFFIC</button>
        <button class="filter-btn" onclick="switchTab('facebook')">FACEBOOK</button>
        <button class="filter-btn" onclick="switchTab('whatsapp')">WHATSAPP</button>
        <button class="filter-btn btn-high-power" onclick="switchTab('high-power')">🔥 TOP HITS</button>
    </div>
    
    <div class="split-container">
        <div class="panel-box">
            <div class="column-header header-alpha">🟢 PANEL A [ MNIT ]</div>
            <div class="column-content" id="col-alpha">
                <p style="text-align:center; color: #10b981; font-weight:bold; letter-spacing:2px;">SCANNING DATA...</p>
            </div>
        </div>
        
        <div class="panel-box">
            <div class="column-header header-nexus">🟣 PANEL B [ NEXA ]</div>
            <div class="column-content" id="col-nexus">
                <p style="text-align:center; color: #8b5cf6; font-weight:bold; letter-spacing:2px;">SCANNING DATA...</p>
            </div>
        </div>
    </div>
    
    <div class="footer-brand">SYS DEPLOYED BY <span>SKY NETWORKS</span></div>
    <div id="toast">✅ NUMBER COPIED!</div>

    <script>
        let currentTab = 'all';

        function switchTab(tab) {
            currentTab = tab;
            document.querySelectorAll('.filter-btn').forEach(btn => btn.classList.remove('active'));
            event.target.classList.add('active');
            fetchData();
        }

        function copyText(text) {
            navigator.clipboard.writeText(text).then(() => {
                var toast = document.getElementById("toast");
                toast.innerText = "📋 " + text + " COPIED!";
                toast.classList.remove("show");
                void toast.offsetWidth; toast.classList.add("show");
            });
        }

        async function fetchData() {
            try {
                const response = await fetch('/api/logs');
                const logs = await response.json();
                renderData(logs);
            } catch (err) { console.error("API ERROR", err); }
        }

        function formatNumberToRange(val) {
            if (!val) return "";
            if (val.toUpperCase().includes('X')) return val.toUpperCase();
            return val + "XXX";
        }

        function buildCard(item, isHighPower) {
            const displayRange = formatNumberToRange(isHighPower ? (item.prefix + "XXXX") : (item.range || item.number || item.number_raw || ''));
            const srvName = isHighPower ? item.service : (item.app_name || item.service || 'SERVICE');
            const ctry = item.country || 'GLOBAL';
            const nodeClass = item.node === 'alpha' ? 'card-alpha' : 'card-nexus';
            const extraClass = isHighPower ? 'high-power-card' : nodeClass;
            
            const topRight = isHighPower ? `<span class="hit-badge">🔥 ${item.count} HITS</span>` : `<span>${item.time || item.delivered_at || ''}</span>`;
            const btmRight = isHighPower ? `<span style="color: #10b981; font-weight:bold;">HIGHLY ACTIVE</span>` : `<span>🏢 ${item.carrier || 'UNKNOWN'}</span>`;

            const rawSms = item.sms || item.message || "NO SMS CONTENT FOUND";
            const cleanSms = rawSms.length > 45 ? rawSms.substring(0, 42) + "..." : rawSms;
            
            const smsHtml = `
            <div class="sms-box" title="FULL MSG: ${rawSms}">
                <span class="sms-icon">💬</span>
                <span style="white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">${cleanSms}</span>
            </div>`;

            return `
            <div class="range-card ${extraClass}">
                <div class="range-header">
                    <span class="service-name">${srvName}</span>
                    ${topRight}
                </div>
                ${smsHtml} 
                <div class="copy-area">
                    <div class="range-number">${displayRange}</div>
                    <button class="copy-btn" onclick="copyText('${displayRange}')">COPY</button>
                </div>
                <div class="range-header" style="margin: 0; color: #fff;">
                    <span>🌐 ${ctry}</span>
                    ${btmRight}
                </div>
            </div>`;
        }

        function renderData(logs) {
            const colAlpha = document.getElementById('col-alpha');
            const colNexus = document.getElementById('col-nexus');
            let htmlAlpha = '';
            let htmlNexus = '';

            if(!logs || logs.length === 0) {
                colAlpha.innerHTML = '<p style="text-align:center; color:#94a3b8; font-weight:bold;">NO ACTIVE DATA</p>';
                colNexus.innerHTML = '<p style="text-align:center; color:#94a3b8; font-weight:bold;">NO ACTIVE DATA</p>';
                return;
            }

            if (currentTab === 'high-power') {
                let rangeCounts = {};
                logs.forEach(log => {
                    const srv = (log.app_name || log.service || 'UNKNOWN').toUpperCase();
                    const rawNum = log.range || log.number || log.number_raw || '';
                    const cleanNum = rawNum.replace(/[^0-9]/g, '');
                    if(cleanNum.length >= 7) {
                        const prefix = cleanNum.substring(0, 7);
                        const key = srv + "|" + prefix + "|" + log.sys_node;
                        if(!rangeCounts[key]) {
                            rangeCounts[key] = { 
                                prefix: prefix, service: srv, count: 0, 
                                country: log.country, node: log.sys_node,
                                sms: log.sms || log.message || "NO SMS CONTENT"
                            };
                        }
                        rangeCounts[key].count++;
                    }
                });

                const sortedRanges = Object.values(rangeCounts).sort((a, b) => b.count - a.count);
                sortedRanges.forEach(r => {
                    if (r.node === 'alpha') htmlAlpha += buildCard(r, true);
                    else htmlNexus += buildCard(r, true);
                });
            } else {
                logs.forEach(log => {
                    const srv = (log.app_name || log.service || 'UNKNOWN').toLowerCase();
                    let matchSrv = currentTab === 'whatsapp' ? 'whatsapp|twilio' : currentTab;
                    if (currentTab !== 'all' && !matchSrv.includes(srv) && !srv.includes(currentTab)) return;

                    log.node = log.sys_node;
                    if (log.sys_node === 'alpha') htmlAlpha += buildCard(log, false);
                    else htmlNexus += buildCard(log, false);
                });
            }

            colAlpha.innerHTML = htmlAlpha || '<p style="text-align:center; color:#94a3b8; font-weight:bold;">NO DATA IN PANEL A</p>';
            colNexus.innerHTML = htmlNexus || '<p style="text-align:center; color:#94a3b8; font-weight:bold;">NO DATA IN PANEL B</p>';
        }
        
        setInterval(fetchData, 5000); 
        fetchData();
    </script>
</body>
</html>
