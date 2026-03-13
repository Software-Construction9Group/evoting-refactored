# National E-Voting System — Refactored

**Course:** Software Construction  
**Year:** 3, Semester 2 — Easter 2026  
**Program:** BSc Computer Science, Uganda Christian University

---

## Overview

This project is a full refactor of a monolithic National E-Voting console application into a clean, modular, object-oriented Python codebase. The application behaviour is identical to the original — same menus, same prompts, same outputs — but the internal architecture has been completely restructured to follow four key software engineering principles:

1. Modular Design  
2. Object-Oriented Design  
3. Separation of Concerns  
4. Clean Code

---

## How to Run

```bash
cd evoting
python3 main.py
```

Default admin credentials: `admin` / `admin123`

---

## Project Structure

```
evoting/
├── main.py                  # Entry point only — wires everything together
├── config.py                # Application-wide constants
│
├── ui/
│   ├── colors.py            # ANSI color codes and theme constants
│   ├── components.py        # Reusable display functions (header, table, menu)
│   └── prompts.py           # Input helpers (prompt, masked_input, pause)
│
├── models/
│   ├── candidate.py         # Candidate data class
│   ├── voter.py             # Voter data class
│   ├── admin.py             # Admin data class
│   ├── poll.py              # Poll, PollPosition, and Position classes
│   ├── station.py           # VotingStation data class
│   └── vote.py              # Vote data class
│
├── services/
│   ├── auth_service.py      # Login validation and session management
│   ├── audit_service.py     # Audit log recording
│   ├── candidate_service.py # Candidate CRUD and eligibility checks
│   ├── voter_service.py     # Voter registration, verification, password change
│   ├── station_service.py   # Voting station CRUD
│   ├── poll_service.py      # Poll and Position lifecycle management
│   ├── vote_service.py      # Ballot casting with duplicate prevention
│   ├── admin_service.py     # Admin account creation and deactivation
│   └── results_service.py   # Vote tallying, turnout, and statistics
│
├── data/
│   └── storage.py           # Central store, JSON save/load, data seeding
│
└── views/
    ├── auth_view.py         # Login menu and voter self-registration screen
    ├── admin_view.py        # All admin-facing menus and screens
    └── voter_view.py        # All voter-facing menus and screens
```

---

## Design Decisions

### 1. Modular Design

The original monolith had all code — constants, global state, UI, and logic — in a single 700+ line file. We split this into **29 focused files** across 5 packages, each with a single clear responsibility. The `config.py` file centralises all constants, eliminating magic numbers and hard-coded strings scattered through the original.

### 2. Object-Oriented Design

The original used plain Python dictionaries to represent every entity. We replaced these with proper classes in the `models/` package:

- Each model (`Candidate`, `Voter`, `Admin`, `Poll`, `VotingStation`, `Vote`) encapsulates its own data and provides `to_dict()` / `from_dict()` methods for serialisation.
- The `Store` class in `data/storage.py` encapsulates all application state and persistence logic.
- The `AuthService` class manages the user session with clear `login_admin()`, `login_voter()`, and `logout()` methods.
- View classes (`AdminView`, `VoterView`, `AuthView`) encapsulate all UI behaviour per role.
- Service classes receive the store via constructor injection (dependency injection), making each testable in isolation.

### 3. Separation of Concerns

The architecture enforces three strict layers:

| Layer | Package | Responsibility |
|---|---|---|
| Presentation | `views/` | Reads input, prints output. Never contains business logic. |
| Business Logic | `services/` | Validates rules, computes results. Never prints or reads input directly. |
| Data | `models/` + `data/` | Defines data shape and handles persistence. No logic, no UI. |

A key example is `cast_vote()`. In the original, one function handled input collection, duplicate checking, vote recording, voter state update, and file saving. In the refactored version, `VoterView.cast_vote()` handles only input/output, and delegates to `VoteService.cast_ballot()` for all logic. The service raises a `ValueError` on any violation; the view catches it and displays the message.

### 4. Clean Code

- All functions and methods have a single clear purpose.
- Meaningful names replace cryptic abbreviations (e.g. `tc`, `ac`, `vc`).
- `ValueError` exceptions replace inline `error()` + `return` patterns in business logic.
- Magic values like `25`, `75`, `18`, and `6` are constants in `config.py`.
- No duplicated code — shared display logic lives in `ui/components.py` and is reused across all views.
- A singleton `store` and `session` are injected into views and services, avoiding global variables.

---

## Features Preserved

All original features work identically after refactoring:

- Candidate CRUD with age, education, and criminal record eligibility checks
- Voting station management
- Position and poll lifecycle (draft → open → closed)
- Voter registration and verification
- Ballot casting with duplicate prevention
- Result tallying with ASCII bar charts and turnout statistics
- Station-wise result breakdowns
- Role-based access for 4 admin types and voters
- Audit log with filtering
- JSON persistence
