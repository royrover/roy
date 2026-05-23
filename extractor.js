const puppeteer = require('puppeteer');
const fs = require('fs');

async function run() {
    const browser = await puppeteer.launch({
        headless: true,
        args: [
            '--no-sandbox', 
            '--disable-setuid-sandbox',
            '--disable-web-security',
            '--disable-features=IsolateOrigins,site-per-process'
        ]
    });
    
    const page = await browser.newPage();
    await page.setViewport({ width: 1280, height: 720 });
    await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36');

    try {
        console.log("กำลังเปิดหน้าเว็บเพลย์ลิสต์ Dailymotion...");
        await page.goto('https://www.dailymotion.com/playlist/x469d3', { 
            waitUntil: 'networkidle2',
            timeout: 60000 
        });
        
        // หน่วงเวลารอระบบสร้าง iframe ตัวเล่นสักครู่
        await new Promise(resolve => setTimeout(resolve, 5000));

        console.log("ค้นหาเฟรมตัวเล่นวิดีโอ (geo.dailymotion.com)...");

        // 🛠️ แผนเด็ด: ค้นหาทุกลิงก์ iframe ที่แอบส่งพิกัดเล่นวิดีโอในหน้าเว็บ
        const frames = page.frames();
        let targetFrame = null;
        let token = null;

        // วนลูปหาเฟรมที่เป็นของดาราดังอย่าง geo.dailymotion
        for (const frame of frames) {
            const url = frame.url();
            if (url.includes('geo.dailymotion.com/player')) {
                targetFrame = frame;
                console.log("พบเฟรมเป้าหมาย:", url);
                break;
            }
        }

        // [กรณีเจอ iframe ของตัวเล่น] -> เจาะเข้าไปคุยในโลกของเฟรมนั้นเพื่อควัก Token
        if (targetFrame) {
            token = await targetFrame.evaluate(() => {
                return window.__PLAYER_CONFIG__?.context?.metadata?.access_token 
                    || window.__PLAYER_CONFIG__?.state?.player?.accessToken
                    || window.__state__?.entities?.player?.accessToken
                    || null;
            });
        }

        // [กรณีแผน 1 พัง หรือไม่เจอเฟรม] -> ดึงข้อมูลจากโค้ดดิบที่มีสิทธิ์สร้าง iframe ซะเลย
        if (!token) {
            console.log("ไม่พบ Token ในเฟรมหลัก กำลังสแกนหาตัวแปรแฝงในสคริปต์...");
            token = await page.evaluate(() => {
                const scripts = Array.from(document.querySelectorAll('script'));
                for (let script of scripts) {
                    const content = script.textContent;
                    if (content) {
                        // เจาะหา Token ที่อาจหลุดมากับ config ตัวเล่นในหน้าหลัก
                        const match = content.match(/"accessToken"\s*:\s*"([^"]+)"/) 
                                   || content.match(/"access_token"\s*:\s*"([^"]+)"/);
                        if (match && match[1]) return match[1];
                    }
                }
                return null;
            });
        }

        if (token) {
            console.log("=== [SUCCESS] เจาะดึง Token สำเร็จ! ===");
            console.log("ค่า Token (ย่อ):", token.substring(0, 25) + "...");
            
            const jsonContent = JSON.stringify({
                "status": "success",
                "updated_at": new Date().toISOString(),
                "access_token": token
            }, null, 4);

            fs.writeFileSync('token_raw.json', jsonContent);
            console.log("บันทึกตลับไฟล์ token_raw.json เรียบร้อย!");
        } else {
            console.log("=== [FAILED] สิ้นสุดการค้นหา ไม่พบ Token ในทุกมิติ ===");
            
            // พ่นโครงสร้างสคริปต์ในเฟรมออกมาดูเพิ่มเพื่อการตัดสินใจรอบหน้า
            if (targetFrame) {
                const frameHtml = await targetFrame.evaluate(() => document.body.innerHTML.substring(0, 500));
                console.log("โครงสร้างเนื้อหาภายใน iframe:\n", frameHtml);
            }
            process.exit(1);
        }
    } catch (error) {
        console.error("เกิดข้อผิดพลาดรุนแรงบนเซิร์ฟเวอร์:", error);
        process.exit(1);
    } finally {
        await browser.close();
    }
}

run();
