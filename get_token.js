const puppeteer = require('puppeteer');
const fs = require('fs');

async function fetchToken(url, label) {
    const browser = await puppeteer.launch({
        // ระบุเส้นทางสำหรับ GitHub Actions / Server
        executablePath: process.env.PUPPETEER_EXECUTABLE_PATH || null, 
        headless: 'new', // หรือ true สำหรับระบบ Server
        args: [
            '--no-sandbox', 
            '--disable-setuid-sandbox', 
            '--disable-web-security',
            // --- เพิ่ม Arguments เหล่านี้เพื่อหลบเลี่ยงการตรวจจับและเปิดเล่นวิดีโอบน Server ---
            '--disable-blink-features=AutomationControlled', // ซ่อนความเป็นบอท
            '--window-size=1920,1080',
            '--mute-audio',
            '--no-first-run',
            '--no-default-browser-check'
        ]
    });
    
    const page = await browser.newPage();
    
    // ตั้งค่าหน้าจอจำลองให้เหมือนคนใช้งานจริง
    await page.setViewport({ width: 1920, height: 1080 });

    // ปลอมแปลงคุณสมบัติของหน้าเว็บเพื่อหลบ Bot Detection
    await page.evaluateOnNewDocument(() => {
        Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
    });

    await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36');

    let token = null;

    const waitForToken = new Promise((resolve) => {
        // เพิ่มเวลาเป็น 45 วินาที เผื่อเซิร์ฟเวอร์ดาวน์โหลดหน้าเว็บช้ากว่าปกติ
        const timeoutId = setTimeout(() => resolve(null), 45000); 

        page.on('response', async response => {
            try {
                const u = response.url();
                if (u.includes('metadata.json')) {
                    const params = new URL(u).searchParams;
                    token = {
                        tt: params.get('tt'),
                        tpbk: params.get('tpbk'),
                        tttlt: params.get('tttlt'),
                        tuid: params.get('tuid'),
                        tdid: params.get('tdid'),
                        updated: new Date().toISOString()
                    };
                    clearTimeout(timeoutId);
                    resolve(token);
                }
            } catch (err) {}
        });
    });

    try {
        // ใช้ networkidle2 เพื่อให้หน้าเว็บโหลดสคริปต์สตรีมมิ่งเสร็จสมบูรณ์
        await page.goto(url, { waitUntil: 'networkidle2', timeout: 60000 });
        
        // รอให้ระบบดักเจอบล็อกข้อมูล
        token = await waitForToken; 
        
    } catch (e) {
        console.error(`${label} error:`, e.message);
    } finally {
        await browser.close(); 
    }
    return token;
}

// ... ส่วนที่เหลือของโค้ดคงเดิม ...


(async () => {
    const results = {};
    
    console.log('Fetching B-TL...');
    results["B-TL"] = await fetchToken('https://aisplay.ais.co.th/portal/live?vid=5f9e908c12008d9caab3cf3b', 'B-TL');
    console.log('B-TL Result:', results["B-TL"] ? 'Success' : 'Failed');
    
    console.log('Waiting for session clear...');
    await new Promise(r => setTimeout(r, 5000)); 

    console.log('Fetching V...');
    results["V"] = await fetchToken('https://aisplay.ais.co.th/portal/live?vid=612e7228b48eb0aad1c66193', 'V');
    console.log('V Result:', results["V"] ? 'Success' : 'Failed');

    fs.writeFileSync('roy_token.json', JSON.stringify(results, null, 2));
    console.log('Done.');
})();
