# Make school identity and branding configurable

## Problem

The app's school name and visual identity are currently fixed in the frontend. Reusing the application for another school would require editing source code.

## Proposed outcome

Move school-specific identity and presentation settings into deployment configuration, including school name, logo, and brand colors.

## Acceptance criteria

- The school name, logo, and supported brand colors can be configured without editing application source.
- Sensible defaults are used when optional branding values are not supplied.
- Invalid configuration is surfaced clearly and does not break page rendering.
- Branding changes are applied consistently across the catalog and sign-up interface.
- School-specific settings do not cause one deployment to display another school's identity.
