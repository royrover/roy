const puppeteer = require('puppeteer');
const fs = require('fs');

async function fetchNationMediaUrl(url, label) {
    const browser = await puppeteer.launch({
        headless: "new",
        // เพิ่ม flags บังคับเปิดเสียงและข้ามระบบล็อกของเบราว์เซอร์บน Linux
        args: [
            '--no-sandbox', 
            '--disable-setuid-sandbox', 
            '--disable-web-security',
            '--autoplay-policy=no-user-gesture-required'
        ]
    });
    const page = await browser.newPage();
    await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36');

    let tokenData = null;

    page.on('request', request => {
        const u = request.url();
        if (u.includes('watch-duration/events') && request.method() === 'POST') {
            try {
                const postDataString = request.postData();
                if (postDataString) {
                    const payload = JSON.parse(postDataString);
                    if (payload && payload.media_url) {
                        tokenData = {
                            project_id: payload.project_id,
                            video_id: payload.video_id,
                            playback_id: payload.playback_id,
                            media_url: payload.media_url,
                            updated: new Date().toISOString()
                        };
                    }
                }
            } catch (e) {}
        }
    });

    try {
        // เปลี่ยนเป็นโหลดหน้าเว็บจนเคลียร์ Network
        await page.goto(url, { waitUntil: 'networkidle0', timeout: 60000 });
        
        console.log('หน้าเว็บโหลดเสร็จแล้ว กำลังกระตุ้นให้ Player ทำงาน...');

        // 🎯 สั่งคลิกหน้าจอ 1 ที เพื่อหลอกเบราว์เซอร์ว่าผู้ใช้มีปฏิสัมพันธ์ (Interaction)
        await page.click('body');

        // 🎯 ส่งสคริปต์เข้าไปกดเล่นวิดีโอและเปิดเสียงในระดับชั้นของ ByteArk Iframe ตรงๆ
        await page.evaluate(() => {
            // ค้นหาแท็ก video ทั้งหมดในหน้าเว็บ (รวมถึงใน iframe ถ้าทะลุผ่านเข้าไปได้)
            const videos = document.querySelectorAll('video');
            videos.forEach(video => {
                video.muted = false; // เปิดเสียง
                video.volume = 0.5;
                video.play().catch(e => console.log("Autoplay blocked, trying forced play"));
            });
        });

        // รออีก 15 วินาทีเพื่อให้เวลาวิดีโอสตรีมและส่ง Payload ออกมา
        await new Promise(r => setTimeout(r, 15000));
    } catch (e) {
        console.error(`${label} error:`, e.message);
    } finally {
        await browser.close();
    }
    return tokenData;
}

(async () => {
    const results = {};
    results["NationTV"] = await fetchNationMediaUrl('https://www.nationtv.tv/category/nationtv/live', 'NationTV');
    fs.writeFileSync('nation_token.json', JSON.stringify(results, null, 2));
    console.log('Nation TV Process Done.');
})();
