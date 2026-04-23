(() => {
  const navToggle = document.querySelector('[data-nav-toggle]');
  const nav = document.querySelector('[data-site-nav]');

  if (navToggle && nav) {
    navToggle.addEventListener('click', () => {
      const open = nav.classList.toggle('is-open');
      navToggle.setAttribute('aria-expanded', String(open));
    });

    nav.querySelectorAll('a').forEach((link) => {
      link.addEventListener('click', () => {
        nav.classList.remove('is-open');
        navToggle.setAttribute('aria-expanded', 'false');
      });
    });
  }

  const roleButtons = Array.from(document.querySelectorAll('[data-role-target]'));
  const roleInput = document.querySelector('[data-role-input]');

  const setRole = (role) => {
    if (!roleInput) return;
    const normalized = role === 'host' ? 'Host' : 'Parent';
    roleInput.value = normalized;
    roleButtons.forEach((button) => {
      const match = button.dataset.roleTarget === role;
      button.classList.toggle('is-active', match);
      button.setAttribute('aria-pressed', String(match));
    });
  };

  const params = new URLSearchParams(window.location.search);
  if (roleInput) {
    setRole(params.get('role') === 'host' ? 'host' : 'parent');
  }

  roleButtons.forEach((button) => {
    button.addEventListener('click', () => setRole(button.dataset.roleTarget));
  });

  const form = document.querySelector('[data-contact-form]');
  const status = document.querySelector('[data-form-status]');

  if (form) {
    form.addEventListener('submit', (event) => {
      event.preventDefault();

      const data = new FormData(form);
      const bodyLines = [
        `Role: ${data.get('role') || ''}`,
        `First name: ${data.get('first_name') || ''}`,
        `Last name: ${data.get('last_name') || ''}`,
        `Email: ${data.get('email') || ''}`,
        `Phone: ${data.get('phone') || ''}`,
        `Zip code: ${data.get('zip') || ''}`,
        `City: ${data.get('city') || ''}`,
        `State: ${data.get('state') || ''}`,
        `Country: ${data.get('country') || ''}`,
        '',
        'Message:',
        `${data.get('message') || ''}`,
      ];

      const subject = encodeURIComponent(`WorldSchool inquiry — ${data.get('role') || 'General'}`);
      const body = encodeURIComponent(bodyLines.join('\n'));
      const mailto = `mailto:Hello@WorldSchool.com?subject=${subject}&body=${body}`;

      if (status) {
        status.textContent = 'Opening your email client with the completed inquiry…';
      }

      window.location.href = mailto;
    });
  }
})();
