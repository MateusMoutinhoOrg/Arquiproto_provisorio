#!/usr/bin/env python3
"""Checks a Lethe prototype against the rules a script can verify.

    python3 check.py [project root]

Prints one line per problem and exits with 1 if there is any, or with 2 if the
folder isn't a Lethe project. It needs only the standard library.

A clean run doesn't prove everything: whether a state really never changes,
whether a popup's sentences are true and how the screen looks are left to a reader.
"""

import os
import re
import sys
from html.parser import HTMLParser

VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}
FIELD_CONTROLS = {"submit", "button", "image", "reset"}
ADDRESS = r"[A-Z][A-Za-z0-9]*/[a-z][a-z0-9_]*"

FORBIDDEN_JS = [
    (2, r"\b(localStorage|sessionStorage|indexedDB)\b|document\.cookie", "uses storage"),
    (2, r"location\.(search|hash)|URLSearchParams|history\.(pushState|replaceState)", "uses the URL to keep state"),
    (2, r"\bfetch\s*\(|XMLHttpRequest|\bimport\s*\(", "requests data"),
    (3, r"\.(innerHTML|outerHTML|innerText|textContent|hidden|style|className|classList)\b"
        r"|createElement|appendChild|insertAdjacent|\.(append|prepend|remove|setAttribute)\s*\(", "changes the screen"),
    (3, r"\b(alert|confirm|prompt)\s*\(", "opens a browser dialog"),
    (4, r"Math\.random|\bDate\b|navigator\.|document\.referrer|history\.length|window\.name",
        "reads something other than the current screen"),
    (5, r"^\s*(import|export)\s", "is a module, which browsers block on file://"),
]


class Node:
    def __init__(self, tag, attrs=(), parent=None):
        self.tag = tag
        self.attrs = dict(attrs)
        self.parent = parent
        self.children = []

    def walk(self):
        for child in self.children:
            if isinstance(child, Node):
                yield child
                yield from child.walk()

    def find_all(self, *tags):
        return [node for node in self.walk() if node.tag in tags]

    def text(self):
        parts = [child if isinstance(child, str) else child.text() for child in self.children]
        return " ".join("".join(parts).split())

    def next_element(self):
        """The element right after this one, or None if text comes first."""
        siblings = self.parent.children
        for item in siblings[siblings.index(self) + 1:]:
            if isinstance(item, Node):
                return item
            if item.strip():
                return None
        return None

    def previous_element(self):
        """The element right before this one, or None if text comes first."""
        siblings = self.parent.children
        for item in reversed(siblings[:siblings.index(self)]):
            if isinstance(item, Node):
                return item
            if item.strip():
                return None
        return None

    def inside(self, *tags):
        node = self.parent
        while node is not None:
            if node.tag in tags:
                return node
            node = node.parent
        return None

    def __str__(self):
        label = self.attrs.get("href") or self.text()
        return "<{}> {!r}".format(self.tag, label[:50])


class Parser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Node("#root")
        self.current = self.root

    def handle_starttag(self, tag, attrs):
        node = Node(tag, attrs, self.current)
        self.current.children.append(node)
        if tag not in VOID:
            self.current = node

    def handle_startendtag(self, tag, attrs):
        self.current.children.append(Node(tag, attrs, self.current))

    def handle_endtag(self, tag):
        node = self.current
        while node is not self.root and node.tag != tag:
            node = node.parent
        if node is not self.root:
            self.current = node.parent

    def handle_data(self, data):
        self.current.children.append(data)


