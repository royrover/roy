const puppeteer = require('puppeteer');
const fs = require('fs');

async function fetchToken(url, label) {
    const browser = await puppeteer.launch({
        // headless: false, // แนะนำให้เปิดบรรทัดนี้เป็น false ก่อนในช่วงทดสอบ เพื่อดูว่าหน้าเว็บโหลดเสร็จจริงไหม
        args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-web-security']
    });
    const page = await browser.newPage();
    await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36');

    let token = null;

    // สร้าง Promise เพื่อล็อกให้ฟังก์ชันรอจนกว่าจะเจอ metadata.json หรือหมดเวลา
    const waitForToken = new Promise((resolve) => {
        // ตั้ง Timeout สูงสุด 30 วินาที ถ้ายังไม่เจอให้ข้าม เผื่อหน้าเว็บค้าง
        const timeoutId = setTimeout(() => resolve(null), 30000); 

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
                    resolve(token); // เจอแล้ว! ส่งค่ากลับไป
                }
            } catch (err) {
                // ป้องกันโค้ดพังในกรณีที่อ่าน URL ของบาง Response ไม่ได้
            }
        });
    });

    try {
        // ใช้ networkidle2 เพื่อให้มั่นใจว่าโหลดพวกสคริปต์และโฆษณาในหน้าเว็บนิ่งแล้ว
        await page.goto(url, { waitUntil: 'networkidle2', timeout: 60000 });
        
        // รอให้ Promise ด้านบนทำงานเสร็จ (ไม่ว่าจะเจอ Token หรือหมดเวลา 30 วิ)
        token = await waitForToken; 
        
    } catch (e) {
        console.error(`${label} error:`, e.message);
    } finally {
        await browser.close(); // ปิด Browser หลังจากที่ได้ Token หรือหมดเวลาอย่างปลอดภัย
    }
    return token;
}

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
