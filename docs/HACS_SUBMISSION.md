# HACS submission checklist

Prepared for later submission. This document is not a claim of acceptance or completed validation.

Repository: https://github.com/gert-bezuidenhout/ha.smartrace-receiver
Category: integration

## Before submitting

- [ ] Confirm a fresh custom-repository install through HACS and successful setup in Home Assistant.
- [ ] Confirm restart, reload and update behaviour on a supported Home Assistant version; document the tested versions.
- [ ] Set a repository description: "SmartRace Receiver for Home Assistant".
- [ ] Set repository topics: home-assistant, hacs, smartrace, custom-integration.
- [ ] Keep Issues enabled and the repository public and active.
- [ ] Confirm GitHub recognises the MIT LICENSE.
- [ ] Run both jobs in Validate and resolve every failure; do not add ignored checks.
- [ ] Review branding rights and ensure the included brand/icon.png is accepted by validation.
- [ ] Publish a full GitHub release after validation passes (not only a tag), matching manifest.json version.
- [ ] Check the latest [HACS inclusion requirements](https://www.hacs.xyz/docs/publish/include/) again.

## Later submission

Create a branch from master in a fork of hacs/default. Add "gert-bezuidenhout/ha.smartrace-receiver" alphabetically to its integration list, following its existing JSON format. Complete the current pull-request template accurately and allow maintainer edits. Submit only after all checks above are complete.

Suggested title: Add gert-bezuidenhout/ha.smartrace-receiver
Suggested summary: Adds SmartRace Receiver for Home Assistant, a community integration with UI setup. Validation and release links should be inserted after they exist.

No HACS default-list submission is made by adding these preparation files.
