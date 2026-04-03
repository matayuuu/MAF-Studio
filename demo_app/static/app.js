/* ── Utility helpers ──────────────────────────────────────────────────────── */
const $ = (sel, ctx = document) => ctx.querySelector(sel);
const $$ = (sel, ctx = document) => [...ctx.querySelectorAll(sel)];
const fmt = (n) => Number(n).toLocaleString('ja-JP');

/* ── Date ─────────────────────────────────────────────────────────────────── */
const today = new Date();
$('#todayDate').textContent =
  today.toLocaleDateString('ja-JP', { year: 'numeric', month: 'long', day: 'numeric', weekday: 'short' });

/* ── Navigation ───────────────────────────────────────────────────────────── */
const TITLES = {
  dashboard: 'ダッシュボード',
  customers: '顧客一覧',
  products: '商品一覧',
  activities: '活動履歴',
  'customer-detail': '顧客詳細',
};

function showView(name) {
  $$('.view').forEach(v => v.classList.remove('active'));
  $$('.nav-item').forEach(n => n.classList.remove('active'));
  const view = $(`#view-${name}`);
  if (view) view.classList.add('active');
  const navBtn = $(`.nav-item[data-view="${name}"]`);
  if (navBtn) navBtn.classList.add('active');
  $('#pageTitle').textContent = TITLES[name] || name;
  // close sidebar on mobile
  if (window.innerWidth <= 900) $('#sidebar').classList.remove('open');
}

$$('.nav-item').forEach(btn => {
  btn.addEventListener('click', () => {
    const view = btn.dataset.view;
    showView(view);
    if (view === 'customers') loadCustomers();
    if (view === 'products') loadProducts();
    if (view === 'activities') loadActivities();
  });
});

$('#menuToggle').addEventListener('click', () => {
  $('#sidebar').classList.toggle('open');
});

$('#backBtn').addEventListener('click', () => {
  showView('customers');
  loadCustomers();
});

/* ── API helper ───────────────────────────────────────────────────────────── */
async function api(path) {
  const res = await fetch(path);
  if (!res.ok) throw new Error(`API ${path} → ${res.status}`);
  return res.json();
}

/* ══════════════════════════════════════════════════════════════════════════ */
/* DASHBOARD                                                                  */
/* ══════════════════════════════════════════════════════════════════════════ */
let productChartInst      = null;
let contractStatusChartInst = null;

async function loadDashboard() {
  const d = await api('/api/dashboard');

  // KPI cards
  const kpis = [
    { label: '総顧客数', value: d.total_customers, unit: '名', cls: 'blue' },
    { label: '有効契約数', value: d.active_contracts, unit: '件', cls: 'green' },
    { label: '無効契約数', value: d.inactive_contracts, unit: '件', cls: 'red' },
    { label: '月間保険料合計', value: fmt(d.total_monthly_premium), unit: '円 / 月', cls: 'blue' },
  ];
  $('#kpiGrid').innerHTML = kpis.map(k => `
    <div class="kpi-card ${k.cls}">
      <div class="kpi-label">${k.label}</div>
      <div class="kpi-value">${k.value}</div>
      <div class="kpi-unit">${k.unit}</div>
    </div>
  `).join('');

  // Product distribution chart
  const prodLabels  = Object.keys(d.product_distribution);
  const prodValues  = Object.values(d.product_distribution);
  const palette = ['#3b7cf4','#2dd4a0','#8b5cf6','#f46060','#f5a623'];

  if (productChartInst) productChartInst.destroy();
  productChartInst = new Chart($('#productChart'), {
    type: 'bar',
    data: {
      labels: prodLabels,
      datasets: [{
        data: prodValues,
        backgroundColor: palette,
        borderRadius: 6,
        borderSkipped: false,
      }],
    },
    options: {
      plugins: { legend: { display: false } },
      scales: {
        x: { ticks: { color: '#8b92a8', font: { size: 11 } }, grid: { color: '#252a38' } },
        y: { ticks: { color: '#8b92a8', font: { size: 11 }, stepSize: 1 }, grid: { color: '#252a38' } },
      },
    },
  });

  // Contract status donut chart
  if (contractStatusChartInst) contractStatusChartInst.destroy();
  contractStatusChartInst = new Chart($('#contractStatusChart'), {
    type: 'doughnut',
    data: {
      labels: ['有効', '無効'],
      datasets: [{
        data: [d.active_contracts, d.inactive_contracts],
        backgroundColor: ['#2dd4a0', '#f46060'],
        hoverOffset: 6,
        borderWidth: 2,
        borderColor: '#13161e',
      }],
    },
    options: {
      plugins: { legend: { labels: { color: '#8b92a8', font: { size: 12 } } } },
      cutout: '68%',
    },
  });

  // Recent activities
  const typeCls = { '訪問': 'act-訪問', '電話': 'act-電話', 'メール': 'act-メール', '初回面談': 'act-初回面談' };
  $('#recentActivities').innerHTML = d.recent_activities.map(a => `
    <div class="activity-row">
      <span class="act-type-badge ${typeCls[a.activity_type] || ''}">${a.activity_type}</span>
      <div class="act-body">
        <div class="act-subject">${a.subject}</div>
        <div class="act-meta">${a.activity_date} · ${a.agent_name} · 顧客ID: ${a.customer_id}</div>
      </div>
    </div>
  `).join('');
}

