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

    slides.forEach(function(_, i) {
        var dot = document.createElement('button');
        dot.classList.add('carousel-dot');
        if (i === 0) dot.classList.add('active');
        dot.setAttribute('aria-label', 'Go to slide ' + (i + 1));
        dot.addEventListener('click', function() { goToSlide(i); });
        dotsContainer.appendChild(dot);
    });

    function goToSlide(index) {
        currentIndex = index;
        track.style.transform = 'translateX(-' + (currentIndex * 100) + '%)';
        var dots = dotsContainer.querySelectorAll('.carousel-dot');
        dots.forEach(function(dot, i) { dot.classList.toggle('active', i === currentIndex); });
    }
    function nextSlide() { goToSlide((currentIndex + 1) % slides.length); }
    function prevSlide() { goToSlide((currentIndex - 1 + slides.length) % slides.length); }
    function startAutoRotate() { stopAutoRotate(); autoRotateInterval = setInterval(nextSlide, 4000); }
    function stopAutoRotate() { if (autoRotateInterval) { clearInterval(autoRotateInterval); autoRotateInterval = null; } }

    if (nextBtn) nextBtn.addEventListener('click', function() { nextSlide(); startAutoRotate(); });
    if (prevBtn) prevBtn.addEventListener('click', function() { prevSlide(); startAutoRotate(); });
    if (carouselBox) {
        carouselBox.addEventListener('mouseenter', stopAutoRotate);
        carouselBox.addEventListener('mouseleave', startAutoRotate);
    }
    startAutoRotate();
})();
