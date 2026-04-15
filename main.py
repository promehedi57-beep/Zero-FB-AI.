// bot.js - Telegram OTP Bot in JavaScript (Telegraf.js)
const { Telegraf, Markup, Scenes, session } = require('telegraf');
const Database = require('better-sqlite3');
const axios = require('axios');
const { DateTime } = require('luxon'); // npm install luxon

// ================= CONFIGURATION =================
const TOKEN = "8647348457:AAEi5Kre2Df4Xeig80aZzsd_7zR9MFO739Y";
const API_BASE_URL = "http://2.58.82.137:5000";
const API_KEY = "nxa_99f2f67b13e0e02bca175b1cbc40d57128958702";
const OTP_GROUP_LINK = "https://t.me/+4nMAFt2hYk04YTRl";
const OTP_GROUP_ID = "-1001234567890"; // ⚠️ আপনার OTP গ্রুপের ID এখানে দিবেন (শুরুতে - থাকবে)

const bot = new Telegraf(TOKEN);

// সেশন (Session) চালু করা হলো
bot.use(session());

const db = new Database('otp_pro_panel.db');

// ================= ANTI-CRASH SHIELD =================
process.on('unhandledRejection', (reason, promise) => {
    console.error('Unhandled Rejection at:', promise, 'reason:', reason);
});
process.on('uncaughtException', (error) => {
    console.error('Uncaught Exception:', error.message);
});
bot.catch((err, ctx) => {
    console.error(`Telegram Error for ${ctx.updateType}:`, err.message);
});

// ================= DATABASE SETUP =================
db.exec(`
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY, 
        balance REAL DEFAULT 0.0, 
        username TEXT, 
        fullname TEXT
    );
    CREATE TABLE IF NOT EXISTS services (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        name TEXT, 
        range_val TEXT, 
        country_code TEXT, 
        flag TEXT
    );
    CREATE TABLE IF NOT EXISTS config (
        key TEXT PRIMARY KEY, 
        value TEXT
    );
    CREATE TABLE IF NOT EXISTS withdraw_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        amount REAL,
        bkash_number TEXT,
        status TEXT DEFAULT 'pending',
        requested_at TEXT
    );
    CREATE TABLE IF NOT EXISTS used_numbers (
        user_id INTEGER,
        number_id TEXT,
        phone_number TEXT,
        service_id INTEGER,
        used_at TEXT,
        PRIMARY KEY (user_id, number_id)
    );
    CREATE TABLE IF NOT EXISTS active_numbers (
        user_id INTEGER,
        number_id TEXT,
        phone_number TEXT,
        service_id INTEGER,
        message_id INTEGER,
        requested_at TEXT,
        PRIMARY KEY (user_id, number_id)
    );
    CREATE TABLE IF NOT EXISTS admins (user_id TEXT PRIMARY KEY);
`);

const configDefaults = [
    ['min_withdraw', '100'],
    ['earning_per_otp', '10'],
    ['maintenance_mode', 'off'],
    ['withdraw_enabled', 'on']
];
configDefaults.forEach(([key, value]) => {
    db.prepare("INSERT OR IGNORE INTO config VALUES (?, ?)").run(key, value);
});

db.prepare("INSERT OR IGNORE INTO admins VALUES (?)").run('6820798198');
db.prepare("INSERT OR IGNORE INTO admins VALUES (?)").run('7689218221');

