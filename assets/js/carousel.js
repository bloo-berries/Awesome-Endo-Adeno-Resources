// Image Carousel - multi-instance support
(function() {
    var sections = document.querySelectorAll('.carousel-section');
    if (!sections.length) return;

    var motionQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    var isTouch = window.matchMedia('(hover: none)').matches;

    function initCarousel(section) {
        var track = section.querySelector('.carousel-track');
        var slides = section.querySelectorAll('.carousel-slide');
        var dotsContainer = section.querySelector('.carousel-dots');
        var prevBtn = section.querySelector('.carousel-prev');
        var nextBtn = section.querySelector('.carousel-next');
        var viewport = section.querySelector('.carousel-viewport');
        if (!track || slides.length === 0) return;

        var currentIndex = 0;
        var autoRotateInterval = null;
        var shouldAutoplay = !motionQuery.matches && !isTouch;

        // Accessibility
        if (viewport) {
            viewport.setAttribute('tabindex', '0');
            viewport.setAttribute('role', 'region');
            viewport.setAttribute('aria-label', 'Image carousel');
        }
        slides.forEach(function(slide, i) {
            slide.setAttribute('aria-roledescription', 'slide');
            slide.setAttribute('aria-label', 'Slide ' + (i + 1) + ' of ' + slides.length);
        });

        // Build dots
        if (dotsContainer) {
            slides.forEach(function(_, i) {
                var dot = document.createElement('button');
                dot.classList.add('carousel-dot');
                if (i === 0) dot.classList.add('active');
                dot.setAttribute('aria-label', 'Go to slide ' + (i + 1));
                dot.addEventListener('click', function() { goToSlide(i); });
                dotsContainer.appendChild(dot);
            });
        }

        function goToSlide(index) {
            currentIndex = index;
            track.style.transform = 'translateX(-' + (currentIndex * 100) + '%)';
            if (dotsContainer) {
                var dots = dotsContainer.querySelectorAll('.carousel-dot');
                dots.forEach(function(dot, i) { dot.classList.toggle('active', i === currentIndex); });
            }
            slides.forEach(function(s, i) { s.setAttribute('aria-hidden', i === currentIndex ? 'false' : 'true'); });
        }
        function nextSlide() { goToSlide((currentIndex + 1) % slides.length); }
        function prevSlide() { goToSlide((currentIndex - 1 + slides.length) % slides.length); }
        function startAutoRotate() {
            if (!shouldAutoplay) return;
            stopAutoRotate();
            autoRotateInterval = setInterval(nextSlide, 4000);
        }
        function stopAutoRotate() { if (autoRotateInterval) { clearInterval(autoRotateInterval); autoRotateInterval = null; } }

        if (nextBtn) nextBtn.addEventListener('click', function() { nextSlide(); startAutoRotate(); });
        if (prevBtn) prevBtn.addEventListener('click', function() { prevSlide(); startAutoRotate(); });
        if (viewport) {
            viewport.addEventListener('mouseenter', stopAutoRotate);
            viewport.addEventListener('mouseleave', startAutoRotate);
            viewport.addEventListener('keydown', function(e) {
                if (e.key === 'ArrowLeft') { prevSlide(); startAutoRotate(); e.preventDefault(); }
                if (e.key === 'ArrowRight') { nextSlide(); startAutoRotate(); e.preventDefault(); }
            });
        }

        motionQuery.addEventListener('change', function(e) {
            shouldAutoplay = !e.matches && !isTouch;
            if (shouldAutoplay) startAutoRotate(); else stopAutoRotate();
        });

        // Initialize aria-hidden state
        slides.forEach(function(s, i) { s.setAttribute('aria-hidden', i === 0 ? 'false' : 'true'); });

        startAutoRotate();
    }

    // NSFW gate: reveal carousel on button click
    sections.forEach(function(section) {
        var gate = section.querySelector('.carousel-nsfw-gate');
        if (!gate) {
            initCarousel(section);
            return;
        }

        var revealBtn = gate.querySelector('.carousel-nsfw-reveal');
        var viewport = section.querySelector('.carousel-viewport');
        var controls = section.querySelector('.carousel-controls');

        if (revealBtn) {
            revealBtn.addEventListener('click', function() {
                gate.setAttribute('hidden', '');
                if (viewport) viewport.removeAttribute('hidden');
                if (controls) controls.removeAttribute('hidden');
                initCarousel(section);
            });
        }
    });
})();
