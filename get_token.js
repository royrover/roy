const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch({
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-web-security']
  });
  const page = await browser.newPage();

  let token = null;

  // ดัก response แทน request
  page.on('response', async response => {
    const url = response.url();
    if (url.includes('metadata.json')) {
      const u = new URL(url);
      token = {
        tt:      u.searchParams.get('tt'),
        tpbk:    u.searchParams.get('tpbk'),
        tttlt:   u.searchParams.get('tttlt'),
        tuid:    u.searchParams.get('tuid'),
        tdid:    u.searchParams.get('tdid'),
        updated: new Date().toISOString()
      };
      console.log('Found token:', token);
    }
  });

  await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36');

  console.log('Opening page...');
  await page.goto('https://aisplay.ais.co.th/portal/live?vid=5f9e908c12008d9caab3cf3b', {
    waitUntil: 'domcontentloaded',
    timeout: 60000
  });

  console.log('Waiting for player...');
  // รอให้ player โหลด
  await new Promise(r => setTimeout(r, 15000));

  // ลองคลิก play ถ้ามี
  try {
    await page.click('button[class*="play"], .play-button, [aria-label*="play"]');
    await new Promise(r => setTimeout(r, 5000));
  } catch(e) {
    console.log('No play button found, continuing...');
  }

  await new Promise(r => setTimeout(r, 5000));
  await browser.close();

  if (token) {
    require('fs').writeFileSync('ais_token.json', JSON.stringify(token, null, 2));
    console.log('Token saved successfully');
  } else {
    console.error('Token not found');
    process.exit(1);
  }
})();
