document.addEventListener("DOMContentLoaded", () => {
	// Найти все слайдеры
	const sliders = document.querySelectorAll(".slider");

	sliders.forEach((slider, index) => {
		const currentImageElement = slider.querySelector(".slider-images img");
		const controlsContainer = slider.querySelector(".slider-controls");
		const hiddenInput = document.querySelector(`#image-index-slider-${index + 1}`);
		// Получаем JSON из соответствующего <script>
		const scriptContent = document.querySelector(`#image-data-slider-${index + 1}`).textContent;

		// Парсим JSON
		const data = JSON.parse(scriptContent);

		// Получаем данные
		const images = data.images;
		const initialIndex = data.initial_index || 0; // Индекс текущего изображения, по умолчанию 0
		
		// Устанавливаем начальное изображение
		currentImageElement.src = images[initialIndex];

		let currentIndex = initialIndex;

		// Функция для создания радиокнопок
		const createRadioButtons = (images, initialIndex) => {
			images.forEach((image, i) => {
				const input = document.createElement("input");
				input.type = "radio";
				input.name = `slider-${index + 1}`;
				input.id = `slide-${index + 1}-${i + 1}`;
				input.value = i;

				// Устанавливаем активную радиокнопку
				if (i === initialIndex) {
					input.checked = true;
				}

				const label = document.createElement("label");
				label.htmlFor = input.id;

				controlsContainer.appendChild(input);
				controlsContainer.appendChild(label);

				// Навешивание события
				input.addEventListener("change", () => {
					currentIndex = parseInt(input.value, 10);
					hiddenInput.value = currentIndex; // Обновляем скрытое поле
					currentImageElement.src = images[currentIndex];
				});
			});
		};

		// Создаём радиокнопки
		createRadioButtons(images, initialIndex);
	});
});