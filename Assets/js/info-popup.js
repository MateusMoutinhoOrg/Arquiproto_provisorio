// Info Popup: a "?" button next to a component, which opens a popup explaining it.
//
//     <button>Log in</button>
//     <template data-info-popup><p>→ Home/initial</p></template>
//
// Stands alone: it needs only info-popup.css, and uses no storage, URL parameters or requests.

(function () {
    var dialog;
    var content;
    var pressed;

    function createDialog() {
        dialog = document.createElement("dialog");
        dialog.className = "info-popup";
        dialog.setAttribute("aria-label", "Info");

        var box = document.createElement("div");
        box.className = "info-popup-box";

        var close = document.createElement("button");
        close.type = "button";
        close.className = "info-popup-close";
        close.setAttribute("aria-label", "Close");
        close.textContent = "×";
        close.addEventListener("click", function () {
            dialog.close();
        });

        content = document.createElement("div");
        content.className = "info-popup-content";

        // The box fills the dialog, so only the backdrop targets the dialog itself.
        // Selecting text and releasing outside also ends on the dialog, but started inside.
        dialog.addEventListener("mousedown", function (event) {
            pressed = event.target;
        });
        dialog.addEventListener("click", function (event) {
            if (event.target === dialog && pressed === dialog) {
                dialog.close();
            }
        });

        box.append(close, content);
        dialog.append(box);

        // In the body, because the component may be inside a form or an inert element.
        document.body.append(dialog);
    }

    function open(template) {
        if (!dialog) {
            createDialog();
        }
        content.replaceChildren(template.content.cloneNode(true));
        dialog.showModal();
    }

    function accessibleName(component) {
        var name = component.getAttribute("aria-label") || component.textContent;
        return "More info: " + name.replace(/\s+/g, " ").trim();
    }

    function addButton(template) {
        var component = template.previousElementSibling;
        if (!component) {
            return;
        }

        var button = document.createElement("button");
        button.type = "button";
        button.className = "info-popup-button";
        button.setAttribute("aria-label", accessibleName(component));
        button.textContent = "?";
        button.addEventListener("click", function (event) {
            event.preventDefault();
            event.stopPropagation();
            open(template);
        });

        // An inline component flows with its text, so the button can simply follow it.
        // Any other fills a box of its own, so a wrapper makes room for the button in that box.
        if (getComputedStyle(component).display.indexOf("inline") === 0) {
            component.after(button);
        } else {
            var host = document.createElement("span");
            host.className = "info-popup-host";
            component.before(host);
            host.append(component, button);
        }
    }

    function init() {
        document.querySelectorAll("template[data-info-popup]").forEach(addButton);
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }
})();
