# Arquiproto

A minimal standard for prototyping web applications as a set of memoryless states.

## Principle

A prototype has no memory, only states. Every action ends in a redirect to a state, and everything that was on screen is lost.

## Structure

```
index.html            default entry of the site, redirects to the first state
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
- `Lib/` in this repository holds the libraries of the architecture, such as the [Info Popup](#info-popup). A project loads them by URL, so it doesn't need this folder.

## Rules

1. **A state never changes.** Opening a state always shows the same thing, wherever the user came from.
2. **Nothing is remembered.** Storage (`localStorage`, `sessionStorage`, IndexedDB, cookies), URL parameters (query string, hash) and requests for data (`fetch`, `XMLHttpRequest`) are forbidden. Loading files from `Assets/` and the Info Popup library is allowed.
3. **Every action ends in a redirect.** An action is a click on a link or button, or a submit; filling a form field (typing, choosing an option, ticking a box) or scrolling is not an action. The target can be another state or the same one, on the same page or another. An action never changes the current screen: an error message, an open modal and a selected tab are other states. Opening or closing an Info Popup is not an action: it documents the prototype and is not part of the screen. A modal of the product is still another state.
4. **Conditions only read the current screen.** An action can check current input values against fixed values, against each other, or for length or format. Every condition has an `else`, so every path ends in a redirect.
5. **A state stands alone.** Each `<state>.html` holds its whole screen, including every link, with no framework or build step, and works when opened directly in a browser. The only shared files are the styles and form behavior in `Assets/` and the [Info Popup](#info-popup) library. They never add markup or links to the screen, except for `info-popup.js`, the only shared file that adds markup, limited to the `?` button and the popup, with no links. Actions are plain links. Forms use `novalidate`, because browser validation would block the redirect, and `onSubmit` from `Assets/js/app.js`, which sets `location.href`, because a native submit would add `?` to the URL, and resets the form on `pageshow`, because the browser's back button would restore typed values. A page's conditions live in `Assets/js/<Page>.js`, loaded as a classic script, because browsers block modules on `file://`.
6. **Every state documents itself.** Every action of rule 3 has an Info Popup next to it, and every state has one next to its `<h1>`. A state with a modal repeats that one next to the modal's title, because the `<h1>` behind the modal can't be clicked.
7. **The site has one default entry.** The `index.html` at the root is what opens when no state is named. It is not a state: it has no screen and only redirects to the first state, with `<meta http-equiv="refresh">`.

## Info Popup

A `?` button next to a component, which opens a popup explaining what the action does and which states it leads to. It is a library of the architecture, not a file of the project: it lives in `Lib/` of [this repository](https://github.com/NEWMOLJUD/Arquiproto_provisorio), which is public, and depends on nothing else.

### Usage

Load the two files in each state from their public URL:

```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/NEWMOLJUD/Arquiproto_provisorio@main/Lib/info-popup.css">
<script src="https://cdn.jsdelivr.net/gh/NEWMOLJUD/Arquiproto_provisorio@main/Lib/info-popup.js"></script>
```

Then put a `<template data-info-popup>` right after the component, with the popup's text inside. A `<template>` renders nothing, so the state works the same without the script.

```html
<button class="btn btn-primary btn-block">Log in</button>
<template data-info-popup>
    <ul>
        <li>if email or password is empty → LoginScreen/required_fields</li>
        <li>if email is user@example.com and password is password123 → Home/initial</li>
        <li>else → LoginScreen/invalid_credentials</li>
    </ul>
</template>
```

The script adds one `?` button per template. The popup closes with its × button, with Esc or with a click outside it, and neither opening nor closing it redirects or changes the rest of the screen.

### Content

- Write in the language of the app.
- Use only text, with no links, buttons or forms. Every link stays in the state itself.
- Next to an action, write one line per path: `if <condition> → <Page>/<state>`, ending in `else → <Page>/<state>`. A plain link has a single line: `→ <Page>/<state>`.
- Match the real behavior, which is the link's `href` or the conditions in `Assets/js/<Page>.js`.
- Next to the `<h1>`, write two paragraphs with one sentence each: what the page is for, then what the user sees and when.
- An item without an action, such as a field, a text or an error message, has no popup, because it is already on the screen.

### Loading

Don't load the files from `raw.githubusercontent.com`, because browsers block a script served as `text/plain`.

Without a connection the `?` buttons don't appear and the state keeps working. To keep them offline, copy `Lib/` to the project's root and load the files by relative path, as the example app does:

```html
<link rel="stylesheet" href="../../Lib/info-popup.css">
<script src="../../Lib/info-popup.js"></script>
```

## Example

`Pages/` holds Worklist, a small task manager with 60 states in 21 pages. Open `index.html` in a browser to run it and log in with `user@example.com` and `password123`.

```
LoginScreen/initial
  log in with the demo login    → Home/initial
  log in with an empty field    → LoginScreen/required_fields
  log in with anything else     → LoginScreen/invalid_credentials
  forgot password               → ForgotPassword/initial
  create account                → CreateAccount/initial

CreateAccount/initial
  create with valid fields      → OnboardingWorkspace/initial
  create with invalid fields    → one error state per check

OnboardingWorkspace/initial     → OnboardingInvite/initial
OnboardingInvite/initial        → OnboardingProject/initial
OnboardingProject/initial       → Home/welcome

Home/initial
  stats, tasks and projects     → Tasks/open, Tasks/done, Projects/initial, Task<Name>/initial, Project<Name>/initial

Tasks/initial
  tabs                          → Tasks/open, Tasks/done
  search with "release"         → Tasks/search_results
  search with anything else     → Tasks/no_results
  new task                      → NewTask/initial → Tasks/task_created
  task row                      → Task<Name>/initial

Task<Name>/initial
  mark as done or reopen        → Task<Name>/completed or Task<Name>/reopened
  edit                          → Task<Name>Edit/initial → Task<Name>/saved
  delete                        → Task<Name>/delete_confirm → Tasks/<name>_deleted

Projects/initial
  new project                   → Projects/new_project → Projects/project_created
  project card                  → Project<Name>/initial

SettingsProfile/initial, SettingsNotifications/initial, SettingsSecurity/initial
  delete account                → SettingsSecurity/delete_account → LoginScreen/account_deleted
```

Because nothing is remembered:

- `Home/initial` always shows Sam Taylor and 2 open tasks, even after creating another account or completing a task.
- `Tasks/task_created` always shows the same new row, whatever title was typed.
- `Tasks/checkout_bug_deleted` hides that task, but it is back on any other state.

Because every page has an `initial` state, each task and project is a page of its own, such as `TaskCheckoutBug`.
