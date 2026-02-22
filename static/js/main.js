(function () {
    var nav = document.querySelector('.nav');
    var toggle = document.querySelector('.nav-toggle');
    if (toggle && nav) {
        toggle.addEventListener('click', function () {
            nav.classList.toggle('is-open');
        });
    }

    var searchInput = document.querySelector('.search-input');
    if (searchInput) {
        searchInput.addEventListener('keydown', function (e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                var q = this.value.trim();
                if (q) window.location.href = '/' + '?q=' + encodeURIComponent(q);
            }
        });
    }

    var cardNumber = document.getElementById('card_number');
    if (cardNumber) {
        cardNumber.addEventListener('input', function () {
            var v = this.value.replace(/\D/g, '');
            var parts = [];
            for (var i = 0; i < v.length && i < 16; i += 4) parts.push(v.slice(i, i + 4));
            this.value = parts.join(' ');
        });
    }
    var expiry = document.getElementById('expiry');
    if (expiry) {
        expiry.addEventListener('input', function () {
            var v = this.value.replace(/\D/g, '');
            if (v.length >= 2) this.value = v.slice(0, 2) + '/' + v.slice(2, 4);
            else this.value = v;
        });
    }
})();
