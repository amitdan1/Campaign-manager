import { PrismaClient } from "@prisma/client";

const prisma = new PrismaClient();

function daysAgo(n: number): Date {
  const d = new Date();
  d.setDate(d.getDate() - n);
  d.setHours(Math.floor(Math.random() * 14) + 8, Math.floor(Math.random() * 60));
  return d;
}

// Real images from ofirassulin.design
const IMG = {
  hero1: "https://static.wixstatic.com/media/0b41c3_6f333c7d19bf44ecb22bc003a8a0d551~mv2.jpg/v1/fill/w_1920,h_1020,fp_0.46_0.56,q_90/0b41c3_6f333c7d19bf44ecb22bc003a8a0d551~mv2.jpg",
  hero2: "https://static.wixstatic.com/media/0b41c3_5fda7b7222fd49d8b75992af680f9901~mv2.jpg/v1/fill/w_1920,h_1020,fp_0.48_0.65,q_90/0b41c3_5fda7b7222fd49d8b75992af680f9901~mv2.jpg",
  hero3: "https://static.wixstatic.com/media/23a2ee_ad475c836fd94937ba910d476ebc5a05~mv2.jpg/v1/fit/w_1920,h_1020,q_90/23a2ee_ad475c836fd94937ba910d476ebc5a05~mv2.jpg",
  project1: "https://static.wixstatic.com/media/0b41c3_602a3ddc65874da6a63b434ef9975072~mv2.jpg/v1/fill/w_800,h_530,fp_0.35_0.59,q_90/0b41c3_602a3ddc65874da6a63b434ef9975072~mv2.jpg",
  project2: "https://static.wixstatic.com/media/0b41c3_91f2262ed307435eb2ab93392b48f365~mv2.jpg/v1/fill/w_800,h_530,fp_0.56_0.51,q_90/0b41c3_91f2262ed307435eb2ab93392b48f365~mv2.jpg",
  project3: "https://static.wixstatic.com/media/0b41c3_3f5a30890ff94c6481f268b5ecdb0e93~mv2.jpg/v1/fit/w_800,h_530,q_90/0b41c3_3f5a30890ff94c6481f268b5ecdb0e93~mv2.jpg",
  project4: "https://static.wixstatic.com/media/0b41c3_58f83b68d442451d888760bc3a17ad53~mv2.jpg/v1/fit/w_800,h_530,q_90/0b41c3_58f83b68d442451d888760bc3a17ad53~mv2.jpg",
  project5: "https://static.wixstatic.com/media/0b41c3_99edc3cc69df4612824dce343941a709~mv2.jpg/v1/fill/w_800,h_530,q_90/0b41c3_99edc3cc69df4612824dce343941a709~mv2.jpg",
  project6: "https://static.wixstatic.com/media/0b41c3_ba5903479b0e4af1a1fa76f5b804e016~mv2.jpg/v1/fill/w_800,h_530,q_90/0b41c3_ba5903479b0e4af1a1fa76f5b804e016~mv2.jpg",
  about: "https://static.wixstatic.com/media/0b41c3_c638871834d342fabcfc3da673dfe32a~mv2.jpg",
  logo: "https://static.wixstatic.com/media/23a2ee_b11a3356168a424bb5dc7bf607c7b85f~mv2.png/v1/fill/w_236,h_57,al_c,q_85,usm_0.66_1.00_0.01/23a2ee_b11a3356168a424bb5dc7bf607c7b85f~mv2.png",
  detail1: "https://static.wixstatic.com/media/0b41c3_cf65638ddbd346f0a13cd901f498a945~mv2.jpg/v1/fill/w_800,h_530,q_90/0b41c3_cf65638ddbd346f0a13cd901f498a945~mv2.jpg",
  detail2: "https://static.wixstatic.com/media/0b41c3_d4d03591065a46d59de1801e5df0b998~mv2.jpg/v1/fill/w_800,h_530,q_90/0b41c3_d4d03591065a46d59de1801e5df0b998~mv2.jpg",
  portrait: "https://static.wixstatic.com/media/23a2ee_b98b937816d34d65afcbacfae74e64ec~mv2.jpg/v1/fill/w_400,h_400,al_c,q_80/23a2ee_b98b937816d34d65afcbacfae74e64ec~mv2.jpg",
};

