function openTab(event, tabName) {
    /**
     * This will close a previously opened tab and open the new one.
     * @param {Element} event clickevent containing data regarding the click.
     * @param {String} tabName which tab needs to be opened.
     */

    // move the active class from the previous tab to the new one.
    document.querySelector("li.is-active").classList.remove("is-active");
    event.target.parentElement.classList.add("is-active");

    // find the new and old tabs on the document
    let new_tab = document.getElementById(tabName);
    let old_tab = document.querySelector("div.active");

    if (new_tab === old_tab || !old_tab) {
        new_tab.className = "content-tab active";
        return;
    }
    // fade the old tab out so that it can be replaced by the new one
    old_tab.className = "content-tab fading";
    setTimeout(function() {
        old_tab.className = "content-tab inactive";

    }, 400);

    // set the new tabs state to active.
    new_tab.className = "content-tab active";
}
