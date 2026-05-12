const puppeteer = require('puppeteer');
const fs = require('fs');

async function fetchToken(url, label) {
    const browser = await puppeteer.launch({
        args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-web-security']
    });
    const page = await browser.newPage();
    await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36');

    let token = null;
    page.on('response', async response => {
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
        }
    });

    try {
        await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 });
        await new Promise(r => setTimeout(r, 15000));
    } catch (e) {
        console.error(`${label} error:`, e.message);
    } finally {
        await browser.close(); // ปิด Browser ทันทีเพื่อให้ Session ขาด
    }
    return token;
}

(async () => {
    const results = {};
    
    // ดึงทีละตัวแบบเริ่ม Browser ใหม่ทิ้งช่วงกัน
    results["B-TL"] = await fetchToken('https://aisplay.ais.co.th/portal/live?vid=5f9e908c12008d9caab3cf3b', 'B-TL');
    
    console.log('Waiting for session clear...');
    await new Promise(r => setTimeout(r, 5000)); 

    results["V"] = await fetchToken('https://aisplay.ais.co.th/portal/live?vid=612e7228b48eb0aad1c66193', 'V');

    fs.writeFileSync('roy_token.json', JSON.stringify(results, null, 2));
    console.log('Done.');
})();
