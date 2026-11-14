# Liver MRI Teaching Toolkit

This repository is a teaching toolkit for liver MRI analysis. It can be used in three ways:

1. As a browser app for quick demonstrations
2. As a desktop app for local exploration
3. As a step-by-step Jupyter notebook for hands-on student workshops

The notebook is the recommended entry point for students because it explains the workflow slowly and clearly. Students can inspect the data, load DICOM files, visualize masks, compute an approximate PDFF map, and compare slice-wise and case-wise measurements.

This project is for teaching and research training only. It is not a clinical tool.

## What Students Will Learn

By working through the notebook, students will learn how to:

- understand the dataset structure
- inspect MRI cases and sequences
- read DICOM files and basic metadata
- visualize liver MRI slices and ground-truth masks
- perform simple quality control (QC)
- compare different slices through the volume
- compute an approximate PDFF map from in-phase and out-phase images
- create and export a liver mask
- apply a mask to an image
- calculate liver PDFF for one slice and for a whole case
- understand why per-slice PDFF and overall average PDFF are not always the same

## Repository Structure

```text
Liver_demo/
|-- app/
|   |-- server.py
|   |-- desktop_main.py
|   `-- core/
|       |-- imaging.py
|       |-- geometry.py
|       `-- store.py
|-- data/
|   |-- sample_data/
|   `-- CHAOS_Train_Sets/
|-- notebooks/
|   `-- liver_mri_student_workshop.ipynb
|-- outputs/
|-- scripts/
|   |-- run_app.ps1
|   `-- run_desktop.ps1
|-- requirements.txt
`-- README.md
```

## Two Types of Data in This Repository

The `data/` folder now has two different purposes:

### `data/sample_data/`

This is a small teaching sample used only to check that the environment is configured correctly.

Students should use `sample_data` first to confirm that:

- Python and packages were installed correctly
- the notebook opens correctly
- the code can find the data folder
- the app can load slices and masks

This sample is for environment testing and quick verification.

### `data/CHAOS_Train_Sets/`

This is the real dataset for the hands-on session.

Students should use this dataset for the actual workshop analysis after they confirm that their environment works with `sample_data`.

## About the CHAOS Dataset

The workshop uses the CHAOS dataset from Zenodo:

