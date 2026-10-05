# Documentation

This documentation is kept in its own repository, separate from the package, so it is not part of what users install and Unity never imports it. GitBook publishes it through Git Sync. `gitbook-docs.yaml` describes the site and its two spaces, English and Vietnamese, and `.gitbook.yaml` names `README.md` and `SUMMARY.md`; both files sit at the root of the documentation.

## Structure

| Section | Purpose |
|---|---|
| Getting started | A new user installs the package and builds a small game step by step |
| Concepts | How the package works: layers, tick, authority, replication, prediction |
| Core, Messaging, Synchronization, Prediction, Physics, Transports, Server, Unity | One guide per feature, with working code |
| Advanced | Custom codecs, performance, debugging |
| Examples | Existing games ported with the package, step by step, with their real code and commits. Generic explanations stay in the feature guides and are linked from here |
| Reference | Short, exact descriptions of the public API, for lookup |
| Contributing | Working on the package and on these pages |

`SUMMARY.md` is the table of contents, and every page must be listed in it.

## Rules

- Write the English pages in plain technical prose. Use sentence case for headings.
- Describe the current code. A feature that is not implemented is marked as such and not described as if it worked.
- Check every type, member and message against the source before writing it down.
- Code examples compile against the current API and use the generated adapter names, such as `ShotNetAdapter.Instance`.
- Use the same name for the same thing everywhere: `NetworkObject`, `NetworkBehaviour`, `NetworkManager`, prediction, reconciliation, rollback, replay.
- Link related pages with relative links, and keep links to headings working when you rename a heading.
- Use GitBook hints (`{% hint style="warning" %}`) only for warnings a reader must not miss.

## Vietnamese translation

The Vietnamese pages live in `vi/`, with their own `README.md` and `SUMMARY.md`, and mirror the English pages file for file. GitBook publishes them as a second space with the language set to `vi`, so readers switch languages from the language picker.

The English pages are the source. When you change an English page, change the Vietnamese page at the same path in the same commit. A Vietnamese page keeps the code blocks of its English page unchanged and has the same headings in the same order. Each translated heading ends with an anchor tag that carries the English anchor, such as `## Teleport <a href="#teleporting" id="teleporting"></a>`, so links to headings work in both languages. Technical terms such as model, codec, tick, peer and owner stay in English in the Vietnamese text.

## Open questions

`DOCUMENTATION-TODO.md` at the root of the documentation lists what the documentation could not settle from the code. It is not part of the published table of contents.
