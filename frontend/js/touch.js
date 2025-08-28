class TouchHandler {
    constructor() {
        this.startX = 0;
        this.startY = 0;
        this.init();
    }

    init() {
        if ('ontouchstart' in window) {
            this.initSwipeGestures();
            this.initPullToRefresh();
        }
    }

    initSwipeGestures() {
        document.addEventListener('touchstart', (e) => {
            this.startX = e.touches[0].clientX;
            this.startY = e.touches[0].clientY;
        }, { passive: true });

        document.addEventListener('touchend', (e) => {
            const endX = e.changedTouches[0].clientX;
            const diffX = this.startX - endX;
            
            if (Math.abs(diffX) > 50) {
                if (diffX > 0) this.onSwipeLeft();
                else this.onSwipeRight();
            }
        }, { passive: true });
    }

    initPullToRefresh() {
        let startY = 0;
        let pullDistance = 0;
        
        document.addEventListener('touchstart', (e) => {
            startY = e.touches[0].clientY;
        }, { passive: true });
        
        document.addEventListener('touchmove', (e) => {
            if (window.scrollY === 0) {
                pullDistance = e.touches[0].clientY - startY;
                if (pullDistance > 100) {
                    document.body.style.transform = 'translateY(20px)';
                }
            }
        }, { passive: true });
        
        document.addEventListener('touchend', () => {
            if (pullDistance > 100 && window.videosModule) {
                window.videosModule.loadVideos();
            }
            document.body.style.transform = '';
            pullDistance = 0;
        }, { passive: true });
    }

    onSwipeLeft() {
        console.log('Swipe left');
    }

    onSwipeRight() {
        console.log('Swipe right');
    }
}

window.TouchHandler = TouchHandler;