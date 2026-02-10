document.addEventListener('DOMContentLoaded', function() {
    const footerContainer = document.getElementById('footer-container');

    if (footerContainer) {
        // Create link element for CSS
        const linkElem = document.createElement('link');
        linkElem.rel = 'stylesheet';
        linkElem.href = '/footer.css';
        document.head.appendChild(linkElem);

        // Footer HTML content
        const footerHTML = `
      <footer class="footer">
        <div class="footer-container">
          <div class="footer-grid">
            <!-- Column 1: About -->
            <div class="footer-column">
              <h2 class="footer-heading">Stanza Decoro</h2>
              <div class="footer-accent-line"></div>
              <p class="footer-text">
                Tradição e qualidade desde 1994. Oferecemos soluções em decoração com excelência e sofisticação para transformar qualquer ambiente.
              </p>
              <p class="footer-copyright">© 2025 Stanza Decoro - Todos os direitos reservados</p>
            </div>

            <!-- Column 2: Contact -->
            <div id="contato" class="footer-column">
              <h2 class="footer-heading">Contato</h2>
              <div class="footer-accent-line"></div>
              <ul class="contact-list">
                <li class="contact-item">
                  <span class="contact-icon">
                    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path></svg>
                  </span>
                  <div class="contact-content">
                    <a title="Clique aqui para iniciar uma conversa" href="https://api.whatsapp.com/send?1=pt_BR&amp;phone=551197556-3037" class="footer-link">(11) 97556-3037</a>
                    <a title="Clique aqui para iniciar uma conversa" href="https://api.whatsapp.com/send?1=pt_BR&amp;phone=5511980156617" class="footer-link">(11) 980156617</a>
                  </div>
                </li>
                <li class="contact-item">
                  <span class="contact-icon">
                    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path><polyline points="22,6 12,13 2,6"></polyline></svg>
                  </span>
                  <a href="mailto:stanzadecoro@gmail.com" class="footer-link">
                    stanzadecoro@gmail.com
                  </a>
                </li>
                <li class="contact-item">
                  <span class="contact-icon">
                    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path><circle cx="12" cy="10" r="3"></circle></svg>
                  </span>
                  <a class="footer-link" href="https://maps.app.goo.gl/UvT1xA6Q6wvU4sv38">
                    Rua Armando Erse Figueiredo, 143<br>
                    São Paulo, Brazil 05761340
                  </a>
                  
                </li>
              </ul>
            </div>

            <!-- Column 3: Links -->
            <div class="footer-column">
              <h2 class="footer-heading">Links Rápidos</h2>
              <div class="footer-accent-line"></div>
              <ul class="links-list">
                <li class="links-item">
                  <a href="index.html#home" class="link-with-icon">
                    <span class="footer-link2">Início</span>
                    <svg class="link-icon" xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="7" y1="17" x2="17" y2="7"></line><polyline points="7 7 17 7 17 17"></polyline></svg>
                  </a>
                </li>
                <li class="links-item">
                  <a href="index.html#sobre" class="link-with-icon">
                    <span class="footer-link2">Sobre</span>
                    <svg class="link-icon" xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="7" y1="17" x2="17" y2="7"></line><polyline points="7 7 17 7 17 17"></polyline></svg>
                  </a>
                </li>
                <li class="links-item">
                  <a href="index.html#servicos" class="link-with-icon">
                    <span class="footer-link2">Últimos Serviços</span>
                    <svg class="link-icon" xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="7" y1="17" x2="17" y2="7"></line><polyline points="7 7 17 7 17 17"></polyline></svg>
                  </a>
                </li>
                <li class="links-item">
                  <a href="index.html#parceiros" class="link-with-icon">
                    <span class="footer-link2">Parcerias</span>
                    <svg class="link-icon" xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="7" y1="17" x2="17" y2="7"></line><polyline points="7 7 17 7 17 17"></polyline></svg>
                  </a>
                </li>
                
              </ul>
            </div>

            <!-- Column 4: Social -->
            <div class="footer-column">
              <h2 class="footer-heading">Redes Sociais</h2>
              <div class="footer-accent-line"></div>
              <div class="social-icons">
                <a href="https://www.instagram.com/stanza_decoro/" class="social-icon" aria-label="Instagram">
                  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="2" width="20" height="20" rx="5" ry="5"></rect><path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"></path><line x1="17.5" y1="6.5" x2="17.51" y2="6.5"></line></svg>
                </a>
                <a href="https://facebook.com" class="social-icon" aria-label="Facebook">
                  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 2h-3a5 5 0 0 0-5 5v3H7v4h3v8h4v-8h3l1-4h-4V7a1 1 0 0 1 1-1h3z"></path></svg>
                </a>
                
              </div>
              
            </div>
          </div>
          
          
          
        </div>
      </footer>
    `;

        footerContainer.innerHTML = footerHTML;
    }
});
