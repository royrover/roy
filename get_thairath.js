const puppeteer = require('puppeteer');
const fs = require('fs');

async function fetchNationMediaUrl(url, label) {
    const browser = await puppeteer.launch({
        headless: "new",
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

    // 🎯 เปลี่ยนมาใช้ตรวจเช็คทราฟฟิกฝั่ง Request โดยเน้นการหาข้อความตรงๆ ไม่พึ่งพา JSON.parse ที่เปราะบาง
    await page.setRequestInterception(true);
    
    page.on('request', request => {
        const reqUrl = request.url();
        
        if (reqUrl.includes('batch/v2/events') && request.method() === 'POST') {
            const postDataString = request.postData();
            
            if (postDataString && postDataString.includes('media_url')) {
                try {
                    // หากแปลง JSON ปกติได้ ให้แปลงเลย
                    const payload = JSON.parse(postDataString);
                    if (payload && payload.media_url) {
                        tokenData = {
                            project_id: payload.project_id,
                            video_id: payload.video_id,
                            playback_id: payload.playback_id,
                            media_url: payload.media_url,
                            updated: new Date().toISOString()
                        };
                        console.log(`✅เจอลิงก์แล้ว (${label}):`, payload.media_url);
                    }
                } catch (e) {
                    // 💥 แผนสำรอง: หาก JSON.parse พังเพราะเจออักขระพิเศษ ให้ใช้ Regex ขูดเอา media_url ออกมาดื้อๆ เลย
                    const match = postDataString.match(/"media_url"\s*:\s*"([^"]+)"/);
                    if (match && match[1]) {
                        tokenData = {
                            media_url: match[1].replace(/\\/g, ''), // ล้าง backslash ออก
                            updated: new Date().toISOString()
                        };
                        console.log(`✅เจอลิงก์แล้ว [Regex Fallback] (${label}):`, tokenData.media_url);
                    }
                }
            }
        }
        request.continue();
    });

    try {
        // โหลดหน้าเว็บ
        await page.goto(url, { waitUntil: 'networkidle2', timeout: 60000 });
        
        console.log('หน้าเว็บโหลดเสร็จแล้ว กำลังกระตุ้นให้ Player ทำงาน...');
        await page.click('body');

        // สั่งเล่นวิดีโอเพื่อกระตุ้นให้ Beacon Events ส่งข้อมูลออกไปหาเซิร์ฟเวอร์ ByteArk
        await page.evaluate(() => {
            const videos = document.querySelectorAll('video');
            videos.forEach(video => {
                video.muted = false;
                video.volume = 0.5;
                video.play().catch(() => {});
            });
        });

        // ลูปเช็คเรื่อยๆ ทุกๆ 500ms ถ้าเจอ Token ปุ๊บให้หลุดลูปทันที ไม่ต้องรอจนครบ 15 วินาทีให้เสียเวลา
        for (let i = 0; i < 30; i++) {
            if (tokenData) break;
            await new Promise(r => setTimeout(r, 500));
        }

    } catch (e) {
        console.error(`${label} error:`, e.message);
    } finally {
        await browser.close();
    }
    return tokenData;
}

(async () => {
    const results = {};
    // แก้ไข Key ให้ตรงกับ Label เพื่อป้องกันความสับสนครับ
    results["ThaiRathTV"] = await fetchNationMediaUrl('https://www.thairath.co.th/tv/live', 'ThaiRath TV');
    
    fs.writeFileSync('thairath_token.json', JSON.stringify(results, null, 2));
    console.log('ThaiRath TV Process Done. ผลลัพธ์ถูกบันทึกลงไฟล์เรียบร้อยแล้ว!');
})();
