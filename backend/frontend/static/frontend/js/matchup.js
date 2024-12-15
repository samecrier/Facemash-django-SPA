import { initializeSlider } from "./slider-utility.js";
import { attachClickHandler } from "./utils.js";

document.addEventListener("DOMContentLoaded", () => {
    const buttons = document.querySelectorAll(".winner-btn");

    const handleWinnerButtonClick = (button) => {
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
                    <p class='competitor-rating'>Rating: ${loserData.rating}</p>
                `;

                loserElement.querySelector(".slider-images").innerHTML = `
                    <a href="profile/${loserData.winner_id}"><img src="${loserData.competitor.images[0].url}" alt="${loserData.competitor.name}">
                `;

                const newFormHtml = `
                    <div class="button">
                        <form method="post">
                            <input type="hidden" name="csrfmiddlewaretoken" value="${csrfToken}">
                            <input type="hidden" name="winner_id" value="${loserData.winner_id}">
                            <input type="hidden" name="winner_position" value="${loserData.winner_position}">
                            <input type="hidden" id="image-index-slider-${loserData.winner_position}" name="winner_image_index" value="0">
                            <input type="hidden" name="loser_id" value="${loserData.loser_id}">
                            <button type="button" class="winner-btn" data-form-id="${competitorKey}">Выбрать</button>
                        </form>
                    </div>
                `;

                loserElement.querySelector(".button").innerHTML = newFormHtml;

                const newButton = loserElement.querySelector(".winner-btn");
                attachClickHandler(newButton, handleWinnerButtonClick);

                const scriptElement = loserElement.querySelector("script");
                scriptElement.textContent = JSON.stringify({
                    images: loserData.competitor.images.map(img => img.url),
                    initial_index: 0,
                });

                const slider = loserElement.querySelector(".slider");
                initializeSlider(slider, parseInt(loserElement.dataset.index, 10) - 1);

				// Обновление победителя
				const winnerElement = button.closest(".competitor");
				
				const winnerRatingElement = winnerElement.querySelector(".competitor-rating");
				winnerRatingElement.textContent = `Rating: ${data.winner_rating}`;
				
				const winnerLoserInput = winnerElement.querySelector("input[name='loser_id']");
				winnerLoserInput.value = loserData.winner_id;
			
				const profileBaseUrl = "/competitor/";

				const topRatingTableBody = document.querySelector(".top-rating tbody");
				topRatingTableBody.innerHTML = ""; // Очищаем текущую таблицу

				data.top_ratings.forEach((competitor, index) => {
					const row = document.createElement("tr");
		
					row.innerHTML = `
						<td>${index + 1}</td>
						<td><a class="profile-ref" href="${profileBaseUrl}${competitor.id}">${competitor.name}</a></td>
						<td>${competitor.city}</td>
						<td>${competitor.rating}</td>
					`;
		
					topRatingTableBody.appendChild(row);
				});




            } else {
                console.error("Error:", data.message);
            }
        });
    };

    buttons.forEach(button => attachClickHandler(button, handleWinnerButtonClick));
});