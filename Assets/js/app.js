// Shared form behavior. It never changes what a state shows: it only resets forms and redirects.

// Turns a state's address ("Page/state") into a relative path. Every state lives at the same depth.
function address(target) {
    var parts = target.split("/");
    return "../../../" + parts[0] + "/states/" + parts[1] + "/index.html";
}

function isEmail(value) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
}

// On submit, redirects to the address returned by `decide`, which receives the form's fields.
// A page's script runs in all its states, so a form that only some states have may be missing.
function onSubmit(formId, decide) {
    var form = document.getElementById(formId);
    if (!form) {
        return;
    }

    // The browser's back button would restore typed values.
    window.addEventListener("pageshow", function () {
        form.reset();
    });

    form.addEventListener("submit", function (event) {
        // A native submit would add "?" to the URL.
        event.preventDefault();
        location.href = address(decide(Object.fromEntries(new FormData(form))));
    });
}
