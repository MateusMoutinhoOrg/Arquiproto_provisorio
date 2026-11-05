# Arquiproto

A minimal standard for prototyping web applications as a set of memoryless states.

## Principle

A prototype has no memory, only states. Every action ends in a redirect to a state, and everything that was on screen is lost.

## Structure

```
index.html            entry point, redirects to the first state
Assets/
  css/app.css         styles of all states
  js/app.js           form behavior of all states
  js/<Page>.js        form conditions of a page
Pages/
  <Page>/
    description.md
    states/
      initial/
        description.md
        index.html
      <state>/...
```

- A state's address is `<Page>/<state>`, for example `LoginScreen/initial`.
- Pages use `PascalCase` and states use `snake_case`.
- Every page has an `initial` state.

## Rules

1. **A state never changes.** Opening a state always shows the same thing, wherever the user came from.
2. **Nothing is remembered.** Storage (`localStorage`, `sessionStorage`, IndexedDB, cookies), URL parameters (query string, hash) and requests for data (`fetch`, `XMLHttpRequest`) are forbidden. Loading files from `Assets/` is allowed.
3. **Every action ends in a redirect.** An action is a click on a link or button, or a submit; filling a form field (typing, choosing an option, ticking a box) or scrolling is not an action. The target can be another state or the same one, on the same page or another. An action never changes the current screen: an error message, an open modal and a selected tab are other states.
4. **Conditions only read the current screen.** An action can check current input values against fixed values, against each other, or for length or format. Every condition has an `else`, so every path ends in a redirect.
5. **A state stands alone.** Each `index.html` holds its whole screen, including every link, with no framework or build step, and works when opened directly in a browser. The only shared files are in `Assets/`: styles and form behavior. They never add markup or links to the screen. Actions are plain links. Forms use `novalidate`, because browser validation would block the redirect, and `onSubmit` from `Assets/js/app.js`, which sets `location.href`, because a native submit would add `?` to the URL, and resets the form on `pageshow`, because the browser's back button would restore typed values. A page's conditions live in `Assets/js/<Page>.js`, loaded as a classic script, because browsers block modules on `file://`.

## Documents

There are only two templates. Their sections are fixed and follow this order.

### Page

`Pages/<Page>/description.md` defines the items and actions shared by all states of the page.

```md
# <Page>

<One sentence: what the page is for.>

## Items

- <item without action>
- <item> → <Page>/<state>
- <item>
  - if <condition> → <Page>/<state>
  - else → <Page>/<state>
```

### State

`Pages/<Page>/states/<state>/description.md` only describes how the state differs from the page.

```md
# <Page>/<state>

<One sentence: what the user sees and when.>

## Items

- <only items this state adds or replaces>
```

An item replaces the page item with the same name. Omit `## Items` when the state has no differences.

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
