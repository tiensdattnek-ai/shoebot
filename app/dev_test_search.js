// dev_test_search.js – tự kiểm tra tìm kiếm của file shoebot_offline.html (cần Node.js)
// Dùng: node app/dev_test_search.js   (chạy trong thư mục shoebot/)
const fs = require('fs');
const html = fs.readFileSync(__dirname + '/shoebot_offline.html', 'utf8');
const script = html.match(/<script>([\s\S]*)<\/script>/)[1];

// stub DOM tối thiểu
const stubEl = { textContent:'', className:'', style:{}, value:'', innerHTML:'',
  appendChild(){}, addEventListener(){}, onclick:null };
global.document = { getElementById: () => Object.assign({}, stubEl),
  createElement: () => Object.assign({}, stubEl), body:{scrollHeight:0} };
global.window = { scrollTo(){} };
const out = [];
global.bubble = (text, who, tag) => out.push({who, tag, text});
global.notice = () => {};
const fn = new Function(script + '\n; return {search, tok, DOCS};');
const {search} = fn();
const tests = ["chân 25cm đi size bao nhiêu", "Samba giá bao nhiêu", "chân bè nên mua giày gì",
  "check nike fake", "vệ sinh da lộn", "chân bẹt giày gì", "Bondi vs Clifton", "xu hướng 2026",
  "bitis hunter x công nghệ", "dr martens đau gót", "phân biệt gucci thật giả", "giày dưới 2 triệu"];
for (const q of tests){
  const r = search(q, 3);
  console.log('Q:', q);
  r.forEach((x,i)=>console.log(`   ${i+1}. [${x.s.toFixed(2)}] ${x.d.cat} · ${x.d.title}`));
  if(!r.length) console.log('   (không match)');
}
