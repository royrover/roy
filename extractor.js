const puppeteer = require('puppeteer');
const fs = require('fs');

async function run() {
    // 1. จำลองการเปิดเบราว์เซอร์ให้เหมือนมนุษย์ที่สุด ปิดสถิติบอททุกช่องทาง
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
    
    // ตั้งค่าขนาดหน้าจอจำลองเพื่อบังคับให้เว็บเรนเดอร์ UI เต็มรูปแบบ
    await page.setViewport({ width: 1280, height: 720 });
    
    // ปลอมแปลง Header เพื่อให้ระบบปลายทางคิดว่าเป็นโครมธรรมดาบน Windows
    await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36');

    try {
        console.log("กำลังวิ่งเข้าหน้าเว็บเพลย์ลิสต์ Dailymotion...");
        
        // 2. วิ่งเข้าหน้าเว็บโดยรอให้ Network นิ่งอย่างน้อย 2 วินาที
        await page.goto('https://www.dailymotion.com/playlist/x469d3', { 
            waitUntil: 'networkidle2',
            timeout: 60000 
        });
        
        // หน่วงเวลาเพิ่มอีก 4 วินาทีเพื่อให้มั่นใจว่าพวกตัวแปรเบื้องหลังทำเซสชันเสร็จ
        await new Promise(resolve => setTimeout(resolve, 4000));

        console.log("หน้าเว็บโหลดเสร็จสิ้น กำลังเริ่มค้นหา Token...");

        // 3. เริ่มกระบวนการแกะรอยหา Token (รองรับ 3 แผนสำรอง)
        const token = await page.evaluate(() => {
            // [แผนที่ 1]: ดึงผ่านออบเจกต์หน้าต่างหลักตัวที่ 1
            let tok = window.__PLAYER_CONFIG__?.context?.metadata?.access_token 
                   || window.__PLAYER_CONFIG__?.state?.player?.accessToken;
            
            if (tok) return tok;

            // [แผนที่ 2]: ดึงผ่านออบเจกต์หน้าต่างหลักตัวที่ 2 (หากระบบเพิ่งอัปเดต)
            tok = window.__state__?.entities?.player?.accessToken 
               || window.__state__?.player?.token;
            
            if (tok) return tok;

            // [แผนที่ 3]: ขุดซากอารยธรรมจากแท็ก <script> ในซอร์สโค้ดดิบ
            const scripts = Array.from(document.querySelectorAll('script'));
            for (let script of scripts) {
                const content = script.textContent;
                if (content && content.includes('accessToken')) {
                    const match = content.match(/"accessToken"\s*:\s*"([^"]+)"/);
                    if (match && match[1]) return match[1];
                }
                if (content && content.includes('access_token')) {
                    const match = content.match(/"access_token"\s*:\s*"([^"]+)"/);
                    if (match && match[1]) return match[1];
                }
            }

            return null;
        });

        if (token) {
            console.log("=== [SUCCESS] พบ Token สำเร็จรูป! ===");
            console.log("ค่าที่ได้ (ย่อ):", token.substring(0, 20) + "...");
            
            // เตรียมจัดรูปแบบ JSON ดิบเขียนลงตลับไฟล์ตามสเปกที่คุณกำหนด
            const jsonContent = JSON.stringify({
                "status": "success",
                "updated_at": new Date().toISOString(),
                "access_token": token
            }, null, 4);

            fs.writeFileSync('token_raw.json', jsonContent);
            console.log("อัปเดตไฟล์ token_raw.json ลงบน workspace สำเร็จ!");
        } else {
            // หากดึงไม่ได้ ให้สั่งแคปเจอร์ซอร์สโค้ดมาวิเคราะห์ใน Log ของ GitHub เผื่อตรวจสอบภายหลัง
            console.log("=== [FAILED] ไม่พบ Token ในระบบโครงสร้างปัจจุบัน ===");
            const bodyHtml = await page.evaluate(() => document.body.innerHTML.substring(0, 1000));
            console.log("ตัวอย่างโครงสร้าง HTML หน้าบ้านช่วงต้น:\n", bodyHtml);
            process.exit(1);
        }
    } catch (error) {
        console.error("เกิดข้อผิดพลาดรุนแรงระหว่างทำงานบน GitHub:", error);
        process.exit(1);
    } finally {
        await browser.close();
    }
}

run();
