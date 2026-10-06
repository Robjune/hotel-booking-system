// Shared site behaviour: mobile menu, dismissible messages, linked date pickers.
(function () {
    var toggle = document.querySelector('[data-nav-toggle]');
    var links = document.getElementById('site-nav-links');
    if (toggle && links) {
        toggle.addEventListener('click', function () {
            var open = links.classList.toggle('is-open');
            toggle.setAttribute('aria-expanded', open);
        });
    }

    document.querySelectorAll('[data-dismiss]').forEach(function (btn) {
        btn.addEventListener('click', function () {
            btn.closest('.alert').remove();
        });
    });

    // Success/info messages fade out on their own; errors stay until dismissed.
    setTimeout(function () {
        document.querySelectorAll('.alert--success, .alert--info').forEach(function (el) {
            el.classList.add('is-hiding');
            setTimeout(function () { el.remove(); }, 400);
        });
    }, 6000);

    // Keep check-out at least one day after check-in on any form that has both.
    document.querySelectorAll('input[name="check_in"]').forEach(function (checkIn) {
        var form = checkIn.form;
        var checkOut = form && form.querySelector('input[name="check_out"]');
        if (!checkOut) return;
        function sync() {
            if (!checkIn.value) return;
            var next = new Date(checkIn.value + 'T00:00:00');
            next.setDate(next.getDate() + 1);
            // Build YYYY-MM-DD from local parts (toISOString would shift to UTC).
            var min = next.getFullYear() + '-' +
                String(next.getMonth() + 1).padStart(2, '0') + '-' +
                String(next.getDate()).padStart(2, '0');
            checkOut.min = min;
            if (!checkOut.value || checkOut.value < min) checkOut.value = min;
            checkOut.dispatchEvent(new Event('change'));
        }
        checkIn.addEventListener('change', sync);
    });
})();