// ================= HELPERS =================
const COUNTRY_PREFIXES = {
    "1": ["US", "🇺🇸"], "7": ["RU", "🇷🇺"], "20": ["EG", "🇪🇬"], "27": ["ZA", "🇿🇦"],
    "30": ["GR", "🇬🇷"], "31": ["NL", "🇳🇱"], "32": ["BE", "🇧🇪"], "33": ["FR", "🇫🇷"],
    "34": ["ES", "🇪🇸"], "36": ["HU", "🇭🇺"], "39": ["IT", "🇮🇹"], "40": ["RO", "🇷🇴"],
    "41": ["CH", "🇨🇭"], "43": ["AT", "🇦🇹"], "44": ["GB", "🇬🇧"], "45": ["DK", "🇩🇰"],
    "46": ["SE", "🇸🇪"], "47": ["NO", "🇳🇴"], "48": ["PL", "🇵🇱"], "49": ["DE", "🇩🇪"],
    "51": ["PE", "🇵🇪"], "52": ["MX", "🇲🇽"], "53": ["CU", "🇨🇺"], "54": ["AR", "🇦🇷"],
    "55": ["BR", "🇧🇷"], "56": ["CL", "🇨🇱"], "57": ["CO", "🇨🇴"], "58": ["VE", "🇻🇪"],
    "60": ["MY", "🇲🇾"], "61": ["AU", "🇦🇺"], "62": ["ID", "🇮🇩"], "63": ["PH", "🇵🇭"],
    "64": ["NZ", "🇳🇿"], "65": ["SG", "🇸🇬"], "66": ["TH", "🇹🇭"], "81": ["JP", "🇯🇵"],
    "82": ["KR", "🇰🇷"], "84": ["VN", "🇻🇳"], "86": ["CN", "🇨🇳"], "90": ["TR", "🇹🇷"],
    "91": ["IN", "🇮🇳"], "92": ["PK", "🇵🇰"], "93": ["AF", "🇦🇫"], "94": ["LK", "🇱🇰"],
    "95": ["MM", "🇲🇲"], "98": ["IR", "🇮🇷"], "211": ["SS", "🇸🇸"], "212": ["MA", "🇲🇦"],
    "213": ["DZ", "🇩🇿"], "216": ["TN", "🇹🇳"], "218": ["LY", "🇱🇾"], "220": ["GM", "🇬🇲"],
    "221": ["SN", "🇸🇳"], "222": ["MR", "🇲🇷"], "223": ["ML", "🇲🇱"], "224": ["GN", "🇬🇳"],
    "225": ["CI", "🇨🇮"], "226": ["BF", "🇧🇫"], "227": ["NE", "🇳🇪"], "228": ["TG", "🇹🇬"],
    "229": ["BJ", "🇧🇯"], "230": ["MU", "🇲🇺"], "231": ["LR", "🇱🇷"], "232": ["SL", "🇸🇱"],
    "233": ["GH", "🇬🇭"], "234": ["NG", "🇳🇬"], "235": ["TD", "🇹🇩"], "236": ["CF", "🇨🇫"],
    "237": ["CM", "🇨🇲"], "238": ["CV", "🇨🇻"], "239": ["ST", "🇸🇹"], "240": ["GQ", "🇬🇶"],
    "241": ["GA", "🇬🇦"], "242": ["CG", "🇨🇬"], "243": ["CD", "🇨🇩"], "244": ["AO", "🇦🇴"],
    "245": ["GW", "🇬🇼"], "246": ["IO", "🇮🇴"], "247": ["AC", "🇦🇨"], "248": ["SC", "🇸🇨"],
    "249": ["SD", "🇸🇩"], "250": ["RW", "🇷🇼"], "251": ["ET", "🇪🇹"], "252": ["SO", "🇸🇴"],
    "253": ["DJ", "🇩🇯"], "254": ["KE", "🇰🇪"], "255": ["TZ", "🇹🇿"], "256": ["UG", "🇺🇬"],
    "257": ["BI", "🇧🇮"], "258": ["MZ", "🇲🇿"], "260": ["ZM", "🇿🇲"], "261": ["MG", "🇲🇬"],
    "262": ["RE", "🇷🇪"], "263": ["ZW", "🇿🇼"], "264": ["NA", "🇳🇦"], "265": ["MW", "🇲🇼"],
    "266": ["LS", "🇱🇸"], "267": ["BW", "🇧🇼"], "268": ["SZ", "🇸🇿"], "269": ["KM", "🇰🇲"],
    "290": ["SH", "🇸🇭"], "291": ["ER", "🇪🇷"], "297": ["AW", "🇦🇼"], "298": ["FO", "🇫🇴"],
    "299": ["GL", "🇬🇱"], "350": ["GI", "🇬🇮"], "351": ["PT", "🇵🇹"], "352": ["LU", "🇱🇺"],
    "353": ["IE", "🇮🇪"], "354": ["IS", "🇮🇸"], "355": ["AL", "🇦🇱"], "356": ["MT", "🇲🇹"],
    "357": ["CY", "🇨🇾"], "358": ["FI", "🇫🇮"], "359": ["BG", "🇧🇬"], "370": ["LT", "🇱🇹"],
    "371": ["LV", "🇱🇻"], "372": ["EE", "🇪🇪"], "373": ["MD", "🇲🇩"], "374": ["AM", "🇦🇲"],
    "375": ["BY", "🇧🇾"], "376": ["AD", "🇦🇩"], "377": ["MC", "🇲🇨"], "378": ["SM", "🇸🇲"],
    "379": ["VA", "🇻🇦"], "380": ["UA", "🇺🇦"], "381": ["RS", "🇷🇸"], "382": ["ME", "🇲🇪"],
    "385": ["HR", "🇭🇷"], "386": ["SI", "🇸🇮"], "387": ["BA", "🇧🇦"], "389": ["MK", "🇲🇰"],
    "420": ["CZ", "🇨🇿"], "421": ["SK", "🇸🇰"], "423": ["LI", "🇱🇮"], "500": ["FK", "🇫🇰"],
    "501": ["BZ", "🇧🇿"], "502": ["GT", "🇬🇹"], "503": ["SV", "🇸🇻"], "504": ["HN", "🇭🇳"],
    "505": ["NI", "🇳🇮"], "506": ["CR", "🇨🇷"], "507": ["PA", "🇵🇦"], "508": ["PM", "🇵🇲"],
    "509": ["HT", "🇭🇹"], "590": ["GP", "🇬🇵"], "591": ["BO", "🇧🇴"], "592": ["GY", "🇬🇾"],
    "593": ["EC", "🇪🇨"], "594": ["GF", "🇬🇫"], "595": ["PY", "🇵🇾"], "596": ["MQ", "🇲🇶"],
    "597": ["SR", "🇸🇷"], "598": ["UY", "🇺🇾"], "599": ["CW", "🇨🇼"], "670": ["TL", "🇹🇱"],
    "672": ["NF", "🇳🇫"], "673": ["BN", "🇧🇳"], "674": ["NR", "🇳🇷"], "675": ["PG", "🇵🇬"],
    "676": ["TO", "🇹🇴"], "677": ["SB", "🇸🇧"], "678": ["VU", "🇻🇺"], "679": ["FJ", "🇫🇯"],
    "680": ["PW", "🇵🇼"], "681": ["WF", "🇼🇫"], "682": ["CK", "🇨🇰"], "683": ["NU", "🇳🇺"],
    "685": ["WS", "🇼🇸"], "686": ["KI", "🇰🇮"], "687": ["NC", "🇳🇨"], "688": ["TV", "🇹🇻"],
    "689": ["PF", "🇵🇫"], "690": ["TK", "🇹🇰"], "691": ["FM", "🇫🇲"], "692": ["MH", "🇲🇭"],
    "850": ["KP", "🇰🇵"], "852": ["HK", "🇭🇰"], "853": ["MO", "🇲🇴"], "855": ["KH", "🇰🇭"],
    "856": ["LA", "🇱🇦"], "880": ["BD", "🇧🇩"], "886": ["TW", "🇹🇼"], "960": ["MV", "🇲🇻"],
    "961": ["LB", "🇱🇧"], "962": ["JO", "🇯🇴"], "963": ["SY", "🇸🇾"], "964": ["IQ", "🇮🇶"],
    "965": ["KW", "🇰🇼"], "966": ["SA", "🇸🇦"], "967": ["YE", "🇾🇪"], "968": ["OM", "🇴🇲"],
    "970": ["PS", "🇵🇸"], "971": ["AE", "🇦🇪"], "972": ["IL", "🇮🇱"], "973": ["BH", "🇧🇭"],
    "974": ["QA", "🇶🇦"], "975": ["BT", "🇧🇹"], "976": ["MN", "🇲🇳"], "977": ["NP", "🇳🇵"],
    "992": ["TJ", "🇹🇯"], "993": ["TM", "🇹🇲"], "994": ["AZ", "🇦🇿"], "995": ["GE", "🇬🇪"],
    "996": ["KG", "🇰🇬"], "998": ["UZ", "🇺🇿"],
};

function getCountryFromPhone(phone) {
    const digits = phone.replace(/\D/g, '');
    if (!digits) return ["BD", "🇧🇩"];
    
    for (let length = 5; length >= 1; length--) {
        const prefix = digits.slice(0, length);
        if (COUNTRY_PREFIXES[prefix]) return COUNTRY_PREFIXES[prefix];
    }
    for (let length = 3; length >= 1; length--) {
        const prefix = digits.slice(0, length);
        if (COUNTRY_PREFIXES[prefix]) return COUNTRY_PREFIXES[prefix];
    }
    return ["BD", "🇧🇩"];
}

function formatNumberWithFlag(phone) {
    const [, flag] = getCountryFromPhone(phone);
    return `${flag} ${phone}`;
}

function isAdmin(userId) {
    const row = db.prepare("SELECT 1 FROM admins WHERE user_id=?").get(String(userId));
    return !!row;
}

function getFlagEmoji(countryCode) {
    if (!countryCode || countryCode.length !== 2) return "🌍";
    const code = countryCode.toUpperCase();
    return String.fromCodePoint(
        0x1F1E6 + code.charCodeAt(0) - 65,
        0x1F1E6 + code.charCodeAt(1) - 65
    );
}

function isMaintenanceMode() {
    const row = db.prepare("SELECT value FROM config WHERE key='maintenance_mode'").get();
    return row && row.value === 'on';
}

function isWithdrawEnabled() {
    const row = db.prepare("SELECT value FROM config WHERE key='withdraw_enabled'").get();
    return row && row.value === 'on';
}

async function checkMaintenance(userId, ctx, isCallback = false) {
    if (isMaintenanceMode() && !isAdmin(userId)) {
        const text = "🔧 *Bot is under maintenance.* Please try again later.";
        if (isCallback) {
            await ctx.answerCbQuery("Maintenance mode is ON", { show_alert: true }).catch(() => {});
            await ctx.editMessageText(text, { parse_mode: "Markdown" }).catch(() => {});
        } else {
            await ctx.reply(text, { parse_mode: "Markdown" }).catch(() => {});
        }
        return true;
    }
    return false;
}

