const puppeteer = require('puppeteer');
const fs = require('fs');

async function run() {
    const browser = await puppeteer.launch({
        headless: true,
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    
    const page = await browser.newPage();
    
    try {
        // วิ่งเข้าหน้าเพลย์ลิสต์เพื่อให้เว็บเจเนอเรต Token หน้าบ้าน
        await page.goto('https://www.dailymotion.com/playlist/x469d3', { waitUntil: 'networkidle2' });
        
        // เจาะหน่วยความจำ window หน้าเว็บเพื่อควักเอา Access Token สำเร็จรูป
        const token = await page.evaluate(() => {
            return window.__PLAYER_CONFIG__?.context?.metadata?.access_token 
                || window.__PLAYER_CONFIG__?.state?.player?.accessToken
                || null;
        });

        if (token) {
            console.log("พบ Token สำเร็จรูป!");
            
            // เตรียมรูปแบบ JSON ดิบตามที่คุณต้องการ
            const jsonContent = JSON.stringify({
                "status": "success",
                "updated_at": new Date().toISOString(),
                "access_token": token
            }, null, 4);

            // เซฟลงไฟล์ในโฟลเดอร์ของ GitHub วัตถุประสงค์เพื่อรอบอทอัปโหลดขากลับ
            fs.writeFileSync('token_raw.json', jsonContent);
            console.log("เขียนไฟล์ token_raw.json เรียบร้อย!");
        } else {
            console.log("ไม่พบ Token ในระบบโครงสร้างปัจจุบัน");
            process.exit(1);
        }
    } catch (error) {
        console.error("เกิดข้อผิดพลาดระหว่างรันบอท:", error);
        process.exit(1);
    } finally {
        await browser.close();
    }
}

run();
