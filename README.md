# National E-Voting System
## Refactoring Report

## Names of Group Members
Odong Jeferson Clinton S24B23/043

Owino Esther Lyn S24B23/032

Kirabo Faith Kiggundu S24B23/083

Mutebi Jonah Mark S24B23/105

Nakibuuka Allen S24B23/048

## Introduction

The original e-voting application was a single Python file of around 650 lines. Everythinglived together in it, the colour codes, global variables for all the data, the business rules, themenus, the input prompts, and the JSON saving and loading. It worked, but the way it was
written made it very difficult to follow and even harder to change safely. The task was to break it apart and restructure it as a proper modular, object-oriented project
while keeping the application behaving exactly the same. This report explains howwe
approached that, what I found in the original that needed fixing, and the decisions we madealong the way. 

## What Was Wrong with the Original.

Before doing anything, we read through the original carefully to understand what it was
actually doing and where the problems were. The first thing I noticed was the global variables. Right near the top of the file, there wereabout 14 module-level variables holding all the application data; things like candidates, voters, polls, votes, admins, and counters for each. Any function anywhere in the file couldread or change these directly, with nothing controlling access. The naming was also hard to follow in places. The view_detailed_statistics() function, for
example, used names like tc, ac, tv, vv, av, ts, ast, tp, op, cp, dp —all defined one after
another in a block at the top of the function. You had to keep looking back to remember what
each one stood for. The biggest issue though was that functions were doing too many things at once. The
cast_vote() function is a good example which handled displaying the poll, collecting theuser's choices for each position, validating input, building the vote records, updating thevoter's history, updating the poll's vote count, writing to the audit log, and saving to the JSONfile, all in one place. That made it very hard to change any one part of it without riskingbreaking something else. The same problem appeared in view_detailed_statistics() which mixed calculations withprint
statements throughout, and in login() which handled admin login, voter login, and voter
registration all branching off the same function. 

## Project Structure

We organised the refactored project into five packages, each with a clear job. The idea wasthat if you need to change something, you know immediately which folder to look in without having to scroll through hundreds of lines.
| Package / File | What it does |
|----------------|--------------|
| `main.py` | Entry point of the application. Creates services and views and starts the program loop. |
| `config.py` | Stores all application constants such as age limits, roles, file names, and election types. |
| `models/` | Contains one class per entity: Candidate, Voter, Admin, Poll, VotingStation, and Vote. |
| `services/` | Contains the business logic layer — one service per functional area. |
| `data/storage.py` | Defines the `Store` class that holds application data and manages JSON save/load operations. |
| `ui/` | Provides colour codes, reusable display helpers, and input prompt utilities. |
| `views/` | Contains the screens and menus — one view file per role (admin, voter, authentication). |

# Design Principles Applied

## Modular Design

The main thing we tried to do was give each file one job. In the original, everything was inone place, so changing how the ballot casting worked meant carefully navigating a functionthat also handled the UI, the audit log, and the file save. In the refactored version, eachof
those concerns is in a different file. We also moved all the constants into config.py early on. The original had values like 25, 75, and 18 scattered through different functions with no explanation of what they meant. Namingthem MIN_CANDIDATE_AGE, MAX_CANDIDATE_AGE, and MIN_VOTER_AGEinone place makes them self-documenting and means you only change themonce. 

## Object-Oriented Design

The original used plain Python dictionaries for everything. A candidate was just a dictionary, a voter was just a dictionary, a vote was just a dictionary so there were no classes at all for
any of the data. We replaced each of these with a proper class in the models/ package. Each class holds its
own data and has to_dict() and from_dict() methods so that saving and loading fromJSONworks cleanly. This also means if you want to know what fields a Candidate has, you lookat
one file — you do not have to trace through the create_candidate() function to find out. The Store class in data/storage.py replaces the 14 global variables from the original. All theapplication data lives inside one object now, and every service receives it through its
constructor. This was a big improvement over the original where any function could reachinand modify candidates or votes or poll_id_counter directly without going through anycontrolled interface.
The AuthService class handles the session of who is logged in and what their role is. Intheoriginal, current_user and current_role were global variables that functions like cast_vote()
and admin_dashboard() accessed directly. 

## Separation of Concerns

This was the hardest part because the original mixed everything together so thoroughly. Wetried to keep three layers completely separate from each other:

| Layer | Where | Rules we Followed |
|------|------|----------------|
| Presentation | `views/`, `ui/` | Only reads input and prints output. No business decisions here. |
| Logic | `services/` | Does the actual work. Never prints anything or reads from the keyboard. |
| Data | `models/`, `data/` | Defines what things look like and handles persistence. No logic, no UI. |

The clearest example of this is ballot casting. In the original, cast_vote() was one longfunction that displayed the poll, looped through positions collecting input, built the voterecords, appended them to the global votes list, updated current_user["has_voted_in"], incremented polls[pid]["total_votes_cast"], wrote to the audit log, and called save_data() —all in one place. 

In the refactored version, VoterView.cast_vote() handles only what the user sees and types, and VoteService.cast_ballot() handles only the logic. If something goes wrong, like the voter
already voted — the service raises a ValueError with a message, and the viewcatches it anddisplays it. Neither one reaches into the other's territory. 

A similar separation happened with view_detailed_statistics(). In the original it calculatedeverything — counting candidates, voters, stations, building age groups, computing
percentages — and printed the results all in the same function. In the refactored version, ResultsService does the calculations and returns the data, and the admin viewjust formats
and prints it. 

## Clean Code

A few specific things we focused on here:
Naming — the view_detailed_statistics() function in the original opened with a line liketc=len(candidates); ac = sum(...) and continued with tv, vv, av, ts, ast —short names you had to keep looking up. We replaced these with full names like total_candidates, active_candidates, verified_voters, which say what they are.
No repeated code — the original had the same kind of table drawing, menu rendering, andpause prompts written out in many different functions. In the refactored version these liveinui/components.py and ui/prompts.py and are shared across all three view files. Short, focused functions — if a function was getting long it was usually because it was doingmore than one thing. For example, the original login() function handled three completelydifferent flows: admin login, voter login, and voter self-registration, all branching insidethesame function. These became three separate methods in the refactored version. Every module also has a short docstring at the top explaining what it is for, which helps alot
when coming back to the code after time away. 

## Features Preserved

All the original features still work. We tested the full flow — logging in as admin, creatingastation, registering and verifying a voter, creating positions and a poll, assigning candidates, opening the poll, logging in as the voter and casting a ballot, then viewing the results. Everything behaved the same as the original. 

• Candidate CRUD with age, education, and criminal record eligibility checks

• Voting station management 

• Position definitions and poll lifecycle (draft, open, closed) 

• Voter self-registration and admin verification workflow

• Ballot casting with duplicate prevention and SHA-256 vote hash

• Results with ASCII bar charts and turnout percentages

• Station-level result breakdowns

• Role-based access for all four admin types and voters

• Audit log with filtering

• JSON persistence across sessions

## Conclusion

Going through this refactor made the problems with the original very clear in a way that just
reading about them in theory does not. When you are actually trying to change somethingandyou realise you have to understand six other things first just to make one edit, you feel whyseparation of concerns matters. The application behaves identically to the original. The structure is cleaner, the names saywhat things are, and any change to one part of the system should not require understandingall the other parts to make safely.