// ================= API FUNCTIONS =================
async function syncServicesFromAPI() {
    const url = `${API_BASE_URL}/app/console`;
    const headers = { "X-API-Key": API_KEY, "Content-Type": "application/json" };
    
    try {
        const resp = await axios.get(url, { headers, timeout: 10000 });
        if (resp.status === 200) {
            let data = resp.data;
            let apiServices = [];
            
            if (typeof data === 'object') {
                if (data.services) apiServices = data.services;
                else if (data.data) apiServices = data.data;
                else apiServices = [data];
            } else if (Array.isArray(data)) {
                apiServices = data;
            }
            
            if (Array.isArray(apiServices)) {
                for (const item of apiServices) {
                    const name = item.name || item.service || item.title || "Unknown";
                    const rval = item.range || item.range_val || item.value || "";
                    const cc = (item.country_code || item.country || "BD").toUpperCase();
                    const flag = getFlagEmoji(cc);
                    
                    if (!rval) continue;
                    
                    const existing = db.prepare("SELECT id FROM services WHERE range_val=?").get(rval);
                    if (existing) {
                        db.prepare("UPDATE services SET name=?, country_code=?, flag=? WHERE range_val=?").run(name, cc, flag, rval);
                    } else {
                        db.prepare("INSERT INTO services (name, range_val, country_code, flag) VALUES (?, ?, ?, ?)").run(name, rval, cc, flag);
                    }
                }
                return true;
            }
        }
    } catch (e) {
        console.error("API sync error:", e.message);
    }
    return false;
}

async function fetchOneNumber(rangeVal, attempt = 0) {
    const url = `${API_BASE_URL}/api/v1/numbers/get`;
    const headers = { "X-API-Key": API_KEY, "Content-Type": "application/json" };
    const payload = { range: rangeVal, format: "international" };
    
    try {
        const resp = await axios.post(url, payload, { headers, timeout: 15000 });
        if (resp.status === 200 && resp.data.number_id && resp.data.number) {
            return [resp.data.number_id, resp.data.number];
        }
    } catch (e) {
        // Silent error
    }
    
    if (attempt < 2) {
        await new Promise(r => setTimeout(r, 2000));
        return fetchOneNumber(rangeVal, attempt + 1);
    }
    return null;
}

async function fetchNumbersByRange(rangeVal, limit = 2) {
    const tasks = Array(limit).fill().map(() => fetchOneNumber(rangeVal));
    const results = await Promise.all(tasks);
    return results.filter(r => r !== null);
}

// ================= KEYBOARDS =================
function mainMenu(userId) {
    return Markup.keyboard([
        ['🟢 📞 𝑮𝑬𝑻 𝑵𝑼𝑴𝑩𝑬𝑹', '🔴 📊 𝑳𝑰𝑽𝑬 𝑺𝑬𝑹𝑽𝑰𝑪𝑬 𝑹𝑨𝑵𝑮𝑬'],
        ['🔵 💰 𝑩𝑨𝑳𝑨𝑵𝑪𝑬'],
        ...(isAdmin(userId) ? [['⚙️ 𝑨𝑫𝑴𝑰𝑵 𝑷𝑨𝑵𝑬𝑳']] : [])
    ]).resize();
}

function groupedServicesKeyboard() {
    const groups = db.prepare(`
        SELECT name, flag, COUNT(*) as cnt FROM services 
        GROUP BY name, flag ORDER BY name
    `).all();
    
    const buttons = groups.map(g => 
        [Markup.button.callback(`${g.flag} ${g.name} (${g.cnt})`, `app_${g.name}`)]
    );
    buttons.push([Markup.button.callback("🔍 Custom Range", "custom_range")]);
    
    return Markup.inlineKeyboard(buttons);
}

function adminMenu() {
    const withdrawStatus = isWithdrawEnabled() ? "ON" : "OFF";
    const maintStatus = isMaintenanceMode() ? "ON" : "OFF";
    
    return Markup.inlineKeyboard([
        [Markup.button.callback("📂 Manage Services", "manage_services"),
         Markup.button.callback("➕ Add Service", "add_service")],
        [Markup.button.callback("🔄 Sync All Ranges", "sync_ranges"),
         Markup.button.callback("👥 Manage Admins", "manage_admins")],
        [Markup.button.callback("📢 Broadcast", "admin_bc"),
         Markup.button.callback("💰 Set OTP Rate", "set_earning_rate")],
        [Markup.button.callback("⚙️ Set Min Withdraw", "set_min_withdraw"),
         Markup.button.callback("📋 Withdraw Requests", "view_withdraw_requests")],
        [Markup.button.callback("📊 Analytics", "analytics"),
         Markup.button.callback(`💸 𝑾𝑰𝑻𝑯𝑫𝑹𝑨𝑾 [${withdrawStatus}]`, "toggle_withdraw")],
        [Markup.button.callback(`🔧 Maintenance [${maintStatus}]`, "toggle_maintenance"),
         Markup.button.callback("🔙 Close", "admin_back")]
    ]);
}

function adminManagementMenu() {
    return Markup.inlineKeyboard([
        [Markup.button.callback("➕ Add Admin", "add_admin_btn")],
        [Markup.button.callback("❌ Remove Admin", "remove_admin_btn")],
        [Markup.button.callback("📋 List Admins", "list_admins")],
        [Markup.button.callback("🔙 Back", "manage_admins")]
    ]);
}

// ================= LIVE STATS =================
async function getLiveStats() {
    const data = db.prepare(`
        SELECT s.id, s.name, s.flag, s.range_val, COUNT(u.number_id) as cnt
        FROM services s LEFT JOIN used_numbers u ON s.id = u.service_id
        GROUP BY s.id
    `).all();
    
    const total = data.reduce((sum, row) => sum + row.cnt, 0);
    const totalUsers = db.prepare("SELECT COUNT(id) as c FROM users").get().c;
    
    if (total === 0) {
        return `📊 *Live Stats*\n\n👥 *Total Users:* ${totalUsers}\n📉 No successful OTPs yet.`;
    }
    
    let text = `📊 *Live Service Range & Value*\n👥 *Total Users:* ${totalUsers}\n\n`;
    
    for (const row of data) {
        const percent = total > 0 ? (row.cnt / total) * 100 : 0;
        const bar = "█".repeat(Math.floor(percent / 5)) + "░".repeat(20 - Math.floor(percent / 5));
        text += `${row.flag} *${row.name}* \`${row.range_val}\`\n   ${row.cnt} (${percent.toFixed(1)}%) \`${bar}\`\n\n`;
    }
    text += `*Total successful OTP:* ${total} | Real-time update`;
    return text;
}

