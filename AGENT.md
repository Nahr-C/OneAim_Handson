# AGENT.md

## Project Overview

Build a polished educational desktop/web application for a hands-on liver MRI segmentation session.

The application is designed for students to:
- browse anonymized liver MRI cases
- inspect individual 2D slices
- understand the liver anatomy with optional GT overlay
- manually draw a liver segmentation on the current slice
- validate whether the drawn contour is closed
- convert the drawing into a binary mask
- compare the student mask with the ground-truth mask
- receive an immediate Dice score and visual overlap feedback
- optionally reconstruct and inspect a simple 3D liver model from the available slices and masks

This project is for **teaching and demonstration**, not for clinical use.

---

## Core Product Goals

The app should feel:
- visually clean
- modern and elegant
- intuitive for non-technical users
- robust enough for live classroom use
- fast to start and easy to operate

The app should prioritize:
1. **excellent user experience**
2. **clear educational value**
3. **stable local execution**
4. **minimal setup friction**
5. **respect for the current repository structure**

---

## Development Rules for Codex

### 1. Respect the existing directory structure
You must **not** arbitrarily redesign the whole repository.

Before making changes:
- inspect the current directory tree
- identify existing app, data, config, scripts, and output locations
- reuse the current structure whenever reasonable
- create new files only where they naturally fit

If the structure is unclear, prefer:
- `app/` or `src/` for application code
- `data/` for local sample data or path references
- `outputs/` for generated results or temporary exports
- `docs/` for documentation
- project root for `README.md`, `AGENT.md`, and launch instructions

### 2. Make minimal, reversible changes
Prefer small, modular additions over broad rewrites.

### 3. Keep the code readable
All code must be in English.
Comments should be placed **above** the relevant code block, not on the right side.
Add helpful docstrings above functions/classes where appropriate.

### 4. Prioritize local usability
The software should run locally from the current repository with as little manual setup as possible.

### 5. Do not hardcode fragile assumptions
Do not assume a fixed MRI file format until the directory has been inspected.
Support the actual format present in this project, such as:
- DICOM
- PNG
- JPG
- NIfTI
- NumPy arrays

Implement format handling based on what is actually found.

---

## Product Requirements

## A. Main Features

### A1. Case and slice browser
The user must be able to:
- select a patient/case from the available dataset
- browse all available slices for that case
- move between slices using:
  - previous/next buttons
  - keyboard shortcuts
  - an optional slice slider
- clearly see the current slice index and total slice count

### A2. MRI image viewer
The current slice must be displayed clearly with:
- appropriate grayscale rendering
- optional brightness/contrast adjustment if feasible
- zoom in / zoom out
- pan support if feasible
- smooth rendering without lag

### A3. Ground-truth teaching overlay
There should be a teaching mode where the user can:
- toggle GT visibility on/off
- view GT as a semi-transparent colored overlay
- optionally view GT contour only
- inspect overlap between image and GT to understand anatomy

This mode is for learning and exploration.

### A4. Manual segmentation drawing tool
The user must be able to draw a segmentation on the current slice using the cursor.

Preferred behavior:
- click to place control points
- show connected polygon edges while drawing
- allow point undo
- allow full reset
- visually indicate start point and current endpoint
- allow closing the polygon by:
  - clicking near the start point, or
  - pressing a finish key/button when closure is valid

### A5. Closed-contour validation
Before scoring:
- check whether the polygon is closed and valid
- if not closed, show a clear, friendly message
- if self-intersecting, warn the user and request correction if feasible
- only proceed to mask generation after validation

### A6. Mask generation and evaluation
Once the contour is valid:
- rasterize the polygon into a binary mask
- compare it to the GT mask for the current slice
- compute Dice score
- optionally compute IoU as a secondary metric
- display the score immediately in a clear result panel

### A7. Visual result feedback
After evaluation, show:
- student mask contour
- GT contour
- overlap visualization
- false positive region
- false negative region

This should be intuitive and educational.

### A8. 3D liver model viewer
The app should support a simple 3D visualization mode built from the stack of slices.

The user should be able to:
- reconstruct a 3D liver surface or voxel volume from GT masks
- optionally compare GT-based 3D reconstruction and student-selected slice context
- rotate the 3D model
- zoom in / out
- inspect from different viewing angles

If full 3D reconstruction from user-drawn masks across many slices is too large for v1, then:
- implement GT-based 3D reconstruction first
- clearly structure the code so future extension to user 3D masks is easy

