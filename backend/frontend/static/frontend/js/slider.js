import { initializeSlider } from "./slider-utility.js";
document.addEventListener("DOMContentLoaded", () => {
    const sliders = document.querySelectorAll(".slider");

    sliders.forEach((slider, index) => {
        console.log(`Initializing slider with index: ${index}`);
        initializeSlider(slider, index);
    });
});