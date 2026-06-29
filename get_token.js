const puppeteer = require('puppeteer');
const fs = require('fs');

async function fetchToken(url, label) {
    const browser = await puppeteer.launch({
        executablePath: process.env.PUPPETEER_EXECUTABLE_PATH || null, 
        headless: 'new',
        args: [
            '--no-sandbox', 
            '--disable-setuid-sandbox', 
            '--disable-web-security',
            '--disable-blink-features=AutomationControlled',
            '--window-size=1920,1080',
            '--mute-audio',
            '--autoplay-policy=no-user-gesture-required', // อนุญาต autoplay
            '--no-first-run',
            '--no-default-browser-check'
        ]
    });
    
    const page = await browser.newPage();
    
    await page.setViewport({ width: 1920, height: 1080 });

    await page.evaluateOnNewDocument(() => {
        Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
    });

    await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36');

    let token = null;

    // เก็บ log ของ network requests ทั้งหมดเพื่อ debug
    const requestUrls = [];
    
    page.on('request', request => {
        requestUrls.push(request.url());
    });

    const waitForToken = new Promise((resolve) => {
        const timeoutId = setTimeout(() => {
            console.log(`${label}: Timeout - No metadata.json found`);
            console.log('Captured URLs:', requestUrls.filter(u => u.includes('metadata') || u.includes('.m3u8')));
            resolve(null);
        }, 60000); // เพิ่มเวลาเป็น 60 วินาที

        page.on('response', async response => {
            try {
                const u = response.url();
                
                // Debug: แสดง URL ที่มี metadata หรือ m3u8
                if (u.includes('metadata') || u.includes('.m3u8')) {
                    console.log(`${label}: Found ${u}`);
                }
                
                if (u.includes('metadata.json')) {
                    const params = new URL(u).searchParams;
                    token = {
                        https_streaming: params.get('https_streaming'),
                        tt: params.get('tt'),
                        tpbk: params.get('tpbk'),
                        tfa: params.get('tfa'),
                        tttlt: params.get('tttlt'),
                        cdn: params.get('cdn'),
                        tuid: params.get('tuid'),
                        tdid: params.get('tdid'),
                        chunkHttps: params.get('chunkHttps'),
                        origin: params.get('origin'),
                        updated: new Date().toISOString(),
                        source_url: u // เก็บ URL ต้นทางไว้ด้วย
                    };
                    console.log(`${label}: Token captured!`);
                    clearTimeout(timeoutId);
                    resolve(token);
                }
            } catch (err) {
                console.error(`${label}: Response error:`, err.message);
            }
        });
    });

    try {
        console.log(`${label}: Navigating to ${url}`);
        await page.goto(url, { waitUntil: 'networkidle2', timeout: 60000 });
        
        // แก้ไขจุดนี้: ใช้ setTimeout ครอบด้วย Promise แทนการเรียก waitForTimeout
        await new Promise(r => setTimeout(r, 3000));
        
        try {
            console.log(`${label}: Looking for video player...`);
            
            // รอให้ video element โหลดขึ้นมา
            await page.waitForSelector('video', { timeout: 10000 });
            
            // คลิกที่วิดีโอเพื่อเริ่มเล่น (กระตุ้น Network Request)
            await page.evaluate(() => {
                const video = document.querySelector('video');
                if (video) {
                    console.log('Video found, attempting to play...');
                    video.play().catch(e => console.log('Play failed:', e));
                    
                    const playBtn = document.querySelector('[class*="play"]') || 
                                   document.querySelector('button[aria-label*="play"]') ||
                                   document.querySelector('.vjs-big-play-button');
                    if (playBtn) playBtn.click();
                }
            });
            
            console.log(`${label}: Video play initiated`);
            
        } catch (e) {
            console.log(`${label}: Could not find/play video:`, e.message);
        }
        
        // รอให้ token ถูกดักจับจาก event response
        token = await waitForToken; 
        
    } catch (e) {
        console.error(`${label}: Navigation error:`, e.message);
    } finally {
        await browser.close(); 
    }
    
    return token;
}

(async () => {
    const results = {};
    
    console.log('\n=== Fetching B-TL ===');
    results["B-TL"] = await fetchToken('https://app.ais-vidnt.com/portal/live?vid=5d4bebb6aae7315312049035', 'B-TL');
    console.log('B-TL Result:', results["B-TL"] ? '✓ Success' : '✗ Failed');
    
    console.log('\n=== Waiting for session clear ===');
    await new Promise(r => setTimeout(r, 5000)); 

    console.log('\n=== Fetching V ===');
    results["V"] = await fetchToken('https://app.ais-vidnt.com/portal/live?vid=68f6eac91b3e3ed505a5f154', 'V');
    console.log('V Result:', results["V"] ? '✓ Success' : '✗ Failed');

    console.log('\n=== Final Results ===');
    console.log(JSON.stringify(results, null, 2));
    
    fs.writeFileSync('roy_token.json', JSON.stringify(results, null, 2));
    console.log('\nSaved to roy_token.json');
})();
