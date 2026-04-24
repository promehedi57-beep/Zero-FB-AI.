from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import httpx
import asyncio

app = FastAPI()

# ======================== API কনফিগারেশন ========================
# 🔴 Gateway Nexus (NEXAOTP - ডান কলাম)
NEXA_API_URL = "http://2.58.82.137:5000/api/v1/console/logs?limit=100"
NEXA_API_KEY = "nxa_b2101087b38e27f8f19f4cdd5963bc695808fbb8"

# 🔴 Gateway Alpha (MNIT - বাম কলাম) - আপনার দেওয়া একদম নতুন কুকি আপডেট করা হলো ✅
MNIT_API_URL = "https://x.mnitnetwork.com/mapi/v1/mdashboard/console/info"
MNIT_MAUTH_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1aWQiOiJNX0k0VkE3RkU2UiIsInJvbGUiOiJ1c2VyIiwiYWNjZXNzX3BhdGgiOlsiL2Rhc2hib2FyZCJdLCJleHBpcnkiOjE3NzcwMjUzODEsImNyZWF0ZWQiOjE3NzY5Mzg5ODEsIjJvbzkiOiJNc0giLCJleHAiOjE3NzcwMjUzODEsImlhdCI6MTc3NjkzODk4MSwic3ViIjoiTV9JNFZBN0ZFNlIifQ.cQmKvwAQAVQrL4mn5ac2aZIf4-q-POoeh-leIuf3RRM"
MNIT_COOKIE = "mauthtoken=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1aWQiOiJNX0k0VkE3RkU2UiIsInJvbGUiOiJ1c2VyIiwiYWNjZXNzX3BhdGgiOlsiL2Rhc2hib2FyZCJdLCJleHBpcnkiOjE3NzcwMjUzODEsImNyZWF0ZWQiOjE3NzY5Mzg5ODEsIjJvbzkiOiJNc0giLCJleHAiOjE3NzcwMjUzODEsImlhdCI6MTc3NjkzODk4MSwic3ViIjoiTV9JNFZBN0ZFNlIifQ.cQmKvwAQAVQrL4mn5ac2aZIf4-q-POoeh-leIuf3RRM; cf_clearance=tmACujVZup.lCMXsXSLT079ahscqkvl8S.g21p4jnIY-1776996209-1.2.1.1-xaVNTryUTWclSn50egbzlchSwW1Uv4TPrhkX1PSn4yG387.05EimOB7qzMfgboQ2WaMOQ41tsfY4fCEOmU5JNTW0Pl2Aya0lXH16Hcr_eCqsjKEvixZ3Qyg1AtyOfQfoigDgjM3W4uB5CFsHspbQrmPlbnIe0DRnp_V98AJ44Urt8xR5Q484WSVuVAWGl2lkhMUDEW5hXSmL.fPYm6eKMDqxHIsr2haVdBRwh1X.mH2tSX6wdts4XKdZfn1JC6du.8NAoWQvjslRENZMq.UzQf5TYTayRQ10ijSp2aUGjlakpPLm7PJSjFSGU1LvIvcHs5wthmNbiWKm2kiMoy3RPQ; TawkConnectionTime=0; twk_uuid_681787a55d55ef191a9da720=%7B%22uuid%22%3A%221.Ws5fNn3B3jtPb5VwJIV72bULtbVrmIGVECkvIdlVtObmwTts0jfxpP7wOqftlRphv8hGSHEouYvyMG8KX6vsSezC5RRocZQO3z6AWCeEWJFEAETJ73gSnDcqX%22%2C%22version%22%3A3%2C%22domain%22%3A%22mnitnetwork.com%22%2C%22ts%22%3A1776996212153%7D"

# ======================== Data Fetching Logic ========================
async def fetch_nexa(client):
    headers = {"X-API-Key": NEXA_API_KEY, "Accept": "application/json"}
    try:
        response = await client.get(NEXA_API_URL, headers=headers, timeout=8.0)
        if response.status_code == 200:
            data = response.json()
            logs = data.get("data", []) if isinstance(data, dict) else data
            if logs:
                for l in logs: l['sys_node'] = "nexus"
                return logs[:50]
    except Exception as e:
        print(f"NEXA Error: {e}")
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
        response = await client.get(MNIT_API_URL, headers=headers, timeout=8.0)
        if response.status_code == 200:
            data = response.json()
            logs = data.get("data", {}).get("logs", [])
            if logs:
                for l in logs: l['sys_node'] = "alpha"
                return logs[:50]
    except Exception as e:
        print(f"MNIT Error: {e}")
    return []

