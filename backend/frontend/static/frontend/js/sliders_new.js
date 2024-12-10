document.addEventListener("DOMContentLoaded", () => {
	// Найти все слайдеры
	const sliders = document.querySelectorAll(".slider");

	sliders.forEach((slider, index) => {
		const currentImageElement = slider.querySelector(".slider-images img");
		const controlsContainer = slider.querySelector(".slider-controls");
		// Получаем JSON из соответствующего <script>
		const scriptContent = document.querySelector(`#image-data-slider-${index + 1}`).textContent;

		// Парсим JSON
		const data = JSON.parse(scriptContent);

		// Получаем данные
		const initialImage = data.initial_image;
		const imageCount = data.image_count;
		const otherImages = data.other_images;

		// Устанавливаем начальное изображение
		currentImageElement.src = initialImage;

		let currentIndex = 0;

		// Функция для создания радиокнопок
		const createRadioButtons = (count) => {
			for (let i = 0; i < count; i++) {
				const input = document.createElement("input");
				input.type = "radio";
				input.name = `slider-${index + 1}`;
				input.id = `slide-${index + 1}-${i + 1}`;
				input.value = i;
				if (i === 0) input.checked = true;

				const label = document.createElement("label");
				label.htmlFor = input.id;

				controlsContainer.appendChild(input);
				controlsContainer.appendChild(label);

				// Навешивание события
				input.addEventListener("change", () => {
					currentIndex = parseInt(input.value, 10);
					if (currentIndex === 0) {
						currentImageElement.src = initialImage; // Первое изображение
					} else {
						currentImageElement.src = otherImages[currentIndex - 1]; // Остальные изображения
					}
				});
			}
		};

		// Создаём радиокнопки
		createRadioButtons(imageCount);
		console.log(`Радиокнопки сгенерированы для слайдера ${index + 1}`);
	});
});