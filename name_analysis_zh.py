<!-- === START CHILD WIDGET (ZH + BASE64 CHART CAPTURE) === -->

<!-- 1) Styles -->
<style>
  @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
  #hiddenForm { opacity: 0; transform: translateY(20px); transition: opacity .5s, transform .5s; display: none; }
  #hiddenForm.show { display: block; opacity: 1; transform: translateY(0); }
  #resultContainer { opacity: 0; transition: opacity .5s; margin-top: 20px; display: none; }
  #resultContainer.show { display: block; opacity: 1; }
  .dob-group { display: flex; gap: 10px; }
  .dob-group select { flex: 1; }
</style>

<!-- 2) Next Button -->
<button id="simulateMessageButton" style="padding:10px 20px;background:#5E9CA0;color:#fff;border:none;border-radius:8px;cursor:pointer;display:none;">下一步</button>

<!-- 3) Hidden Form -->
<div id="hiddenForm">
  <form id="userDetailsForm" method="POST" style="margin-top:20px;display:flex;flex-direction:column;gap:20px;pointer-events:none;opacity:0.3;">
    <label>👤 英文姓名</label>
    <input type="text" id="name" required disabled>

    <label>🈶 中文姓名</label>
    <input type="text" id="chinese_name" disabled>

    <label>⚧️ 性别</label>
    <select id="gender" required disabled>
      <option value="">请选择</option>
      <option>男</option>
      <option>女</option>
    </select>

    <label>🎂 出生日期</label>
    <div class="dob-group">
      <select id="dob_day" required disabled><option value="">日</option></select>
      <select id="dob_month" required disabled><option value="">月</option>
        <option>一月</option><option>二月</option><option>三月</option><option>四月</option><option>五月</option><option>六月</option>
        <option>七月</option><option>八月</option><option>九月</option><option>十月</option><option>十一月</option><option>十二月</option>
      </select>
      <select id="dob_year" required disabled><option value="">年</option></select>
    </div>

    <label>📞 家长电话</label>
    <input type="tel" id="phone" required pattern="[0-9]+" disabled>

    <label>📧 家长邮箱</label>
    <input type="email" id="email" required disabled>

    <label>🌍 国家</label>
    <select id="country" required disabled>
      <option value="">请选择</option><option>新加坡</option><option>马来西亚</option><option>台湾</option>
    </select>

    <label>💬 推荐人（选填）</label>
    <input type="text" id="referrer" disabled>

    <label><input type="checkbox" id="pdpaCheckbox" style="margin-right:10px;">我同意授权分析（PDPA）</label>
    <button type="submit" id="submitButton" disabled style="padding:12px;background:#5E9CA0;color:#fff;border:none;border-radius:6px;cursor:pointer;">🚀 提交</button>
  </form>
</div>

<!-- 4) Spinner -->
<div id="loadingMessage" style="display:none;text-align:center;margin-top:30px;">
  <div style="width:60px;height:60px;border:6px solid #ccc;border-top:6px solid #5E9CA0;border-radius:50%;animation:spin 1s linear infinite;margin:0 auto;"></div>
  <p style="color:#5E9CA0;margin-top:10px;">🔄 正在分析，请稍候…</p>
</div>

<!-- 5) Result Container -->
<div id="resultContainer">
  <h4 style="text-align:center;font-size:28px;font-weight:bold;color:#5E9CA0;">🎉 全球学习洞察</h4>
  <div id="charts" style="max-width:700px;margin:0 auto 30px;"></div>
  <div id="resultContent" style="white-space:pre-wrap;"></div>
</div>

<!-- 6) Chart.js -->
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

