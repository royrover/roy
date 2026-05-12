const puppeteer = require('puppeteer');
const fs = require('fs');

async function run() {
    const browser = await puppeteer.launch({
        args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-web-security']
    });

    const targets = [
        { label: "B-TL", url: 'https://aisplay.ais.co.th/portal/live?vid=5f9e908c12008d9caab3cf3b' },
        { label: "V", url: 'https://aisplay.ais.co.th/portal/live?vid=612e7228b48eb0aad1c66193' }
    ];

    const results = {};

    for (const target of targets) {
        console.log(`Processing ${target.label}...`);
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
            await page.goto(target.url, { waitUntil: 'domcontentloaded', timeout: 60000 });
            await new Promise(r => setTimeout(r, 15000));
            results[target.label] = token;
            
            // ล้าง Cookies/Cache ทันทีหลังจบแต่ละรอบ
            const client = await page.target().createCDPSession();
            await client.send('Network.clearBrowserCookies');
            await client.send('Network.clearBrowserCache');
        } catch (e) {
            console.error(`Error ${target.label}:`, e.message);
        } finally {
            await page.close();
        }
    }

    await browser.close();
    fs.writeFileSync('roy_token.json', JSON.stringify(results, null, 2));
}

run();