/* ══════════════════════════════════════════════════════════════════════════ */
/* CUSTOMERS                                                                  */
/* ══════════════════════════════════════════════════════════════════════════ */
let currentCustomers = [];

async function loadCustomers(search = '') {
  let url = '/api/customers';
  if (search) url += '?search=' + encodeURIComponent(search);

  const customers = await api(url);
  currentCustomers = customers;
  renderCustomerTable(customers);
}

function renderCustomerTable(customers) {
  $('#customerTbody').innerHTML = customers.length
    ? customers.map(c => `
      <tr data-id="${c.customer_id}">
        <td>${c.customer_id}</td>
        <td><strong>${c.last_name} ${c.first_name}</strong></td>
        <td>${c.age}</td>
        <td>${c.prefecture}</td>
        <td>${c.occupation || '—'}</td>
        <td>${c.annual_income > 0 ? fmt(c.annual_income) + ' 円' : '—'}</td>
        <td>${c.assigned_agent}</td>
        <td>${c.last_contact_date}</td>
      </tr>
    `).join('')
    : '<tr><td colspan="8" class="empty">該当する顧客がいません</td></tr>';

  $$('#customerTbody tr[data-id]').forEach(tr => {
    tr.addEventListener('click', () => openCustomerDetail(tr.dataset.id));
  });
}

// Search in customers
let searchTimer;
$('#customerSearch').addEventListener('input', e => {
  clearTimeout(searchTimer);
  searchTimer = setTimeout(() => {
    loadCustomers(e.target.value.trim());
  }, 200);
});

/* ── Customer Detail ────────────────────────────────────────────────────── */
async function openCustomerDetail(customerId) {
  showView('customer-detail');
  $('#customerDetailContent').innerHTML = '<div class="loading">読み込み中…</div>';

  const data = await api(`/api/customers/${customerId}`);
  const { customer: c, contracts, activities } = data;

  const contractsHTML = contracts.length
    ? contracts.map(ct => `
      <div class="contract-card">
        <div class="cc-head">
          <div class="cc-product">${ct.product?.product_name || ct.product_id}</div>
          <div class="cc-premium">¥${fmt(ct.monthly_premium)} / 月</div>
        </div>
        <div class="cc-meta">
          ${ct.product?.product_category || ''} ·
          契約日: ${ct.contract_date} ·
          受取人: ${ct.beneficiary_name}（${ct.beneficiary_relation}）·
          <span class="badge badge-${ct.contract_status === '有効' ? 'valid' : 'dormant'}">${ct.contract_status}</span>
        </div>
      </div>
    `).join('')
    : '<p class="empty">契約なし</p>';

  const typeCls = { '訪問': 'act-訪問', '電話': 'act-電話', 'メール': 'act-メール', '初回面談': 'act-初回面談' };
  const activitiesHTML = activities.length
    ? activities.map(a => `
      <div class="activity-row">
        <span class="act-type-badge ${typeCls[a.activity_type] || ''}">${a.activity_type}</span>
        <div class="act-body">
          <div class="act-subject">${a.subject}</div>
          <div class="act-meta">${a.activity_date} · ${a.agent_name}</div>
          <div style="font-size:12px;color:var(--text2);margin-top:4px">${a.content}</div>
          ${a.next_action ? `<div style="font-size:11px;color:var(--gold);margin-top:4px">→ ${a.next_action}（${a.next_action_date}）</div>` : ''}
        </div>
      </div>
    `).join('')
    : '<p class="empty">活動履歴なし</p>';

  $('#customerDetailContent').innerHTML = `
    <div class="detail-header">
      <div class="detail-avatar">${c.last_name.charAt(0)}</div>
      <div>
        <div class="detail-name">${c.last_name} ${c.first_name}</div>
        <div class="detail-kana">${c.last_name_kana} ${c.first_name_kana}</div>
        <div class="detail-tags">
          <span class="badge" style="background:rgba(59,124,244,.15);color:var(--accent2)">${c.gender}</span>
          <span class="badge" style="background:rgba(139,92,246,.15);color:#a78bfa">${c.age}歳</span>
        </div>
      </div>
    </div>

    <div class="detail-grid">
      <div class="card">
        <div class="card-header">基本情報</div>
        <ul class="detail-info-list">
          <li><span class="dil-key">生年月日</span><span class="dil-val">${c.birth_date}</span></li>
          <li><span class="dil-key">電話</span><span class="dil-val">${c.phone}</span></li>
          <li><span class="dil-key">メール</span><span class="dil-val">${c.email}</span></li>
          <li><span class="dil-key">住所</span><span class="dil-val">${c.prefecture}${c.city}${c.address}</span></li>
          <li><span class="dil-key">職業</span><span class="dil-val">${c.occupation || '—'}</span></li>
          <li><span class="dil-key">年収</span><span class="dil-val">${c.annual_income > 0 ? '¥' + fmt(c.annual_income) : '—'}</span></li>
          <li><span class="dil-key">担当者</span><span class="dil-val">${c.assigned_agent}</span></li>
          <li><span class="dil-key">最終接触</span><span class="dil-val">${c.last_contact_date}</span></li>
        </ul>
        ${c.notes ? `<div style="margin-top:12px;padding:10px;background:var(--bg3);border-radius:6px;font-size:12px;color:var(--text2)">${c.notes}</div>` : ''}
      </div>

      <div class="card">
        <div class="card-header">契約一覧（${contracts.length}件）</div>
        ${contractsHTML}
      </div>
    </div>

    <div class="card">
      <div class="card-header">活動履歴（${activities.length}件）</div>
      ${activitiesHTML}
    </div>
  `;
}

