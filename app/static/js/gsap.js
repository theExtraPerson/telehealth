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

// GSAP animation for mobile menu description
const mobileNav = document.querySelector("#mobileNav");

const observer = new MutationObserver(() => {
    if (mobileNav.classList.contains("show")) {
        gsap.fromTo(
            ".mobile-menu",
            { height: 0, opacity: 0},
            { height: "auto", opacity: 1, duration: 0.4, ease: "power2.out"}
        );
    }
});

observer.observe(mobileNav, {attributes: true})

gsap.from(".mobile-menu", {
  y: -20,
  opacity: 0,
  duration: 0.4,
  ease: "power2.out"
});

//animate the glass desktop nav into view
document.addEventListener("DOMContentLoaded", () => {
    gsap.from(".desktop-glass-nav", {
        y: -20,
        opacity: 0,
        duration: 0.6,
        ease: "power3.out"
    })
})

// Some cards GSAP

document.addEventListener("DOMContentLoaded", function() {
    gsap.from(".card", { duration: 1, opacity: 0, y: 50, stagger: 0.3 });
});

// index page service cards

document.addEventListener("DOMContentLoaded", function() {
    gsap.from(".service-card", { duration: 1, opacity: 0, y: 50, stagger: 0.3, ease: "power2.out" });
});

// manage appointments page

document.addEventListener("DOMContentLoaded", () => {
    gsap.from("#appointments", {
      opacity: 0,
      y: 50,
      duration: 1,
      ease: "power2.out"
    });

    gsap.from(".accordion-item", {
      opacity: 0,
      y: 30,
      stagger: 0.1,
      delay: 0.3,
      duration: 0.6
    });
  });


// edit profile page

document.addEventListener("DOMContentLoaded", () => {
    gsap.from("#profile-form", {
      opacity: 0,
      y: 50,
      duration: 1,
      ease: "power2.out"
    });

    gsap.from("input, select, textarea, button", {
      opacity: 0,
      y: 20,
      stagger: 0.1,
      duration: 0.8,
      delay: 0.2
    });
  });

// register page
gsap.from("#registerCard", {
    y: 50,
    opacity: 0,
    duration: 1.2,
    ease: "power3.out"
  });

  // Password validation
  document.getElementById('registerForm').addEventListener('submit', function (e) {
    const pass = document.getElementById('password').value;
    const confirm = document.getElementById('confirm_password').value;
    if (pass !== confirm) {
      e.preventDefault();
      alert("Passwords do not match!");
    }
  });

 // GSAP Animation for Sidebar Transition
    gsap.from(".sidebar img", {
        duration: 1,
        opacity: 0,
        scale: 0.5,
        ease: "back.out(1.7)",
    });

    gsap.from(".nav-link", {
        duration: 1,
        opacity: 0,
        x: -20,
        stagger: 0.2,    // Stagger the animation for list items
        ease: "power4.out",
    });
