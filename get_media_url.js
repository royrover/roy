const puppeteer = require('puppeteer');
const fs = require('fs');

async function fetchMediaUrl(url, label) {
    const browser = await puppeteer.launch({
        headless: true, // หรือเปลี่ยนเป็น false ถ้าต้องการเปิดจอมาดูมันรัน
        args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-web-security']
    });
    const page = await browser.newPage();
    await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36');

    let resultData = null;

    // เปลี่ยนจาก 'response' มาใช้ 'request' เพราะเราต้องการแงะดู POST Payload (Body)
    page.on('request', request => {
        const reqUrl = request.url();
        
        // เจาะจงไปที่ endpoint ที่คุณส่งมา และต้องเป็น POST Method เท่านั้น
        if (reqUrl.includes('watch-duration/events') && request.method() === 'POST') {
            try {
                // ดึงข้อมูลดิบใน Body (Payload ที่ส่งไป)
                const postDataString = request.postData();
                if (postDataString) {
                    const payload = JSON.parse(postDataString);
                    
                    // ฉกเอา media_url และค่าสำคัญอื่นๆ ออกมาตรงๆ
                    if (payload && payload.media_url) {
                        resultData = {
                            project_id: payload.project_id,
                            video_id: payload.video_id,
                            playback_id: payload.playback_id,
                            media_url: payload.media_url, // 🎯 นี่คือสิ่งที่คุณอยากได้
                            updated: new Date().toISOString()
                        };
                    }
                }
            } catch (err) {
                // ป้องกันกรณี JSON Parse พัง
            }
        }
    });

    try {
        // วิ่งไปที่หน้าเว็บเป้าหมาย
        await page.goto(url, { waitUntil: 'networkidle2', timeout: 60000 });
        
        // รอ 15 วินาทีเท่าเดิม เพื่อให้ระบบฝั่งเครื่องเล่นวิดีโอทำงานและยิง Event ออกมา
        await new Promise(r => setTimeout(r, 15000));
    } catch (e) {
        console.error(`${label} error:`, e.message);
    } finally {
        await browser.close(); 
    }
    return resultData;
}

(async () => {
    const results = {};
    
    console.log('Starting grab Nation TV Media URL...');
    results["NationTV"] = await fetchMediaUrl('https://www.nationtv.tv/category/nationtv/live', 'NationTV');
    
    // บันทึกผลลงไฟล์ JSON โครงสร้างแบบเดิมที่คุณคุ้นเคย
    fs.writeFileSync('nation_token.json', JSON.stringify(results, null, 2));
    console.log('Done. ตรวจสอบลิงก์ได้ที่ไฟล์ nation_token.json');
})();