[CHAOS - Combined (CT-MR) Healthy Abdominal Organ Segmentation Challenge Data](https://zenodo.org/records/3431873)

According to the Zenodo record, this dataset contains abdominal CT and MRI data from different patients. The CT set includes 20 training and 20 testing cases. The MRI set includes 20 training and 20 testing cases with `T1-Dual` and `T2 SPIR` sequences. The training set contains both DICOM images and ground-truth masks, while the testing set contains DICOM images only. In CT, only liver annotations are provided. In MRI, liver, left kidney, right kidney, and spleen annotations are provided. The test-set ground truths are not publicly released. Source: [Zenodo record](https://zenodo.org/records/3431873).

The Zenodo page also states that the data may be used for research and related work as long as users give appropriate credit, provide a link to the license, and indicate whether changes were made. The listed license is [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/). Source: [Zenodo record](https://zenodo.org/records/3431873).

If you use the dataset in teaching material, slides, or reports, credit the CHAOS authors and cite the dataset.

## Recommended Learning Path

For a student workshop, use this order:

1. Install Python and the required packages
2. Use `sample_data` to verify that the environment works
3. Download the official CHAOS training set
4. Copy the extracted `CHAOS_Train_Sets` folder into `data/`
5. Open the notebook
6. In the notebook, change the data path from `sample_data` to the full CHAOS MRI training folder
7. Follow the notebook from top to bottom

## Step 1: Install Python

If Python is not already installed, install Python 3.11.

Recommended:

- Python 3.11 from the official installer
- or Anaconda / Miniconda with a Python 3.11 environment

To check whether Python is available, open PowerShell in this folder and run:

```powershell
python --version
```

You should see a Python 3.11 version.

## Step 2: Create a Clean Environment

This is strongly recommended, especially for students.

### Option A: Using `venv`

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### Option B: Using Conda

```powershell
conda create -n liver-mri-teaching python=3.11 -y
conda activate liver-mri-teaching
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If PowerShell blocks script execution, you can use:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Then try the activation command again.

## Step 3: Verify Your Setup With `sample_data`

Before downloading the full dataset, use the included sample to make sure your setup works.

The browser app, desktop app, and default notebook configuration all start from:

```text
data/sample_data/
```

Use that sample to check that:

- the app launches
- the notebook runs
- MRI slices can be loaded
- masks are visible
- PDFF-related cells run on dual-echo examples

If this step works, your environment is ready.

## Step 4: Download the Real Workshop Dataset

For the actual hands-on session, students should download the official training set from Zenodo:

[Download CHAOS_Train_Sets.zip](https://zenodo.org/records/3431873?preview_file=CHAOS_Train_Sets.zip)

After downloading:

1. Extract `CHAOS_Train_Sets.zip`
2. Copy the extracted folder `CHAOS_Train_Sets` into the repository's `data/` folder

After that, your local structure should look like this:

```text
data/
|-- sample_data/
`-- CHAOS_Train_Sets/
    `-- Train_Sets/
        `-- MR/
```

For this notebook and the current MRI teaching workflow, the important full-data path is:

```text
data/CHAOS_Train_Sets/Train_Sets/MR/
```

## Step 5: Start the Notebook

The teaching notebook is:

[notebooks/liver_mri_student_workshop.ipynb](./notebooks/liver_mri_student_workshop.ipynb)

After installing the requirements, start Jupyter:

```powershell
jupyter lab
```

If that command does not work, try:

```powershell
python -m jupyter lab
```

Then open the notebook in your browser.

## Step 6: Change the Data Path Inside the Notebook

The notebook begins with `sample_data` so students can test their setup safely.

For the real workshop, students should edit the data path in the notebook and change it from:

```python
ACTIVE_DATA_DIR = SAMPLE_DATA_DIR
```

to:

```python
ACTIVE_DATA_DIR = CHAOS_MR_DATA_DIR
```

This is intentional. It is a small hands-on step so students learn where the real dataset lives and how code connects to data folders.

## Running the Browser App

The browser app is useful for quick demonstrations and environment checks.

Start it with:

```powershell
.\scripts\run_app.ps1
```

Or:

```powershell
python .\app\server.py
```

Then open:

[http://127.0.0.1:8765](http://127.0.0.1:8765)

Important:

- the app currently defaults to `data/sample_data/`
- this is intended for setup verification and lightweight teaching demos

## Running the Desktop App

The desktop app is useful for a local GUI-based workflow.

Start it with:

```powershell
.\scripts\run_desktop.ps1
```

Or:

```powershell
python .\app\desktop_main.py
```

Important:

- the desktop app currently defaults to `data/sample_data/`
- this is intended for setup verification and lightweight teaching demos

## What the MRI Data Looks Like

Inside the MRI training set, each patient folder may contain:

- `T1DUAL`
- `T2SPIR`

Each sequence folder usually contains:

- `DICOM_anon/`: MRI images in DICOM format
- `Ground/`: teaching ground-truth masks

For dual-echo T1 data, `DICOM_anon/` contains:

- `InPhase/`
- `OutPhase/`

These paired images are used in the notebook to compute an approximate PDFF map.

## Troubleshooting

### `python` is not recognized

Python is not installed or not added to your PATH. Install Python 3.11 and reopen PowerShell.

### `jupyter lab` is not recognized

Your environment may not be activated. Activate it and try again.

### A notebook cell says a package is missing

Reinstall the requirements:

```powershell
python -m pip install -r requirements.txt
```

### The notebook cannot find the project root

Make sure you opened Jupyter from the repository folder, or open the notebook after navigating into this repository first.

### The notebook runs on `sample_data` but not on CHAOS

Check these points:

- `CHAOS_Train_Sets.zip` was fully downloaded
- the zip file was extracted successfully
- the extracted folder was copied to `data/`
- the notebook path was changed to `data/CHAOS_Train_Sets/Train_Sets/MR`

### A case does not show PDFF

Only dual-echo T1 cases with matched in-phase and out-phase images support the approximate PDFF demonstration.

### The notebook image is not clickable in the segmentation step

Make sure the latest requirements are installed:

```powershell
python -m pip install -r requirements.txt
```

Then restart the Jupyter kernel and run the notebook from the top again. The interactive segmentation step uses `ipympl` and `%matplotlib widget`.

## For Instructors

Suggested workshop format:

1. 10 minutes: explain the data structure and the learning goals
2. 10 minutes: verify student environments with `sample_data`
3. 10 minutes: guide students through downloading and placing CHAOS
4. 15 minutes: change the notebook path to the real dataset
5. 20 minutes: students visualize slices and masks
6. 20 minutes: students inspect PDFF and QC
7. 15 minutes: students export masks and compute measurements
8. 10 minutes: discuss slice-wise versus case-wise averages

The notebook is intentionally structured so students both follow instructions and still complete small coding tasks on their own.

## Summary

If you want the shortest working path:

1. Install Python 3.11
2. Install `requirements.txt`
3. Test the setup with `sample_data`
4. Download `CHAOS_Train_Sets.zip` from Zenodo
5. Extract it and copy `CHAOS_Train_Sets` into `data/`
6. Run `jupyter lab`
7. Open `notebooks/liver_mri_student_workshop.ipynb`
8. Change the notebook data path from `SAMPLE_DATA_DIR` to `CHAOS_MR_DATA_DIR`
9. Follow the notebook step by step

That is the recommended student workflow.