class Project:
    def __init__(self, root):
        self.root = root
        self.problems = []
        self.warnings = []
        self.files = set()
        # Comes from a listing, so a path with the wrong case doesn't match, even on macOS.
        for folder, dirs, names in os.walk(root):
            dirs[:] = [name for name in dirs if not name.startswith(".")]
            for name in names:
                if not name.startswith("."):
                    path = os.path.relpath(os.path.join(folder, name), root)
                    self.files.add(path.replace(os.sep, "/"))
        self.states = sorted(path for path in self.files if re.fullmatch(r"Pages/[^/]+/[^/]+\.html", path))
        self.handlers = {}  # page -> form id -> addresses it can redirect to
        self.fields = {}    # (page, form id) -> fields its conditions read
        self.popups = {}    # state address -> the paragraphs of the popup next to its <h1>
        self.reached = set()

    def report(self, path, rule, message):
        self.problems.append("{}: rule {}: {}".format(path, rule, message))

    def read(self, path):
        with open(os.path.join(self.root, path), encoding="utf-8") as file:
            return file.read()

    def parse(self, path):
        parser = Parser()
        parser.feed(self.read(path))
        parser.close()
        return parser.root


def address_of(path):
    match = re.fullmatch(r"Pages/([^/]+)/([^/]+)\.html", path)
    return "{}/{}".format(match.group(1), match.group(2)) if match else None


def is_external(url):
    return re.match(r"[a-zA-Z][a-zA-Z0-9+.-]*:|//", url) is not None


def resolve(path, url):
    return os.path.normpath(os.path.join(os.path.dirname(path), url)).replace(os.sep, "/")


def strip_comments(source):
    source = re.sub(r"/\*.*?\*/", "", source, flags=re.S)
    return re.sub(r"(^|\s)//.*", "", source)


def closing_brace(source, opening):
    """The index of the brace that closes the one at `opening`, ignoring strings."""
    depth = 0
    quote = None
    index = opening
    while index < len(source):
        char = source[index]
        if quote:
            if char == "\\":
                index += 1
            elif char == quote:
                quote = None
        elif char in "\"'`":
            quote = char
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return index
        index += 1
    return -1


def ends_in_redirect(body):
    """Whether the last statement of a function always redirects, so every path has an else."""
    body = body.strip()
    if body.endswith("}"):
        depth = 0
        for index in range(len(body) - 1, -1, -1):
            if body[index] == "}":
                depth += 1
            elif body[index] == "{":
                depth -= 1
                if depth == 0:
                    return body[:index].rstrip().endswith("else")
        return False
    last = re.split(r"[;{}]", body.rstrip("; \n"))[-1].strip()
    last = re.sub(r"^else\s+", "", last)
    return last.startswith("return") and re.search(ADDRESS, last) is not None


def check_structure(project):
    if not os.path.isfile(os.path.join(project.root, ".nojekyll")):
        project.report(".nojekyll", 8, "missing, so GitHub Pages would run Jekyll")
    elif os.path.getsize(os.path.join(project.root, ".nojekyll")) != 0:
        project.report(".nojekyll", 8, "should be empty")
    if "Assets/css/app.css" not in project.files:
        project.report("Assets/css/app.css", 5, "missing, it holds the styles of all states")

    pages_dir = os.path.join(project.root, "Pages")
    for page in sorted(os.listdir(pages_dir)):
        if os.path.isdir(os.path.join(pages_dir, page)):
            if not re.fullmatch(r"[A-Z][A-Za-z0-9]*", page):
                project.report("Pages/" + page, "structure", "a page's name uses PascalCase")
            if "Pages/{}/initial.html".format(page) not in project.files:
                project.report("Pages/" + page, "structure", "every page has an initial state")

    for path in sorted(project.files):
        if path.startswith("Pages/") and path not in project.states:
            project.report(path, "structure", "Pages/ holds only <Page>/<state>.html files")
    for path in project.states:
        if not re.fullmatch(r"[a-z][a-z0-9_]*", path.split("/")[2][:-len(".html")]):
            project.report(path, "structure", "a state's name uses snake_case")


