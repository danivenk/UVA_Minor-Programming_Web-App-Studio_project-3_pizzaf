// init() executes after DOMContent has been loaded
function init() {
    // find form and validation items in the page
    const forms = document.querySelectorAll("form");
    const dropdown_menu = document.querySelector("#drop_menu");
    const dropdown_link = document.querySelector("#drop_link");
    const navbar = document.querySelector("#nav_menu");

    // loop over each form
    forms.forEach(function(form) {
        // check if required fields are empty upon submitting and stop it if that's the case
        form.addEventListener("submit", function(event) {
            // find the items to validate in the form
            const validation_items = event.target.closest("form").querySelectorAll(".form-control");
            
            // for each to be validated item validate
            for (const item of validation_items) {
                if (item.value === "") {
                    event.preventDefault();
                    event.stopPropagation();
                }
            };

            // find the input with class cart (cart page)
            const cart = event.target.closest("form").querySelector(".cart");

            // if cart is defined then ask for confirmation, not if cart is not defined
            //  it is nested because if you put these in the same if statement it'll ask confirmation for every form
            if (cart) {
                if (!confirm("Are you sure?")) {
                    event.preventDefault();
                    event.stopPropagation();
                };
            };

            // give was-validated class to form if validation was completed
            form.classList.remove("needs-validation");
            form.classList.add("was-validated");

            // keep the login dropdown showing after validation
            if (form.parentElement.id == "drop_menu") {
                dropdown_menu.classList.add("show");
                navbar.classList.add("show");
                dropdown_link.getAttribute("aria-expanded") = true;
            };
        }, false);
    });

    // define all links and forms in the menu list
    const a = document.querySelectorAll("a.menu");
    const form = document.querySelectorAll("form.menu");

    // for each link add a toggle function which toggles visablity of the form
    a.forEach(function(link, index) {
        link.addEventListener("click", function () {

            // toggle visibility of the form upon click of the link
            if (form[index].style.display === "flex") {
                form[index].style.display = "";
            } else if (form[index].style.display === "") {
                form[index].style.display = "flex";
            };
        }, false);
    });
    
}
// make sure DOMContent is loaded before the code runs
document.addEventListener("DOMContentLoaded", init, false);