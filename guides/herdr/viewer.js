const $ = selector => document.querySelector(selector);
const $$ = selector => [...document.querySelectorAll(selector)];
const config = JSON.parse($('#guide-config').textContent);
const stepOrder = config.steps.map(step => step.id);
const stepLabels = Object.fromEntries(config.steps.map(step => [step.id, step.label]));
const storageKey = 'gon-herdr-cli-guide-v1';
const defaults = { path: '/home/gon/dev/apps/gon-todo-practice', name: '개인 할 일 앱' };
let storageError = false;
let all = false;

function object(value) {
  return value !== null && typeof value === 'object' && !Array.isArray(value);
}

function absolutePath(value) {
  return typeof value === 'string' && value.startsWith('/') && !/[\r\n\0]/.test(value);
}

function readState() {
  let raw = {};
  try {
    const current = localStorage.getItem(storageKey);
    raw = JSON.parse(current || '{}');
  } catch {
    storageError = true;
  }
  if (!object(raw)) raw = {};
  const values = object(raw.values) ? raw.values : {};
  const state = {
    values: {
      path: absolutePath(values.path) ? values.path : defaults.path,
      name: typeof values.name === 'string' && values.name.trim() ? values.name : defaults.name,
    },
    scenario: raw.scenario === 'project' ? 'project' : 'exercise',
    active: stepOrder.includes(raw.active) ? raw.active : stepOrder[0],
    checks: object(raw.checks) ? raw.checks : {},
  };
  // 이전 버전의 체크는 당시 프로젝트의 예제 경로로 한 번 옮긴다.
  for (const [key, value] of Object.entries(raw)) {
    if (/^\d+-\d+$/.test(key) && value === true) {
      state.checks[JSON.stringify([state.values.path, 'exercise', key])] = true;
    }
  }
  return state;
}

let saved = readState();
let active = saved.active;
let applied = saved.values;
let scenario = saved.scenario;

function notify(text) {
  $('#toast').textContent = text;
  $('#toast').hidden = false;
  clearTimeout(window.toastTimer);
  window.toastTimer = setTimeout(() => { $('#toast').hidden = true; }, 5000);
}

function persist() {
  try {
    localStorage.setItem(storageKey, JSON.stringify(saved));
    return true;
  } catch {
    notify('이 브라우저에서는 기록을 저장할 수 없습니다. 안내·복사는 계속 사용할 수 있습니다.');
    return false;
  }
}

function values() {
  return {
    path: $('#project-path').value.trim(),
    name: $('#project-name').value.trim() || defaults.name,
  };
}

function checkKey(element) {
  const scope = element.closest('.planning-step') ? 'planning' : element.closest('.scenario').dataset.scenario;
  return JSON.stringify([applied.path, scope, element.dataset.check]);
}

function progress() {
  let checked = 0;
  let completed = 0;
  for (const number of stepOrder) {
    const checks = $$(`#step-${number} .scenario[data-scenario="${scenario}"] [data-check]`);
    checked += checks.filter(check => check.checked).length;
    const done = checks.length > 0 && checks.every(check => check.checked);
    $(`#status-${number}`).textContent = done ? '✓' : '';
    if (done) completed++;
  }
  $('#progress').textContent = `확인한 항목 ${checked}개 · 단계 ${completed}개 · 선택하지 않은 단계는 체크 불필요`;
}

function currentPrompt() {
  return $(`#step-${active} .scenario[data-scenario="${scenario}"] pre[data-primary]`);
}

function show(number, scroll = false, updateHash = true) {
  active = stepOrder.includes(number) ? number : stepOrder[0];
  $$('.step').forEach(element => { element.hidden = !all && Number(element.dataset.step) !== active; });
  $$('.node').forEach(element => {
    const yes = Number(element.dataset.goto) === active;
    element.classList.toggle('active', yes);
    if (yes) element.setAttribute('aria-current', 'step');
    else element.removeAttribute('aria-current');
  });
  $('#current-label').textContent = all ? '전체 단계 펼침' : `${stepLabels[active]} 단계 보는 중`;
  $('#prev').disabled = active === stepOrder[0];
  $('#next').disabled = active === stepOrder.at(-1);
  $('#next').hidden = config.choiceSteps.includes(active);
  $('#copy-current').disabled = !currentPrompt();
  saved.active = active;
  if (updateHash) history.replaceState(null, '', `#step-${active}`);
  persist();
  if (scroll) {
    const heading = $(`#step-${active} .scenario[data-scenario="${scenario}"] h2`);
    heading.focus({ preventScroll: true });
    $(`#step-${active}`).scrollIntoView({ block: 'start' });
  }
}

function apply(message = false) {
  const nextValues = values();
  if (!absolutePath(nextValues.path)) {
    $('#project-path').setAttribute('aria-invalid', 'true');
    notify('폴더는 /home/내계정/...처럼 /로 시작하는 실제 절대경로를 입력하세요. ~와 상대경로는 사용할 수 없습니다.');
    $('#project-path').focus();
    return false;
  }
  $('#project-path').removeAttribute('aria-invalid');
  applied = nextValues;
  scenario = $('#scenario').value === 'project' ? 'project' : 'exercise';
  $$('[data-template]').forEach(element => {
    const shellPath = "'" + applied.path.replaceAll("'", "'\\''") + "'";
    element.textContent = element.dataset.template.replaceAll('{{shell_path}}', shellPath)
      .replaceAll('{{path}}', applied.path).replaceAll('{{name}}', applied.name);
  });
  $$('.scenario').forEach(element => { element.hidden = element.dataset.scenario !== scenario; });
  $$('[data-check]').forEach(element => { element.checked = saved.checks[checkKey(element)] === true; });
  $$('.node small[data-project]').forEach(element => { element.textContent = element.dataset[scenario]; });
  saved.values = applied;
  saved.scenario = scenario;
  $('#print-context').textContent = `선택 경로: ${scenario === 'project' ? '내 기획 문서' : '할 일 앱 예제'} · 앱: ${applied.name} · 폴더: ${applied.path}`;
  progress();
  $('#copy-current').disabled = !currentPrompt();
  const stored = persist();
  if (message && stored) notify('선택 경로·앱 이름·폴더를 안내와 요청문에 반영했습니다.');
  return true;
}

