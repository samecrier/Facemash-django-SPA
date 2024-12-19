document.addEventListener('DOMContentLoaded', function () {
    const numRoundsInput = document.getElementById('id_num_rounds'); // Поле "Количество раундов"
    const numPerMatchupInput = document.getElementById('id_num_per_matchup'); // Поле "Количество участников в матчапе"
    const numParticipantsInput = document.getElementById('id_num_participants'); // Поле "Общее количество участников"
    const userCountDisplay = document.getElementById('user-count-display'); // Поле с доступным числом пользователей

    // Создаём элемент для отображения ошибки
    const errorDisplay = document.createElement('p');
    errorDisplay.style.color = 'red';
    userCountDisplay.parentNode.insertBefore(errorDisplay, userCountDisplay.nextSibling);

    // Функция для получения доступного количества пользователей
    const getAvailableUsers = () => {
        const match = userCountDisplay.textContent.match(/(\d+)/); // Извлекаем число из текста
        return match ? parseInt(match[1], 10) : 0; // Если число найдено, возвращаем его, иначе 0
    };

    // Функция для отправки данных на сервер
    const updateNumParticipants = async () => {
        const numRounds = parseInt(numRoundsInput.value) || 0;
        const numPerMatchup = parseInt(numPerMatchupInput.value) || 0;
        const availableUsers = getAvailableUsers(); // Получаем доступное количество пользователей

        try {
            const response = await fetch('/api/v01/calculate-participants/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    num_rounds: numRounds,
                    num_per_matchup: numPerMatchup,
                    available_users: availableUsers
                })
            });

            if (response.ok) {
                const data = await response.json();
                errorDisplay.textContent = ''; // Убираем сообщение об ошибке
                numParticipantsInput.placeholder = data.calculated_participants; // Устанавливаем значение
            } else {
                const errorData = await response.json();
                errorDisplay.textContent = errorData.error || 'Ошибка сервера.';
                numParticipantsInput.value = ''; // Очищаем поле "Количество участников"
            }
        } catch (error) {
            errorDisplay.textContent = 'Не удалось выполнить расчёт.';
            console.error('Ошибка при запросе:', error);
        }
    };

    // Слушаем события ввода на полях
    numRoundsInput.addEventListener('input', updateNumParticipants);
    numPerMatchupInput.addEventListener('input', updateNumParticipants);
});