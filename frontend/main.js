const API = 'http://localhost:5000/api';

function showToast(msg, ms=3500) {
  const c = document.getElementById('toast-container');
  if(!c) return;
  const t = document.createElement('div');
  t.className = 'toast'; t.textContent = msg;
  c.appendChild(t);
  setTimeout(() => { t.style.opacity='0'; t.style.transform='translateY(8px)'; t.style.transition='all .3s'; setTimeout(()=>t.remove(),300); }, ms);
}
function showLoading(txt='Loading...') {
  const o=document.getElementById('loading-overlay');
  const p=document.getElementById('loading-text');
  if(o) o.style.display='flex';
  if(p) p.textContent=txt;
}
function hideLoading() {
  const o=document.getElementById('loading-overlay');
  if(o) o.style.display='none';
}
function esc(s=''){return String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}

document.addEventListener('DOMContentLoaded',()=>{
  const p = window.location.pathname.split('/').pop()||'index.html';
  document.querySelectorAll('.nav-links a').forEach(a=>{
    const h = a.getAttribute('href');
    a.classList.toggle('active', h===p||(p===''&&h==='index.html'));
  });
});