const LANDING_PAGE_VILLA = `<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Giving Soul To Spaces — אופיר אסולין עיצוב פנים</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Segoe UI',Tahoma,sans-serif;color:#2c2c2c;background:#faf9f7}
.hero{position:relative;height:100vh;display:flex;align-items:center;justify-content:center;overflow:hidden}
.hero::before{content:'';position:absolute;inset:0;background:url('${IMG.hero1}') center/cover;filter:brightness(.4)}
.hero-content{position:relative;z-index:1;text-align:center;color:#fff;max-width:800px;padding:0 2rem}
.hero-logo{width:200px;margin:0 auto 2rem;opacity:.9}
.hero h1{font-size:3.5rem;font-weight:300;margin-bottom:1rem;line-height:1.2;letter-spacing:1px}
.hero h1 strong{font-weight:700;color:#c9a96e}
.hero p{font-size:1.15rem;opacity:.85;margin-bottom:2.5rem;line-height:1.8}
.cta-btn{display:inline-block;background:#c9a96e;color:#fff;padding:1rem 3rem;border-radius:0;font-size:1rem;font-weight:600;text-decoration:none;transition:all .3s;letter-spacing:1px;border:2px solid #c9a96e}
.cta-btn:hover{background:transparent;color:#c9a96e}
.gallery{padding:5rem 2rem;max-width:1200px;margin:0 auto}
.section-title{text-align:center;font-size:2rem;font-weight:300;margin-bottom:.5rem;color:#1a1a2e;letter-spacing:1px}
.section-title strong{color:#c9a96e;font-weight:600}
.section-sub{text-align:center;color:#999;font-size:.95rem;margin-bottom:3rem}
.gallery-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:1.2rem}
.gallery-item{position:relative;height:320px;overflow:hidden;cursor:pointer}
.gallery-item img{width:100%;height:100%;object-fit:cover;transition:transform .5s}
.gallery-item:hover img{transform:scale(1.05)}
.gallery-item .overlay{position:absolute;bottom:0;left:0;right:0;padding:1.5rem;background:linear-gradient(transparent,rgba(0,0,0,.75));color:#fff;transform:translateY(20px);opacity:0;transition:all .3s}
.gallery-item:hover .overlay{transform:translateY(0);opacity:1}
.services{padding:5rem 2rem;background:#1a1a2e;color:#fff}
.services-inner{max-width:1100px;margin:0 auto}
.services .section-title{color:#fff}
.services-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:2rem;margin-top:3rem}
.svc{background:rgba(255,255,255,.04);border:1px solid rgba(201,169,110,.15);padding:2.5rem 2rem;text-align:center;transition:all .3s}
.svc:hover{background:rgba(201,169,110,.08);border-color:rgba(201,169,110,.4)}
.svc-icon{font-size:2rem;margin-bottom:1.2rem;color:#c9a96e}
.svc h3{font-size:1.1rem;margin-bottom:.8rem;color:#e8d5a8;font-weight:500}
.svc p{font-size:.85rem;color:rgba(255,255,255,.5);line-height:1.7}
.about{padding:5rem 2rem;max-width:1100px;margin:0 auto;display:grid;grid-template-columns:1fr 1fr;gap:4rem;align-items:center}
.about img{width:100%;height:auto;object-fit:cover}
.about-text h2{font-size:2rem;font-weight:300;margin-bottom:1.5rem;color:#1a1a2e}
.about-text h2 strong{color:#c9a96e}
.about-text p{font-size:.95rem;color:#666;line-height:1.8;margin-bottom:1.5rem}
.contact{padding:5rem 2rem;background:linear-gradient(135deg,#c9a96e,#b8944f);text-align:center;color:#fff}
.contact h2{font-size:2.2rem;font-weight:300;margin-bottom:1rem}
.contact p{font-size:1.05rem;opacity:.9;margin-bottom:2rem;max-width:550px;margin-left:auto;margin-right:auto}
.contact .cta-btn{background:#1a1a2e;color:#fff;border-color:#1a1a2e}
.contact .cta-btn:hover{background:transparent;border-color:#fff}
.contact-row{display:flex;justify-content:center;gap:3rem;margin-top:2rem;font-size:.9rem}
.footer{text-align:center;padding:2rem;background:#1a1a2e;color:rgba(255,255,255,.4);font-size:.75rem;letter-spacing:1px}
@media(max-width:768px){.hero h1{font-size:2.2rem}.gallery-grid,.services-grid{grid-template-columns:1fr}.about{grid-template-columns:1fr}}
</style>
</head>
<body>
<section class="hero">
<div class="hero-content">
<img src="${IMG.logo}" alt="Ofir Assulin Design" class="hero-logo">
<h1>Giving <strong>Soul</strong> To Spaces</h1>
<p>הבית הוא הנשמה שלכם בעולם החומר. אנחנו יוצרים עבורכם מקום שמותאם בדיוק לצרכים שלכם ולמי שאתם — מקום שמעניק את התחושות הנכונות כשאתם נכנסים אליו.</p>
<a href="#contact" class="cta-btn">לתיאום ייעוץ ראשוני ←</a>
</div>
</section>

<section class="gallery">
<h2 class="section-title">הפרויקטים <strong>שלנו</strong></h2>
<p class="section-sub">הצצה לפרויקטים אחרונים מהסטודיו</p>
<div class="gallery-grid">
<div class="gallery-item"><img src="${IMG.project1}" alt=""><div class="overlay"><h3>סלון מודרני</h3><p>עיצוב מינימליסטי · תל אביב</p></div></div>
<div class="gallery-item"><img src="${IMG.project2}" alt=""><div class="overlay"><h3>חלל מגורים</h3><p>שילוב חומרים טבעיים · הרצליה</p></div></div>
<div class="gallery-item"><img src="${IMG.project3}" alt=""><div class="overlay"><h3>מטבח ופינת אוכל</h3><p>עיצוב פונקציונלי · רמת השרון</p></div></div>
</div>
</section>

<section class="services">
<div class="services-inner">
<h2 class="section-title">ליווי מתחילת <strong>הפרויקט</strong> ועד סופו</h2>
<div class="services-grid">
<div class="svc"><div class="svc-icon">📐</div><h3>תכנון מלא</h3><p>סט תכניות מלא לביצוע — תכנית העמדה, בנייה, חשמל ותאורה, אינסטלציה, תקרה ומיזוג</p></div>
<div class="svc"><div class="svc-icon">🎨</div><h3>קונספט עיצובי</h3><p>הדמיות תלת-ממד, בחירת חומרים, צבעים, ריהוט ותאורה — הכל מותאם בדיוק לסגנון שלכם</p></div>
<div class="svc"><div class="svc-icon">🔑</div><h3>ניהול פרויקט</h3><p>ביקורים במבנה, בקרת איכות, התנהלות מול ספקים, ניהול תקציב ויציאה לימי שטח לרכישות</p></div>
</div>
</div>
</section>

<section class="about">
<img src="${IMG.about}" alt="אופיר אסולין">
<div class="about-text">
<h2>אופיר <strong>אסולין</strong></h2>
<p>הסטודיו הוקם מתוך תשוקה עמוקה ליצירת שינוי מהותי באיכות חייהם של אנשים, וליצור עבורם מרחב אישי בטוח.</p>
<p>כבעלת סטודיו לעיצוב וכאמנית, אני משלבת את שני העולמות יחד. אני מתמחה בתכנון רהיטים בהתאמה אישית — שוני, ייחודיות וחדשנות שמוציאים אתכם מהמשבצת של מוצרי מדף.</p>
<a href="https://api.whatsapp.com/send/?phone=972526269261" class="cta-btn" style="background:#1a1a2e;color:#fff;border-color:#1a1a2e;font-size:.9rem;padding:.8rem 2rem">💬 שלחו הודעה בוואטסאפ</a>
</div>
</section>

<section class="contact" id="contact">
<h2>מוכנים להתחיל?</h2>
<p>צרו קשר לייעוץ ראשוני ללא עלות. נשמח להכיר את הפרויקט שלכם ולהתחיל לדמיין ביחד.</p>
<a href="tel:052-626-9261" class="cta-btn">📞 052-626-9261</a>
<div class="contact-row">
<div>📧 ofirassulin.design@gmail.com</div>
<div>🌐 www.ofirassulin.design</div>
</div>
</section>

<footer class="footer">© 2026 OFIR ASSULIN DESIGN · כל הזכויות שמורות</footer>
</body>
</html>`;

