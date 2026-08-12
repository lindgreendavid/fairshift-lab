# Security policy

## Supported version

Security fixes are applied to the latest Fairshift Lab release. The project is research and educational software; it must not be used for high-impact decisions or exposed as an unreviewed data-processing service.

## Reporting a vulnerability

Please use GitHub's private vulnerability-reporting flow for this repository. Do not include secrets, personal data, or exploit payloads in a public issue.

## Dependency boundary

CI rejects known high-severity vulnerabilities in production dependencies. Release `0.3.0` also updates the web build chain to patched versions of React Server Components, Vite, Wrangler, Undici, Sharp, and WebSocket dependencies.

The development-only `image-size` package currently has two published denial-of-service advisories ([ICNS](https://github.com/advisories/GHSA-w3rx-r6r6-pgpr), [JXL/HEIF](https://github.com/advisories/GHSA-5p2g-fcmc-qvqq)) with no patched npm release. It is a transitive Vinext build dependency, is absent from the deployed worker bundle, and Fairshift Lab accepts no file uploads or remote image input. The residual build-time risk remains tracked until an upstream fix is available.