<!-- 7) JavaScript Logic -->
<script>
window.addEventListener('load', () => {
  const simulateBtn = document.getElementById('simulateMessageButton');
  const hiddenForm = document.getElementById('hiddenForm');
  const pdpa = document.getElementById('pdpaCheckbox');
  const form = document.getElementById('userDetailsForm');
  const spinner = document.getElementById('loadingMessage');
  const resultDiv = document.getElementById('resultContainer');
  const chartsDiv = document.getElementById('charts');
  const resultContent = document.getElementById('resultContent');

  pdpa.checked = false;
  simulateBtn.style.display = 'none';
  setTimeout(() => simulateBtn.style.display = 'inline-block', 5000);

  simulateBtn.addEventListener('click', () => {
    hiddenForm.style.display = 'block';
    requestAnimationFrame(() => hiddenForm.classList.add('show'));
  });

  pdpa.addEventListener('change', () => {
    const fields = form.querySelectorAll('input, select, button[type="submit"]');
    fields.forEach(f => f.disabled = !pdpa.checked);
    form.style.opacity = pdpa.checked ? '1' : '0.3';
    form.style.pointerEvents = pdpa.checked ? 'auto' : 'none';
  });

  for (let d = 1; d <= 31; d++) document.getElementById('dob_day').innerHTML += `<option>${d}</option>`;
  const months = ["一月", "二月", "三月", "四月", "五月", "六月", "七月", "八月", "九月", "十月", "十一月", "十二月"];
  months.forEach(m => document.getElementById('dob_month').innerHTML += `<option>${m}</option>`);
  const yearSel = document.getElementById('dob_year');
  const thisYear = new Date().getFullYear();
  for (let y = thisYear - 21; y <= thisYear - 3; y++) yearSel.innerHTML += `<option>${y}</option>`;

  form.addEventListener('submit', async e => {
    e.preventDefault();
    spinner.style.display = 'block';
    resultDiv.style.display = 'none';
    chartsDiv.innerHTML = '';
    resultContent.innerHTML = '';

    const get = id => document.getElementById(id).value;

    const payload = {
      name:         get('name'),
      chinese_name: get('chinese_name'),
      gender:       get('gender'),
      dob_day:      get('dob_day'),
      dob_month:    get('dob_month'),
      dob_year:     get('dob_year'),
      phone:        get('phone'),
      email:        get('email'),
      country:      get('country'),
      referrer:     get('referrer'),
      chart_images: []
    };

    try {
      const res = await fetch("https://name-analysis-zh.onrender.com/analyze_name", {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      const data = await res.json();
      spinner.style.display = 'none';
      resultDiv.style.display = 'block';
      requestAnimationFrame(() => resultDiv.classList.add('show'));

      if (data.error) {
        resultContent.innerText = '⚠️ ' + data.error;
        return;
      }

      data.metrics.forEach((m, idx) => {
        const c = document.createElement('canvas');
        chartsDiv.appendChild(c);
        const ctx = c.getContext('2d');
        const palette = ['#5E9CA0','#FF9F40','#9966FF'];
        const grads = m.labels.map((_, i) => {
          const grad = ctx.createLinearGradient(0, 0, 0, c.height);
          grad.addColorStop(0, palette[i % palette.length] + 'DD');
          grad.addColorStop(1, palette[i % palette.length] + '44');
          return grad;
        });

        new Chart(ctx, {
          type: 'bar',
          data: {
            labels: m.labels,
            datasets: [{
              label: m.title,
              data: m.values,
              backgroundColor: grads,
              borderColor: palette,
              borderWidth: 2,
              borderRadius: 6,
              barPercentage: 0.6,
              categoryPercentage: 0.7
            }]
          },
          options: {
            indexAxis: m.title === '学习投入' ? 'y' : 'x',
            animation: { duration: 800, easing: 'easeOutQuart', delay: ctx => ctx.dataIndex * 100 + idx * 200 },
            scales: { x: { beginAtZero: true, max: 100 }, y: { grid: { display: false } } },
            plugins: {
              title: { display: true, text: m.title, font: { size: 18 }, padding: { top: 10, bottom: 30 } },
              legend: { display: false }
            }
          }
        });
      });

      resultContent.innerHTML = data.analysis;
    } catch (err) {
      console.error(err);
      spinner.style.display = 'none';
      resultDiv.style.display = 'block';
      resultContent.innerText = '⚠️ 网络错误或服务器异常';
    }
  });
});
</script>

<!-- === END CHILD WIDGET === -->