const LANDING_PAGE_RENOVATION = `<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>שיפוץ מקצועי — אופיר אסולין עיצוב פנים</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Segoe UI',Tahoma,sans-serif;color:#2c2c2c;background:#faf9f7}
.hero{display:grid;grid-template-columns:1fr 1fr;min-height:100vh}
.hero-text{display:flex;flex-direction:column;justify-content:center;padding:4rem 5rem;background:#faf9f7}
.hero-text img{width:140px;margin-bottom:2rem;opacity:.8}
.hero-text h1{font-size:2.8rem;font-weight:300;line-height:1.3;margin-bottom:1.5rem;color:#1a1a2e}
.hero-text h1 strong{color:#c9a96e;font-weight:700}
.hero-text p{font-size:1.05rem;color:#666;line-height:1.8;margin-bottom:2rem}
.hero-text .features{list-style:none;margin-bottom:2.5rem}
.hero-text .features li{padding:.6rem 0;font-size:.95rem;color:#444;display:flex;align-items:center;gap:.8rem}
.hero-text .features li::before{content:'✓';display:flex;align-items:center;justify-content:center;width:26px;height:26px;background:#c9a96e;color:#fff;font-size:.75rem;flex-shrink:0}
.btn{display:inline-block;background:#c9a96e;color:#fff;padding:1rem 2.5rem;font-size:1rem;font-weight:600;text-decoration:none;transition:all .3s;border:2px solid #c9a96e;letter-spacing:.5px}
.btn:hover{background:transparent;color:#c9a96e}
.btn-dark{background:#1a1a2e;border-color:#1a1a2e;color:#fff}
.btn-dark:hover{background:transparent;color:#1a1a2e}
.hero-img{background:url('${IMG.hero2}') center/cover;position:relative}
.hero-img::after{content:'';position:absolute;inset:0;background:linear-gradient(to left,transparent 60%,#faf9f7)}
.process{padding:5rem 2rem;background:#fff}
.process-inner{max-width:1000px;margin:0 auto;text-align:center}
.process h2{font-size:2rem;font-weight:300;margin-bottom:.5rem;color:#1a1a2e}
.process h2 strong{color:#c9a96e}
.process-sub{color:#999;margin-bottom:3.5rem;font-size:.95rem}
.steps{display:grid;grid-template-columns:repeat(4,1fr);gap:2rem;counter-reset:step}
.step{text-align:center}
.step::before{counter-increment:step;content:counter(step);display:flex;align-items:center;justify-content:center;width:50px;height:50px;background:#c9a96e;color:#fff;font-size:1.3rem;font-weight:700;margin:0 auto 1.2rem}
.step h3{font-size:1rem;margin-bottom:.5rem;color:#1a1a2e}
.step p{font-size:.82rem;color:#999;line-height:1.6}
.projects{padding:5rem 2rem;background:#f5f0e8}
.projects-inner{max-width:1100px;margin:0 auto;text-align:center}
.projects h2{font-size:2rem;font-weight:300;margin-bottom:3rem;color:#1a1a2e}
.projects h2 strong{color:#c9a96e}
.p-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:1.5rem}
.p-card{overflow:hidden;background:#fff;box-shadow:0 2px 15px rgba(0,0,0,.05)}
.p-card img{width:100%;height:260px;object-fit:cover;transition:transform .4s}
.p-card:hover img{transform:scale(1.03)}
.p-card .info{padding:1.5rem}
.p-card .info h3{font-size:1.05rem;margin-bottom:.4rem;color:#1a1a2e}
.p-card .info p{font-size:.85rem;color:#888;line-height:1.6}
.cta{padding:5rem 2rem;background:#1a1a2e;text-align:center;color:#fff}
.cta h2{font-size:2rem;font-weight:300;margin-bottom:1rem}
.cta h2 strong{color:#c9a96e}
.cta p{font-size:1rem;opacity:.7;margin-bottom:2.5rem;max-width:550px;margin-left:auto;margin-right:auto}
.footer{text-align:center;padding:2rem;background:#111;color:rgba(255,255,255,.3);font-size:.75rem;letter-spacing:1px}
@media(max-width:768px){.hero{grid-template-columns:1fr}.hero-img{height:300px}.hero-text{padding:3rem 2rem}.steps{grid-template-columns:1fr 1fr}.p-grid{grid-template-columns:1fr}}
</style>
</head>
<body>
<section class="hero">
<div class="hero-text">
<img src="${IMG.logo}" alt="Ofir Assulin Design">
<h1>הפכו את הבית שלכם<br>ל<strong>מרחב שמדבר אליכם</strong></h1>
<p>ליווי מקצועי מתכנון ועד הלבשה סופית — שיפוץ בלי כאב ראש, עם תוצאה שתאהבו לשנים.</p>
<ul class="features">
<li>סט תכניות מלא — העמדה, חשמל, אינסטלציה, נגרות</li>
<li>הדמיות 3D לפני תחילת עבודה</li>
<li>ניהול מלא מול ספקים וקבלנים</li>
<li>ריהוט בהתאמה אישית — ייחודי ולא מדף</li>
</ul>
<div style="display:flex;gap:1rem;flex-wrap:wrap">
<a href="https://api.whatsapp.com/send/?phone=972526269261" class="btn">💬 שלחו וואטסאפ</a>
<a href="tel:052-626-9261" class="btn btn-dark">📞 052-626-9261</a>
</div>
</div>
<div class="hero-img"></div>
</section>

<section class="process">
<div class="process-inner">
<h2>התהליך <strong>שלנו</strong></h2>
<p class="process-sub">מהפגישה הראשונה ועד שאתם נכנסים לבית המחודש</p>
<div class="steps">
<div class="step"><h3>פגישת היכרות</h3><p>הבנת הצרכים, התקציב וסגנון החיים</p></div>
<div class="step"><h3>תכנון ועיצוב</h3><p>סט תכניות + הדמיות 3D + קונספט עיצובי</p></div>
<div class="step"><h3>ביצוע וליווי</h3><p>ביקורים באתר, בקרת איכות, ניהול ספקים</p></div>
<div class="step"><h3>הלבשה ומסירה</h3><p>ריהוט, אקססוריז, פרטים אחרונים</p></div>
</div>
</div>
</section>

<section class="projects">
<div class="projects-inner">
<h2>מהפרויקטים <strong>שלנו</strong></h2>
<div class="p-grid">
<div class="p-card"><img src="${IMG.project4}" alt=""><div class="info"><h3>שיפוץ דירה בתל אביב</h3><p>הפיכת חלל ישן לעיצוב מודרני עם חומרים טבעיים</p></div></div>
<div class="p-card"><img src="${IMG.project5}" alt=""><div class="info"><h3>עיצוב מלא ברמת השרון</h3><p>תכנון מלא מאפס כולל נגרות בהתאמה אישית</p></div></div>
</div>
</div>
</section>

<section class="cta">
<h2>מוכנים <strong>להתחיל?</strong></h2>
<p>ספרו לנו על הפרויקט שלכם ונחזור אליכם עם הצעה מותאמת תוך 24 שעות.</p>
<a href="tel:052-626-9261" class="btn">📞 דברו איתנו</a>
</section>

<footer class="footer">© 2026 OFIR ASSULIN DESIGN · כל הזכויות שמורות</footer>
</body>
</html>`;