// ================= SEND NUMBERS MESSAGE =================
async function sendNumbersMessage(ctx, serviceId, limit = 2, rangeValOverride = null) {
    let rangeVal, name, flag, sid, countryCode;
    
    if (rangeValOverride) {
        rangeVal = rangeValOverride;
        name = "Custom Range";
        flag = "🌍";
        sid = null;
    } else {
        const svc = db.prepare("SELECT id, name, range_val, flag, country_code FROM services WHERE id=?").get(serviceId);
        if (!svc) {
            await (ctx.callbackQuery ? ctx.answerCbQuery("Service not found!", {show_alert:true}).catch(()=>{}) : ctx.reply("Service not found!").catch(()=>{}));
            return null;
        }
        ({id: sid, name, range_val: rangeVal, flag, country_code: countryCode} = svc);
    }
    
    const userId = ctx.from.id;
    const numbers = await fetchNumbersByRange(rangeVal, limit);
    
    if (!numbers || !numbers.length) {
        const msgText = `❌ Could not fetch any numbers for \`${rangeVal}\`. Please try again later.`;
        if (ctx.callbackQuery) await ctx.editMessageText(msgText, {parse_mode:"Markdown"}).catch(()=>{});
        else await ctx.reply(msgText, {parse_mode:"Markdown"}).catch(()=>{});
        return null;
    }
    
    const countryMap = {
        "BD":"Bangladesh","US":"United States","IN":"India","MM":"Myanmar",
        "PK":"Pakistan","RU":"Russia","UA":"Ukraine","GB":"United Kingdom",
        "FR":"France","DE":"Germany","IT":"Italy","ES":"Spain",
        "BR":"Brazil","AR":"Argentina","MX":"Mexico","ID":"Indonesia",
        "PH":"Philippines","VN":"Vietnam","TH":"Thailand","TR":"Turkey",
        "EG":"Egypt","NG":"Nigeria","ZA":"South Africa","KE":"Kenya"
    };
    
    if (rangeValOverride) {
        const [cc] = getCountryFromPhone(numbers[0][1]);
        flag = getCountryFromPhone(numbers[0][1])[1];
        countryCode = cc;
    }
    const countryName = countryMap[countryCode] || countryCode;
    const rangeInfo = `${flag} *${countryName}* \`${rangeVal}\``;
    const text = `${rangeInfo}\n━━━━━━━━━━━━━━━━━━━━\n⏳ *Waiting for OTP...*`;
    
    // বাটনগুলো আলাদা আলাদা লাইনে করা হলো যাতে একসাথে চাপ না লাগে
    const buttons = [];
    for (const [nid, phone] of numbers) {
        const formatted = formatNumberWithFlag(phone);
        buttons.push([{ text: `📱 ${formatted}`, copy_text: { text: phone } }]);
        
        db.prepare(`INSERT OR REPLACE INTO active_numbers 
            (user_id, number_id, phone_number, service_id, message_id, requested_at) 
            VALUES (?, ?, ?, ?, ?, ?)`).run(
            userId, nid, phone, sid || 0, 0, new Date().toISOString()
        );
    }
    
    const changeData = rangeValOverride 
        ? `change_custom_${rangeVal}_${limit}` 
        : `change_${serviceId}_${limit}`;
    
    buttons.push([Markup.button.callback("🔴 𝑪𝑯𝑨𝑵𝑮𝑬", changeData)]);
    buttons.push([Markup.button.url("🔵 𝑮𝑬𝑻 𝑶𝑻𝑷 📲", OTP_GROUP_LINK)]);
    buttons.push([Markup.button.callback("🟢 𝑩𝑨𝑪𝑲 𝑻𝑶 𝑴𝑬𝑵𝑼", "main_menu")]);
    
    if (ctx.callbackQuery) {
        await ctx.deleteMessage().catch(()=>{});
        return ctx.reply(text, {parse_mode:"Markdown", ...Markup.inlineKeyboard(buttons)}).catch(()=>{});
    } else {
        return ctx.reply(text, {parse_mode:"Markdown", ...Markup.inlineKeyboard(buttons)}).catch(()=>{});
    }
}

// ================= SMART OTP FORWARDING (GROUP -> USER) =================
bot.on('message', async (ctx, next) => {
    // চেক করা হচ্ছে মেসেজটা গ্রুপ থেকে আসছে কি না
    if (ctx.chat && (ctx.chat.type === 'group' || ctx.chat.type === 'supergroup')) {
        if (String(ctx.chat.id) !== String(OTP_GROUP_ID)) {
            return next();
        }

        const text = ctx.message?.text || ctx.message?.caption;
        if (!text) return next();

        // মেসেজ থেকে সব স্পেস, ড্যাশ, অক্ষর বাদ দিয়ে শুধু নাম্বার বের করা
        const cleanText = text.replace(/[^\d]/g, '');

        // ডাটাবেস থেকে সব এক্টিভ নাম্বার বের করা
        const activeUsers = db.prepare(`SELECT user_id, phone_number FROM active_numbers`).all();

        for (const user of activeUsers) {
            const cleanPhone = user.phone_number.replace(/[^\d]/g, '');
            // নাম্বারের শেষের ১০ ডিজিট
            const last10 = cleanPhone.slice(-10);
            
            // যদি গ্রুপ মেসেজের ভেতর এই নাম্বারের শেষের ১০ ডিজিট থাকে (কাস্টম রেঞ্জসহ সব কাজ করবে)
            if (last10.length >= 8 && cleanText.includes(last10)) {
                try {
                    await bot.telegram.sendMessage(user.user_id, 
                        `🔔 *OTP Received!*\n\n📱 Number: \`${user.phone_number}\`\n\n📨 Message:\n${text}\n\n⏰ Time: ${new Date().toLocaleTimeString('bn-BD', { timeZone: 'Asia/Dhaka' })}`,
                        { parse_mode: "Markdown" }
                    );
                } catch (e) {
                    console.error("Failed to forward OTP to user:", e.message);
                }
            }
        }
        return; // গ্রুপের কাজ শেষ
    }
    
    return next(); 
});


// ================= USER HANDLERS =================
bot.start(async (ctx) => {
    const userId = ctx.from.id;
    db.prepare("INSERT OR IGNORE INTO users (id, username, fullname) VALUES (?, ?, ?)")
        .run(userId, ctx.from.username, ctx.from.first_name);
    
    if (await checkMaintenance(userId, ctx)) return;
    
    const userName = ctx.from.first_name;
    const welcomeText = `আসসালামু আলাইকুম, *${userName}*!! 👋
*𝑺𝑲𝒀𝑺𝑴𝑺𝑷𝑹𝑶 𝑩𝑶𝑻*-এ আপনাকে স্বাগতম! 🚀

এই বটটির মাধ্যমে আপনি খুব সহজেই যেকোনো সার্ভিসের ভেরিফিকেশনের জন্য ভার্চুয়াল নাম্বার এবং OTP পেতে পারেন।

👇 *কীভাবে ব্যবহার করবেন?*
📊 *𝑳𝑰𝑽𝑬 𝑺𝑬𝑹𝑽𝑰𝑪𝑬 𝑹𝑨𝑵𝑮𝑬:* লাইভ আপডেট দেখুন
📞 *𝑮𝑬𝑻 𝑵𝑼𝑴𝑩𝑬𝑹:* নাম্বার নিন
💰 *𝑩𝑨𝑳𝑨𝑵𝑪𝑬:* ব্যালেন্স চেক করুন

💡 _সাহায্যের জন্য সাপোর্ট গ্রুপে যুক্ত থাকুন।_`;
    
    await ctx.reply(welcomeText, {parse_mode:"Markdown", ...mainMenu(userId)}).catch(()=>{});
});

bot.hears('🔴 📊 𝑳𝑰𝑽𝑬 𝑺𝑬𝑹𝑽𝑰𝑪𝑬 𝑹𝑨𝑵𝑮𝑬', async (ctx) => {
    if (await checkMaintenance(ctx.from.id, ctx)) return;
    
    await ctx.reply(
        `📊 *𝑳𝑰𝑽𝑬 𝑺𝑬𝑹𝑽𝑰𝑪𝑬 𝑹𝑨𝑵𝑮𝑬*\n\n🔹 *লাইভ রেঞ্জ আপডেট পেতে নিচের বাটনে ক্লিক করুন!*\n\n👇 👇 👇`,
        {
            parse_mode: "Markdown",
            ...Markup.inlineKeyboard([[
                Markup.button.url("📊 𝐉𝐎𝐈𝐍 𝐋𝐈𝐕𝐄 𝐑𝐀𝐍𝐆𝐄 𝐆𝐑𝐎𝐔𝐏 📊", "https://t.me/SMSSKYOTP")
            ]])
        }
    ).catch(()=>{});
});

