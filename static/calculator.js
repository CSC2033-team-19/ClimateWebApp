document.addEventListener("DOMContentLoaded", (doc_event) => {
    // get the range slider element.
    let electricity_factor_input = document.getElementById("clean_electricity_factor");

    // initialise tooltip for electricity factor input
    let electricity_factor_input_tooltip = new bootstrap.Tooltip(electricity_factor_input);

    // set up the default value
    electricity_factor_input.setAttribute("data-bs-original-title", electricity_factor_input.value + "%");

    // Add event listener for clean electricity update
    electricity_factor_input.addEventListener("input", (_) => {
        electricity_factor_input.setAttribute("data-bs-original-title", electricity_factor_input.value + "%");
        electricity_factor_input_tooltip.show();
    });

    // close the tooltip when the mouse leaves the slider
    electricity_factor_input.addEventListener("mouseleave", (_) => {
        electricity_factor_input_tooltip.hide();
    })
})