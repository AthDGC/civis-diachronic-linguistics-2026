// Mobile menu toggle
document.addEventListener('DOMContentLoaded', function () {
    const toggle = document.querySelector('.mobile-toggle');
    const menu = document.querySelector('.nav-menu');

    if (toggle && menu) {
        toggle.addEventListener('click', function () {
            menu.classList.toggle('active');
        });
    }

    // Close mobile menu when clicking on a menu item
    const menuItems = document.querySelectorAll('.nav-menu a');
    menuItems.forEach(item => {
        item.addEventListener('click', function () {
            if (window.innerWidth <= 768) {
                menu.classList.remove('active');
            }
        });
    });

    // Social sharing functions
    window.shareOnFacebook = function () {
        const url = encodeURIComponent(window.location.href);
        window.open(`https://www.facebook.com/sharer/sharer.php?u=${url}`, '_blank');
    };

    window.shareOnTwitter = function () {
        const url = encodeURIComponent(window.location.href);
        const text = encodeURIComponent('Check out this CIVIS Diachronic Linguistics 2026 programme!');
        window.open(`https://twitter.com/intent/tweet?url=${url}&text=${text}`, '_blank');
    };

    window.shareOnLinkedIn = function () {
        const url = encodeURIComponent(window.location.href);
        window.open(`https://www.linkedin.com/shareArticle?mini=true&url=${url}`, '_blank');
    };
});
