# Track activity fees and payment status

## Problem

The application has no way to record activity fees or communicate whether a fee is due, paid, or overdue.

## Proposed outcome

Add staff-managed payment records and student/parent views of payment status. The initial scope is tracking and reporting, not processing card payments.

## Acceptance criteria

- Authorized staff can record a fee for a student and activity/group.
- Payment records have a clear status such as due, paid, waived, or overdue, and can include due date and amount.
- Authorized staff can record an offline payment and its date.
- Students/parents can see payment information only for students they are authorized to view.
- Payment changes are persisted and errors are reported.
- The interface does not imply that online payment processing is available unless that is implemented separately.
