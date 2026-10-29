(() => {
  const form = document.getElementById('composer');
  if (!form) return;
  const input = document.getElementById('question');
  const stream = document.getElementById('messages');
  const welcome = document.getElementById('welcome');
  const error = document.getElementById('error');
  const status = document.getElementById('status');
  const send = document.getElementById('send');
  const nav = document.getElementById('conversations');
  const sessions = []; let current; let busy = false;
  function addMessage(role, content, sources) {
    const article = document.createElement('article'); article.className = 'message ' + role;
    const label = document.createElement('div'); label.className = 'message-label'; label.textContent = role === 'user' ? 'Você' : 'ZeladorX AI';
    const body = document.createElement('div'); body.className = 'message-body'; body.textContent = content;
    article.append(label, body);
    if (sources?.length) {
      const details = document.createElement('details'); const summary = document.createElement('summary');
      summary.textContent = 'Consultas e fontes · ' + sources.length; details.append(summary);
      sources.forEach(source => { const pre = document.createElement('pre'); pre.textContent = JSON.stringify(source, null, 2); details.append(pre); });
      article.append(details);
    }
    stream.append(article); stream.scrollTop = stream.scrollHeight;
  }
  function render() {
    stream.querySelectorAll('.message').forEach(el => el.remove());
    welcome.hidden = current.messages.length > 0; welcome.style.display = current.messages.length ? 'none' : '';
    current.messages.forEach(m => addMessage(m.role, m.content, m.sources));
    nav.replaceChildren(); sessions.forEach(session => {
      const button = document.createElement('button'); button.textContent = session.title; button.className = session === current ? 'active' : '';
      button.disabled = busy; button.onclick = () => { current = session; error.hidden = true; render(); }; nav.append(button);
    });
  }
  function newChat() { if (busy) return; current = { title: 'Nova conversa', messages: [] }; sessions.push(current); render(); input.focus(); }
  document.getElementById('new-chat').onclick = newChat;
  document.getElementById('menu').onclick = event => {
    const mobile = window.matchMedia('(max-width:760px)').matches;
    document.body.classList.toggle(mobile ? 'menu-open' : 'collapsed');
    event.currentTarget.setAttribute('aria-expanded', String(mobile ? document.body.classList.contains('menu-open') : !document.body.classList.contains('collapsed')));
  };
  document.querySelectorAll('[data-prompt]').forEach(button => button.onclick = () => { if (!busy) { input.value = button.dataset.prompt; form.requestSubmit(); } });
  input.addEventListener('keydown', event => { if (event.key === 'Enter' && !event.shiftKey) { event.preventDefault(); if (!busy) form.requestSubmit(); } });
  form.addEventListener('submit', async event => {
    event.preventDefault(); const question = input.value.trim(); if (!question || busy) return;
    const history = current.messages.slice(-20).map(({role,content}) => ({role,content:content.slice(0,8000)}));
    busy = true; send.disabled = true; input.disabled = true; error.hidden = true;
    current.title = current.messages.length ? current.title : question.slice(0,55);
    current.messages.push({ role:'user', content:question }); input.value = ''; render(); status.textContent = 'Consultando os dados…';
    try {
      const response = await fetch(form.action, { method:'POST', credentials:'same-origin',
        headers:{'Content-Type':'application/json','X-CSRFToken':form.querySelector('[name=csrfmiddlewaretoken]').value},
        body:JSON.stringify({pergunta:question,historico:history}) });
      const data = await response.json(); if (!response.ok) throw new Error(data.erro || 'Não foi possível consultar os dados.');
      current.messages.push({role:'assistant',content:data.resposta,sources:data.fontes});
    } catch (failure) {
      error.textContent = failure.message; error.hidden = false; current.messages.pop(); input.value = question;
    } finally { busy = false; send.disabled = false; input.disabled = false; status.textContent = 'Somente consulta · Dados do seu acesso'; render(); input.focus(); }
  });
  newChat();
})();
