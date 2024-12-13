export const attachClickHandler = (button, callback) => {
	button.addEventListener("click", (event) => {
		event.preventDefault();
		callback(button);
	});
};