/* ══════════════════════════════════════════════════════════════════════════ */
/* PRODUCTS                                                                   */
/* ══════════════════════════════════════════════════════════════════════════ */
async function loadProducts() {
  const products = await api('/api/products');

  $('#productGrid').innerHTML = products.map(p => {
    const features = p.features ? p.features.split('/') : [];
    const cat = p.product_category;
    return `
      <div class="product-card cat-${cat}">
        <div class="pc-cat">${cat}</div>
        <div class="pc-name">${p.product_name}</div>
        <div class="pc-desc">${p.description}</div>
        <div class="pc-range">月額保険料: <span>¥${fmt(p.monthly_premium)} 円</span></div>
        ${Number(p.coverage_amount) > 0 ? `<div class="pc-range">保障額: <span>¥${fmt(p.coverage_amount)} 円</span></div>` : ''}
        <div class="pc-range">対象年齢: <span>${p.target_age_min}〜${p.target_age_max}歳</span></div>
        <div class="pc-features">
          ${features.map(f => `<span class="pc-feat">${f.trim()}</span>`).join('')}
        </div>
      </div>
    `;
  }).join('');
}

/* ══════════════════════════════════════════════════════════════════════════ */
/* ACTIVITIES                                                                 */
/* ══════════════════════════════════════════════════════════════════════════ */
async function loadActivities() {
  const activities = await api('/api/activities');
  const typeCls = { '訪問': 'act-訪問', '電話': 'act-電話', 'メール': 'act-メール', '初回面談': 'act-初回面談' };

  $('#activityTbody').innerHTML = activities.map(a => `
    <tr>
      <td>${a.activity_date}</td>
      <td>${a.customer_id}</td>
      <td><span class="act-type-badge ${typeCls[a.activity_type] || ''}">${a.activity_type}</span></td>
      <td>${a.subject}</td>
      <td>${a.agent_name}</td>
      <td>${a.outcome}</td>
      <td class="next-action-cell">${a.next_action ? a.next_action + '<br>' + a.next_action_date : '—'}</td>
    </tr>
  `).join('');
}

/* ══════════════════════════════════════════════════════════════════════════ */
/* GLOBAL SEARCH                                                              */
/* ══════════════════════════════════════════════════════════════════════════ */
let allCustomers = [];

async function initSearch() {
  allCustomers = await api('/api/customers');
}

const searchInput = $('#globalSearch');
const searchDropdown = $('#searchDropdown');

searchInput.addEventListener('input', () => {
  const q = searchInput.value.trim().toLowerCase();
  if (!q) { searchDropdown.classList.remove('open'); return; }

  const results = allCustomers.filter(c =>
    (c.last_name + c.first_name).includes(q) ||
    (c.last_name_kana + c.first_name_kana).toLowerCase().includes(q) ||
    c.email.toLowerCase().includes(q)
  ).slice(0, 8);

  if (!results.length) { searchDropdown.classList.remove('open'); return; }

  searchDropdown.innerHTML = results.map(c => `
    <div class="search-result-item" data-id="${c.customer_id}">
      <div>
        <div class="sri-name">${c.last_name} ${c.first_name}</div>
        <div class="sri-meta">${c.customer_id} · ${c.status} · ${c.prefecture}</div>
      </div>
    </div>
  `).join('');
  searchDropdown.classList.add('open');

  $$('.search-result-item').forEach(item => {
    item.addEventListener('click', () => {
      openCustomerDetail(item.dataset.id);
      searchInput.value = '';
      searchDropdown.classList.remove('open');
    });
  });
});

document.addEventListener('click', e => {
  if (!searchInput.contains(e.target) && !searchDropdown.contains(e.target)) {
    searchDropdown.classList.remove('open');
  }
});

/* ══════════════════════════════════════════════════════════════════════════ */
/* INIT                                                                       */
/* ══════════════════════════════════════════════════════════════════════════ */
(async () => {
  await Promise.all([loadDashboard(), initSearch()]);
})();
