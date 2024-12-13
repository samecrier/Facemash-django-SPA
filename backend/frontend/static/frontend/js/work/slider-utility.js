const initializeSlider = (slider, index) => {
	const currentImageElement = slider.querySelector(".slider-images img");
	const controlsContainer = slider.querySelector(".slider-controls");
	console.log(`Looking for script element with id: image-data-slider-${index + 1}`);
	const hiddenInput = document.querySelector(`#image-index-slider-${index + 1}`);
	const scriptContent = document.querySelector(`#image-data-slider-${index + 1}`).textContent;
	

	const data = JSON.parse(scriptContent);
	const images = data.images;
	const initialIndex = data.initial_index || 0;

	currentImageElement.src = images[initialIndex];
	hiddenInput.value = initialIndex;

	let currentIndex = initialIndex;

	// Очищаем старые радио-кнопки
	controlsContainer.innerHTML = "";

	// Создаём новые радио-кнопки
	images.forEach((image, i) => {
		const input = document.createElement("input");
		input.type = "radio";
		input.name = `slider-${index + 1}`;
		input.id = `slide-${index + 1}-${i + 1}`;
		input.value = i;

		if (i === initialIndex) {
			input.checked = true;
		}

		const label = document.createElement("label");
		label.htmlFor = input.id;

		controlsContainer.appendChild(input);
		controlsContainer.appendChild(label);

		input.addEventListener("change", () => {
			currentIndex = parseInt(input.value, 10);
			hiddenInput.value = currentIndex;
			currentImageElement.src = images[currentIndex];
		});
	});
};