bot.hears('🟢 📞 𝑮𝑬𝑻 𝑵𝑼𝑴𝑩𝑬𝑹', async (ctx) => {
    if (await checkMaintenance(ctx.from.id, ctx)) return;
    
    const msg = await ctx.reply("⏳ 🔄 Syncing latest ranges from API...").catch(()=>{});
    if(!msg) return;
    await syncServicesFromAPI();
    await ctx.deleteMessage(msg.message_id).catch(()=>{});
    await ctx.reply("📱 Select an App:", groupedServicesKeyboard()).catch(()=>{});
});

bot.action(/^app_(.+)$/, async (ctx) => {
    await ctx.answerCbQuery().catch(()=>{}); 
    if (await checkMaintenance(ctx.from.id, ctx, true)) return;
    
    const appName = ctx.match[1];
    const ranges = db.prepare(`
        SELECT id, name, flag, range_val FROM services 
        WHERE name = ? ORDER BY range_val
    `).all(appName);
    
    if (!ranges.length) {
        await ctx.answerCbQuery("No ranges found for this app.", {show_alert:true}).catch(()=>{});
        return;
    }
    
    const buttons = ranges.map(r => 
        [Markup.button.callback(`${r.flag} ${r.name} [${r.range_val}]`, `service_${r.id}`)]
    );
    buttons.push([Markup.button.callback("🔙 Back", "back_to_apps")]);
    
    await ctx.editMessageText(`📱 *${appName}* - Select a range:`, {
        parse_mode: "Markdown",
        ...Markup.inlineKeyboard(buttons)
    }).catch(()=>{});
});

bot.action('back_to_apps', async (ctx) => {
    await ctx.answerCbQuery().catch(()=>{}); 
    if (await checkMaintenance(ctx.from.id, ctx, true)) return;
    await ctx.editMessageText("📱 Select an App:", groupedServicesKeyboard()).catch(()=>{});
});

bot.action(/^service_(\d+)$/, async (ctx) => {
    await ctx.answerCbQuery("⏳ Preparing numbers...").catch(()=>{}); 
    if (await checkMaintenance(ctx.from.id, ctx, true)) return;
    const serviceId = parseInt(ctx.match[1]);
    await sendNumbersMessage(ctx, serviceId, 2);
});

bot.action('custom_range', async (ctx) => {
    await ctx.answerCbQuery().catch(()=>{});
    if (await checkMaintenance(ctx.from.id, ctx, true)) return;
    await ctx.editMessageText("✏️ Please send the range value (e.g., `99298XXX`):", {parse_mode:"Markdown"}).catch(()=>{});
    ctx.session = ctx.session || {};
    ctx.session.waiting_custom_range = true;
});


// ================= MASTER TEXT CONTROLLER =================
bot.on('text', async (ctx, next) => {
    const text = ctx.message.text.trim();
    const userId = ctx.from.id;
    ctx.session = ctx.session || {};

    // ১. Admin Panel Input
    if (isAdmin(userId) && ctx.session.admin_step) {
        const step = ctx.session.admin_step;
        
        if (step === 'add_service_name') {
            ctx.session.admin_data = {name: text};
            ctx.session.admin_step = 'add_service_range';
            await ctx.reply("✏️ Enter Range Value (e.g., 99298XXX):").catch(()=>{});
            return;
        }
        if (step === 'add_service_range') {
            ctx.session.admin_data.range_val = text;
            ctx.session.admin_step = 'add_service_country';
            await ctx.reply("✏️ Enter Country Code (2 letters, e.g., BD, US, IN):").catch(()=>{});
            return;
        }
        if (step === 'add_service_country') {
            const cc = text.toUpperCase();
            if (cc.length !== 2) {
                await ctx.reply("❌ Invalid code. Must be exactly 2 letters.").catch(()=>{});
                return;
            }
            const {name, range_val} = ctx.session.admin_data;
            const flag = getFlagEmoji(cc);
            db.prepare("INSERT INTO services (name, range_val, country_code, flag) VALUES (?,?,?,?)").run(name, range_val, cc, flag);
            await ctx.reply(`✅ ${flag} *${name}* added successfully.`, {parse_mode:"Markdown"}).catch(()=>{});
            delete ctx.session.admin_step;
            delete ctx.session.admin_data;
            await ctx.reply("⚙️ 𝑨𝑫𝑴𝑰𝑵 𝑷𝑨𝑵𝑬𝑳", {parse_mode:"Markdown", ...adminMenu()}).catch(()=>{});
            return;
        }
        if (step === 'add_admin') {
            if (!/^\d+$/.test(text)) {
                await ctx.reply("❌ Invalid ID. Please enter a numeric user ID.").catch(()=>{});
                return;
            }
            db.prepare("INSERT OR IGNORE INTO admins VALUES (?)").run(text);
            await ctx.reply(`✅ User \`${text}\` is now an admin.`, {parse_mode:"Markdown"}).catch(()=>{});
            delete ctx.session.admin_step;
            await ctx.reply("⚙️ 𝑨𝑫𝑴𝑰𝑵 𝑷𝑨𝑵𝑬𝑳", {parse_mode:"Markdown", ...adminMenu()}).catch(()=>{});
            return;
        }
        if (step === 'remove_admin') {
            if (text === String(userId)) {
                await ctx.reply("❌ You cannot remove yourself.").catch(()=>{});
                return;
            }
            db.prepare("DELETE FROM admins WHERE user_id=?").run(text);
            await ctx.reply(`✅ User \`${text}\` is no longer an admin.`, {parse_mode:"Markdown"}).catch(()=>{});
            delete ctx.session.admin_step;
            await ctx.reply("⚙️ 𝑨𝑫𝑴𝑰𝑵 𝑷𝑨𝑵𝑬𝑳", {parse_mode:"Markdown", ...adminMenu()}).catch(()=>{});
            return;
        }
        if (step === 'broadcast') {
            const users = db.prepare("SELECT id FROM users").all();
            let success = 0;
            await ctx.reply("⏳ Sending broadcast...").catch(()=>{});
            for (const {id} of users) {
                try {
                    await bot.telegram.sendMessage(id, `📢 *Broadcast Message*\n\n${text}`, {parse_mode:"Markdown"});
                    success++;
                    await new Promise(r => setTimeout(r, 50));
                } catch(e) {}
            }
            await ctx.reply(`✅ Broadcast sent to ${success} users.`).catch(()=>{});
            delete ctx.session.admin_step;
            await ctx.reply("⚙️ 𝑨𝑫𝑴𝑰𝑵 𝑷𝑨𝑵𝑬𝑳", {parse_mode:"Markdown", ...adminMenu()}).catch(()=>{});
            return;
        }
        if (step === 'set_earning_rate') {
            const rate = parseFloat(text);
            if (isNaN(rate) || rate < 0) {
                await ctx.reply("❌ Invalid number.").catch(()=>{});
                delete ctx.session.admin_step;
                return;
            }
            db.prepare("UPDATE config SET value=? WHERE key='earning_per_otp'").run(String(rate));
            await ctx.reply(`✅ Rate set to ৳${rate} per OTP.`).catch(()=>{});
            delete ctx.session.admin_step;
            await ctx.reply("⚙️ 𝑨𝑫𝑴𝑰𝑵 𝑷𝑨𝑵𝑬𝑳", {parse_mode:"Markdown", ...adminMenu()}).catch(()=>{});
            return;
        }
        if (step === 'set_min_withdraw') {
            const m = parseFloat(text);
            if (isNaN(m) || m < 0) {
                await ctx.reply("❌ Invalid number.").catch(()=>{});
                delete ctx.session.admin_step;
                return;
            }
            db.prepare("UPDATE config SET value=? WHERE key='min_withdraw'").run(String(m));
            await ctx.reply(`✅ Minimum withdraw set to ৳${m}.`).catch(()=>{});
            delete ctx.session.admin_step;
            await ctx.reply("⚙️ 𝑨𝑫𝑴𝑰𝑵 𝑷𝑨𝑵𝑬𝑳", {parse_mode:"Markdown", ...adminMenu()}).catch(()=>{});
            return;
        }
    }

    // ২. Withdraw Input
    if (ctx.session.withdraw_step) {
        if (ctx.session.withdraw_step === 'number') {
            if (!/^\d{11}$/.test(text) || !text.startsWith('01')) {
                await ctx.reply("❌ Invalid number. Must be 11 digits starting with 01.").catch(()=>{});
                return;
            }
            ctx.session.withdraw_step = 'amount';
            ctx.session.withdraw_user.bkash = text;
            await ctx.reply("💰 How much TK do you want to withdraw?").catch(()=>{});
            return;
        }
        if (ctx.session.withdraw_step === 'amount') {
            const amt = parseFloat(text);
            const {id: uid, balance: bal, bkash} = ctx.session.withdraw_user;
            const minW = parseFloat(db.prepare("SELECT value FROM config WHERE key='min_withdraw'").get()?.value || 100);

            if (isNaN(amt) || amt <= 0 || amt > bal || amt < minW) {
                await ctx.reply("❌ Invalid amount.").catch(()=>{});
                delete ctx.session.withdraw_step;
                return;
            }

            db.prepare(`INSERT INTO withdraw_requests (user_id, amount, bkash_number, requested_at) VALUES (?, ?, ?, ?)`).run(uid, amt, bkash, new Date().toISOString());
            await ctx.reply(`✅ Withdraw request for ${amt} TK submitted successfully.`).catch(()=>{});

            const admins = db.prepare("SELECT user_id FROM admins").all();
            for (const admin of admins) {
                try {
                    await bot.telegram.sendMessage(admin.user_id, `🔔 *New Withdraw Request*\n👤 User: \`${uid}\`\n📱 bKash: \`${bkash}\`\n💰 Amount: \`৳${amt}\``, {parse_mode:"Markdown"});
                } catch(e) {}
            }
            delete ctx.session.withdraw_step;
            return;
        }
    }

    // ৩. Custom Range Input
    if (ctx.session.waiting_custom_range) {
        delete ctx.session.waiting_custom_range;
        if (!text) {
            await ctx.reply("❌ Invalid range. Please try again.").catch(()=>{});
            return;
        }
        const test = await fetchOneNumber(text);
        if (!test) {
            await ctx.reply(`❌ Range \`${text}\` does not exist.`, {parse_mode:"Markdown"}).catch(()=>{});
            return;
        }
        const existing = db.prepare("SELECT id FROM services WHERE range_val=?").get(text);
        if (existing) {
            await sendNumbersMessage(ctx, existing.id, 2, text);
        } else {
            await sendNumbersMessage(ctx, null, 2, text);
        }
        return;
    }

    // ৪. Skip Commands and Keyboards
    if (text.startsWith('/') || ['🔴 📊 𝑳𝑰𝑽𝑬 𝑺𝑬𝑹𝑽𝑰𝑪𝑬 𝑹𝑨𝑵𝑮𝑬','🟢 📞 𝑮𝑬𝑻 𝑵𝑼𝑴𝑩𝑬𝑹','🔵 💰 𝑩𝑨𝑳𝑨𝑵𝑪𝑬','⚙️ 𝑨𝑫𝑴𝑰𝑵 𝑷𝑨𝑵𝑬𝑳'].includes(text)) {
        return next();
    }

    // ৫. Auto-detect Range (যদি উপরের কোনো অপশন একটিভ না থাকে)
    const rangePattern = /[\+]?(\d{5,12}[Xx]{2,5})/;
    const match = text.match(rangePattern);
    
    if (match && !(await checkMaintenance(userId, ctx))) {
        let rangeVal = match[1].toUpperCase();
        if (rangeVal.startsWith('+')) rangeVal = rangeVal.slice(1);
        
        await ctx.reply(`🔍 Auto-detected range: \`${rangeVal}\`\n⏳ Checking availability...`, {parse_mode:"Markdown"}).catch(()=>{});
        
        const test = await fetchOneNumber(rangeVal);
        if (!test) {
            await ctx.reply(`❌ Range \`${rangeVal}\` does not exist.`, {parse_mode:"Markdown"}).catch(()=>{});
            return;
        }
        
        const existing = db.prepare("SELECT id FROM services WHERE range_val=?").get(rangeVal);
        if (existing) {
            await sendNumbersMessage(ctx, existing.id, 2, rangeVal);
        } else {
            await sendNumbersMessage(ctx, null, 2, rangeVal);
        }
    } else {
        return next();
    }
});