const LANDING_PAGE_PENTHOUSE = `<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>עיצוב דירות יוקרה — אופיר אסולין</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Segoe UI',Tahoma,sans-serif;color:#2c2c2c;background:#0a0a0a}
.hero{height:100vh;display:flex;flex-direction:column;justify-content:flex-end;position:relative;padding:5rem}
.hero::before{content:'';position:absolute;inset:0;background:url('${IMG.hero3}') center/cover}
.hero::after{content:'';position:absolute;inset:0;background:linear-gradient(to top,rgba(0,0,0,.85) 0%,rgba(0,0,0,.2) 60%)}
.hero>*{position:relative;z-index:1}
.hero .eyebrow{color:#c9a96e;font-size:.85rem;letter-spacing:3px;text-transform:uppercase;margin-bottom:1rem}
.hero h1{color:#fff;font-size:3.5rem;font-weight:300;line-height:1.2;margin-bottom:1.5rem;max-width:700px}
.hero h1 strong{font-weight:700}
.hero p{color:rgba(255,255,255,.7);font-size:1.1rem;max-width:550px;line-height:1.8;margin-bottom:2.5rem}
.btn{display:inline-block;padding:1rem 2.5rem;font-size:.95rem;font-weight:600;text-decoration:none;transition:all .3s;letter-spacing:.5px}
.btn-gold{background:#c9a96e;color:#0a0a0a;border:2px solid #c9a96e}
.btn-gold:hover{background:transparent;color:#c9a96e}
.btn-ghost{background:transparent;color:#fff;border:1px solid rgba(255,255,255,.3)}
.btn-ghost:hover{border-color:#c9a96e;color:#c9a96e}
.scroll-line{position:absolute;bottom:2rem;left:50%;transform:translateX(-50%);display:flex;flex-direction:column;align-items:center;gap:.5rem;color:rgba(255,255,255,.4);font-size:.7rem;letter-spacing:2px;z-index:1}
.scroll-line::after{content:'';width:1px;height:40px;background:linear-gradient(rgba(201,169,110,.8),transparent);animation:pulse 2s infinite}
@keyframes pulse{0%,100%{opacity:.3}50%{opacity:1}}
.story{display:grid;grid-template-columns:1fr 1fr;min-height:80vh}
.story-img{background-size:cover;background-position:center}
.story-text{display:flex;flex-direction:column;justify-content:center;padding:5rem;background:#0a0a0a;color:#fff}
.story-text .num{color:#c9a96e;font-size:4.5rem;font-weight:100;opacity:.4;margin-bottom:.5rem}
.story-text h2{font-size:1.8rem;font-weight:300;margin-bottom:1.5rem;line-height:1.4}
.story-text h2 strong{color:#c9a96e;font-weight:600}
.story-text p{color:rgba(255,255,255,.55);line-height:1.8;font-size:.95rem;margin-bottom:1.5rem}
.story-text ul{list-style:none}
.story-text ul li{padding:.6rem 0;border-bottom:1px solid rgba(255,255,255,.06);color:rgba(255,255,255,.65);font-size:.9rem;display:flex;align-items:center;gap:.8rem}
.story-text ul li span{color:#c9a96e}
.values{padding:5rem 2rem;background:#111;text-align:center}
.values h2{color:#fff;font-size:2rem;font-weight:300;margin-bottom:.8rem}
.values h2 strong{color:#c9a96e}
.values>p{color:rgba(255,255,255,.45);max-width:650px;margin:0 auto 3.5rem;line-height:1.8;font-size:.95rem}
.v-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:1px;max-width:900px;margin:0 auto;background:rgba(255,255,255,.05)}
.v-item{background:#111;padding:3rem 2rem;transition:background .3s}
.v-item:hover{background:#1a1a1a}
.v-item h3{color:#e8d5a8;font-size:.95rem;margin-bottom:.6rem;font-weight:600}
.v-item p{color:rgba(255,255,255,.35);font-size:.82rem;line-height:1.6}
.contact{padding:5rem 2rem;background:#0a0a0a;text-align:center;border-top:1px solid rgba(201,169,110,.12)}
.contact img{width:160px;margin-bottom:2rem;opacity:.7}
.contact h2{color:#fff;font-size:2rem;font-weight:300;margin-bottom:.8rem}
.contact h2 strong{color:#c9a96e}
.contact p{color:rgba(255,255,255,.45);font-size:1rem;margin-bottom:2.5rem}
.contact-row{display:flex;justify-content:center;gap:1.5rem;flex-wrap:wrap}
.contact-links{display:flex;justify-content:center;gap:2.5rem;margin-top:2.5rem}
.contact-links a{color:rgba(255,255,255,.4);text-decoration:none;font-size:.85rem;transition:color .3s}
.contact-links a:hover{color:#c9a96e}
.footer{text-align:center;padding:1.5rem;background:#050505;color:rgba(255,255,255,.18);font-size:.7rem;letter-spacing:1px}
@media(max-width:768px){.hero{padding:3rem 2rem}.hero h1{font-size:2.3rem}.story{grid-template-columns:1fr}.story-img{height:300px}.story-text{padding:3rem 2rem}.v-grid{grid-template-columns:1fr}}
</style>
</head>
<body>
<section class="hero">
<div class="eyebrow">OFIR ASSULIN · INTERIOR DESIGN</div>
<h1>הבית הוא <strong>הנשמה שלכם</strong> בעולם החומר</h1>
<p>אני לא מגדירה את השפה העיצובית שלי, כי אני מאמינה שכל בית צריך להתאים עצמו למשפחה ולא להיפך. עיצוב פנים שמרגיש — בדיוק כמוכם.</p>
<div style="display:flex;gap:1.5rem;flex-wrap:wrap">
<a href="#contact" class="btn btn-gold">לקביעת פגישה</a>
<a href="#story" class="btn btn-ghost">הכירו אותנו</a>
</div>
<div class="scroll-line">SCROLL</div>
</section>

<section class="story" id="story">
<div class="story-img" style="background-image:url('${IMG.project1}')"></div>
<div class="story-text">
<div class="num">01</div>
<h2>כל פרויקט מתחיל <strong>בהקשבה</strong></h2>
<p>אנחנו לא מגיעים עם תבניות מוכנות. כל בית הוא סיפור ייחודי — ותפקידנו להוציא אותו מהדמיון אל המציאות.</p>
<ul>
<li><span>→</span> פגישת היכרות אישית בנכס</li>
<li><span>→</span> הבנת סגנון החיים והצרכים</li>
<li><span>→</span> בניית קונספט עיצובי והדמיות 3D</li>
<li><span>→</span> סט תכניות מלא לביצוע</li>
</ul>
</div>
</section>

<section class="story" style="direction:ltr">
<div class="story-text" style="direction:rtl">
<div class="num">02</div>
<h2>חומרים ופרטים <strong>בהתאמה אישית</strong></h2>
<p>כבעלת סטודיו לעיצוב וכאמנית, אני משלבת את שני העולמות. אני מתמחה בתכנון רהיטים בהתאמה אישית — ותופתעו לגלות, לרוב גם מוזיל עלויות.</p>
<ul>
<li><span>→</span> ריהוט בייצור אישי — ייחודי ולא מדף</li>
<li><span>→</span> ליווי ביקורים ובקרת איכות</li>
<li><span>→</span> ניהול תקציב וספקים</li>
<li><span>→</span> יציאה לימי שטח לרכישת כלל האלמנטים</li>
</ul>
</div>
<div class="story-img" style="background-image:url('${IMG.project6}')"></div>
</section>

<section class="values">
<h2>הגישה <strong>שלנו</strong></h2>
<p>עיצוב פנים משפיע על תחושות, זיכרונות, חוויות ורגשות. אנחנו יוצרים עבורכם מרחב אישי בטוח — מקום שמעניק את התחושות הנכונות.</p>
<div class="v-grid">
<div class="v-item"><h3>התאמה מושלמת</h3><p>כל בית צריך להתאים עצמו למשפחה — ולא להיפך</p></div>
<div class="v-item"><h3>פונקציה ואסתטיקה</h3><p>פונקציונלי, פרקטי, נוח — ובאותה נשימה מדויק לשפה שאתם אוהבים</p></div>
<div class="v-item"><h3>ייחודיות ושוני</h3><p>תכנון בייצור אישי שמביא חדשנות — ולא עוד מוצרי מדף</p></div>
</div>
</section>

<section class="contact" id="contact">
<img src="${IMG.logo}" alt="Ofir Assulin Design">
<h2>מזמינה אתכם <strong>לצאת למסע</strong></h2>
<p>להתאמה מושלמת בין הבית שלכם לבין מי שאתם.</p>
<div class="contact-row">
<a href="https://api.whatsapp.com/send/?phone=972526269261" class="btn btn-gold">💬 וואטסאפ</a>
<a href="tel:052-626-9261" class="btn btn-ghost">📞 052-626-9261</a>
</div>
<div class="contact-links">
<a href="https://www.ofirassulin.design">www.ofirassulin.design</a>
<a href="https://instagram.com/ofirassulin.design">@ofirassulin.design</a>
</div>
</section>

<footer class="footer">© 2026 OFIR ASSULIN DESIGN · ALL RIGHTS RESERVED</footer>
</body>
</html>`;

