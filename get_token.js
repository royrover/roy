const puppeteer = require('puppeteer');
const fs = require('fs');

async function getToken(context, targetUrl, label) {
    console.log(`Getting token for ${label}...`);
    const page = await context.newPage();
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
            console.log(`Found ${label} token`);
        }
    });

    try {
        await page.goto(targetUrl, { waitUntil: 'domcontentloaded', timeout: 60000 });
        await new Promise(r => setTimeout(r, 15000)); 
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

    // ดึงกลุ่ม B-TL
    const ctx1 = await browser.createIncognitoBrowserContext();
    results["B-TL"] = await getToken(ctx1, 'https://aisplay.ais.co.th/portal/live?vid=5f9e908c12008d9caab3cf3b', 'B-TL');
    await ctx1.close();

    // ดึงกลุ่ม V
    const ctx2 = await browser.createIncognitoBrowserContext();
    results["V"] = await getToken(ctx2, 'https://aisplay.ais.co.th/portal/live?vid=612e7228b48eb0aad1c66193', 'V');
    await ctx2.close();

    await browser.close();

    if (results["B-TL"] || results["V"]) {
        fs.writeFileSync('roy_token.json', JSON.stringify(results, null, 2));
        console.log('All tokens saved successfully');
    } else {
        process.exit(1);
    }
})();
