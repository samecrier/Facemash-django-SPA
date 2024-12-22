document.addEventListener('DOMContentLoaded', () => {
	const competitorRows = document.querySelectorAll('.competitor-name');

	competitorRows.forEach(row => {
		row.addEventListener('click', async () => {
			const competitorId = row.getAttribute('data-competitor-id');

			try {
				const response = await fetch(`/api/v01/competitor/${competitorId}/`);
				if (!response.ok) throw new Error('Ошибка загрузки профиля');

				const data = await response.json();
				
				const profileDetail = document.getElementById('profile-detail');

				if (isAuth) {
					profileDetail.innerHTML = `
						<div class="slider">
							<div class="slider-controls"></div>
							<img id="current-image" src="" alt="Текущая фотография" />
						</div>
						<div class="profile-info">
							<table>
								<tbody>
									<tr>
										<td class="key">Name</td>
										<td class="value">${data.name}</td>
									</tr>
									${data.age !== null 
										? `<tr>
											<td class="key">Age</td>
											<td class="value">${data.age}</td>
										</tr>`
										: ''}
									<tr>
										<td class="key">City</td>
										<td class="value">${data.city}</td>
									</tr>
									<tr>
										<td class="key">Bio</td>
										<td class="value">${data.bio}</td>
									</tr>
								</tbody>
								</table>
								<div class="link-to-competitor">
									<a href="/competitor/${data.id}">На страничку компетитора</a>
								</div>

					</div>
					`;
				} else {
					profileDetail.innerHTML = `
					<div class="slider">
						<div class="slider-controls"></div>
						<img id="current-image" src="" alt="Текущая фотография" />
					</div>
					<div class="profile-info">
						<table>
							<tbody>
								<tr>
									<td class="key">Name</td>
									<td class="value">${data.name}</td>
								</tr>
								<tr>
									<td class="key">Age</td>
									<td class="value">${data.age}</td>
								</tr>
								<tr>
									<td class="key">City</td>
									<td class="value">${data.city}</td>
								</tr>
							</tbody>
							</table>
							<div class="link-to-competitor">
								<a href="/competitor/${data.id}">На страничку компетитора</a>
							</div>

				</div>
				`;
				}

				// Инициализируем слайдер для изображений
				initializeSlider(data.images);
			} catch (error) {
				console.error('Ошибка:', error);
			}
		});
	});

	/**
	 * Функция для инициализации слайдера
	 * @param {Array} images - массив URL изображений
	 */
	function initializeSlider(images) {
		const slider = document.querySelector(".slider");
		const currentImageElement = slider.querySelector("#current-image");
		const controlsContainer = slider.querySelector(".slider-controls");

		if (!slider || !currentImageElement || !controlsContainer) {
			console.error("Элементы слайдера не найдены!");
			return;
		}

		let currentIndex = 0;

		// Функция для обновления текущего изображения
		const updateImage = (index) => {
			currentImageElement.src = images[index].url;
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
	}
});