# ======================== API Endpoints ========================
@app.get("/api/logs")
async def get_logs():
    # Vercel Serverless এ একসাথেই দুই প্যানেলের ডেটা আনবে
    async with httpx.AsyncClient() as client:
        mnit_task = fetch_mnit(client)
        nexa_task = fetch_nexa(client)
        # দুটো থেকে প্যারালালি ডেটা আনা হচ্ছে (সুপারফাস্ট)
        mnit_logs, nexa_logs = await asyncio.gather(mnit_task, nexa_task)
        
        combined_logs = mnit_logs + nexa_logs
        return combined_logs

@app.get("/")
def read_root():
    return HTMLResponse(content=INDEX_HTML)

# ======================== PREMIUM UI ========================
INDEX_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SKY RANGE ⚡ - Split Dashboard</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&family=JetBrains+Mono:wght@700&display=swap" rel="stylesheet">
    <style>
        :root { 
            --bg-main: #060913; --card-bg: rgba(17, 24, 39, 0.6); --card-border: rgba(255, 255, 255, 0.08); 
            --card-hover: #38bdf8; --text-main: #f8fafc; --text-muted: #94a3b8; --accent: #00f2fe; 
            --node-alpha: #10b981; /* Green */
            --node-nexus: #8b5cf6; /* Purple */
        }
        
        body { background-color: var(--bg-main); color: var(--text-main); font-family: 'Inter', sans-serif; margin: 0; padding: 0; background-image: radial-gradient(circle at 50% 0%, rgba(6, 182, 212, 0.05) 0%, transparent 50%); background-attachment: fixed; }
        
        .top-header { display: flex; justify-content: space-between; padding: 15px 20px; background: rgba(6, 9, 19, 0.85); backdrop-filter: blur(12px); position: sticky; top: 0; z-index: 50; border-bottom: 1px solid var(--card-border); }
        .brand-title { font-size: 1.2rem; font-weight: 800; color: white; letter-spacing: 0.5px;}
        
        .logo-area { padding: 30px 20px 20px 20px; display: flex; justify-content: space-between; align-items: center; }
        .logo-text { font-size: 2.2rem; font-weight: 900; background: linear-gradient(to right, #4facfe 0%, #00f2fe 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; letter-spacing: 1px;}
        .logo-text span { background: linear-gradient(to right, #a18cd1 0%, #fbc2eb 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .live-badge { background: rgba(0, 242, 254, 0.1); color: var(--accent); padding: 6px 16px; border-radius: 30px; font-weight: 800; box-shadow: 0 0 15px rgba(0, 242, 254, 0.2); border: 1px solid rgba(0, 242, 254, 0.3);}
        
        .filters { display: flex; gap: 12px; padding: 0 20px; overflow-x: auto; margin-bottom: 25px; scrollbar-width: none; justify-content: center;}
        .filters::-webkit-scrollbar { display: none; }
        .filter-btn { background: var(--card-bg); border: 1px solid var(--card-border); color: var(--text-muted); padding: 10px 20px; border-radius: 30px; cursor: pointer; white-space: nowrap; font-weight: 600; transition: all 0.3s; backdrop-filter: blur(5px); }
        .filter-btn.active { background: rgba(0, 242, 254, 0.15); color: var(--accent); border-color: var(--accent); box-shadow: 0 0 20px rgba(0, 242, 254, 0.15); }
        .btn-high-power { background: linear-gradient(135deg, #ff0844 0%, #ffb199 100%); color: white !important; border: none; font-weight: 800; box-shadow: 0 4px 15px rgba(255, 8, 68, 0.4); }
        
        /* SPLIT LAYOUT CSS */
        .split-container { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; padding: 0 20px 50px 20px; max-width: 1400px; margin: 0 auto;}
        @media (max-width: 768px) { .split-container { grid-template-columns: 1fr; } } 
        
        .column-header { text-align: center; padding: 12px; margin-bottom: 15px; font-weight: 800; border-radius: 12px; text-transform: uppercase; letter-spacing: 1.5px; font-size: 1.1rem; backdrop-filter: blur(10px);}
        .header-alpha { background: rgba(16, 185, 129, 0.1); color: var(--node-alpha); border: 1px solid rgba(16, 185, 129, 0.3); box-shadow: 0 0 20px rgba(16, 185, 129, 0.1);}
        .header-nexus { background: rgba(139, 92, 246, 0.1); color: var(--node-nexus); border: 1px solid rgba(139, 92, 246, 0.3); box-shadow: 0 0 20px rgba(139, 92, 246, 0.1);}
        
        .column-content { display: flex; flex-direction: column; gap: 15px; }

        .range-card { background: var(--card-bg); border: 1px solid var(--card-border); border-radius: 16px; padding: 18px; transition: all 0.3s; position: relative; overflow: hidden; backdrop-filter: blur(10px); }
        .range-card:hover { transform: translateY(-4px) scale(1.01); z-index: 10; box-shadow: 0 10px 20px rgba(0,0,0,0.4);}
        
        .card-alpha { border-left: 4px solid var(--node-alpha); }
        .card-nexus { border-left: 4px solid var(--node-nexus); }
        .card-alpha:hover { border-color: var(--node-alpha); box-shadow: 0 10px 25px -5px rgba(16, 185, 129, 0.2); }
        .card-nexus:hover { border-color: var(--node-nexus); box-shadow: 0 10px 25px -5px rgba(139, 92, 246, 0.2); }
        
        .high-power-card { background: linear-gradient(145deg, rgba(17, 24, 39, 0.9), rgba(67, 20, 30, 0.4)); border: 1px solid rgba(255, 8, 68, 0.3); border-left: 4px solid #ff0844;}
        
        .range-header { display: flex; justify-content: space-between; align-items: center; color: var(--text-muted); font-size: 0.85rem; margin-bottom: 12px; }
        .service-name { color: #f8fafc; font-weight: 800; font-size: 1.05rem; display: flex; align-items: center; gap: 8px;}
        
        .copy-area { background: rgba(0, 0, 0, 0.3); border-radius: 12px; padding: 12px 15px; display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; border: 1px solid rgba(255,255,255,0.05); }
        .range-number { font-size: 1.3rem; font-family: 'JetBrains Mono', monospace; color: #fff; font-weight: 700; letter-spacing: 1px; }
        .high-power-card .range-number { color: #ffb199; }
        
        .copy-btn { background: rgba(255, 255, 255, 0.05); color: #fff; border: 1px solid rgba(255, 255, 255, 0.1); padding: 6px 14px; border-radius: 8px; cursor: pointer; font-weight: 600; font-size: 0.85rem; transition: all 0.2s;}
        .copy-btn:hover { background: #fff; color: #000; }
        .copy-btn:active { transform: scale(0.92); }
        
        .hit-badge { background: linear-gradient(45deg, #ff0844, #ffb199); color: white; padding: 4px 10px; border-radius: 20px; font-weight: 800; font-size: 0.75rem;}
        
        .footer-brand { text-align: center; color: rgba(255,255,255,0.3); font-size: 0.85rem; margin: 40px 0; padding-bottom: 20px;}
        .footer-brand span { color: rgba(255,255,255,0.6); font-weight: bold;}

        #toast { visibility: hidden; min-width: 260px; background: rgba(16, 185, 129, 0.9); backdrop-filter: blur(10px); color: #fff; text-align: center; border-radius: 12px; padding: 16px; position: fixed; z-index: 1000; bottom: 40px; left: 50%; transform: translateX(-50%); font-weight: 800; font-size: 0.95rem;}
        #toast.show { visibility: visible; animation: popUp 0.4s forwards, fadeOut 0.4s ease-in 2.5s forwards; }
        @keyframes popUp { 0% { bottom: 0; opacity: 0; transform: translateX(-50%) scale(0.8); } 100% { bottom: 40px; opacity: 1; transform: translateX(-50%) scale(1); } }
        @keyframes fadeOut { from { opacity: 1; } to { opacity: 0; visibility: hidden;} }
    </style>
</head>
<body>
    <div class="top-header"><div class="brand-title">☁️ SKY RANGE ⚡</div></div>
    <div class="logo-area">
        <div class="logo-text">SKY<span>·RANGE</span></div>
        <div class="live-badge">⚡ SERVERLESS</div>
    </div>
    <div class="filters">
        <button class="filter-btn active" onclick="switchTab('all')">◉ Live Data</button>
        <button class="filter-btn" onclick="switchTab('facebook')">Facebook</button>
        <button class="filter-btn" onclick="switchTab('whatsapp')">WhatsApp</button>
        <button class="filter-btn btn-high-power" onclick="switchTab('high-power')">🔥 TOP RANGES</button>
    </div>
    
    <div class="split-container">
        <div>
            <div class="column-header header-alpha">🟢 Gateway 01 (A)</div>
            <div class="column-content" id="col-alpha">
                <p style="text-align:center; color: #94a3b8;">Loading...</p>
            </div>
        </div>
        <div>
            <div class="column-header header-nexus">🟣 Gateway 02 (B)</div>
            <div class="column-content" id="col-nexus">
                <p style="text-align:center; color: #94a3b8;">Loading...</p>
            </div>
        </div>
    </div>
    
    <div class="footer-brand">⚡ VERCEL SYSTEM DEPLOYED BY <span>SKY NETWORKS</span></div>
    <div id="toast">✅ Copied to clipboard!</div>

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
                toast.innerText = "📋 " + text + " Copied!";
                toast.classList.remove("show");
                void toast.offsetWidth; toast.classList.add("show");
            });
        }

        async function fetchData() {
            try {
                const response = await fetch('/api/logs');
                const logs = await response.json();
                renderData(logs);
            } catch (err) { console.error("Error", err); }
        }

        function formatNumberToRange(val) {
            if (!val) return "";
            if (val.toUpperCase().includes('X')) return val.toUpperCase();
            return val + "XXX";
        }

        function buildCard(item, isHighPower) {
            const displayRange = formatNumberToRange(isHighPower ? (item.prefix + "XXXX") : (item.range || item.number || item.number_raw || ''));
            const srvName = isHighPower ? item.service : (item.app_name || item.service || 'Service');
            const ctry = item.country || 'Global';
            const nodeClass = item.node === 'alpha' ? 'card-alpha' : 'card-nexus';
            const extraClass = isHighPower ? 'high-power-card' : nodeClass;
            
            const topRight = isHighPower ? `<span class="hit-badge">🔥 ${item.count} HITS</span>` : `<span style="font-size:0.8rem; opacity:0.8;">${item.time || item.delivered_at || ''}</span>`;
            const btmRight = isHighPower ? `<span style="color: #10b981; font-weight:bold;">Highly Active</span>` : `<span>🏢 ${item.carrier || 'Unknown'}</span>`;

            return `
            <div class="range-card ${extraClass}">
                <div class="range-header">
                    <span class="service-name">${srvName}</span>
                    ${topRight}
                </div>
                <div class="copy-area">
                    <div class="range-number">${displayRange}</div>
                    <button class="copy-btn" onclick="copyText('${displayRange}')">Copy</button>
                </div>
                <div class="range-header" style="margin: 0;">
                    <span style="font-weight:600;">🌐 ${ctry}</span>
                    ${btmRight}
                </div>
            </div>`;
        }

        function renderData(logs) {
            const colAlpha = document.getElementById('col-alpha');
            const colNexus = document.getElementById('col-nexus');
            let htmlAlpha = '';
            let htmlNexus = '';

            if(logs.length === 0) {
                colAlpha.innerHTML = '<p style="text-align:center; color:#94a3b8;">No data found</p>';
                colNexus.innerHTML = '<p style="text-align:center; color:#94a3b8;">No data found</p>';
                return;
            }

            if (currentTab === 'high-power') {
                let rangeCounts = {};
                logs.forEach(log => {
                    const srv = log.app_name || log.service || 'Unknown';
                    const rawNum = log.range || log.number || log.number_raw || '';
                    const cleanNum = rawNum.replace(/[^0-9]/g, '');
                    if(cleanNum.length >= 7) {
                        const prefix = cleanNum.substring(0, 7);
                        const key = srv + "|" + prefix + "|" + log.sys_node;
                        if(!rangeCounts[key]) rangeCounts[key] = { prefix: prefix, service: srv, count: 0, country: log.country, node: log.sys_node };
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
                    const srv = (log.app_name || log.service || 'Unknown').toLowerCase();
                    let matchSrv = currentTab === 'whatsapp' ? 'whatsapp|twilio' : currentTab;
                    if (currentTab !== 'all' && !matchSrv.includes(srv) && !srv.includes(currentTab)) return;

                    log.node = log.sys_node;
                    if (log.sys_node === 'alpha') htmlAlpha += buildCard(log, false);
                    else htmlNexus += buildCard(log, false);
                });
            }

            colAlpha.innerHTML = htmlAlpha || '<p style="text-align:center; color:#94a3b8;">No live ranges</p>';
            colNexus.innerHTML = htmlNexus || '<p style="text-align:center; color:#94a3b8;">No live ranges</p>';
        }
        
        setInterval(fetchData, 5000); 
        fetchData();
    </script>
</body>
</html>
"""
