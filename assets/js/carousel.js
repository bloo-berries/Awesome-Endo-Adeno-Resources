// Image Carousel
(function() {
    var track = document.querySelector('.carousel-track');
    var slides = document.querySelectorAll('.carousel-slide');
    var dotsContainer = document.querySelector('.carousel-dots');
    var prevBtn = document.querySelector('.carousel-prev');
    var nextBtn = document.querySelector('.carousel-next');
    var carouselBox = document.querySelector('.carousel-box');
    if (!track || slides.length === 0) return;

    var currentIndex = 0;
    var autoRotateInterval = null;

    // Accessibility: make carousel a keyboard-navigable region
    if (carouselBox) {
        carouselBox.setAttribute('tabindex', '0');
        carouselBox.setAttribute('role', 'region');
        carouselBox.setAttribute('aria-label', 'Image carousel');
    }
    slides.forEach(function(slide, i) {
        slide.setAttribute('aria-roledescription', 'slide');
        slide.setAttribute('aria-label', 'Slide ' + (i + 1) + ' of ' + slides.length);
    });

    slides.forEach(function(_, i) {
        var dot = document.createElement('button');
        dot.classList.add('carousel-dot');
        if (i === 0) dot.classList.add('active');
        dot.setAttribute('aria-label', 'Go to slide ' + (i + 1));
        dot.addEventListener('click', function() { goToSlide(i); });
        dotsContainer.appendChild(dot);
    });

    // Respect prefers-reduced-motion: skip autoplay for users who request reduced motion.
    // Touch users also don't get hover-pause, so autoplay on touch can feel intrusive.
    var motionQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    var isTouch = window.matchMedia('(hover: none)').matches;
    var shouldAutoplay = !motionQuery.matches && !isTouch;

    function goToSlide(index) {
        currentIndex = index;
        track.style.transform = 'translateX(-' + (currentIndex * 100) + '%)';
        var dots = dotsContainer.querySelectorAll('.carousel-dot');
        dots.forEach(function(dot, i) { dot.classList.toggle('active', i === currentIndex); });
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
    if (carouselBox) {
        carouselBox.addEventListener('mouseenter', stopAutoRotate);
        carouselBox.addEventListener('mouseleave', startAutoRotate);
        carouselBox.addEventListener('keydown', function(e) {
            if (e.key === 'ArrowLeft') { prevSlide(); startAutoRotate(); e.preventDefault(); }
            if (e.key === 'ArrowRight') { nextSlide(); startAutoRotate(); e.preventDefault(); }
        });
    }

    // If the user changes their motion preference mid-session, adapt.
    motionQuery.addEventListener('change', function(e) {
        shouldAutoplay = !e.matches && !isTouch;
        if (shouldAutoplay) startAutoRotate(); else stopAutoRotate();
    });

    // Initialize aria-hidden state
    slides.forEach(function(s, i) { s.setAttribute('aria-hidden', i === 0 ? 'false' : 'true'); });

    startAutoRotate();
})();
