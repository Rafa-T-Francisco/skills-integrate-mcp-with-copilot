# Enforce activity capacity and support waitlists

## Problem

Activities display remaining places, but the signup endpoint does not enforce the maximum participant limit. As a result, concurrent or later signups can exceed the stated capacity.

## Proposed outcome

Enforce capacity when processing signups and offer an explicit waitlist when an activity is full.

## Acceptance criteria

- The server rejects a signup or places the student on a waitlist when an activity is at capacity; it never silently overbooks.
- Duplicate signups continue to be rejected.
- A waitlisted student receives a clear response and the UI distinguishes waitlisted from confirmed participants.
- When a confirmed participant unregisters, the system follows a documented policy for the newly available place (for example, promoting the next student in queue).
- Capacity decisions remain correct when two signup requests arrive at nearly the same time.