async function copy(pre) {
  if (!pre) return;
  try {
    await navigator.clipboard.writeText(pre.textContent);
    const kind = pre.closest('.prompt').dataset.kind;
    notify(kind === 'shell' ? '쉘 명령을 복사했습니다. Codex가 실행되지 않은 분할 터미널에 붙여 넣으세요.'
      : '복사했습니다. 표시된 역할의 Codex 입력칸에 붙여 넣으세요.');
  } catch {
    const range = document.createRange();
    range.selectNodeContents(pre);
    const selection = getSelection();
    selection.removeAllRanges();
    selection.addRange(range);
    pre.focus();
    notify('자동 복사가 차단되어 내용을 선택했습니다. Ctrl+C로 복사하세요.');
  }
}

function openExtra(id) {
  const target = document.getElementById(id);
  if (target?.tagName !== 'DETAILS') return;
  target.open = true;
  history.replaceState(null, '', `#${id}`);
  target.querySelector('summary').focus({ preventScroll: true });
  target.scrollIntoView({ block: 'start' });
}

$$('[data-check]').forEach(element => element.addEventListener('change', () => {
  saved.checks[checkKey(element)] = element.checked;
  persist();
  progress();
}));
$$('[data-goto]').forEach(link => link.addEventListener('click', event => {
  event.preventDefault();
  show(Number(link.dataset.goto), true);
}));
$$('[data-extra], .entrylinks a[href^="#"]').forEach(link => link.addEventListener('click', event => {
  event.preventDefault();
  openExtra(link.dataset.extra || link.getAttribute('href').slice(1));
}));
$$('[data-project-start], [data-project-step]').forEach(button => button.addEventListener('click', event => {
  event.preventDefault();
  $('#scenario').value = 'project';
  if (!apply()) return;
  show(button.dataset.projectStep ? Number(button.dataset.projectStep) : 1, true);
}));
$$('.copy').forEach(button => button.addEventListener('click', () => {
  if (!apply()) return;
  copy(button.closest('.prompt').querySelector('pre'));
}));
$('#copy-current').addEventListener('click', () => { if (apply()) copy(currentPrompt()); });
$('#apply').addEventListener('click', () => apply(true));
$('#scenario').addEventListener('change', () => { if (apply(true)) show(active); });
$('#prev').addEventListener('click', () => show(stepOrder[stepOrder.indexOf(active) - 1], true));
$('#next').addEventListener('click', () => show(stepOrder[stepOrder.indexOf(active) + 1], true));
$('#toggle-all').addEventListener('click', () => {
  all = !all;
  $('#toggle-all').textContent = all ? '한 단계씩 보기' : '전체 단계 펼치기';
  $('#toggle-all').setAttribute('aria-pressed', String(all));
  show(active);
});
$('#print').addEventListener('click', () => { if (apply()) window.print(); });
$$('[data-workbench]').forEach(button => button.addEventListener('click', () => {
  $$('[data-workbench]').forEach(item => item.setAttribute('aria-pressed', String(item === button)));
  $$('[data-workbench-view]').forEach(view => { view.hidden = view.dataset.workbenchView !== button.dataset.workbench; });
}));
let oldDetails = [];
addEventListener('beforeprint', () => {
  oldDetails = $$('details').map(detail => detail.open);
  $$('details').forEach(detail => { detail.open = true; });
});
addEventListener('afterprint', () => {
  $$('details').forEach((detail, index) => { detail.open = oldDetails[index]; });
});
$('#reset').addEventListener('click', () => {
  if (!confirm('현재 프로젝트의 공통 기획 체크와 선택한 개발 경로의 체크를 지울까요? 프로젝트 파일에는 영향을 주지 않습니다.')) return;
  $$(`.scenario[data-scenario="${scenario}"] [data-check]`).forEach(element => {
    element.checked = false;
    delete saved.checks[checkKey(element)];
  });
  persist();
  progress();
});

$('#project-path').value = saved.values.path;
$('#project-name').value = saved.values.name;
$('#scenario').value = saved.scenario;
apply();
function restoreLocation() {
  const match = location.hash.match(/^#step-(\d+)$/);
  show(match ? Number(match[1]) : saved.active, false, false);
  if (location.hash && !match) {
    let id;
    try { id = decodeURIComponent(location.hash.slice(1)); } catch { return; }
    const target = document.getElementById(id);
    if (target?.tagName === 'DETAILS') target.open = true;
  }
}
restoreLocation();
addEventListener('hashchange', restoreLocation);
if (storageError) notify('이전 저장 기록을 읽지 못해 기본값으로 열었습니다. 안내·복사는 계속 사용할 수 있습니다.');
