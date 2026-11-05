# Arquiproto

A minimal standard for prototyping web applications as a set of memoryless states.

## Principle

A prototype has no memory, only states. Every action ends in a redirect to a state, and everything that was on screen is lost.

## Structure

```
index.html            entry point, redirects to the first state
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
2. **Nothing is remembered.** Storage (`localStorage`, `sessionStorage`, IndexedDB, cookies), URL parameters (query string, hash) and network requests are forbidden.
3. **Every action ends in a redirect.** An action is a click or a submit; typing or scrolling is not an action. The target can be another state or the same one, on the same page or another. An action never changes the current screen: an error message, an open modal and a selected tab are other states.
4. **Conditions only read the current screen.** An action can compare current input values with fixed values. Every condition has an `else`, so every path ends in a redirect.
5. **A state stands alone.** Each `index.html` is a single file, with no framework, build step or shared files, and works when opened directly in a browser. Actions are plain links. Forms use a short inline script that sets `location.href`, because a native submit would add `?` to the URL, and `novalidate`, because browser validation would block the redirect. The script also resets the form on `pageshow`, because the browser's back button would restore typed values.

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

`Pages/` holds a working login flow. Open `index.html` in a browser to run it.

```
LoginScreen/initial
LoginScreen/email_already_exists
  confirm with user@example.com → Home/initial
  confirm with any other email  → LoginScreen/email_already_exists
  create account                → CreateAccount/initial

CreateAccount/initial
  create                        → Home/initial
  back to login                 → LoginScreen/initial

Home/initial
  logout                        → LoginScreen/initial
```

`Home/initial` always shows `user@example.com`, even after creating an account with another email, because nothing is remembered.
