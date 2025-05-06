document.addEventListener('DOMContentLoaded', function() {
    const toggleBtn = document.getElementById('sidebar-toggle');
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.getElementById('main-content');
    
    toggleBtn.addEventListener('click', function() {
        document.body.classList.toggle('sidebar-open');
        
        // Acessibilidade
        const isOpen = document.body.classList.contains('sidebar-open');
        sidebar.setAttribute('aria-expanded', isOpen);
        toggleBtn.setAttribute('aria-label', isOpen ? 'Fechar menu' : 'Abrir menu');
    });
});