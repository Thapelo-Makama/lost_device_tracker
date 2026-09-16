document.addEventListener('DOMContentLoaded', () => {
  const toggle = document.getElementById('aiToggle');
  const box = document.getElementById('aiContainer');
  const body = document.getElementById('aiBody');
  const input = document.getElementById('aiInput');
  const send = document.getElementById('aiSend');
  const close = document.getElementById('aiClose');
  const sugg = document.getElementById('aiSuggestions');
  let typing = false;

  toggle.addEventListener('click', () => {
    box.classList.toggle('open');
    if (box.classList.contains('open')) { input.focus(); body.scrollTop = body.scrollHeight; }
  });
  close.addEventListener('click', () => box.classList.remove('open'));

  const add = (text, who) => {
    const m = document.createElement('div');
    m.className = 'ai-msg ' + who;
    const av = document.createElement('div');
    av.className = 'ai-avatar';
    av.innerHTML = who === 'bot' ? '<i class="fas fa-robot"></i>' : '<i class="fas fa-user"></i>';
    const c = document.createElement('div');
    c.className = 'ai-content';
    c.innerHTML = text.replace(/\n/g, '<br>');
    if (who === 'user') { m.appendChild(c); m.appendChild(av); }
    else { m.appendChild(av); m.appendChild(c); }
    body.appendChild(m);
    body.scrollTop = body.scrollHeight;
  };

  const showTyping = () => {
    const m = document.createElement('div');
    m.className = 'ai-msg bot'; m.id = 'typing';
    m.innerHTML = '<div class="ai-avatar"><i class="fas fa-robot"></i></div><div class="ai-content typing"><span></span><span></span><span></span></div>';
    body.appendChild(m); body.scrollTop = body.scrollHeight;
  };
  const hideTyping = () => { const t = document.getElementById('typing'); if (t) t.remove(); };

  const updateSuggestions = (list) => {
    sugg.innerHTML = '';
    list.forEach(s => {
      const b = document.createElement('button');
      b.className = 'ai-suggestion'; b.textContent = s;
      b.addEventListener('click', () => { input.value = s; submit(); });
      sugg.appendChild(b);
    });
  };

  const submit = () => {
    const text = input.value.trim();
    if (!text || typing) return;
    add(text, 'user'); input.value = ''; typing = true; showTyping();
    fetch('/ai/chat', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: text, page_url: window.location.pathname })
    })
    .then(r => r.json())
    .then(d => { hideTyping(); typing = false; add(d.response, 'bot');
                 if (d.suggestions) updateSuggestions(d.suggestions); })
    .catch(() => { hideTyping(); typing = false; add('⚠️ Error. Please try again.', 'bot'); });
  };

  send.addEventListener('click', submit);
  input.addEventListener('keypress', e => { if (e.key === 'Enter') { e.preventDefault(); submit(); }});

  fetch('/ai/suggestions?page=' + encodeURIComponent(window.location.pathname))
    .then(r => r.json()).then(d => { if (d.suggestions) updateSuggestions(d.suggestions); });
});