def check_scripts(project):
    pages = {path.split("/")[1] for path in project.states}
    scripts = sorted(path for path in project.files if re.fullmatch(r"Assets/js/[^/]+\.js", path))
    for path in scripts:
        source = strip_comments(project.read(path))
        for rule, pattern, message in FORBIDDEN_JS:
            match = re.search(pattern, source, flags=re.M)
            if match:
                project.report(path, rule, "{} ({})".format(message, match.group(0).strip()))

        page = path.split("/")[2][:-len(".js")]
        if page == "app":
            continue
        if page not in pages:
            project.report(path, 5, "a script in Assets/js/ is named after a page, and {} isn't one".format(page))

        handlers = project.handlers.setdefault(page, {})
        for match in re.finditer(r"""onSubmit\(\s*["']([^"']+)["']""", source):
            form_id = match.group(1)
            opening = source.find("{", match.end())
            closing = closing_brace(source, opening)
            if opening == -1 or closing == -1:
                project.report(path, 4, "can't read the conditions of the form {!r}".format(form_id))
                continue
            body = source[opening + 1:closing]
            handlers[form_id] = set(re.findall(r"""["'](""" + ADDRESS + r""")["']""", body))
            parameter = re.search(r"function\s*\(\s*(\w+)", source[match.end():opening])
            if parameter:
                project.fields[(page, form_id)] = set(re.findall(r"\b" + parameter.group(1) + r"\.(\w+)", body))
            if not ends_in_redirect(body):
                project.report(path, 4, "the form {!r} has a path with no redirect: end it with a return or an else".format(form_id))
            for target in handlers[form_id]:
                project.reached.add(target)
                if "Pages/{}.html".format(target) not in project.files:
                    project.report(path, 3, "the form {!r} redirects to {}, which doesn't exist".format(form_id, target))


def paths_of(project, path, template, component):
    """The addresses in a popup of an action, checking the notation of its lines."""
    items = [node.text() for node in template.find_all("p", "li")] or [template.text()]
    targets = set()
    for line in items:
        match = re.fullmatch(r"(.*?)\s*→\s*(" + ADDRESS + r")", line)
        if not match:
            project.report(path, 6, "the popup of {} has a line that doesn't end in → <Page>/<state>: {!r}".format(component, line[:60]))
            continue
        targets.add(match.group(2))
        if len(items) > 1 and not match.group(1):
            project.report(path, 6, "the popup of {} has several paths, and each one needs its condition".format(component))
    return targets


def popup_after(project, path, component):
    template = component.next_element()
    if template is None or template.tag != "template" or "data-info-popup" not in template.attrs:
        project.report(path, 6, "{} has no Info Popup right after it".format(component))
        return None
    return template


def check_head(project, path, tree, page, has_form):
    links = [node for node in tree.find_all("link") if node.attrs.get("rel") == "stylesheet"]
    scripts = tree.find_all("script")
    urls = [node.attrs.get("href", "") for node in links] + [node.attrs.get("src", "") for node in scripts]

    for name in ("info-popup.css", "info-popup.js"):
        if not any(url.endswith("/" + name) for url in urls):
            project.report(path, 6, "doesn't load {}".format(name))
    for url in urls:
        if "raw.githubusercontent.com" in url:
            project.report(path, 5, "loads {} from raw.githubusercontent.com, which browsers block".format(url))

    loaded = {}
    for script in scripts:
        src = script.attrs.get("src")
        if not src:
            project.report(path, 5, "has an inline script, and a page's conditions live in Assets/js/{}.js".format(page))
        elif script.attrs.get("type") == "module":
            project.report(path, 5, "loads {} as a module, which browsers block on file://".format(src))
        elif is_external(src):
            if not src.endswith("/info-popup.js"):
                project.report(path, 5, "loads {}, and a state has no framework".format(src))
        else:
            resolved = resolve(path, src)
            loaded[resolved] = script
            allowed = {"Assets/js/app.js", "Assets/js/{}.js".format(page)}
            if resolved not in allowed and not resolved.endswith("/info-popup.js"):
                project.report(path, 5, "loads {}, and only app.js and {}.js are its scripts".format(src, page))

    for link in links:
        href = link.attrs.get("href", "")
        if is_external(href):
            if not href.endswith("/info-popup.css"):
                project.report(path, 5, "loads {}, and the shared styles live in Assets/".format(href))
        elif not resolve(path, href).startswith("Assets/css/") and not href.endswith("/info-popup.css"):
            project.report(path, 5, "loads {}, and the shared styles live in Assets/css/".format(href))

    if has_form:
        order = list(tree.walk())
        app = loaded.get("Assets/js/app.js")
        conditions = loaded.get("Assets/js/{}.js".format(page))
        if app is None or conditions is None:
            project.report(path, 5, "has a form, so it loads Assets/js/app.js and Assets/js/{}.js".format(page))
        else:
            last_form = max(order.index(form) for form in tree.find_all("form"))
            if not order.index(app) < order.index(conditions):
                project.report(path, 5, "loads {}.js before app.js, which defines onSubmit".format(page))
            if order.index(conditions) < last_form and "defer" not in conditions.attrs:
                project.report(path, 5, "loads {}.js before its form exists, so the form would submit natively".format(page))