async function main() {
  console.log("🌱 Seeding database...\n");

  // Clear existing data
  await prisma.interaction.deleteMany();
  await prisma.aBTestVariant.deleteMany();
  await prisma.aBTest.deleteMany();
  await prisma.tokenUsage.deleteMany();
  await prisma.chatMessage.deleteMany();
  await prisma.agentMemory.deleteMany();
  await prisma.brandAsset.deleteMany();
  await prisma.proposal.deleteMany();
  await prisma.campaign.deleteMany();
  await prisma.lead.deleteMany();

  // === LEADS (18) ===
  console.log("👥 Creating leads...");
  const leads = await Promise.all([
    prisma.lead.create({ data: { name: "רונית כהן", phone: "052-123-4567", email: "ronit@gmail.com", source: "google", status: "converted", qualityScore: 9, scoreReasoning: "תקציב גבוה, אזור יעד, פרויקט וילה", location: "הרצליה", budget: "800,000", projectType: "villa", notes: "מחפשת עיצוב מודרני מינימליסטי", createdAt: daysAgo(28) } }),
    prisma.lead.create({ data: { name: "אילן לוי", phone: "054-987-6543", email: "ilan.levi@outlook.com", source: "facebook", status: "consultation_booked", qualityScore: 8, scoreReasoning: "אזור מרכז, שיפוץ מקיף", location: "רמת השרון", budget: "350,000", projectType: "renovation", notes: "שיפוץ דירה 5 חדרים", createdAt: daysAgo(25) } }),
    prisma.lead.create({ data: { name: "דנה מילר", phone: "050-555-1234", email: "dana.m@gmail.com", source: "instagram", status: "qualified", qualityScore: 9, scoreReasoning: "פנטהאוז בתל אביב, תקציב מאוד גבוה", location: "תל אביב", budget: "1,200,000", projectType: "penthouse", notes: "פנטהאוז 200 מ״ר, רוצה סגנון עכשווי", createdAt: daysAgo(22) } }),
    prisma.lead.create({ data: { name: "יוסי אברהם", phone: "053-111-2222", email: "yossi.a@gmail.com", source: "google", status: "contacted", qualityScore: 7, scoreReasoning: "תקציב בינוני, פרויקט שיפוץ", location: "כפר שמריהו", budget: "250,000", projectType: "renovation", createdAt: daysAgo(20) } }),
    prisma.lead.create({ data: { name: "מיכל שרון", phone: "050-333-4444", email: "michal.sharon@yahoo.com", source: "facebook", status: "consultation_booked", qualityScore: 8, scoreReasoning: "בנייה חדשה, אזור יעד", location: "סביון", budget: "600,000", projectType: "new_build", createdAt: daysAgo(18) } }),
    prisma.lead.create({ data: { name: "עמית דוד", phone: "054-222-3333", email: "amit.d@gmail.com", source: "organic", status: "new", qualityScore: 6, scoreReasoning: "תקציב בינוני-נמוך", location: "רעננה", budget: "150,000", projectType: "renovation", createdAt: daysAgo(15) } }),
    prisma.lead.create({ data: { name: "נועה פרידמן", phone: "052-444-5555", email: "noa.f@gmail.com", source: "google", status: "qualified", qualityScore: 9, scoreReasoning: "וילה חדשה, תקציב גבוה מאוד", location: "הרצליה פיתוח", budget: "1,500,000", projectType: "villa", notes: "וילה 450 מ״ר, שני קומות + בריכה", createdAt: daysAgo(14) } }),
    prisma.lead.create({ data: { name: "אורי גולדשטיין", phone: "050-666-7777", email: "ori.g@walla.co.il", source: "instagram", status: "contacted", qualityScore: 7, scoreReasoning: "דירת יוקרה, תקציב טוב", location: "תל אביב", budget: "400,000", projectType: "luxury_apt", createdAt: daysAgo(12) } }),
    prisma.lead.create({ data: { name: "שירה בן-עמי", phone: "053-888-9999", email: "shira.ba@gmail.com", source: "facebook", status: "new", qualityScore: 5, scoreReasoning: "תקציב לא ברור", location: "פתח תקוה", budget: "", projectType: "renovation", createdAt: daysAgo(10) } }),
    prisma.lead.create({ data: { name: "רועי כץ", phone: "054-111-0000", email: "roei.k@gmail.com", source: "google", status: "converted", qualityScore: 10, scoreReasoning: "וילה מפוארת, תקציב ללא הגבלה", location: "סביון", budget: "2,000,000", projectType: "villa", notes: "וילה 600 מ״ר, סגנון קלאסי מודרני", createdAt: daysAgo(9) } }),
    prisma.lead.create({ data: { name: "יעל אוחנה", phone: "050-222-1111", email: "yael.o@gmail.com", source: "manual", status: "consultation_booked", qualityScore: 8, scoreReasoning: "הפנייה מלקוחה קודמת, פנטהאוז", location: "תל אביב", budget: "900,000", projectType: "penthouse", createdAt: daysAgo(7) } }),
    prisma.lead.create({ data: { name: "תומר אשכנזי", phone: "052-333-2222", email: "tomer.a@gmail.com", source: "google", status: "qualified", qualityScore: 7, scoreReasoning: "שיפוץ מקיף, אזור מרכז", location: "רמת השרון", budget: "300,000", projectType: "renovation", createdAt: daysAgo(5) } }),
    prisma.lead.create({ data: { name: "ליאת ברק", phone: "054-444-3333", email: "liat.b@hotmail.com", source: "facebook", status: "new", qualityScore: 6, scoreReasoning: "שיפוץ קטן", location: "הרצליה", budget: "180,000", projectType: "renovation", createdAt: daysAgo(4) } }),
    prisma.lead.create({ data: { name: "אלון מזרחי", phone: "050-555-4444", email: "alon.m@gmail.com", source: "instagram", status: "contacted", qualityScore: 8, scoreReasoning: "דירת יוקרה גדולה", location: "תל אביב", budget: "500,000", projectType: "luxury_apt", createdAt: daysAgo(3) } }),
    prisma.lead.create({ data: { name: "רותם חן", phone: "053-666-5555", email: "rotem.c@gmail.com", source: "google", status: "new", qualityScore: 7, scoreReasoning: "בנייה חדשה, תקציב סביר", location: "כפר שמריהו", budget: "700,000", projectType: "new_build", createdAt: daysAgo(2) } }),
    prisma.lead.create({ data: { name: "גיל רפפורט", phone: "052-777-6666", email: "gil.r@gmail.com", source: "organic", status: "new", qualityScore: 5, scoreReasoning: "שאלה כללית, לא ברור אם רציני", location: "ראשון לציון", budget: "", projectType: "", createdAt: daysAgo(1) } }),
    prisma.lead.create({ data: { name: "נטע שמש", phone: "054-888-7777", email: "neta.s@gmail.com", source: "facebook", status: "lost", qualityScore: 4, scoreReasoning: "תקציב נמוך, מחוץ לאזור שירות", location: "באר שבע", budget: "80,000", projectType: "renovation", createdAt: daysAgo(20) } }),
    prisma.lead.create({ data: { name: "עידן לנגר", phone: "050-999-8888", email: "idan.l@gmail.com", source: "manual", status: "lost", qualityScore: 3, scoreReasoning: "לא ענה לטלפון מספר פעמים", location: "נתניה", budget: "120,000", projectType: "renovation", createdAt: daysAgo(26) } }),
  ]);
  console.log(`  ✅ ${leads.length} leads created`);

  // === CAMPAIGNS (8) ===
  console.log("📢 Creating campaigns...");
  const campaignData = [
    { campaignId: "G-001", campaignName: "וילות יוקרה - חיפוש", platform: "google", impressions: 12400, clicks: 310, conversions: 8, cost: 1850 },
    { campaignId: "G-002", campaignName: "שיפוצים מרכז - חיפוש", platform: "google", impressions: 18700, clicks: 467, conversions: 12, cost: 2100 },
    { campaignId: "G-003", campaignName: "מעצבת פנים תל אביב", platform: "google", impressions: 9200, clicks: 184, conversions: 5, cost: 980 },
    { campaignId: "FB-001", campaignName: "קרוסלה - פרויקטים", platform: "facebook", impressions: 45000, clicks: 890, conversions: 6, cost: 1200 },
    { campaignId: "FB-002", campaignName: "לידים - שיפוצים", platform: "facebook", impressions: 32000, clicks: 640, conversions: 9, cost: 1450 },
    { campaignId: "FB-003", campaignName: "ריטרגטינג - אתר", platform: "facebook", impressions: 8500, clicks: 255, conversions: 4, cost: 520 },
    { campaignId: "IG-001", campaignName: "סטוריז - לפני/אחרי", platform: "instagram", impressions: 28000, clicks: 1120, conversions: 7, cost: 890 },
    { campaignId: "IG-002", campaignName: "ריליזים - סיורי פרויקט", platform: "instagram", impressions: 52000, clicks: 2080, conversions: 3, cost: 650 },
  ];

  const campaigns = [];
  for (const c of campaignData) {
    const ctr = c.impressions > 0 ? (c.clicks / c.impressions) * 100 : 0;
    const cpl = c.conversions > 0 ? c.cost / c.conversions : 0;
    const convRate = c.clicks > 0 ? (c.conversions / c.clicks) * 100 : 0;
    campaigns.push(
      await prisma.campaign.create({
        data: { ...c, cpl, ctr, conversionRate: convRate, date: daysAgo(Math.floor(Math.random() * 25) + 1) },
      })
    );
  }
  console.log(`  ✅ ${campaigns.length} campaigns created`);

  // === PROPOSALS (10 including 3 landing pages) ===
  console.log("📋 Creating proposals...");
  const proposals = await Promise.all([
    prisma.proposal.create({ data: { agentName: "strategy", proposalType: "weekly_plan", title: "תוכנית שבועית — פוקוס על וילות הרצליה", summary: "הגדלת תקציב Google Ads ב-20% לקמפיין וילות יוקרה. הוספת מילות מפתח חדשות ושיפור דפי נחיתה.", status: "approved", createdAt: daysAgo(20) } }),
    prisma.proposal.create({ data: { agentName: "content", proposalType: "ad_copy", title: "מודעת פייסבוק — שיפוצים", summary: "קופי חדש למודעת קרוסלה עם דגש על לפני/אחרי ואחריות על התוצאה. כולל 3 וריאציות של כותרות.", status: "approved", createdAt: daysAgo(18) } }),
    prisma.proposal.create({ data: { agentName: "budget", proposalType: "budget_change", title: "העברת תקציב מ-Instagram ל-Google", summary: "בהתבסס על נתוני המרה — Google Ads מביא CPL נמוך ב-35% מ-Instagram. מומלץ להעביר ₪200 חודשי.", status: "pending_review", createdAt: daysAgo(10) } }),
    prisma.proposal.create({ data: { agentName: "content", proposalType: "email", title: "אימייל מעקב — לידים שלא המירו", summary: "סדרת 3 אימיילים אוטומטית ללידים שנוצר איתם קשר אך לא קבעו ייעוץ. כוללת תמונות פרויקט ועדויות.", status: "pending_review", createdAt: daysAgo(8) } }),
    prisma.proposal.create({ data: { agentName: "campaign", proposalType: "campaign", title: "קמפיין חדש — פנטהאוזים תל אביב", summary: "קמפיין ממוקד בגוגל ובפייסבוק לקהל יעד של רוכשי פנטהאוזים בצפון תל אביב. תקציב מוצע: ₪1,500/חודש.", status: "pending_review", createdAt: daysAgo(5) } }),
    prisma.proposal.create({ data: { agentName: "strategy", proposalType: "weekly_plan", title: "תוכנית שבועית — A/B טסט דפי נחיתה", summary: "ריצת A/B טסט על שני דפי נחיתה שונים לקמפיין וילות. מדידת שיעור המרה ואיכות לידים.", status: "executing", createdAt: daysAgo(4) } }),
    prisma.proposal.create({ data: { agentName: "content", proposalType: "ad_copy", title: "קופי מודעה — Google RSA", summary: "15 כותרות ו-4 תיאורים למודעת Responsive Search Ad בגוגל. מילות מפתח: עיצוב פנים, מעצבת פנים, שיפוץ יוקרתי.", status: "completed", createdAt: daysAgo(15) } }),
    // Landing page proposals with real HTML
    prisma.proposal.create({ data: { agentName: "landingPage", proposalType: "landing_page", title: "דף נחיתה — וילות יוקרה", summary: "דף נחיתה בסגנון Hero Gallery לקמפיין וילות יוקרה. כולל גלריית פרויקטים, שירותים, עדויות ו-CTA.", content: JSON.stringify({ html: LANDING_PAGE_VILLA }), status: "approved", createdAt: daysAgo(12) } }),
    prisma.proposal.create({ data: { agentName: "landingPage", proposalType: "landing_page", title: "דף נחיתה — שיפוצים", summary: "דף נחיתה בסגנון Split Layout לקמפיין שיפוצים. כולל תהליך עבודה, לפני/אחרי וסטטיסטיקות.", content: JSON.stringify({ html: LANDING_PAGE_RENOVATION }), status: "approved", createdAt: daysAgo(10) } }),
    prisma.proposal.create({ data: { agentName: "landingPage", proposalType: "landing_page", title: "דף נחיתה — פנטהאוזים", summary: "דף נחיתה בסגנון Story Flow לקמפיין פנטהאוזים. עיצוב דארק יוקרתי עם סיפור מותג.", content: JSON.stringify({ html: LANDING_PAGE_PENTHOUSE }), status: "pending_review", createdAt: daysAgo(3) } }),
  ]);
  console.log(`  ✅ ${proposals.length} proposals created`);

  // === BRAND ASSETS (8) ===
  console.log("🖼️  Creating brand assets...");
  const assets = await Promise.all([
    prisma.brandAsset.create({ data: { assetType: "image", source: "website", url: IMG.project1, assetMetadata: JSON.stringify({ width: 800, height: 530, alt: "סלון מודרני — פרויקט עיצוב פנים" }) } }),
    prisma.brandAsset.create({ data: { assetType: "image", source: "website", url: IMG.project2, assetMetadata: JSON.stringify({ width: 800, height: 530, alt: "חלל מגורים — שילוב חומרים טבעיים" }) } }),
    prisma.brandAsset.create({ data: { assetType: "image", source: "website", url: IMG.project3, assetMetadata: JSON.stringify({ width: 800, height: 530, alt: "מטבח ופינת אוכל — עיצוב פונקציונלי" }) } }),
    prisma.brandAsset.create({ data: { assetType: "image", source: "instagram", url: IMG.project4, assetMetadata: JSON.stringify({ width: 800, height: 530, alt: "פרויקט עיצוב — חלל אורח" }) } }),
    prisma.brandAsset.create({ data: { assetType: "image", source: "instagram", url: IMG.project5, assetMetadata: JSON.stringify({ width: 800, height: 530, alt: "פרויקט שיפוץ — חדר שינה" }) } }),
    prisma.brandAsset.create({ data: { assetType: "image", source: "website", url: IMG.hero1, assetMetadata: JSON.stringify({ width: 1920, height: 1020, alt: "Hero — חלל ראשי" }) } }),
    prisma.brandAsset.create({ data: { assetType: "text", source: "website", url: "https://www.ofirassulin.design/about", assetMetadata: JSON.stringify({ type: "about_text", text: "הסטודיו הוקם מתוך תשוקה עמוקה ליצירת שינוי מהותי באיכות חייהם של אנשים, וליצור עבורם את מרחב אישי בטוח. הבית הוא הנשמה שלכם בעולם החומר." }) } }),
    prisma.brandAsset.create({ data: { assetType: "image", source: "website", url: IMG.about, assetMetadata: JSON.stringify({ alt: "אופיר אסולין — תמונת פרופיל" }) } }),
    prisma.brandAsset.create({ data: { assetType: "image", source: "website", url: IMG.logo, assetMetadata: JSON.stringify({ type: "logo", alt: "לוגו — Ofir Assulin Design" }) } }),
  ]);
  console.log(`  ✅ ${assets.length} brand assets created`);

  // === INTERACTIONS (linked to leads) ===
  console.log("💬 Creating interactions...");
  const interactions = await Promise.all([
    prisma.interaction.create({ data: { leadId: leads[0].id, channel: "phone", interactionType: "call", content: "שיחת ייעוץ ראשונית, נקבעה פגישה", status: "completed", createdAt: daysAgo(27) } }),
    prisma.interaction.create({ data: { leadId: leads[0].id, channel: "email", interactionType: "followup", content: "נשלח סיכום פגישה עם הצעת מחיר", status: "sent", createdAt: daysAgo(25) } }),
    prisma.interaction.create({ data: { leadId: leads[1].id, channel: "whatsapp", interactionType: "message", content: "שלום אילן, תודה על הפנייה! נשמח לקבוע פגישת ייעוץ", status: "sent", createdAt: daysAgo(24) } }),
    prisma.interaction.create({ data: { leadId: leads[1].id, channel: "phone", interactionType: "call", content: "נקבע ייעוץ ליום ראשון", status: "completed", createdAt: daysAgo(22) } }),
    prisma.interaction.create({ data: { leadId: leads[2].id, channel: "email", interactionType: "intro", content: "נשלח מייל היכרות עם פורטפוליו פנטהאוזים", status: "sent", createdAt: daysAgo(21) } }),
    prisma.interaction.create({ data: { leadId: leads[3].id, channel: "whatsapp", interactionType: "message", content: "הודעת WhatsApp ראשונית", status: "sent", createdAt: daysAgo(19) } }),
    prisma.interaction.create({ data: { leadId: leads[4].id, channel: "phone", interactionType: "call", content: "שיחה טלפונית, מעוניינת בפגישה", status: "completed", createdAt: daysAgo(17) } }),
    prisma.interaction.create({ data: { leadId: leads[6].id, channel: "email", interactionType: "intro", content: "נשלח מייל עם דוגמאות וילות", status: "sent", createdAt: daysAgo(13) } }),
    prisma.interaction.create({ data: { leadId: leads[7].id, channel: "instagram", interactionType: "message", content: "תגובה להודעה באינסטגרם", status: "sent", createdAt: daysAgo(11) } }),
    prisma.interaction.create({ data: { leadId: leads[9].id, channel: "phone", interactionType: "call", content: "שיחת סגירה — לקוח חתם על הסכם!", status: "completed", createdAt: daysAgo(7) } }),
    prisma.interaction.create({ data: { leadId: leads[10].id, channel: "whatsapp", interactionType: "followup", content: "תזכורת לפגישת ייעוץ מחר", status: "sent", createdAt: daysAgo(6) } }),
    prisma.interaction.create({ data: { leadId: leads[13].id, channel: "email", interactionType: "intro", content: "מייל היכרות ראשוני", status: "sent", createdAt: daysAgo(2) } }),
  ]);
  console.log(`  ✅ ${interactions.length} interactions created`);

  // === CHAT MESSAGES (12) ===
  console.log("🗨️  Creating chat messages...");
  const messages = await Promise.all([
    prisma.chatMessage.create({ data: { role: "user", content: "מה המצב של הלידים השבוע?", createdAt: daysAgo(6) } }),
    prisma.chatMessage.create({ data: { role: "assistant", agentName: "orchestrator", content: "השבוע נכנסו 5 לידים חדשים. 2 מהם קיבלו ציון איכות גבוה (8+). הליד הטוב ביותר הוא נועה פרידמן — פרויקט וילה בהרצליה פיתוח עם תקציב של ₪1.5M.", createdAt: daysAgo(6) } }),
    prisma.chatMessage.create({ data: { role: "user", content: "מה הביצועים של קמפיין הוילות בגוגל?", createdAt: daysAgo(5) } }),
    prisma.chatMessage.create({ data: { role: "assistant", agentName: "campaignTracking", content: "קמפיין 'וילות יוקרה - חיפוש' מראה ביצועים טובים:\n• CTR: 2.5% (מעל הממוצע)\n• CPL: ₪231\n• 8 המרות החודש\n• עלות כוללת: ₪1,850\n\nהמלצה: להגדיל תקציב ב-15% ולהוסיף מילות מפתח Long-tail.", createdAt: daysAgo(5) } }),
    prisma.chatMessage.create({ data: { role: "user", content: "צור דף נחיתה לקמפיין הפנטהאוזים", createdAt: daysAgo(3) } }),
    prisma.chatMessage.create({ data: { role: "assistant", agentName: "landingPage", content: "יצרתי דף נחיתה בסגנון Story Flow לקמפיין פנטהאוזים. הדף כולל:\n• Hero section דארק עם תמונת רקע\n• סיפור בשני חלקים (הקשבה + חומרים)\n• פילוסופיית עיצוב\n• CTA ליצירת קשר\n\nהדף נשמר כהצעה וממתין לאישורך.", createdAt: daysAgo(3) } }),
    prisma.chatMessage.create({ data: { role: "user", content: "תן לי המלצות לשיפור שיעור ההמרה", createdAt: daysAgo(2) } }),
    prisma.chatMessage.create({ data: { role: "assistant", agentName: "strategy", content: "הנה 3 המלצות לשיפור שיעור ההמרה:\n\n1. **מהירות מענה** — לידים שנענים תוך שעה ממירים פי 3. כרגע זמן המענה הממוצע: 4 שעות.\n\n2. **דפי נחיתה ייעודיים** — קמפיין הפנטהאוזים עדיין מפנה לדף הבית. דף נחיתה ממוקד יעלה את ההמרה ב-40%.\n\n3. **WhatsApp Follow-up** — 70% מהלידים מגיבים ל-WhatsApp יותר ממייל. מומלץ להוסיף מעקב אוטומטי.", createdAt: daysAgo(2) } }),
    prisma.chatMessage.create({ data: { role: "user", content: "מה התקציב שנותר החודש?", createdAt: daysAgo(1) } }),
    prisma.chatMessage.create({ data: { role: "assistant", agentName: "budgetOptimizer", content: "סיכום תקציב חודשי:\n• סה\"כ תקציב: ₪500\n• הוצאה עד כה: ₪387\n• נותר: ₪113\n\nחלוקה:\n• Google Ads: ₪245 / ₪300 (82%)\n• Facebook/IG: ₪142 / ₪200 (71%)\n\nקצב ההוצאה תקין — צפוי לסיים את החודש בתקציב.", createdAt: daysAgo(1) } }),
    prisma.chatMessage.create({ data: { role: "user", content: "כמה לידים איכותיים יש לנו?", createdAt: daysAgo(0) } }),
    prisma.chatMessage.create({ data: { role: "assistant", agentName: "leadScoring", content: "יש לנו 7 לידים עם ציון איכות 7 ומעלה:\n• 3 לידים בציון 9+ (פנטהאוזים ווילות)\n• 2 לידים בציון 8 (שיפוצים בינוניים-גדולים)\n• 2 לידים בציון 7\n\nמתוכם:\n• 2 כבר הומרו ללקוחות ✅\n• 3 בשלב ייעוץ/פגישה\n• 2 בשלב מתאים/ממתינים", createdAt: daysAgo(0) } }),
  ]);
  console.log(`  ✅ ${messages.length} chat messages created`);

  // === AGENT MEMORIES (6) ===
  console.log("🧠 Creating agent memories...");
  const memories = await Promise.all([
    prisma.agentMemory.create({ data: { agentName: "strategy", memoryType: "semantic", key: "best_performing_channel", value: JSON.stringify({ channel: "google", cpl: 231, conversionRate: 2.5 }), context: "Based on last 30 days campaign data" } }),
    prisma.agentMemory.create({ data: { agentName: "leadScoring", memoryType: "episodic", key: "high_value_segment", value: JSON.stringify({ segment: "villa_new_build", avgScore: 9.2, avgBudget: 1200000 }), context: "Villa leads consistently score highest" } }),
    prisma.agentMemory.create({ data: { agentName: "content", memoryType: "semantic", key: "top_performing_cta", value: JSON.stringify({ cta: "לתיאום ייעוץ ראשוני חינם", ctr: 3.8 }), context: "CTA analysis from last 3 months" } }),
    prisma.agentMemory.create({ data: { agentName: "budgetOptimizer", memoryType: "episodic", key: "budget_allocation_feb", value: JSON.stringify({ google: 300, facebook: 200, recommendation: "shift 10% from IG to Google" }), context: "February budget review" } }),
    prisma.agentMemory.create({ data: { agentName: "landingPage", memoryType: "semantic", key: "best_lp_variant", value: JSON.stringify({ variant: "hero_gallery", conversionRate: 4.2, avgTimeOnPage: 95 }), context: "Landing page A/B test results" } }),
    prisma.agentMemory.create({ data: { agentName: "campaignTracking", memoryType: "episodic", key: "facebook_audience_insight", value: JSON.stringify({ topAge: "35-44", topLocation: "תל אביב", topInterest: "עיצוב פנים" }), context: "Facebook audience analysis" } }),
  ]);
  console.log(`  ✅ ${memories.length} agent memories created`);

  // === A/B TESTS (2) ===
  console.log("🧪 Creating A/B tests...");
  const test1 = await prisma.aBTest.create({ data: { name: "דף נחיתה וילות — Hero vs Split", status: "active", createdAt: daysAgo(14) } });
  await prisma.aBTestVariant.createMany({
    data: [
      { testId: test1.id, proposalId: proposals[7].id, variantName: "Hero Gallery", weight: 0.5, views: 342, conversions: 14 },
      { testId: test1.id, proposalId: proposals[8].id, variantName: "Split Layout", weight: 0.5, views: 338, conversions: 11 },
    ],
  });
  const test2 = await prisma.aBTest.create({ data: { name: "קופי מודעה — רגשי vs עובדתי", status: "completed", createdAt: daysAgo(30), endedAt: daysAgo(16) } });
  await prisma.aBTestVariant.createMany({
    data: [
      { testId: test2.id, proposalId: proposals[1].id, variantName: "רגשי", weight: 0.5, views: 1200, conversions: 38 },
      { testId: test2.id, proposalId: proposals[6].id, variantName: "עובדתי", weight: 0.5, views: 1180, conversions: 29 },
    ],
  });
  console.log(`  ✅ 2 A/B tests created`);

  // === TOKEN USAGE (last 30 days) ===
  console.log("📊 Creating token usage records...");
  const tokenRecords = [];
  for (let i = 0; i < 30; i++) {
    const day = daysAgo(i);
    const endpoints = ["chat", "lead-scoring", "content-gen", "strategy", "landing-page"];
    const ep = endpoints[Math.floor(Math.random() * endpoints.length)];
    const prompt = Math.floor(Math.random() * 2000) + 500;
    const completion = Math.floor(Math.random() * 1500) + 300;
    tokenRecords.push({
      date: day,
      model: "gpt-4o-mini",
      prompt,
      completion,
      total: prompt + completion,
      endpoint: ep,
    });
  }
  await prisma.tokenUsage.createMany({ data: tokenRecords });
  console.log(`  ✅ ${tokenRecords.length} token usage records created`);

  console.log("\n🎉 Seed complete! Database is populated with realistic data.\n");
}

main()
  .catch((e) => { console.error(e); process.exit(1); })
  .finally(() => prisma.$disconnect());
