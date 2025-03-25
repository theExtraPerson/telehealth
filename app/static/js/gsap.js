let gsap;
        gsap.from("#navbar", {
            duration: 1,
            y: "-100%",
            ease: "power2.inOut"
        });
        gsap.from(".gsap-logo", {
            duration: 1.5,
            scale: 0.5,
            opacity: 0,
            ease: "elastic.inOut",
            delay: 0.5
        });


document.addEventListener("DOMContentLoaded", function() {
    gsap.from(".card", { duration: 1, opacity: 0, y: 50, stagger: 0.3 });
});