def check_local_paths(project, path, tree):
    for node in tree.walk():
        for attribute in ("src", "href"):
            url = node.attrs.get(attribute)
            if not url or url.startswith("#") or is_external(url) or node.tag == "a":
                continue
            if url.startswith("/"):
                project.report(path, 8, "{} uses an absolute path".format(url))
            elif resolve(path, url.split("#")[0].split("?")[0]) not in project.files:
                project.report(path, 8, "{} doesn't exist, or its case doesn't match the file".format(url))


def check_link(project, path, link):
    href = link.attrs.get("href")
    if not href:
        project.report(path, 3, "{} has no href, so it doesn't redirect".format(link))
        return
    if "?" in href or "#" in href:
        project.report(path, 2, "{} uses URL parameters".format(link))
        return
    if is_external(href) or href.startswith("/"):
        project.report(path, 3, "{} doesn't lead to a state by a relative path".format(link))
        return
    target = address_of(resolve(path, href))
    if target is None or "Pages/{}.html".format(target) not in project.files:
        project.report(path, 3, "{} leads to a state that doesn't exist, or its case doesn't match the file".format(link))
        return
    if target != address_of(path):
        project.reached.add(target)
    template = popup_after(project, path, link)
    if template is not None and paths_of(project, path, template, link) != {target}:
        project.report(path, 6, "the popup of {} doesn't say → {}".format(link, target))


def check_button(project, path, button, page):
    form = button.inside("form")
    kind = button.attrs.get("type", "submit").lower()
    if form is None:
        project.report(path, 3, "{} is outside a form, so it can't redirect: use a link".format(button))
    elif kind in ("button", "reset"):
        project.report(path, 3, "{} has type={}, so it doesn't redirect".format(button, kind))
    template = popup_after(project, path, button)
    if template is None or form is None:
        return
    targets = project.handlers.get(page, {}).get(form.attrs.get("id"))
    written = paths_of(project, path, template, button)
    if targets is not None and written != targets:
        project.report(path, 6, "the popup of {} says {}, and the conditions say {}".format(
            button, sorted(written), sorted(targets)))


def check_form(project, path, form, page):
    if "novalidate" not in form.attrs:
        project.report(path, 5, "the form {!r} has no novalidate, so the browser would block the redirect".format(form.attrs.get("id")))
    for attribute in ("action", "method"):
        if attribute in form.attrs:
            project.report(path, 5, "the form {!r} has {}, and only onSubmit redirects".format(form.attrs.get("id"), attribute))
    form_id = form.attrs.get("id")
    if not form_id:
        project.report(path, 5, "a form has no id, so onSubmit can't find it")
    elif form_id not in project.handlers.get(page, {}):
        project.report(path, 5, "the form {!r} has no onSubmit in Assets/js/{}.js".format(form_id, page))
    names = {node.attrs.get("name") for node in form.find_all("input", "select", "textarea")}
    for field in sorted(project.fields.get((page, form_id), set()) - names):
        project.report(path, 4, "the conditions of the form {!r} read the field {!r}, and it has no input with that name".format(form_id, field))


