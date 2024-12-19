document.addEventListener('DOMContentLoaded', function() {
    const checkboxes = document.querySelectorAll('.checkbox-container input[type="checkbox"]');
    const userCountDisplay = document.getElementById('user-count-display');

    // Функция для получения CSRF-токена
    const getCSRFToken = () => {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
        return csrfToken ? csrfToken.value : '';
    };

    const updateUserCount = async () => {
        const selectedCities = Array.from(checkboxes)
            .filter(checkbox => checkbox.checked)
            .map(checkbox => checkbox.value);

        if (selectedCities.length === 0) {
            userCountDisplay.textContent = "Выбрано пользователей: 0";
            return;
        }

        try {
            const response = await fetch('/api/v01/count-competitors/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken() // Передаём CSRF-токен в заголовке
                },
                body: JSON.stringify({ cities: selectedCities })
            });

            if (response.ok) {
                const data = await response.json();
                userCountDisplay.textContent = `Выбрано пользователей: ${data.count}`;
            } else {
                userCountDisplay.textContent = "Ошибка сервера.";
                console.error("Ошибка ответа сервера:", response.statusText);
            }
        } catch (error) {
            userCountDisplay.textContent = "Не удалось получить данные.";
            console.error("Ошибка при запросе:", error);
        }
    };

    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', updateUserCount);
    });
});