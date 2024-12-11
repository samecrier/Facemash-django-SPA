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
		const initialImage = data.initial_image;
		const imageCount = data.image_count;
		const otherImages = data.other_images;

        // Получаем индекс начального изображения из данных
        const initialIndex = data.initial_index; // По умолчанию 0
		
        // Устанавливаем начальное изображение
        currentImageElement.src = initialIndex === 0 ? initialImage : otherImages[initialIndex-1];

		let currentIndex = 0;
		// Функция для создания радиокнопок
		const createRadioButtons = (count, initialIndex) => {
			for (let i = 0; i < count; i++) {
				const input = document.createElement("input");
				input.type = "radio";
				input.name = `slider-${index + 1}`;
				input.id = `slide-${index + 1}-${i + 1}`;
				input.value = i;
				// Проверяем, соответствует ли текущий индекс initialIndex
				if (i === initialIndex) {
					console.log(`Устанавливаем checked для i=${i}`);
					input.checked = true; // Устанавливаем radio-button как активный
				}

				const label = document.createElement("label");
				label.htmlFor = input.id;

				controlsContainer.appendChild(input);
				controlsContainer.appendChild(label);

				// Навешивание события
				input.addEventListener("change", () => {
					currentIndex = parseInt(input.value, 10);
					hiddenInput.value = currentIndex; // Обновляем скрытое поле
					if (currentIndex === 0) {
						currentImageElement.src = initialImage; // Первое изображение
					} else {
						currentImageElement.src = otherImages[currentIndex-1]; // Остальные изображения
					}
				});
			}
		};

		// Создаём радиокнопки
		createRadioButtons(imageCount, initialIndex);
		console.log(`Радиокнопки сгенерированы для слайдера ${index + 1}`);
	});
});