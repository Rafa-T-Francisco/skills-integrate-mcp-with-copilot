# Add student and parent activity dashboards

## Problem

The current page is a shared public catalog. Students and parents cannot sign in to see their own activity applications, registrations, schedules, or status updates.

## Proposed outcome

Provide authenticated, role-appropriate views for students and parents to review a student's activity participation and enrollment status.

## Acceptance criteria

- A student can view their own registrations and application statuses.
- A parent can view the students linked to their account and each student's registrations.
- Views distinguish confirmed, pending, waitlisted, and cancelled states where those states are supported.
- A user cannot view another student's private information without an authorized relationship.
- Public catalog browsing remains available according to the school's chosen access policy.
- Authentication and role checks build on existing issue #5 rather than introducing a conflicting login system.