bot.action(/^change_(.+)$/, async (ctx) => {
    await ctx.answerCbQuery("⏳ Preparing new numbers...").catch(()=>{}); 
    if (await checkMaintenance(ctx.from.id, ctx, true)) return;
    
    const userId = ctx.from.id;
    db.prepare("DELETE FROM active_numbers WHERE user_id=?").run(userId);
    
    const parts = ctx.match[1].split('_');
    if (parts[0] === 'custom') {
        const rangeVal = parts[1];
        const limit = parseInt(parts[2]);
        const existing = db.prepare("SELECT id FROM services WHERE range_val=?").get(rangeVal);
        if (existing) {
            await sendNumbersMessage(ctx, existing.id, limit, rangeVal);
        } else {
            await sendNumbersMessage(ctx, null, limit, rangeVal);
        }
    } else {
        const serviceId = parseInt(parts[0]);
        const limit = parseInt(parts[1]);
        await sendNumbersMessage(ctx, serviceId, limit);
    }
});

bot.action('main_menu', async (ctx) => {
    await ctx.answerCbQuery().catch(()=>{}); 
    if (await checkMaintenance(ctx.from.id, ctx, true)) return;
    await ctx.deleteMessage().catch(()=>{});
    await ctx.reply("🔽 *Main Menu* 🔽", {parse_mode:"Markdown", ...mainMenu(ctx.from.id)}).catch(()=>{});
});

// ================= BALANCE & WITHDRAW =================
bot.hears('🔵 💰 𝑩𝑨𝑳𝑨𝑵𝑪𝑬', async (ctx) => {
    if (await checkMaintenance(ctx.from.id, ctx)) return;
    
    const userId = ctx.from.id;
    const bal = db.prepare("SELECT balance FROM users WHERE id=?").get(userId)?.balance || 0;
    const minW = db.prepare("SELECT value FROM config WHERE key='min_withdraw'").get()?.value || 100;
    const earn = db.prepare("SELECT value FROM config WHERE key='earning_per_otp'").get()?.value || 10;
    
    let text = `💰 *Your Wallet*\n\n🏦 Balance: ৳${bal}\n⬇️ Min withdraw: ৳${minW}\n💵 Per OTP: ৳${earn}`;
    
    const kb = isWithdrawEnabled() 
        ? Markup.inlineKeyboard([[Markup.button.callback("💸 𝑾𝑰𝑻𝑯𝑫𝑹𝑨𝑾", "withdraw_req")]]) 
        : {};
    
    await ctx.reply(text, {parse_mode:"Markdown", ...kb}).catch(()=>{});
});