def check_popup_placement(project, path, tree, modal_titles):
    for template in tree.find_all("template"):
        if "data-info-popup" not in template.attrs:
            continue
        before = template.previous_element()
        is_action = before is not None and (
            before.tag in ("a", "button", "h1") or before in modal_titles or
            (before.tag == "input" and before.attrs.get("type", "").lower() in FIELD_CONTROLS))
        if not is_action:
            project.report(path, 6, "a popup isn't right after an action, an <h1> or a modal's title: {!r}".format(template.text()[:50]))
        if template.find_all("a", "button", "form", "input", "select", "textarea"):
            project.report(path, 6, "a popup has links, buttons or forms, and it uses only text: {!r}".format(template.text()[:50]))


def check_state(project, path):
    address = address_of(path)
    page = address.split("/")[0]
    tree = project.parse(path)
    forms = tree.find_all("form")

    check_head(project, path, tree, page, bool(forms))
    check_local_paths(project, path, tree)

    for node in tree.walk():
        for attribute in node.attrs:
            if attribute.startswith("on"):
                project.report(path, 5, "{} has {}, and actions are plain links".format(node, attribute))
        if node.tag in ("details", "dialog") or "popover" in node.attrs:
            project.report(path, 3, "<{}> changes the screen without a redirect: make it another state".format(node.tag))
        if node.tag in ("iframe", "object", "embed"):
            project.report(path, 5, "<{}> brings content from elsewhere, and a state holds its whole screen".format(node.tag))

    for form in forms:
        check_form(project, path, form, page)
    for link in tree.find_all("a"):
        check_link(project, path, link)
    for node in tree.find_all("button", "input"):
        if node.tag == "button" or node.attrs.get("type", "").lower() in FIELD_CONTROLS:
            check_button(project, path, node, page)

    headings = tree.find_all("h1")
    if not headings:
        project.report(path, 6, "has no <h1>, which holds the popup of the state")
    for heading in headings:
        template = popup_after(project, path, heading)
        if template is not None:
            paragraphs = [node.text() for node in template.find_all("p")]
            if len(paragraphs) != 2:
                project.report(path, 6, "the popup of the <h1> has {} paragraphs, and it has 2".format(len(paragraphs)))
            project.popups[address] = paragraphs

    modal_titles = []
    for modal in tree.walk():
        if modal.attrs.get("role") in ("dialog", "alertdialog") or modal.attrs.get("aria-modal") == "true":
            label = modal.attrs.get("aria-labelledby")
            nodes = modal.find_all("h1", "h2", "h3", "h4", "h5", "h6")
            title = next((node for node in nodes if label and node.attrs.get("id") == label), nodes[0] if nodes else None)
            if title is None:
                project.report(path, 6, "a modal has no title to hold the popup of the state")
                continue
            modal_titles.append(title)
            template = popup_after(project, path, title)
            if template is not None and [node.text() for node in template.find_all("p")] != project.popups.get(address):
                project.report(path, 6, "the popup of the modal's title doesn't repeat the one of the <h1>")
    check_popup_placement(project, path, tree, modal_titles)


def check_page_purposes(project):
    purposes = {}
    for address, paragraphs in sorted(project.popups.items()):
        if paragraphs:
            purposes.setdefault(address.split("/")[0], {}).setdefault(paragraphs[0], address)
    for page, found in sorted(purposes.items()):
        if len(found) > 1:
            project.report("Pages/" + page, 6, "the first paragraph of the <h1>'s popup says what the page is for, and it differs in {}".format(
                ", ".join(sorted(found.values()))))