### A9. Anatomy teaching support
The UI should help explain what is shown.

Possible teaching aids:
- display labels like “liver region”, “current slice”, “superior/inferior direction” if inferable
- show a mini panel explaining:
  - image slice
  - GT region
  - user region
  - overlap meaning

---

## B. GUI and UX Requirements

The GUI must be **beautiful, polished, and friendly**.

### B1. Visual style
Use a modern medical-imaging-inspired design:
- calm dark or neutral theme
- elegant accent colors
- high contrast for important interactive elements
- restrained use of color
- visually pleasant spacing
- rounded panels/cards where appropriate

Suggested palette direction:
- background: charcoal / slate / deep gray
- image panel: dark neutral
- GT overlay: cyan or teal
- user contour: warm yellow or orange
- overlap/success accent: green
- warning/error accent: soft red

Do not use overly saturated or chaotic colors.

### B2. Layout
The layout should be clear and balanced.

Preferred layout:
- left sidebar: case selection, slice controls, mode toggles
- center: large main MRI canvas
- right sidebar: score panel, legend, interaction help, optional 3D viewer toggle
- optional bottom area: status bar / hints / anatomy notes

### B3. Usability
The app should be easy for students to use without long instructions.

Include:
- obvious buttons
- hover tooltips where useful
- short on-screen guidance
- a friendly empty state
- keyboard shortcuts for common actions

### B4. Feedback
Every user action should get clear feedback:
- contour started
- point added
- contour closed
- invalid contour
- score computed
- overlay toggled
- 3D model loaded

---

## C. Recommended Tech Direction

Choose the implementation path that best fits the current repository and environment.

### Preferred option
If no GUI framework is already established, prefer one of these:

#### Option 1: Streamlit
Use Streamlit if the priority is rapid local development and easy launch.
Pros:
- fast to prototype
- simple local execution
- good for teaching/demo
Cons:
- freehand drawing support may require a custom component or workaround

#### Option 2: PySide6 / PyQt
Use PySide6 if robust interactive drawing is the main requirement.
Pros:
- strong desktop GUI
- better control over drawing tools
- better suited for polished annotation interaction
Cons:
- slightly higher development complexity

#### Option 3: Web app with React frontend + Python backend
Use only if the current repo is already oriented this way.
Pros:
- strongest UI flexibility
Cons:
- more moving parts
- unnecessary for a fast educational prototype unless already supported

### Recommendation for this project
If starting from scratch, **prefer PySide6** for the best drawing experience and stable local demo.
If the current environment strongly favors web tooling, a lightweight web solution is acceptable.

---

## D. Data Handling Requirements

### D1. Dataset assumptions
The repository contains:
- multiple patients/cases
- multiple MRI slices per case
- corresponding ground-truth masks

Codex must inspect the actual structure and then implement a data loader around it.

Possible structures may include:
- one folder per patient
- separate image and mask directories
- paired filenames
- DICOM series
- image stacks

### D2. Loader design
Implement a clean data abstraction, for example:
- `CaseIndex`
- `CaseRecord`
- `SliceRecord`

The loader should:
- discover cases automatically
- pair each slice with its corresponding GT mask
- sort slices in the correct order
- expose metadata needed by the GUI

### D3. Robustness
Handle missing or mismatched files gracefully:
- skip broken pairs
- log useful warnings
- do not crash the app if one case is malformed

### D4. Performance
Do not preload everything if unnecessary.
Use lazy loading or lightweight caching where useful.

---

## E. Scoring Logic

### E1. Dice definition
Use the standard Dice coefficient for binary masks:

Dice = 2 * |A ∩ B| / (|A| + |B|)

Requirements:
- masks must be binarized consistently
- handle the empty-mask edge case explicitly
- document the behavior in code

Suggested edge-case policy:
- if both masks are empty, return Dice = 1.0 only if this is intentionally desired and documented
- otherwise, prefer avoiding slices with empty GT in the teaching workflow unless such cases are pedagogically useful

### E2. Additional metrics
Optionally include:
- IoU
- precision
- recall

But Dice must be the main metric.

---

## F. Interaction Details

### F1. Drawing workflow
Target workflow:
1. user selects a patient
2. user selects a slice
3. user optionally inspects GT overlay in learning mode
4. user hides GT
5. user draws a liver contour
6. user clicks “Validate” or “Finish”
7. system checks contour validity
8. system computes mask and Dice
9. system shows score and visual comparison

