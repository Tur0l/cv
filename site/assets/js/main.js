/* CV de Alberto Morales: progreso, raíl, apariciones al hacer scroll y las dos demos.
   Sin dependencias y sin innerHTML: todo el DOM se toca con textContent y nodos. */
(() => {
  'use strict';

  const root = document.documentElement;
  root.classList.add('js');
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)');
  const hasIO = 'IntersectionObserver' in window;
  const wait = (ms) => new Promise((r) => setTimeout(r, ms));
  const sections = Array.from(document.querySelectorAll('main > section[id]'));
  const LANG = root.lang.startsWith('en') ? 'en' : 'es';

  /* Textos que escribe el script, en los dos idiomas de la web */
  const T = {
    es: {
      verdict: { checking: 'comprobando', pass: 'pasa', block: 'bloqueada', owned: 'comprometida', unreached: '' },
      arrives: 'llega',
      checking: 'Comprobando…',
      intro: ['Elige quién llama.', 'Cada petición recorre las capas en orden hasta que una la para.'],
      scenarios: {
        legit: ['Llega al servicio.', 'País permitido, IP limpia, nombre publicado, servicio en la lista blanca del túnel y passkey válida.'],
        foreign: ['Bloqueada en el geobloqueo.', 'El cortafuegos del VPS descarta la conexión antes de que empiece el TLS. Para el escáner, ahí no hay nada.'],
        brute: ['Bloqueada por CrowdSec.', 'Viene de una IP española, así que pasa el geobloqueo. CrowdSec lee los logs del proxy, ve los intentos fallidos y banea la IP.'],
        host: ['Bloqueada en el proxy.', 'Prueba la IP a pelo o un subdominio inventado. El proxy solo responde a los nombres publicados y no enseña nada más.'],
        vps: ['Bloqueada en el túnel.', 'El atacante controla el VPS, así que las tres primeras capas ya no cuentan. Intenta saltar a otros equipos de casa, pero el túnel solo deja pasar a los servicios publicados.'],
        stolen: ['Bloqueada en el login.', 'Con la contraseña cruza la red como cualquier usuario. Pero el login pide passkey o segundo factor, y eso no se roba junto con la contraseña.'],
      },
      ha: {
        online: 'en línea', down: 'caído',
        running: 'HA · en marcha', noNode: 'HA · sin nodo', restarted: 'HA · rearrancada',
        failing: 'pve-nodo1 deja de responder. El resto del clúster mantiene el quorum y ha-manager reubica la VM.',
        done: (s) => `La VM vuelve a funcionar en pve-nodo2 a los ${s} s, como en el ensayo real.`,
        run: 'Simular caída de pve-nodo1', again: 'Volver a empezar',
      },
      copy: 'Copiar', copied: 'Copiado', selected: 'Seleccionado',
    },
    en: {
      verdict: { checking: 'checking', pass: 'passes', block: 'blocked', owned: 'compromised', unreached: '' },
      arrives: 'gets in',
      checking: 'Checking…',
      intro: ['Pick who’s calling.', 'Each request goes through the layers in order until one stops it.'],
      scenarios: {
        legit: ['Gets through to the service.', 'Allowed country, clean IP, published hostname, service on the tunnel’s allow-list and a valid passkey.'],
        foreign: ['Blocked by geo-blocking.', 'The VPS firewall drops the connection before TLS even starts. To the scanner, there is nothing there.'],
        brute: ['Blocked by CrowdSec.', 'It comes from a Spanish IP, so it passes geo-blocking. CrowdSec reads the proxy logs, spots the failed attempts and bans the IP.'],
        host: ['Blocked at the proxy.', 'It tries the bare IP or a made-up subdomain. The proxy only answers for published hostnames and reveals nothing else.'],
        vps: ['Blocked at the tunnel.', 'The attacker controls the VPS, so the first three layers no longer count. They try to jump to other machines at home, but the tunnel only lets traffic through to the published services.'],
        stolen: ['Blocked at login.', 'With the password it crosses the network like any other user. But the login asks for a passkey or a second factor, and those aren’t stolen along with the password.'],
      },
      ha: {
        online: 'online', down: 'down',
        running: 'HA · running', noNode: 'HA · no node', restarted: 'HA · restarted',
        failing: 'pve-nodo1 stops responding. The rest of the cluster keeps quorum and ha-manager relocates the VM.',
        done: (s) => `The VM is running again on pve-nodo2 after ${s} s, just like in the real test.`,
        run: 'Simulate a pve-nodo1 failure', again: 'Start over',
      },
      copy: 'Copy', copied: 'Copied', selected: 'Selected',
    },
  }[LANG];

  /* Línea de progreso */
  const bar = document.querySelector('.progress span');
  let ticking = false;
  const paintProgress = () => {
    ticking = false;
    const max = root.scrollHeight - window.innerHeight;
    const p = max > 0 ? Math.min(1, Math.max(0, window.scrollY / max)) : 0;
    if (bar) bar.style.transform = `scaleX(${p.toFixed(4)})`;
  };
  const onScroll = () => {
    if (!ticking) { ticking = true; requestAnimationFrame(paintProgress); }
  };
  window.addEventListener('scroll', onScroll, { passive: true });
  window.addEventListener('resize', onScroll);
  paintProgress();

  /* Raíl de secciones + aviso de "has llegado a esta diapositiva" */
  const railLinks = new Map();
  document.querySelectorAll('.rail a').forEach((a) => railLinks.set(a.hash.slice(1), a));
  let currentId = 'inicio';
  // Al cambiar de idioma se sigue en la misma diapositiva (los id son iguales en las dos)
  document.querySelectorAll('.lang a:not([aria-current])').forEach((a) => {
    a.addEventListener('click', () => { a.hash = currentId === 'inicio' ? '' : currentId; });
  });
  if (hasIO) {
    const current = new IntersectionObserver((entries) => {
      entries.forEach((e) => {
        if (!e.isIntersecting) return;
        currentId = e.target.id;
        railLinks.forEach((a, id) => {
          if (id === e.target.id) a.setAttribute('aria-current', 'true');
          else a.removeAttribute('aria-current');
        });
        e.target.dispatchEvent(new CustomEvent('slide:enter'));
      });
    }, { rootMargin: '-45% 0px -50% 0px' });
    sections.forEach((s) => current.observe(s));
  }

  /* Apariciones: arrancan justo antes de entrar en pantalla. Lo que ya se ve al
     cargar no se anima, así la página está completa desde el primer momento. */
  if (hasIO && !reduce.matches) {
    sections.forEach((s) => {
      s.querySelectorAll('.reveal').forEach((el, i) => el.style.setProperty('--d', `${Math.min(i, 6) * 70}ms`));
    });
    const seen = new WeakSet();
    const reveal = new IntersectionObserver((entries, obs) => {
      entries.forEach((e) => {
        if (!seen.has(e.target)) {
          seen.add(e.target);
          if (e.isIntersecting) { obs.unobserve(e.target); return; }
        }
        if (e.isIntersecting) {
          e.target.classList.add('is-in');
          obs.unobserve(e.target);
        }
      });
    }, { rootMargin: '12% 0px 12% 0px' });
    document.querySelectorAll('.reveal').forEach((el) => reveal.observe(el));
  }

  /* Tarjetas deslizables del homelab: puntos de posición */
  document.querySelectorAll('.cards').forEach((track) => {
    const dots = track.nextElementSibling;
    if (!hasIO || !dots || !dots.classList.contains('cards-dots')) return;
    const cards = Array.from(track.children);
    const marks = cards.map(() => dots.appendChild(document.createElement('span')));
    marks[0].classList.add('on');
    const io = new IntersectionObserver((entries) => {
      entries.forEach((e) => {
        if (!e.isIntersecting) return;
        const i = cards.indexOf(e.target);
        marks.forEach((m, j) => m.classList.toggle('on', i === j));
      });
    }, { root: track, threshold: 0.6 });
    cards.forEach((c) => io.observe(c));
  });

  /* Demo 1: sigue una petición */
  const sim = document.querySelector('.sim');
  if (sim) {
    const picker = sim.querySelector('.sim-picker');
    const result = sim.querySelector('.sim-result');
    const layers = Array.from(sim.querySelectorAll('.layer'));
    const order = layers.map((l) => l.dataset.layer);
    // Dónde empieza cada petición y qué capa la para (null = llega al servicio)
    const SCENARIOS = {
      legit: { start: 'geo', stop: null },
      foreign: { start: 'geo', stop: 'geo' },
      brute: { start: 'geo', stop: 'crowdsec' },
      host: { start: 'geo', stop: 'proxy' },
      vps: { start: 'wg', stop: 'wg' },
      stolen: { start: 'geo', stop: 'login' },
    };

    const setState = (layer, state, label) => {
      if (state) layer.dataset.state = state;
      else delete layer.dataset.state;
      layer.querySelector('.verdict').textContent = label ?? T.verdict[state] ?? '';
    };
    const say = (title, text, tone) => {
      const strong = document.createElement('strong');
      strong.textContent = title;
      result.replaceChildren(strong, document.createTextNode(text));
      if (tone) result.dataset.tone = tone;
      else delete result.dataset.tone;
    };

    let run = 0;
    const play = async (key) => {
      const s = SCENARIOS[key];
      if (!s) return;
      const id = ++run;
      picker.querySelectorAll('button').forEach((b) => b.setAttribute('aria-pressed', String(b.dataset.s === key)));
      layers.forEach((l) => setState(l, null));
      say(T.checking, '', null);
      const step = reduce.matches ? 0 : 430;
      const startAt = order.indexOf(s.start);
      for (let i = 0; i < layers.length; i += 1) {
        if (id !== run) return;
        const layer = layers[i];
        if (i < startAt) { setState(layer, 'owned'); continue; }
        setState(layer, 'checking');
        if (step) await wait(step);
        if (id !== run) return;
        if (order[i] === s.stop) {
          setState(layer, 'block');
          layers.slice(i + 1).forEach((l) => setState(l, 'unreached'));
          break;
        }
        setState(layer, 'pass', i === layers.length - 1 ? T.arrives : undefined);
      }
      if (id !== run) return;
      const [title, text] = T.scenarios[key];
      say(title, ` ${text}`, s.stop ? 'block' : 'pass');
    };

    picker.hidden = false;
    result.hidden = false;
    say(T.intro[0], ` ${T.intro[1]}`, null);
    picker.addEventListener('click', (ev) => {
      const btn = ev.target.closest('button[data-s]');
      if (btn) play(btn.dataset.s);
    });
    // La primera vez que se llega a la diapositiva, se ve el camino completo
    const slide = sim.closest('section');
    let autoplayed = false;
    slide?.addEventListener('slide:enter', () => {
      if (autoplayed || run > 0) return;
      autoplayed = true;
      play('legit');
    });
  }

  /* Demo 2: caída de un nodo del clúster del TFC */
  const ha = document.querySelector('.ha');
  if (ha) {
    const btn = ha.querySelector('#ha-run');
    const clock = ha.querySelector('#ha-t');
    const status = ha.querySelector('#ha-status');
    const vm = ha.querySelector('.vm');
    const vmState = vm.querySelector('.vm-state');
    const n1 = ha.querySelector('[data-node="1"]');
    const n2 = ha.querySelector('[data-node="2"]');
    const home = n1.querySelector('.slot');
    const away = n2.querySelector('.slot');
    const originalNote = status.textContent;
    const TOTAL = 140;
    let phase = 'idle';

    const finish = () => {
      away.appendChild(vm);
      vm.dataset.state = 'moved';
      vmState.textContent = T.ha.restarted;
      n2.dataset.state = 'host';
      status.textContent = T.ha.done(TOTAL);
      btn.textContent = T.ha.again;
      btn.disabled = false;
      phase = 'done';
    };
    const fail = () => {
      phase = 'running';
      btn.disabled = true;
      n1.dataset.state = 'down';
      n1.querySelector('.node-state').textContent = T.ha.down;
      vm.dataset.state = 'stopped';
      vmState.textContent = T.ha.noNode;
      status.textContent = T.ha.failing;
      const dur = reduce.matches ? 0 : 2800;
      const t0 = performance.now();
      const tick = (now) => {
        const k = dur ? Math.min(1, (now - t0) / dur) : 1;
        clock.textContent = String(Math.round(TOTAL * k));
        if (k < 1) requestAnimationFrame(tick);
        else finish();
      };
      requestAnimationFrame(tick);
    };
    const reset = () => {
      home.appendChild(vm);
      delete vm.dataset.state;
      vmState.textContent = T.ha.running;
      delete n1.dataset.state;
      delete n2.dataset.state;
      n1.querySelector('.node-state').textContent = T.ha.online;
      clock.textContent = '0';
      status.textContent = originalNote;
      btn.textContent = T.ha.run;
      phase = 'idle';
    };

    ha.querySelector('.ha-controls').hidden = false;
    btn.addEventListener('click', () => {
      if (phase === 'idle') fail();
      else if (phase === 'done') reset();
    });
  }

  /* Email: se monta aquí para que no quede entero en el HTML */
  document.querySelectorAll('[data-email]').forEach((box) => {
    const addr = `${box.dataset.u}@${box.dataset.d}`;
    const text = box.querySelector('.email-text');
    const actions = box.querySelector('.email-actions');
    const write = actions.querySelector('a');
    const copy = actions.querySelector('button');
    const label = copy.querySelector('span');
    text.textContent = addr;
    write.href = `mailto:${addr}`;
    actions.hidden = false;
    let timer = 0;
    copy.addEventListener('click', () => {
      const done = (msg) => {
        label.textContent = msg;
        clearTimeout(timer);
        timer = setTimeout(() => { label.textContent = T.copy; }, 2200);
      };
      const select = () => {
        const range = document.createRange();
        range.selectNodeContents(text);
        const sel = window.getSelection();
        sel.removeAllRanges();
        sel.addRange(range);
        done(T.selected);
      };
      if (navigator.clipboard?.writeText) {
        navigator.clipboard.writeText(addr).then(() => done(T.copied), select);
      } else {
        select();
      }
    });
  });
})();