def check_hub(project):
    path = "index.html"
    if path not in project.files:
        project.report(path, 7, "missing, it is the default entry of the site")
        return
    tree = project.parse(path)

    bodies = tree.find_all("body")
    if not bodies or "test-hub" not in bodies[0].attrs.get("class", "").split():
        project.report(path, 7, "the <body> has no class test-hub")
    if not any(node.attrs.get("href", "").endswith("/test-hub.css") for node in tree.find_all("link")):
        project.report(path, 7, "doesn't load test-hub.css")
    if tree.find_all("script", "form"):
        project.report(path, 7, "has a script or a form, and the hub only lists states")
    if any("data-info-popup" in node.attrs for node in tree.find_all("template")):
        project.report(path, 7, "has an Info Popup, and the hub only lists states")
    check_local_paths(project, path, tree)

    listed = {}
    for link in tree.find_all("a"):
        href = link.attrs.get("href", "")
        target = address_of(resolve(path, href)) if not is_external(href) else None
        if target is None or "Pages/{}.html".format(target) not in project.files:
            project.report(path, 7, "{} doesn't lead to a state".format(link))
        elif link.inside("li") is None:
            project.reached.add(target)

    for section in tree.find_all("section"):
        titles = section.find_all("h2")
        page = titles[0].text() if titles else None
        if page is None:
            project.report(path, 7, "a section has no <h2> with the name of the page")
            continue
        purpose = next((node.text() for node in section.children if isinstance(node, Node) and node.tag == "p"), None)
        items = section.find_all("li")
        for number, item in enumerate(items):
            links = item.find_all("a")
            if not links:
                project.report(path, 7, "{}: an item has no link: {!r}".format(page, item.text()[:50]))
                continue
            target = address_of(resolve(path, links[0].attrs.get("href", "")))
            if target is None:
                continue
            listed[target] = listed.get(target, 0) + 1
            state = target.split("/")[1]
            if target.split("/")[0] != page:
                project.report(path, 7, "the section {} lists {}".format(page, target))
            if links[0].text() != state:
                project.report(path, 7, "the link to {} is named {!r}".format(target, links[0].text()))
            if number == 0 and state != "initial":
                project.report(path, 7, "the section {} lists {} first, and initial comes first".format(page, state))
            paragraphs = project.popups.get(target)
            if paragraphs and len(paragraphs) == 2:
                if purpose != paragraphs[0]:
                    project.report(path, 7, "the <p> of {} differs from the first paragraph of the popup of {}".format(page, target))
                if item.text()[len(links[0].text()):].strip() != paragraphs[1]:
                    project.report(path, 7, "the line of {} differs from the second paragraph of its popup".format(target))

    for state_path in project.states:
        address = address_of(state_path)
        if listed.get(address, 0) != 1:
            project.report(path, 7, "lists {} {} times, and every state appears exactly once".format(address, listed.get(address, 0)))
        if address not in project.reached:
            project.warnings.append("{}: nothing leads to this state".format(state_path))


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else "."
    if not os.path.isdir(os.path.join(root, "Pages")):
        print("{} has no Pages/ folder, so it isn't a Lethe project.".format(os.path.abspath(root)))
        return 2

    project = Project(root)
    check_structure(project)
    check_scripts(project)
    for path in project.states:
        check_state(project, path)
    check_page_purposes(project)
    check_hub(project)

    for line in project.problems:
        print(line)
    for line in project.warnings:
        print("warning: " + line)

    pages = {path.split("/")[1] for path in project.states}
    print("{} states in {} pages: {} problems, {} warnings.".format(
        len(project.states), len(pages), len(project.problems), len(project.warnings)))
    return 1 if project.problems else 0


if __name__ == "__main__":
    sys.exit(main())
