(function($) {
    $(document).ready(function() {
        // Form yuklanganda status tanlovi
        function updateStatusChoices() {
            var statusSelect = $('select[name="status"]');
            if (!statusSelect.length) return;

            // Django'dan kelgan status tanlovlarini olish
            var choices = statusSelect.data('choices');
            if (!choices) return;

            // Mavjud tanlovlarni tozalash
            statusSelect.empty();

            // Django'dan kelgan tanlovlarni qo'shish
            Object.entries(choices).forEach(([value, label]) => {
                statusSelect.append(new Option(label, value));
            });

            // Agar mavjud qiymat bo'lsa, uni tanlash
            var currentValue = statusSelect.data('initial');
            if (currentValue) {
                statusSelect.val(currentValue);
            }
        }

        // Sahifa yuklanganda
        updateStatusChoices();
    });
})(window.django ? window.django.jQuery : window.jQuery);