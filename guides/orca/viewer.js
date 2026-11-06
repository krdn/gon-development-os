'use strict';
(() => {
  const key = 'gon-orca-guide-v1';
  const fields = ['project-name', 'project-path', 'repo-name'];
  let settings = {};
  let checks = {};
  let appliedPath = '';
  let toastTimer;
  const status = document.querySelector('#config-status');
  const toast = (message) => {
    const node = document.querySelector('#toast');
    node.textContent = message;
    node.classList.add('visible');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => node.classList.remove('visible'), 3500);
  };
  const quote = (value) => "'" + value.replaceAll("'", "'\\''") + "'";
  const getSettings = () => Object.fromEntries(fields.map(id => [id, document.getElementById(id).value.trim()]));
  const validate = (value) => {
    if (!value['project-name'] || /[\r\n\x00-\x1f]/.test(value['project-name'])) return '프로젝트명을 한 줄로 입력하세요.';
    const path = value['project-path'];
    if (!path.startsWith('/') || path === '/' || /[\r\n\x00-\x1f]/.test(path)) return '프로젝트 폴더는 /로 시작하는 실제 절대 경로를 입력하세요.';
    const repo = value['repo-name'];
    if (repo && !/^[A-Za-z0-9][A-Za-z0-9-]*\/[A-Za-z0-9_.-]+$/.test(repo)) return 'GitHub 이름은 소유자/저장소 형태로 입력하세요.';
    return '';
  };
  const save = () => {
    try { localStorage.setItem(key, JSON.stringify({ settings, checks })); }
    catch { status.textContent += ' 이 브라우저에서는 저장이 제한되어 현재 화면에만 반영됩니다.'; }
  };
  const updateProgress = () => {
    const all = [...document.querySelectorAll('[data-check]')];
    document.querySelector('#progress').textContent = `확인 ${all.filter(n => n.checked).length} / ${all.length}`;
  };
  const restoreChecks = () => {
    const projectChecks = checks[appliedPath] || {};
    document.querySelectorAll('[data-check]').forEach(n => { n.checked = projectChecks[n.dataset.check] === true; });
    updateProgress();
  };
  const apply = (persist = true) => {
    const value = getSettings();
    const error = validate(value);
    if (error) {
      status.textContent = error;
      status.classList.add('error');
      return false;
    }
    settings = value;
    appliedPath = value['project-path'];
    const data = {
      name: value['project-name'], path: appliedPath,
      shell_path: quote(appliedPath), selector_path: quote('path:' + appliedPath),
      repo: value['repo-name'] || '[GitHub 소유자/저장소 입력 필요]',
    };
    document.querySelectorAll('[data-template]').forEach(node => {
      node.textContent = node.dataset.template.replace(/\{\{(\w+)\}\}/g, (_, name) => data[name] ?? `[${name} 확인 필요]`);
    });
    status.classList.remove('error');
    status.textContent = '요청문에 반영했습니다. GitHub 이름이 없는 요청은 G1 전에 입력하세요.';
    restoreChecks();
    if (persist) save();
    return true;
  };
  try {
    const stored = JSON.parse(localStorage.getItem(key) || '{}');
    if (stored && typeof stored === 'object') {
      checks = stored.checks && typeof stored.checks === 'object' ? stored.checks : {};
      if (stored.settings && !validate(stored.settings)) {
        fields.forEach(id => { document.getElementById(id).value = stored.settings[id] || ''; });
      }
    }
  } catch { /* 저장값이 손상되면 화면의 기본값으로 시작한다. */ }
  apply(false);
  document.querySelector('#config').addEventListener('submit', event => { event.preventDefault(); apply(); });
  document.querySelectorAll('[data-check]').forEach(node => node.addEventListener('change', () => {
    checks[appliedPath] = checks[appliedPath] || {};
    checks[appliedPath][node.dataset.check] = node.checked;
    save(); updateProgress();
  }));
  const copyText = async (text) => {
    if (navigator.clipboard?.writeText) {
      try { await navigator.clipboard.writeText(text); return; } catch { /* 로컬 파일은 대체 복사를 시도한다. */ }
    }
    const area = document.createElement('textarea');
    area.value = text; area.style.position = 'fixed'; area.style.opacity = '0';
    document.body.append(area); area.select();
    const copied = document.execCommand('copy');
    area.remove();
    if (!copied) throw new Error('자동 복사를 사용할 수 없습니다.');
  };
  document.querySelectorAll('.copy').forEach(button => button.addEventListener('click', async () => {
    if (!apply()) { toast('프로젝트 설정의 오류를 먼저 고쳐 주세요.'); return; }
    const text = button.closest('.copybox').querySelector('pre').textContent;
    if (text.includes('[GitHub 소유자/저장소 입력 필요]')) { toast('위에서 GitHub 소유자/저장소를 입력하고 반영하세요.'); return; }
    try { await copyText(text); toast('복사했습니다. 표시된 입력 위치에 붙여 넣으세요.'); }
    catch { toast('복사하지 못했습니다. 요청문을 직접 선택해 복사하세요.'); }
  }));
  const revealHash = () => {
    if (!location.hash.startsWith('#step-')) return;
    const node = document.getElementById(location.hash.slice(1));
    if (node?.matches('details.step')) { node.open = true; node.scrollIntoView({ block: 'start' }); }
  };
  document.querySelectorAll('a[href^="#step-"]').forEach(link => link.addEventListener('click', () => {
    const node = document.querySelector(link.getAttribute('href'));
    if (node) node.open = true;
    if (location.hash === link.getAttribute('href')) revealHash();
  }));
  window.addEventListener('hashchange', revealHash);
  revealHash();
  document.querySelector('#expand-all').addEventListener('click', event => {
    const nodes = [...document.querySelectorAll('details.step')];
    const shouldOpen = nodes.some(n => !n.open);
    nodes.forEach(n => { n.open = shouldOpen; });
    event.currentTarget.textContent = shouldOpen ? '모든 단계 접기' : '모든 단계 펼치기';
  });
  let beforePrint;
  window.addEventListener('beforeprint', () => {
    beforePrint = [...document.querySelectorAll('details')].map(n => [n, n.open]);
    document.querySelectorAll('details').forEach(n => { n.open = true; });
  });
  window.addEventListener('afterprint', () => { beforePrint?.forEach(([n, open]) => { n.open = open; }); });
  document.querySelector('#print').addEventListener('click', () => { if (apply()) window.print(); });
})();