bot.action('withdraw_req', async (ctx) => {
    await ctx.answerCbQuery().catch(()=>{});
    if (!isWithdrawEnabled()) {
        await ctx.answerCbQuery("❌ Withdraw is currently disabled.", {show_alert:true}).catch(()=>{});
        return;
    }
    if (await checkMaintenance(ctx.from.id, ctx, true)) return;
    
    const userId = ctx.from.id;
    const bal = db.prepare("SELECT balance FROM users WHERE id=?").get(userId)?.balance || 0;
    const minW = parseFloat(db.prepare("SELECT value FROM config WHERE key='min_withdraw'").get()?.value || 100);
    
    if (bal < minW) {
        await ctx.answerCbQuery(`Minimum withdraw is ${minW} TK. You have ${bal} TK.`, {show_alert:true}).catch(()=>{});
        return;
    }
    
    ctx.session = ctx.session || {};
    ctx.session.withdraw_step = 'number';
    ctx.session.withdraw_user = {id: userId, balance: bal};
    
    await ctx.reply("✏️ Enter your bKash number (01XXXXXXXXX):").catch(()=>{});
});


// ================= ADMIN PANEL =================
bot.hears('⚙️ 𝑨𝑫𝑴𝑰𝑵 𝑷𝑨𝑵𝑬𝑳', async (ctx) => {
    if (!isAdmin(ctx.from.id)) {
        await ctx.reply("❌ You are not an admin.").catch(()=>{});
        return;
    }
    await ctx.reply("⚙️ 𝑨𝑫𝑴𝑰𝑵 𝑷𝑨𝑵𝑬𝑳", {parse_mode:"Markdown", ...adminMenu()}).catch(()=>{});
});

bot.command('admin', async (ctx) => {
    if (!isAdmin(ctx.from.id)) return;
    await ctx.reply("⚙️ 𝑨𝑫𝑴𝑰𝑵 𝑷𝑨𝑵𝑬𝑳", {parse_mode:"Markdown", ...adminMenu()}).catch(()=>{});
});

bot.action('analytics', async (ctx) => {
    await ctx.answerCbQuery().catch(()=>{});
    if (!isAdmin(ctx.from.id)) {
        await ctx.answerCbQuery("Permission denied!", {show_alert:true}).catch(()=>{});
        return;
    }
    const stats = await getLiveStats();
    await ctx.editMessageText(stats, {
        parse_mode: "Markdown",
        ...Markup.inlineKeyboard([[Markup.button.callback("🔙 Back", "admin_back")]])
    }).catch(()=>{});
});

bot.action('manage_services', async (ctx) => {
    await ctx.answerCbQuery().catch(()=>{});
    if (!isAdmin(ctx.from.id)) return;
    
    const services = db.prepare("SELECT id, name, flag, range_val FROM services").all();
    if (!services.length) {
        await ctx.editMessageText("No services found.").catch(()=>{});
        return;
    }
    
    const buttons = services.map(s => 
        [Markup.button.callback(`🗑️ Delete: ${s.flag} ${s.name} [${s.range_val}]`, `del_srv_${s.id}`)]
    );
    buttons.push([Markup.button.callback("➕ Add Service", "add_service")]);
    buttons.push([Markup.button.callback("🔙 Back", "admin_back")]);
    
    await ctx.editMessageText("📂 *Service List* (Click to delete):", {
        parse_mode: "Markdown",
        ...Markup.inlineKeyboard(buttons)
    }).catch(()=>{});
});

bot.action('add_service', async (ctx) => {
    await ctx.answerCbQuery().catch(()=>{});
    if (!isAdmin(ctx.from.id)) return;
    await ctx.editMessageText("✏️ Enter Service Name (e.g. Telegram, WhatsApp):").catch(()=>{});
    ctx.session = ctx.session || {};
    ctx.session.admin_step = 'add_service_name';
});

bot.action('sync_ranges', async (ctx) => {
    await ctx.answerCbQuery().catch(()=>{});
    if (!isAdmin(ctx.from.id)) return;
    await ctx.editMessageText("⏳ 🔄 Syncing ranges from API...").catch(()=>{});
    const success = await syncServicesFromAPI();
    await ctx.editMessageText(success ? "✅ Ranges synced successfully." : "❌ Sync failed.").catch(()=>{});
    await new Promise(r => setTimeout(r, 2000));
    await ctx.editMessageText("⚙️ 𝑨𝑫𝑴𝑰𝑵 𝑷𝑨𝑵𝑬𝑳", {parse_mode:"Markdown", ...adminMenu()}).catch(()=>{});
});

bot.action(/^del_srv_(\d+)$/, async (ctx) => {
    await ctx.answerCbQuery("✅ Service deleted.").catch(()=>{});
    if (!isAdmin(ctx.from.id)) return;
    const sid = ctx.match[1];
    db.prepare("DELETE FROM services WHERE id=?").run(sid);
    
    const services = db.prepare("SELECT id, name, flag, range_val FROM services").all();
    const buttons = services.map(s => 
        [Markup.button.callback(`🗑️ ${s.flag} ${s.name}`, `del_srv_${s.id}`)]
    );
    buttons.push([Markup.button.callback("➕ Add", "add_service")]);
    buttons.push([Markup.button.callback("🔙 Back", "admin_back")]);

    await ctx.editMessageText("📂 *Service List* (Click to delete):", {
        parse_mode: "Markdown",
        ...Markup.inlineKeyboard(buttons)
    }).catch(()=>{});
});

bot.action('manage_admins', async (ctx) => {
    await ctx.answerCbQuery().catch(()=>{});
    if (!isAdmin(ctx.from.id)) return;
    await ctx.editMessageText("👥 *Admin Management*:", {parse_mode:"Markdown", ...adminManagementMenu()}).catch(()=>{});
});

bot.action('add_admin_btn', async (ctx) => {
    await ctx.answerCbQuery().catch(()=>{});
    if (!isAdmin(ctx.from.id)) return;
    await ctx.editMessageText("✏️ Enter the User ID to add as Admin:").catch(()=>{});
    ctx.session = ctx.session || {};
    ctx.session.admin_step = 'add_admin';
});

bot.action('remove_admin_btn', async (ctx) => {
    await ctx.answerCbQuery().catch(()=>{});
    if (!isAdmin(ctx.from.id)) return;
    await ctx.editMessageText("✏️ Enter the User ID to remove from Admins:").catch(()=>{});
    ctx.session = ctx.session || {};
    ctx.session.admin_step = 'remove_admin';
});

bot.action('list_admins', async (ctx) => {
    await ctx.answerCbQuery().catch(()=>{});
    if (!isAdmin(ctx.from.id)) return;
    const admins = db.prepare("SELECT user_id FROM admins").all();
    const text = admins.length 
        ? "👥 *Current Admins:*\n\n" + admins.map(a => `• \`${a.user_id}\``).join('\n')
        : "No admins found.";
    
    await ctx.editMessageText(text, {
        parse_mode: "Markdown",
        ...Markup.inlineKeyboard([[Markup.button.callback("🔙 Back", "manage_admins")]])
    }).catch(()=>{});
});

bot.action('admin_bc', async (ctx) => {
    await ctx.answerCbQuery().catch(()=>{});
    if (!isAdmin(ctx.from.id)) return;
    await ctx.editMessageText("✏️ Enter broadcast message (Markdown supported):").catch(()=>{});
    ctx.session = ctx.session || {};
    ctx.session.admin_step = 'broadcast';
});

bot.action('set_earning_rate', async (ctx) => {
    await ctx.answerCbQuery().catch(()=>{});
    if (!isAdmin(ctx.from.id)) return;
    const current = db.prepare("SELECT value FROM config WHERE key='earning_per_otp'").get()?.value || 10;
    await ctx.editMessageText(`✏️ Enter new earning amount per OTP (Current: ৳${current}):`).catch(()=>{});
    ctx.session = ctx.session || {};
    ctx.session.admin_step = 'set_earning_rate';
});

