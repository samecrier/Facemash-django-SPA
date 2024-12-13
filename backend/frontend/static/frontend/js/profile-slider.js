document.addEventListener("DOMContentLoaded", () => {
    const slider = document.querySelector(".slider");
    if (!slider) {
        console.error("Slider element not found!");
        return;
    }

    const currentImageElement = slider.querySelector("#current-image");
    const controlsContainer = slider.querySelector(".slider-controls");
	
    // Получаем данные из JSON, встроенного в HTML
    const scriptElement = document.querySelector("#image-data-slider-1");
    if (!scriptElement) {
        console.error("Script element with image data not found!");
        return;
    }

    const data = JSON.parse(scriptElement.textContent);
    const images = data.images;
	console.log(images)
	let currentIndex = 0;

    // Устанавливаем начальное изображение
    const updateImage = (index) => {
        currentImageElement.src = images[index];
        currentIndex = index;
    };

    updateImage(0); // Устанавливаем первое изображение

    // Функция для создания радио-кнопок
    const createRadioButtons = () => {
        controlsContainer.innerHTML = ""; // Очищаем контейнер

        images.forEach((image, index) => {
            const input = document.createElement("input");
            input.type = "radio";
            input.name = "profile-slider";
            input.id = `slide-${index}`;
            input.value = index;

            if (index === 0) {
                input.checked = true; // Устанавливаем первую кнопку активной
            }

            const label = document.createElement("label");
            label.htmlFor = input.id;

            // Добавляем событие переключения изображений
            input.addEventListener("change", () => {
                updateImage(index);
            });

            controlsContainer.appendChild(input);
            controlsContainer.appendChild(label);
        });
    };

    // Создаём радио-кнопки
    createRadioButtons();
});