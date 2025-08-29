/**
 * Mobile Navigation Module
 * Handles hamburger menu and mobile-specific interactions
 */
class MobileNavigationModule {
    constructor() {
        this.isMenuOpen = false;
        this.init();
    }

    init() {
        this.createMobileNav();
        this.bindEvents();
        this.handleResize();
    }

    createMobileNav() {
        // Create mobile navigation HTML
        const mobileNavHTML = `
            <div class="mobile-nav" id="mobileNav">
                <div class="mobile-nav-content">
                    <div class="mobile-logo">
                        🎬 Video SStech
                    </div>
                    <div class="hamburger-menu" id="hamburgerMenu">
                        <div class="hamburger-line"></div>
                        <div class="hamburger-line"></div>
                        <div class="hamburger-line"></div>
                    </div>
                </div>
            </div>
            
            <div class="mobile-menu" id="mobileMenu">
                <div class="mobile-menu-item" onclick="window.mobileNav.closeMenu(); window.videosModule.loadVideos();">
                    🏠 Início
                </div>
                <div class="mobile-menu-item" onclick="window.mobileNav.closeMenu(); document.getElementById('uploadToggle').click();">
                    ⬆️ Upload
                </div>
                <div class="mobile-menu-item" onclick="window.mobileNav.closeMenu(); document.getElementById('showFoldersBtn').click();">
                    📁 Mostrar Pastas
                </div>
                <div class="mobile-menu-item" onclick="window.mobileNav.closeMenu(); document.getElementById('searchInput').focus();">
                    🔍 Buscar
                </div>
                <div class="mobile-menu-item" onclick="window.mobileNav.closeMenu(); window.authModule.logout();">
                    🚪 Sair
                </div>
            </div>
        `;

        // Insert at beginning of body
        document.body.insertAdjacentHTML('afterbegin', mobileNavHTML);
    }

    bindEvents() {
        const hamburger = document.getElementById('hamburgerMenu');
        const mobileMenu = document.getElementById('mobileMenu');

        if (hamburger) {
            hamburger.addEventListener('click', () => {
                this.toggleMenu();
            });
        }

        // Close menu when clicking outside
        document.addEventListener('click', (e) => {
            if (this.isMenuOpen && 
                !e.target.closest('#mobileMenu') && 
                !e.target.closest('#hamburgerMenu')) {
                this.closeMenu();
            }
        });

        // Close menu on escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isMenuOpen) {
                this.closeMenu();
            }
        });

        // Handle swipe gestures
        this.handleSwipeGestures();
    }

    toggleMenu() {
        if (this.isMenuOpen) {
            this.closeMenu();
        } else {
            this.openMenu();
        }
    }

    openMenu() {
        const mobileMenu = document.getElementById('mobileMenu');
        const hamburger = document.getElementById('hamburgerMenu');
        
        if (mobileMenu && hamburger) {
            mobileMenu.classList.add('active');
            hamburger.classList.add('active');
            this.isMenuOpen = true;
            
            // Prevent body scroll
            document.body.style.overflow = 'hidden';
        }
    }

    closeMenu() {
        const mobileMenu = document.getElementById('mobileMenu');
        const hamburger = document.getElementById('hamburgerMenu');
        
        if (mobileMenu && hamburger) {
            mobileMenu.classList.remove('active');
            hamburger.classList.remove('active');
            this.isMenuOpen = false;
            
            // Restore body scroll
            document.body.style.overflow = '';
        }
    }

    handleResize() {
        window.addEventListener('resize', () => {
            // Close menu on resize to desktop
            if (window.innerWidth > 1024 && this.isMenuOpen) {
                this.closeMenu();
            }
        });
    }

    handleSwipeGestures() {
        let startX = 0;
        let startY = 0;
        let endX = 0;
        let endY = 0;

        document.addEventListener('touchstart', (e) => {
            startX = e.touches[0].clientX;
            startY = e.touches[0].clientY;
        });

        document.addEventListener('touchend', (e) => {
            endX = e.changedTouches[0].clientX;
            endY = e.changedTouches[0].clientY;
            
            const deltaX = endX - startX;
            const deltaY = endY - startY;
            
            // Swipe right from left edge to open menu
            if (startX < 50 && deltaX > 100 && Math.abs(deltaY) < 100) {
                this.openMenu();
            }
            
            // Swipe left to close menu
            if (this.isMenuOpen && deltaX < -100 && Math.abs(deltaY) < 100) {
                this.closeMenu();
            }
        });
    }

    // Utility methods for other modules
    isMobile() {
        return window.innerWidth <= 768;
    }

    isTablet() {
        return window.innerWidth > 768 && window.innerWidth <= 1024;
    }

    isDesktop() {
        return window.innerWidth > 1024;
    }

    // Show mobile loading
    showMobileLoading(message = 'Carregando...') {
        if (!this.isMobile()) return;
        
        const loadingHTML = `
            <div class="mobile-loading" id="mobileLoading">
                <div style="text-align: center;">
                    <div style="margin-bottom: 10px;">⏳</div>
                    <div>${message}</div>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', loadingHTML);
    }

    hideMobileLoading() {
        const loading = document.getElementById('mobileLoading');
        if (loading) {
            loading.remove();
        }
    }

    // Optimize modals for mobile
    optimizeModalForMobile(modal) {
        if (!this.isMobile()) return;
        
        const modalContent = modal.querySelector('.modal-content');
        if (modalContent) {
            modalContent.style.width = '100vw';
            modalContent.style.height = '100vh';
            modalContent.style.maxWidth = 'none';
            modalContent.style.maxHeight = 'none';
            modalContent.style.borderRadius = '0';
            modalContent.style.margin = '0';
        }
    }

    // Add pull-to-refresh functionality
    addPullToRefresh(callback) {
        if (!this.isMobile()) return;
        
        let startY = 0;
        let currentY = 0;
        let isPulling = false;
        
        document.addEventListener('touchstart', (e) => {
            if (window.scrollY === 0) {
                startY = e.touches[0].clientY;
                isPulling = true;
            }
        });
        
        document.addEventListener('touchmove', (e) => {
            if (!isPulling) return;
            
            currentY = e.touches[0].clientY;
            const pullDistance = currentY - startY;
            
            if (pullDistance > 100) {
                // Show pull indicator
                this.showPullIndicator();
            }
        });
        
        document.addEventListener('touchend', () => {
            if (!isPulling) return;
            
            const pullDistance = currentY - startY;
            if (pullDistance > 100) {
                callback();
            }
            
            this.hidePullIndicator();
            isPulling = false;
        });
    }

    showPullIndicator() {
        if (document.getElementById('pullIndicator')) return;
        
        const indicator = document.createElement('div');
        indicator.id = 'pullIndicator';
        indicator.innerHTML = '🔄 Solte para atualizar';
        indicator.style.cssText = `
            position: fixed;
            top: 80px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(0,0,0,0.8);
            color: white;
            padding: 10px 20px;
            border-radius: 20px;
            z-index: 10001;
            font-size: 14px;
        `;
        
        document.body.appendChild(indicator);
    }

    hidePullIndicator() {
        const indicator = document.getElementById('pullIndicator');
        if (indicator) {
            indicator.remove();
        }
    }
}

// Initialize mobile navigation
window.mobileNav = new MobileNavigationModule();