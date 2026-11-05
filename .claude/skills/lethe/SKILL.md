---
name: lethe
description: Build, change, review and publish web prototypes with the Lethe architecture, where a prototype is a set of memoryless HTML states and every action is a redirect to a state. Use this skill whenever the user mentions Lethe, asks to prototype a web app, screen or flow, or works on a project with Pages/Page/state.html files, Info Popups (data-info-popup) or a Test Hub, even if they only say "add a state", "add a screen", "crie uma tela", "novo estado" or "protótipo" without naming the architecture. It holds the rules, the templates and a script that checks a project against them.
---

# Lethe

A prototype has no memory, only states. Every action ends in a redirect to a state, and everything that was on screen is lost.

The value of this constraint is that anyone can open any state directly and see exactly what it shows, with no setup and no build. So when something seems to need memory or a bit of JavaScript, the answer is almost always one more state.

The rules below are the standard itself. If one of them blocks what the user asked for, keep to the rule, tell the user what the limitation is, and propose a change for them to decide. Don't bend it silently.

## Workflow

1. **Read what exists.** If the project has `Pages/`, read `index.html` and the states closest to the change, and reuse their markup and CSS classes. Otherwise create the [structure](#structure): copy `assets/app.js` from this skill to `Assets/js/app.js`, write `Assets/css/app.css`, and create an empty `.nojekyll`.
2. **Map the states before writing HTML.** Write one line per action, as in [State map](#state-map), and count the states. Show the map to the user first if the flow wasn't specified or is large, because each state is a whole file and a wrong map is expensive to redo.
3. **Write each state as a complete file**, from the [templates](#templates). Copy the shared markup, such as the navigation, into every state: there are no includes, because a state stands alone.
4. **Write the conditions** of each form in `Assets/js/<Page>.js`.
5. **Add the Info Popups**, one per action and one per `<h1>`, matching the real behavior.
6. **Update the Test Hub** with one line per new state.
7. **Run the checker** from the project's root, and fix what it reports until it is clean:

   ```bash
   python3 <this skill's directory>/scripts/check.py .
   ```

   It only verifies what a script can. It can't tell whether a state really never changes, whether a popup's sentences are true or whether the screen looks right, so read those yourself.
8. **Open it in a browser if you can**, by `file://`: follow each path of each form, and look at desktop and phone widths and at the console.

A change often touches more than one file:

| Change | Also update |
| --- | --- |
| New state | The action that leads to it and its popup, in every state where that action appears, and the hub |
| Renamed state or page | Links, popups, addresses in `Assets/js/` and the hub |
| Shared markup, such as the navigation | Every state that repeats it. A throwaway script is fine, but don't leave it in the repository, because there is no build step |
| Popup next to the `<h1>` | The hub, which repeats its text, and every state of the page if it's the first paragraph |
| New condition | The popup of the form's button, and the state it leads to |

## Structure

```
index.html            default entry of the site, the test hub
.nojekyll             makes GitHub Pages publish the files as they are
Assets/
  css/app.css         styles of all states
  js/app.js           form behavior of all states
  js/<Page>.js        form conditions of a page
Pages/
  <Page>/
    initial.html
    <state>.html
```

- A state's address is `<Page>/<state>`, for example `LoginScreen/initial`.
- Pages use `PascalCase` and states use `snake_case`.
- Every page has an `initial` state.
- The libraries of the architecture, the [Info Popup](#info-popup) and the [Test Hub](#test-hub), are loaded by URL, so a project doesn't need a folder for them.

## Rules

1. **A state never changes.** Opening a state always shows the same thing, wherever the user came from.
2. **Nothing is remembered.** Storage (`localStorage`, `sessionStorage`, IndexedDB, cookies), URL parameters (query string, hash) and requests for data (`fetch`, `XMLHttpRequest`) are forbidden. Loading files from `Assets/` and the libraries of the architecture is allowed.
3. **Every action ends in a redirect.** An action is a click on a link or button, or a submit; filling a form field (typing, choosing an option, ticking a box) or scrolling is not an action. The target can be another state or the same one, on the same page or another. An action never changes the current screen: an error message, an open modal and a selected tab are other states. Opening or closing an Info Popup is not an action: it documents the prototype and is not part of the screen. A modal of the product is still another state.
4. **Conditions only read the current screen.** An action can check current input values against fixed values, against each other, or for length or format. Every condition has an `else`, so every path ends in a redirect.
5. **A state stands alone.** Each `<state>.html` holds its whole screen, including every link, with no framework or build step, and works when opened directly in a browser. The only shared files are the styles and form behavior in `Assets/` and the [Info Popup](#info-popup) library. They never add markup or links to the screen, except for `info-popup.js`, the only shared file that adds markup, limited to the `?` button and the popup, with no links. Actions are plain links. Forms use `novalidate`, because browser validation would block the redirect, and `onSubmit` from `Assets/js/app.js`, which sets `location.href`, because a native submit would add `?` to the URL, and resets the form on `pageshow`, because the browser's back button would restore typed values. A page's conditions live in `Assets/js/<Page>.js`, loaded as a classic script, because browsers block modules on `file://`.
6. **Every state documents itself.** Every action of rule 3 has an Info Popup next to it, and every state has one next to its `<h1>`. A state with a modal repeats that one next to the modal's title, because the `<h1>` behind the modal can't be clicked.
7. **The site has one default entry, the [Test Hub](#test-hub).** The `index.html` at the root is what opens when no state is named. It is not a state and not part of the product: it only lists every page and state, each with a plain link and what it does. Every link opens in a new tab, with `<base target="_blank">` in its `<head>`, so the hub stays open while a state is tested. It has no forms, scripts or Info Popups, and remembers nothing.
8. **The repository is the site.** GitHub Pages publishes its root as it is, with no build, because an empty `.nojekyll` at the root turns off Jekyll. Every path to a file of the project is relative, because the site is served from `/<repository>/`, and matches the case of the file, because GitHub Pages is case-sensitive, unlike macOS and Windows.

## State map

```
LoginScreen/initial
  log in with the demo login    → Home/initial
  log in with an empty field    → LoginScreen/required_fields
  log in with anything else     → LoginScreen/invalid_credentials
  forgot password               → ForgotPassword/initial

Task<Name>/initial
  edit                          → Task<Name>Edit/initial → Task<Name>/saved
  delete                        → Task<Name>/delete_confirm → Tasks/<name>_deleted
```

Counting states is where the rules bite, so go through these when mapping:

- Each error message, notice, open modal and selected tab is its own state.
- Each record with its own screen is its own page, such as `TaskCheckoutBug`, because a state can't take an id in the URL.
- The data is fixed. Choose it up front, such as a demo login and a few rows, because `Tasks/task_created` always shows the same new row, whatever title was typed, and a deleted row is back on any other state.

When a request implies behavior the rules forbid, use the state that shows the result:

| Instead of | Use |
| --- | --- |
| Showing an error under a field with JavaScript | A redirect to `<Page>/<error>`, with the form empty, because nothing is remembered |
| Opening a modal, a dropdown or `<details>` in place | A state with it open, and a link to the state without it |
| Switching tabs in place | One state per tab, with plain links |
| Passing an id or a filter in the URL | One page per record, and one state per filter |
| Carrying a typed name to the next screen | Fixed text, the same for everyone |
| Sharing the header through JavaScript or an include | The same markup copied into each state |

## Info Popup

A `?` button next to a component, which opens a popup explaining what the action does and which states it leads to. It is a library of the architecture, not a file of the project: it lives in `Lib/` of the [Lethe repository](https://github.com/MateusMoutinhoOrg/Lethe), which is public, and depends on nothing else.

Put a `<template data-info-popup>` right after the component, with the popup's text inside. A `<template>` renders nothing, so the state works the same without the script. The script adds one `?` button per template.

- Write in the language of the app.
- Use only text, with no links, buttons or forms. Every link stays in the state itself.
- Next to an action, write one line per path: `if <condition> → <Page>/<state>`, ending in `else → <Page>/<state>`. A plain link has a single line: `→ <Page>/<state>`.
- Match the real behavior, which is the link's `href` or the conditions in `Assets/js/<Page>.js`.
- Next to the `<h1>`, write two paragraphs with one sentence each: what the page is for, then what the user sees and when.
- An item without an action, such as a field, a text or an error message, has no popup, because it is already on the screen.

Don't load the files from `raw.githubusercontent.com`, because browsers block a script served as `text/plain`.

Without a connection the `?` buttons don't appear and the state keeps working. To keep them offline, run this at the project's root, which copies `Lib/` from the Lethe repository and, run again, updates it:

```bash
curl -fsSL https://github.com/MateusMoutinhoOrg/Lethe/archive/refs/heads/main.tar.gz | tar -xz --strip-components=1 Lethe-main/Lib
```

Then load the files by relative path from each state, `../../Lib/info-popup.css` and `../../Lib/info-popup.js`.

## Test Hub

The page at the root of the site, from which anyone testing the prototype can see what each state does and open it directly. It is a library of the architecture, but only a stylesheet: the list itself is plain HTML, so its links work even if the stylesheet doesn't load.

- Write in the language of the app.
- List every state in `Pages/` exactly once, with the pages in the order of the app's flow and `initial` first in each page.
- The `<p>` before the first `<section>` says which state to start at and what the test needs, such as a demo login.
- The `<h2>` is the name of the page, and the `<p>` below it is what the page is for: the first paragraph of the Info Popup next to the `<h1>` of its states.
- Each `<li>` is a link named after the state, followed by what the user sees and when: the second paragraph of that same Info Popup. A change to that popup is also made in the hub.
- Every link opens in a new tab, through the `<base target="_blank">` in the `<head>`, so the hub stays open as the place to come back to. Don't put a `target` on a single link, because the `<base>` already covers them all. The states keep opening in the same tab, because an action of a state is a redirect, not a new tab.

## Templates

### A state with a form and links

The scripts go at the end of the `<body>`, with `app.js` first, because `onSubmit` looks for the form as soon as it runs. If the form isn't there yet, the browser falls back to a native submit.

```html
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LoginScreen/initial</title>
    <link rel="stylesheet" href="../../Assets/css/app.css">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/MateusMoutinhoOrg/Lethe@main/Lib/info-popup.css">
    <script src="https://cdn.jsdelivr.net/gh/MateusMoutinhoOrg/Lethe@main/Lib/info-popup.js"></script>
</head>

<body>
    <main>
        <h1>Log in</h1>
        <template data-info-popup>
            <p>Authentication of an existing user.</p>
            <p>Empty login form, shown when the user logs out.</p>
        </template>

        <form id="login" novalidate autocomplete="off">
            <label for="email">Email</label>
            <input id="email" name="email" type="email">

            <label for="password">Password</label>
            <input id="password" name="password" type="password">

            <button>Log in</button>
            <template data-info-popup>
                <ul>
                    <li>if email or password is empty → LoginScreen/required_fields</li>
                    <li>if email is user@example.com and password is password123 → Home/initial</li>
                    <li>else → LoginScreen/invalid_credentials</li>
                </ul>
            </template>
        </form>

        <a href="../ForgotPassword/initial.html">Forgot password?</a>
        <template data-info-popup><p>→ ForgotPassword/initial</p></template>
    </main>

    <script src="../../Assets/js/app.js"></script>
    <script src="../../Assets/js/LoginScreen.js"></script>
</body>

</html>
```

`Assets/js/LoginScreen.js`, where the last line is the `else`. `onSubmit` gives the function the form's fields by `name`, and `isEmail` from `app.js` checks the format of an email:

```js
onSubmit("login", function (f) {
    if (f.email === "" || f.password === "") return "LoginScreen/required_fields";
    if (f.email === "user@example.com" && f.password === "password123") return "Home/initial";
    return "LoginScreen/invalid_credentials";
});
```

### A state with a modal

The whole screen stays behind the modal, marked `inert`, with its usual popups. The modal's title repeats the popup of the `<h1>`.

```html
<body>
    <div class="app" inert>
        <main>
            <h1>Fix checkout bug</h1>
            <template data-info-popup>
                <p>Details of the task "Fix checkout bug".</p>
                <p>The task behind a confirmation modal, shown after choosing delete.</p>
            </template>
            <a href="../Tasks/initial.html">All tasks</a>
            <template data-info-popup><p>→ Tasks/initial</p></template>
        </main>
    </div>

    <div class="modal-overlay">
        <div class="modal" role="dialog" aria-modal="true" aria-labelledby="modal-title">
            <h2 id="modal-title">Delete this task?</h2>
            <template data-info-popup>
                <p>Details of the task "Fix checkout bug".</p>
                <p>The task behind a confirmation modal, shown after choosing delete.</p>
            </template>
            <a href="../TaskCheckoutBug/initial.html">Cancel</a>
            <template data-info-popup><p>→ TaskCheckoutBug/initial</p></template>
            <a href="../Tasks/checkout_bug_deleted.html">Delete task</a>
            <template data-info-popup><p>→ Tasks/checkout_bug_deleted</p></template>
        </div>
    </div>
</body>
```

### The Test Hub

```html
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Worklist test hub</title>
    <base target="_blank">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/MateusMoutinhoOrg/Lethe@main/Lib/test-hub.css">
</head>

<body class="test-hub">
    <main>
        <h1>Worklist test hub</h1>
        <p>Start at <a href="Pages/LoginScreen/initial.html">LoginScreen/initial</a> and log in with <code>user@example.com</code> and <code>password123</code>.</p>

        <section>
            <h2>LoginScreen</h2>
            <p>Authentication of an existing user.</p>
            <ul>
                <li><a href="Pages/LoginScreen/initial.html">initial</a> Empty login form, shown when the user logs out.</li>
                <li><a href="Pages/LoginScreen/invalid_credentials.html">invalid_credentials</a> Empty login form with an error, shown after submitting wrong credentials.</li>
            </ul>
        </section>
    </main>
</body>

</html>
```

## Publishing

In the repository's Settings → Pages, choose **Deploy from a branch**, with the default branch and `/ (root)`. The site is served from `https://<owner>.github.io/<repository>/`, and every push to that branch publishes it.
