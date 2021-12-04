function openTab(event, tabName) {
    /**
     * This will close a previously open tab and open the one which is clicked
     * @param {Event} event Event object containing data about the element
     * @param {String} tabName Decides which tab is being opened
     */

    // move the active class from the previous tab to the new one
    document.querySelector("li.is-active").classList.remove("is-active");
    event.target.parentElement.classList.add("is-active");

    // find the new and old tabs on the document
    let new_tab = document.getElementById(tabName);
    let old_tab = document.querySelector("div.active");

    // fade the old tab out so that the new tab can replace it.
    old_tab.className = "content-tab fading";
    setTimeout(function() {
        old_tab.className = "content-tab inactive";
    }, 400);

    // set the new tabs state to active.
    new_tab.className = "content-tab active";
}