### F2. Required controls
Include at minimum:
- case selector
- slice selector
- previous slice
- next slice
- show/hide GT
- show/hide contours
- start drawing
- undo point
- reset drawing
- validate/finish
- score/evaluate
- open 3D viewer
- reset zoom

### F3. Keyboard shortcuts
Add if feasible:
- left/right arrow: previous/next slice
- `G`: toggle GT
- `U`: undo point
- `R`: reset drawing
- `Enter`: finish contour / evaluate when valid
- `+` / `-`: zoom

---

## G. 3D Viewer Requirements

The 3D viewer is important, but should not block delivery of the main 2D workflow.

### G1. Priority
Implement in this order:
1. solid 2D viewer and scoring workflow
2. GT overlay teaching mode
3. 3D viewer
4. optional advanced features

### G2. Minimum viable 3D viewer
The minimum acceptable 3D feature is:
- build a 3D binary volume from stacked GT masks
- render a rotatable 3D view
- support zoom and basic interaction

Good implementation options:
- pyqtgraph OpenGL
- vtk / pyvista
- plotly volume or mesh viewer
- trimesh or skimage marching cubes plus a compatible viewer

### G3. Nice-to-have
If feasible:
- synchronize 2D slice position with 3D position
- highlight the currently viewed slice plane in the 3D panel

---

## H. Project Structure Guidance

Adapt to the current repository, but prefer a modular design like:

```text
project_root/
├─ AGENT.md
├─ README.md
├─ requirements.txt
├─ app/
│  ├─ main.py
│  ├─ ui/
│  ├─ widgets/
│  ├─ viewers/
│  ├─ controllers/
│  └─ styles/
├─ src/
│  ├─ data/
│  ├─ metrics/
│  ├─ geometry/
│  ├─ rendering/
│  └─ utils/
├─ data/
│  └─ ...
├─ outputs/
└─ tests/
```

This is only a guideline.
Do **not** force this structure if the current repository already has a suitable one.

---

## I. Implementation Strategy

Follow this order:

### Phase 1: inspect and plan
- inspect current directory structure
- identify data organization
- identify current environment and dependencies
- propose minimal file additions
- do not start by writing large amounts of speculative code

### Phase 2: data loading
- implement reliable case/slice/GT discovery
- verify several cases load correctly
- verify slice order and mask alignment

### Phase 3: 2D viewer
- build the image viewer
- add case/slice navigation
- add GT overlay

### Phase 4: drawing and validation
- add polygon drawing
- add contour closure detection
- add mask rasterization
- add error handling

### Phase 5: metrics and feedback
- compute Dice
- show visual overlap
- add result panel and guidance text

### Phase 6: 3D viewer
- stack masks
- generate 3D model
- add interactive 3D window/panel

### Phase 7: polishing
- improve visual design
- improve shortcuts
- improve onboarding text
- test classroom workflow end-to-end

---

## J. Quality Expectations

The final result should:
- launch reliably
- work on local sample data
- avoid crashing on common mistakes
- look polished enough for a student workshop
- be understandable for future extension

### Code quality
- modular
- typed where reasonable
- documented
- no giant monolithic script if avoidable
- clear separation of UI, data loading, metrics, and rendering

### Testing
At minimum, add lightweight tests or verification scripts for:
- case discovery
- slice-mask pairing
- Dice computation
- polygon-to-mask conversion if practical

---

## K. Non-Goals

Do not over-engineer this into a full annotation platform.

This project does **not** need:
- user accounts
- online database
- cloud deployment
- multi-user collaboration
- clinical compliance
- deep learning inference in v1

Keep it focused on the teaching use case.

---

## L. Deliverables

Codex should aim to produce:
1. a runnable local application
2. clear setup instructions
3. a short README explaining how to launch and use it
4. a clean implementation of:
   - data loading
   - slice viewing
   - GT overlay
   - manual polygon drawing
   - contour validation
   - Dice scoring
   - optional 3D viewer
5. a polished GUI suitable for student demonstration

---

## M. Final Working Principles

When in doubt:
- choose clarity over cleverness
- choose robustness over complexity
- choose good UX over feature overload
- choose minimal intrusion over restructuring the repo
- choose a beautiful, stable teaching demo over an overly ambitious prototype

Build something that is delightful for students to use and straightforward for the instructor to run.
