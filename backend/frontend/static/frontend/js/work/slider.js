document.addEventListener("DOMContentLoaded", () => {
	console.log("DOMContentLoaded event triggered");
	const sliders = document.querySelectorAll(".slider");
	
	sliders.forEach((slider, index) => {
		console.log(`Initializing slider with index: ${index}`);
		initializeSlider(slider, index);
	});
});