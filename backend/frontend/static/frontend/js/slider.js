document.addEventListener("DOMContentLoaded", () => {
	const currentImageElement = document.getElementById("current-image");
	const controlsContainer = document.getElementById("slider-controls");

	// Получаем JSON из тега <script>
	const scriptContent = document.querySelector("#image-data").textContent;


	// Парсим JSON
	const data = JSON.parse(scriptContent);

	// Получаем данные
	const initialImage = data.initial_image;

	
	const imageCount = data.image_count;
	const otherImages = data.other_images;

	// Проверяем данные
	console.log("Initial Image:", initialImage);
	console.log("Image Count:", imageCount);
	console.log("Other Images:", otherImages);

	// Пример использования
	currentImageElement.src = initialImage;

	let currentIndex = 0;

	// Функция для создания radio buttons
	const createRadioButtons = (count) => {
		for (let i = 0; i < count; i++) {
			const input = document.createElement("input");
			input.type = "radio";
			input.name = "slider";
			input.id = `slide${i + 1}`;
			input.value = i;
			if (i === 0) input.checked = true;

			const label = document.createElement("label");
			label.htmlFor = `slide${i + 1}`;

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

	// Создаём radio buttons
	createRadioButtons(imageCount);
	console.log("Radio buttons сгенерированы для", imageCount, "изображений");
});