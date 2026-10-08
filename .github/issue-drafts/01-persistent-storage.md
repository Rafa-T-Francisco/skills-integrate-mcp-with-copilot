# Persist activities and registrations across restarts

## Problem

The application currently stores activities and participants in memory. Any restart loses registrations and resets activity data, so the app cannot reliably serve as the school's ongoing sign-up system.

## Proposed outcome

Store activities and registrations in durable storage so updates survive application restarts and are shared between users.

## Acceptance criteria

- Activity records and student registrations survive an application restart.
- Signup and unregister operations update persistent records.
- The API continues to return the existing activity response shape unless an intentional API change is documented.
- Storage failures are reported to the caller rather than appearing as successful updates.
- The implementation documents how to initialize and run the storage locally.

## Related work

Issue #3 covers moving activity definitions out of the Python source file. This issue is about durable runtime storage, not just separating static activity data into a file.
