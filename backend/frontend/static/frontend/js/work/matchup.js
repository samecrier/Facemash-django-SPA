document.addEventListener("DOMContentLoaded", () => {
    const buttons = document.querySelectorAll(".winner-btn");
    console.log("Button clicked, sending AJAX request...");

    // Функция для обработки кнопки
    const attachClickHandler = (button) => {
        button.addEventListener("click", () => {
            const form = button.closest("form");
            const formData = new FormData(form);
            const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;

            fetch(form.action, {
                method: "POST",
                headers: {
                    "X-Requested-With": "XMLHttpRequest",
                    "X-CSRFToken": csrfToken,
                },
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === "success") {
                    const competitorKey = Object.keys(data.loser_data)[0];
                    const loserElement = document.querySelector(`#${competitorKey}`);

                    const loserData = data.loser_data[competitorKey];
                    loserElement.querySelector(".bio").innerHTML = `
                        <p>${loserData.competitor.name}, ${loserData.competitor.age}</p>
                        <p>Rating: ${loserData.rating}</p>
                    `;

                    loserElement.querySelector(".slider-images").innerHTML = `
                        <img src="${loserData.competitor.images[0].url}" alt="${loserData.competitor.name}">
                    `;

                    const newFormHtml = `
                        <div class="button">
                            <form method="post">
                                <input type="hidden" name="csrfmiddlewaretoken" value="${document.querySelector('input[name="csrfmiddlewaretoken"]').value}">
                                <input type="hidden" name="winner_id" value="${loserData.winner_id}">
                                <input type="hidden" name="winner_position" value="${loserData.winner_position}">
                                <input type="hidden" id="image-index-slider-${loserData.winner_position}" name="winner_image_index" value="0">
                                <input type="hidden" name="loser_id" value="${loserData.loser_id}">
                                <button type="button" class="winner-btn" data-form-id="${competitorKey}">Выбрать</button>
                            </form>
                        </div>
                    `;

                    loserElement.querySelector(".button").innerHTML = newFormHtml;

                    // Навешиваем обработчик на новую кнопку
                    const newButton = loserElement.querySelector(".winner-btn");
                    attachClickHandler(newButton);

                    const scriptElement = loserElement.querySelector("script");
                    scriptElement.textContent = JSON.stringify({
                        images: loserData.competitor.images.map(img => img.url),
                        initial_index: 0,
                    });

                    const slider = loserElement.querySelector(".slider");
                    initializeSlider(slider, parseInt(loserElement.dataset.index, 10) - 1);
                } else {
                    console.error("Error:", data.message);
                }
            });
        });
    };

    // Навешиваем обработчик на все кнопки
    buttons.forEach(button => attachClickHandler(button));
});