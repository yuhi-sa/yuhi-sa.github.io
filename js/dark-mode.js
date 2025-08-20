class DarkModeManager {
  constructor() {
    this.storageKey = 'theme-preference';
    this.toggleButton = document.getElementById('darkModeToggle');
    this.html = document.documentElement;
    
    this.init();
  }
  
  init() {
    // Set initial theme based on saved preference or system preference
    this.setTheme(this.getTheme());
    
    // Update toggle button appearance
    this.updateToggleButton();
    
    // Add event listeners
    if (this.toggleButton) {
      this.toggleButton.addEventListener('click', () => this.toggleTheme());
    }
    
    // Listen for system theme changes
    window.matchMedia('(prefers-color-scheme: dark)')
          .addEventListener('change', (e) => {
            if (!localStorage.getItem(this.storageKey)) {
              this.setTheme(e.matches ? 'dark' : 'light');
            }
          });
  }
  
  getTheme() {
    const stored = localStorage.getItem(this.storageKey);
    if (stored) {
      return stored;
    }
    
    // Default to system preference
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }
  
  setTheme(theme) {
    this.html.setAttribute('data-theme', theme);
    localStorage.setItem(this.storageKey, theme);
    this.updateToggleButton(theme);
  }
  
  toggleTheme() {
    const currentTheme = this.html.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    this.setTheme(newTheme);
  }
  
  updateToggleButton(theme = null) {
    if (!this.toggleButton) return;
    
    const currentTheme = theme || this.html.getAttribute('data-theme');
    const icon = this.toggleButton.querySelector('#darkModeIcon');
    const darkText = this.toggleButton.querySelector('.toggle-text:not(.toggle-light)');
    const lightText = this.toggleButton.querySelector('.toggle-light');
    
    // Update icon if present
    if (icon) {
      if (currentTheme === 'dark') {
        icon.className = 'fas fa-sun';
      } else {
        icon.className = 'fas fa-moon';
      }
    }
    
    // Update text if present
    if (darkText && lightText) {
      if (currentTheme === 'dark') {
        darkText.style.display = 'none';
        lightText.style.display = 'flex';
      } else {
        darkText.style.display = 'flex';
        lightText.style.display = 'none';
      }
    }

    // Update navbar theme
    this.updateNavbarTheme(currentTheme);
    
    // Update aria-label for better accessibility
    const label = currentTheme === 'dark' ? 'ライトモードに切り替え' : 'ダークモードに切り替え';
    this.toggleButton.setAttribute('aria-label', label);
    this.toggleButton.setAttribute('title', label);
  }
  
  updateNavbarTheme(theme) {
    const navbar = document.querySelector('.navbar');
    if (navbar) {
      if (theme === 'dark') {
        navbar.classList.remove('navbar-light', 'bg-light');
        navbar.classList.add('navbar-dark', 'bg-dark');
      } else {
        navbar.classList.remove('navbar-dark', 'bg-dark');
        navbar.classList.add('navbar-light', 'bg-light');
      }
    }
  }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  new DarkModeManager();
});

// Handle theme on page load (before DOMContentLoaded for faster loading)
(() => {
  const theme = localStorage.getItem('theme-preference') ||
                (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
  document.documentElement.setAttribute('data-theme', theme);
})();
