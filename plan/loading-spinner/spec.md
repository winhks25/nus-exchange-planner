# Feature: Consistent page loading spinner

Date: 2026-10-21. Status: task planning only.

## Confirmed scope

Show a simple centered spinner in the main content area on Recommend (`/`) and Compare (`/compare`) during initial loading, pending route loading, and result fetching after a selection. The user confirmed that the header and sidebar stay visible. Use the existing theme tokens. No skeletons, animation library, artificial waiting period, or backend changes.

### US1 — Page and route loading (P1, MVP)

As a student, I see the same loading indicator when opening either page or navigating to a page that is still loading, with navigation available throughout.

Acceptance:
- Direct entry and refresh on both routes show the spinner while the catalog is pending, then show page content or the existing error message.
- Pending route boundaries and Compare's existing Suspense fallback use the same loading component. Cached/instant transitions need no forced animation.
- Initial loading replaces page content inside the shell; it does not cover the header/sidebar. The application can only render its loading UI once its initial HTML arrives.
- One readable status message accompanies a decorative spinner. Existing catalog status wording is preserved. Respect reduced-motion preferences with a static indicator and status text.
- The component fits mobile and desktop without overflow or duplicate main landmarks/status announcements.

### US2 — Result loading (P1)

As a student, I see the same spinner while recommendations or mappings are being fetched, and can continue using the page's selectors and navigation.

Acceptance:
- Show the indicator centered in the results area while retaining the hero and selectors. Preserve “Finding partner universities…” and “Loading mappings…” status wording.
- Success, empty results, and errors replace loading with the appropriate existing view.
- Clearing a selection, changing it quickly, or navigating away does not leave a stuck indicator or allow obsolete responses to overwrite current results.
- A valid Compare deep link progresses from catalog loading into mapping loading without showing a misleading empty state between dependent requests.

No new automated test suite is requested. Verify these scenarios manually and run existing relevant checks during implementation.
