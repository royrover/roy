const puppeteer = require('puppeteer');
const fs = require('fs');

async function getToken(browser, targetUrl, label) {
    console.log(`Getting token for ${label}...`);
    const page = await browser.newPage();
    await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36');

    let token = null;
    page.on('response', async response => {
        const url = response.url();
        if (url.includes('metadata.json')) {
            const u = new URL(url);
            token = {
                tt: u.searchParams.get('tt'),
                tpbk: u.searchParams.get('tpbk'),
                tttlt: u.searchParams.get('tttlt'),
                tuid: u.searchParams.get('tuid'),
                tdid: u.searchParams.get('tdid'),
                updated: new Date().toISOString()
            };
        }
    });

    try {
        await page.goto(targetUrl, { waitUntil: 'domcontentloaded', timeout: 60000 });
        await new Promise(r => setTimeout(r, 15000)); // รอโหลด Player
    } catch (e) {
        console.error(`Error loading ${label}:`, e.message);
    } finally {
        await page.close();
    }
    return token;
}

(async () => {
    const browser = await puppeteer.launch({
        args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-web-security']
    });

    const results = {};

    // 1. เก็บกลุ่ม B-TL (ใช้ URL เดิมที่คุณมี)
    results["B-TL"] = await getToken(browser, 'https://aisplay.ais.co.th/portal/live?vid=5f9e908c12008d9caab3cf3b', 'B-TL');

    // 2. เก็บกลุ่ม V (ใช้ URL ใหม่ที่คุณแจ้งมา)
    results["V"] = await getToken(browser, 'https://aisplay.ais.co.th/portal/live?vid=612e7228b48eb0aad1c66193', 'V');

    await browser.close();

    if (results["B-TL"] || results["V"]) {
        fs.writeFileSync('roy_token.json', JSON.stringify(results, null, 2));
        console.log('Tokens saved successfully');
    } else {
        console.error('No tokens found');
        process.exit(1);
    }
})();
