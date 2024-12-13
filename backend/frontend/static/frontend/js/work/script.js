document.addEventListener("DOMContentLoaded", () => {
	// Найти контейнер слайдера и изображений
	const slider = document.querySelector(".slider");
	const sliderImages = document.querySelector(".slider-images");
	const radioButtons = document.querySelectorAll(".slider-controls input");

	console.log("Контейнер слайдера найден:", slider);
	// Функция для вычисления ширины контейнера
	// const getContainerWidth = () => Math.round(slider.getBoundingClientRect().width);

    const rect = slider.getBoundingClientRect(); // Точные размеры
	console.log(rect)
	const getContainerWidth = () => slider.clientWidth; // Ширина контейнера без рамки
	// Навешивание обработчиков на радиокнопки
	radioButtons.forEach((radio, index) => {
		console.log(`Навешиваем обработчик на радиокнопку ${index + 1}`);

		radio.addEventListener("change", () => {
			console.log(`Радиокнопка ${index + 1} активирована`);

			// Вычисляем смещение на основе ширины контейнера
			const containerWidth = getContainerWidth();
			console.log(`Ширина контейнера: ${containerWidth}px`);

			const offset = Math.round(-index * containerWidth);
			console.log(`Вычисленное смещение: ${offset}px`);

			// Сдвигаем изображения
			sliderImages.style.transform = `translateX(${offset}px)`;
			console.log(`Контейнер изображений сдвинут на ${offset}px`);
		});
	});

	console.log("Все обработчики событий навешаны");
});
