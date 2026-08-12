# Accessibility statement

Fairshift Lab is designed toward WCAG 2.2 Level AA. Accessibility is treated as a
release requirement, not an optional visual polish step. This statement covers the public
interactive laboratory at https://fairshift-lab.lindgreendavid.chatgpt.site.

## What is supported

- Semantic landmarks, ordered headings, a skip link, descriptive page title, and visible
  keyboard focus.
- Full keyboard operation for every experiment control; no drag-only custom interaction.
- Minimum 44-by-44-pixel interactive targets where layout permits, exceeding WCAG 2.2's
  24-by-24-pixel AA minimum.
- Text and pattern cues in addition to color, plus high-contrast and forced-color modes.
- Text summaries and data tables for charts so that visual plots are not the only way to
  obtain the result.
- Polite announcements for updated result interpretation without moving focus.
- Reflow down to a 320 CSS-pixel viewport and support for 200% text zoom without hiding
  navigation destinations.
- Reduced-motion support and no autoplay, flashing, time limit, authentication, audio, or
  video.

## Verification

Every change passes semantic HTML assertions and `eslint-plugin-jsx-a11y`. The release
checklist also covers keyboard order, focus visibility, non-text alternatives, labels,
status announcements, zoom/reflow, reduced motion, target size, and color-independent
meaning. Automated checks cannot prove accessibility or compatibility with every
assistive-technology combination.

## Known limitations

- Browser-generated random samples can create dense tables; summaries are provided before
  detail, but the full threshold table is intentionally long.
- Mathematical notation is expressed as Unicode and plain text rather than MathML.
- The interface and documentation are currently in English.

## Feedback

Open an accessibility issue at
https://github.com/lindgreendavid/fairshift-lab/issues/new and include the page section,
browser, assistive technology, and expected behavior when possible. Security-sensitive
reports should use the private process in [`SECURITY.md`](SECURITY.md).

## Standard

The target is the W3C Web Content Accessibility Guidelines 2.2 Level AA:
https://www.w3.org/TR/WCAG22/. Conformance language is intentionally bounded: this is an
engineering statement and testing record, not a third-party accessibility certification.
