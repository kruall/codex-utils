# TM_TUI Refactoring Plan

This document summarizes code review findings for the Textual TUI
implementation (`task_manager/tui.py`) and lists follow-up tasks.

## Findings

- All UI logic resides in a single `TMApp` class with large `on_button_pressed` method.
- Screens are assembled imperatively without reusing components, making
  future extensions difficult.
- There is no keyboard navigation beyond the default button focus.
- No automated tests cover the TUI behaviour.

## Created tasks

- **TM_TUI-4** – Refactor TUI into separate screen classes and components.
- **TM_TUI-5** – Implement keyboard navigation and focus management.
- **TM_TUI-6** – Add tests for the TUI using Textual's testing utilities.
- **TM_TUI-7** – Simplify event handling using custom message objects.

These tasks will improve maintainability and user experience of the TUI.