bot.action('set_min_withdraw', async (ctx) => {
    await ctx.answerCbQuery().catch(()=>{});
    if (!isAdmin(ctx.from.id)) return;
    const current = db.prepare("SELECT value FROM config WHERE key='min_withdraw'").get()?.value || 100;
    await ctx.editMessageText(`✏️ Enter new minimum withdraw amount (Current: ৳${current}):`).catch(()=>{});
    ctx.session = ctx.session || {};
    ctx.session.admin_step = 'set_min_withdraw';
});

bot.action('view_withdraw_requests', async (ctx) => {
    await ctx.answerCbQuery().catch(()=>{});
    if (!isAdmin(ctx.from.id)) return;
    
    const requests = db.prepare(`
        SELECT id, user_id, amount, bkash_number, requested_at 
        FROM withdraw_requests WHERE status='pending' 
        ORDER BY requested_at DESC
    `).all();
    
    if (!requests.length) {
        await ctx.editMessageText("📭 No pending withdraw requests.", 
            Markup.inlineKeyboard([[Markup.button.callback("🔙 Back", "admin_back")]])
        ).catch(()=>{});
        return;
    }
    
    await ctx.deleteMessage().catch(()=>{});
    
    for (const req of requests) {
        const uname = db.prepare("SELECT username FROM users WHERE id=?").get(req.user_id)?.username || "N/A";
        const text = `📋 *Request #${req.id}*\n👤 User ID: \`${req.user_id}\` (@${uname})\n💰 Amount: \`৳${req.amount}\`\n📱 bKash: \`${req.bkash_number}\`\n🕒 Time: ${req.requested_at}`;
        
        await ctx.reply(text, {
            parse_mode: "Markdown",
            ...Markup.inlineKeyboard([
                [Markup.button.callback("✅ Approve", `approve_wd_${req.id}`),
                 Markup.button.callback("❌ Reject", `reject_wd_${req.id}`)]
            ])
        }).catch(()=>{});
    }
    
    await ctx.reply("All pending requests listed above.", 
        Markup.inlineKeyboard([[Markup.button.callback("◀️ Back to Admin Panel", "admin_back")]])
    ).catch(()=>{});
});

bot.action(/^approve_wd_(\d+)$/, async (ctx) => {
    if (!isAdmin(ctx.from.id)) return;
    const rid = ctx.match[1];
    const req = db.prepare("SELECT user_id, amount, status FROM withdraw_requests WHERE id=?").get(rid);
    
    if (!req || req.status !== 'pending') {
        await ctx.answerCbQuery("Request not found or already processed.", {show_alert:true}).catch(()=>{});
        return;
    }
    
    const bal = db.prepare("SELECT balance FROM users WHERE id=?").get(req.user_id)?.balance || 0;
    if (bal < req.amount) {
        db.prepare("UPDATE withdraw_requests SET status='rejected' WHERE id=?").run(rid);
        try {
            await bot.telegram.sendMessage(req.user_id, `❌ Your withdrawal of ৳${req.amount} was rejected due to insufficient balance.`);
        } catch(e) {}
        await ctx.answerCbQuery("User balance too low. Auto-rejected.", {show_alert:true}).catch(()=>{});
        await ctx.editMessageText(`❌ Request #${rid} Auto-Rejected (Low Balance).`).catch(()=>{});
        return;
    }
    
    db.prepare("UPDATE users SET balance=? WHERE id=?").run(bal - req.amount, req.user_id);
    db.prepare("UPDATE withdraw_requests SET status='approved' WHERE id=?").run(rid);
    
    try {
        await bot.telegram.sendMessage(req.user_id, 
            `✅ *Congratulations!*\nYour withdrawal of \`৳${req.amount}\` has been approved.\n🏦 New Balance: \`৳${bal - req.amount}\``,
            {parse_mode:"Markdown"}
        );
    } catch(e) {}
    
    await ctx.answerCbQuery("✅ Approved!", {show_alert:true}).catch(()=>{});
    await ctx.editMessageText(`✅ Request #${rid} has been *Approved*.`, {parse_mode:"Markdown"}).catch(()=>{});
});

bot.action(/^reject_wd_(\d+)$/, async (ctx) => {
    if (!isAdmin(ctx.from.id)) return;
    const rid = ctx.match[1];
    const req = db.prepare("SELECT user_id, amount FROM withdraw_requests WHERE id=? AND status='pending'").get(rid);
    
    if (!req) {
        await ctx.answerCbQuery("Request not found or already processed.", {show_alert:true}).catch(()=>{});
        return;
    }
    
    db.prepare("UPDATE withdraw_requests SET status='rejected' WHERE id=?").run(rid);
    try {
        await bot.telegram.sendMessage(req.user_id, `❌ Your withdrawal request for ৳${req.amount} has been rejected.`);
    } catch(e) {}
    
    await ctx.answerCbQuery("❌ Rejected!", {show_alert:true}).catch(()=>{});
    await ctx.editMessageText(`❌ Request #${rid} has been *Rejected*.`, {parse_mode:"Markdown"}).catch(()=>{});
});

bot.action('admin_back', async (ctx) => {
    await ctx.answerCbQuery().catch(()=>{});
    if (!isAdmin(ctx.from.id)) return;
    await ctx.editMessageText("⚙️ 𝑨𝑫𝑴𝑰𝑵 𝑷𝑨𝑵𝑬𝑳", {parse_mode:"Markdown", ...adminMenu()}).catch(()=>{});
});

bot.action('toggle_maintenance', async (ctx) => {
    if (!isAdmin(ctx.from.id)) {
        await ctx.answerCbQuery("Unauthorized!", {show_alert:true}).catch(()=>{});
        return;
    }
    const newVal = isMaintenanceMode() ? 'off' : 'on';
    db.prepare("UPDATE config SET value=? WHERE key='maintenance_mode'").run(newVal);
    await ctx.answerCbQuery(`Maintenance mode turned ${newVal.toUpperCase()}`, {show_alert:true}).catch(()=>{});
    await ctx.editMessageText("⚙️ 𝑨𝑫𝑴𝑰𝑵 𝑷𝑨𝑵𝑬𝑳", {parse_mode:"Markdown", ...adminMenu()}).catch(()=>{});
});

bot.action('toggle_withdraw', async (ctx) => {
    if (!isAdmin(ctx.from.id)) {
        await ctx.answerCbQuery("Unauthorized!", {show_alert:true}).catch(()=>{});
        return;
    }
    const newVal = isWithdrawEnabled() ? 'off' : 'on';
    db.prepare("UPDATE config SET value=? WHERE key='withdraw_enabled'").run(newVal);
    await ctx.answerCbQuery(`Withdraw mode turned ${newVal.toUpperCase()}`, {show_alert:true}).catch(()=>{});
    await ctx.editMessageText("⚙️ 𝑨𝑫𝑴𝑰𝑵 𝑷𝑨𝑵𝑬𝑳", {parse_mode:"Markdown", ...adminMenu()}).catch(()=>{});
});

// ================= SHUTDOWN =================
process.once('SIGINT', () => bot.stop('SIGINT'));
process.once('SIGTERM', () => bot.stop('SIGTERM'));

// ================= LAUNCH =================
bot.launch().then(() => {
    console.log('✅ Bot started successfully! Complete System Running Perfectly!');
    console.log(`👤 Bot username: @${bot.botInfo?.username}`);
}).catch(console.error);
