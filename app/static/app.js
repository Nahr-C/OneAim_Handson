const state = {
  cases: [],
  patient: null,
  sequence: null,
  organs: [],
  organ: "liver",
  caseDetail: null,
  sliceIndex: 0,
  sliceData: null,
  volumeData: null,
  orthogonalData: null,
  triView: { axial: null, coronal: null, sagittal: null, active: null },
  viewMode: "slice",
  imageMode: "anatomy",
  polygon: [],
  closed: false,
  comparisonOverlay: null,
  imageElement: null,
  waterElement: null,
  fatElement: null,
  gtElement: null,
  pdffElement: null,
  comparisonElement: null,
  viewport: { scale: 1, offsetX: 0, offsetY: 0 },
  dragging: false,
  dragMode: null,
  dragStart: null,
  volumeView: { yaw: -0.6, pitch: 0.55, zoom: 10 },
  seg: {
    session: null,
    current: 0,
    records: [],
    sliceData: null,
    imageElement: null,
    comparisonElement: null,
    polygon: [],
    closed: false,
    viewport: { scale: 1, offsetX: 0, offsetY: 0 },
    evaluation: null,
    evalCurrent: 0,
    evalMode: "2d",
    volumeView: { yaw: -0.6, pitch: 0.55, zoom: 10 },
  },
};

const refs = {
  patientSelect: document.getElementById("patientSelect"),
  sequenceSelect: document.getElementById("sequenceSelect"),
  organSelect: document.getElementById("organSelect"),
  datasetSummary: document.getElementById("datasetSummary"),
  sliceCount: document.getElementById("sliceCount"),
  sliceBadge: document.getElementById("sliceBadge"),
  sliceSlider: document.getElementById("sliceSlider"),
  prevSliceBtn: document.getElementById("prevSliceBtn"),
  nextSliceBtn: document.getElementById("nextSliceBtn"),
  spacingText: document.getElementById("spacingText"),
  thicknessText: document.getElementById("thicknessText"),
  sliceLabel: document.getElementById("sliceLabel"),
  showGtToggle: document.getElementById("showGtToggle"),
  showContourToggle: document.getElementById("showContourToggle"),
  teachingText: document.getElementById("teachingText"),
  statusBadge: document.getElementById("statusBadge"),
  statusText: document.getElementById("statusText"),
  diceValue: document.getElementById("diceValue"),
  iouValue: document.getElementById("iouValue"),
  studentArea: document.getElementById("studentArea"),
  gtArea: document.getElementById("gtArea"),
  pdffLabel: document.getElementById("pdffLabel"),
  gtPdffMeanMode: document.getElementById("gtPdffMeanMode"),
  gtPdffMean: document.getElementById("gtPdffMean"),
  gtPdffMedian: document.getElementById("gtPdffMedian"),
  userPdffMean: document.getElementById("userPdffMean"),
  userPdffMedian: document.getElementById("userPdffMedian"),
  canvasLegend: document.getElementById("canvasLegend"),
  canvasHelp: document.getElementById("canvasHelp"),
  pdffColorbar: document.getElementById("pdffColorbar"),
  scaleBar: document.getElementById("scaleBar"),
  scaleBarLine: document.getElementById("scaleBarLine"),
  scaleBarLabel: document.getElementById("scaleBarLabel"),
  volumePdffBadge: document.getElementById("volumePdffBadge"),
  volumePdffMedian: document.getElementById("volumePdffMedian"),
  imageModeGroup: document.getElementById("imageModeGroup"),
  sliceCanvas: document.getElementById("sliceCanvas"),
  volumeCanvas: document.getElementById("volumeCanvas"),
  undoBtn: document.getElementById("undoBtn"),
  resetBtn: document.getElementById("resetBtn"),
  closeBtn: document.getElementById("closeBtn"),
  evaluateBtn: document.getElementById("evaluateBtn"),
  viewModeBtn: document.getElementById("viewModeBtn"),
  triViewBtn: document.getElementById("triViewBtn"),
  fitBtn: document.getElementById("fitBtn"),
  triViewPanel: document.getElementById("triViewPanel"),
  triViewOverview: document.getElementById("triViewOverview"),
  triViewDetail: document.getElementById("triViewDetail"),
  axialTitle: document.getElementById("axialTitle"),
  axialMeta: document.getElementById("axialMeta"),
  axialImage: document.getElementById("axialImage"),
  coronalTitle: document.getElementById("coronalTitle"),
  coronalMeta: document.getElementById("coronalMeta"),
  coronalImage: document.getElementById("coronalImage"),
  sagittalTitle: document.getElementById("sagittalTitle"),
  sagittalMeta: document.getElementById("sagittalMeta"),
  sagittalImage: document.getElementById("sagittalImage"),
  triDetailTitle: document.getElementById("triDetailTitle"),
  triDetailMeta: document.getElementById("triDetailMeta"),
  triDetailImage: document.getElementById("triDetailImage"),
  triDetailSlider: document.getElementById("triDetailSlider"),
  triBackBtn: document.getElementById("triBackBtn"),
  triDirectionFigure: document.getElementById("triDirectionFigure"),
  triExplainTitle: document.getElementById("triExplainTitle"),
  triExplainText: document.getElementById("triExplainText"),
  demoShell: document.getElementById("demoShell"),
  segmentationShell: document.getElementById("segmentationShell"),
  enterSegmentationBtn: document.getElementById("enterSegmentationBtn"),
  backToDemoBtn: document.getElementById("backToDemoBtn"),
  segStartPanel: document.getElementById("segStartPanel"),
  segWorkspace: document.getElementById("segWorkspace"),
  segEvaluation: document.getElementById("segEvaluation"),
  segPatientSelect: document.getElementById("segPatientSelect"),
  startSegSessionBtn: document.getElementById("startSegSessionBtn"),
  segStartStatus: document.getElementById("segStartStatus"),
  segProgressStrip: document.getElementById("segProgressStrip"),
  segSliceQuickSlider: document.getElementById("segSliceQuickSlider"),
  segCompletionFill: document.getElementById("segCompletionFill"),
  segCompletionText: document.getElementById("segCompletionText"),
  finishSegBtn: document.getElementById("finishSegBtn"),
  segSliceTitle: document.getElementById("segSliceTitle"),
  segCanvas: document.getElementById("segCanvas"),
  segPrevBtn: document.getElementById("segPrevBtn"),
  segNextBtn: document.getElementById("segNextBtn"),
  segUndoBtn: document.getElementById("segUndoBtn"),
  segRedoBtn: document.getElementById("segRedoBtn"),
  segCloseBtn: document.getElementById("segCloseBtn"),
  segSaveBtn: document.getElementById("segSaveBtn"),
  segStatusBadge: document.getElementById("segStatusBadge"),
  segStatusText: document.getElementById("segStatusText"),
  segEvalStrip: document.getElementById("segEvalStrip"),
  segEvalSliceSlider: document.getElementById("segEvalSliceSlider"),
  segScoreBadge: document.getElementById("segScoreBadge"),
  segEvalTitle: document.getElementById("segEvalTitle"),
  segEval2dBtn: document.getElementById("segEval2dBtn"),
  segEval3dBtn: document.getElementById("segEval3dBtn"),
  segEval2dPanel: document.getElementById("segEval2dPanel"),
  segEval3dPanel: document.getElementById("segEval3dPanel"),
  segEvalCanvas: document.getElementById("segEvalCanvas"),
  segStudentVolumeCanvas: document.getElementById("segStudentVolumeCanvas"),
  segGtVolumeCanvas: document.getElementById("segGtVolumeCanvas"),
  segStudentVolumePdff: document.getElementById("segStudentVolumePdff"),
  segGtVolumePdff: document.getElementById("segGtVolumePdff"),
  segEvalDice: document.getElementById("segEvalDice"),
  segEvalIou: document.getElementById("segEvalIou"),
  segEvalUserPdff: document.getElementById("segEvalUserPdff"),
  segEvalGtPdff: document.getElementById("segEvalGtPdff"),
};

const sliceCtx = refs.sliceCanvas.getContext("2d");
const volumeCtx = refs.volumeCanvas.getContext("2d");
const segCtx = refs.segCanvas.getContext("2d");
const segEvalCtx = refs.segEvalCanvas.getContext("2d");
const segStudentVolumeCtx = refs.segStudentVolumeCanvas.getContext("2d");
const segGtVolumeCtx = refs.segGtVolumeCanvas.getContext("2d");

const TRI_VIEW_EXPLAINERS = {
  axial: {
    title: "Axial View",
    text: "Viewed from inferior to superior: from the feet toward the head.",
    image: "/explainers/axial.png",
  },
  coronal: {
    title: "Coronal View",
    text: "Viewed from anterior to posterior: from the front of the body toward the back.",
    image: "/explainers/coronal.png",
  },
  sagittal: {
    title: "Sagittal View",
    text: "Viewed from lateral to medial: from one side of the body toward the midline.",
    image: "/explainers/sagittal.png",
  },
};

async function apiGet(path) {
  const response = await fetch(path);
  if (!response.ok) {
    const payload = await response.json().catch(() => ({}));
    throw new Error(payload.error || "Request failed");
  }
  return response.json();
}

async function apiPost(path, body) {
  const response = await fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const payload = await response.json();
  if (!response.ok) {
    throw new Error(payload.message || payload.error || "Request failed");
  }
  return payload;
}

function loadImage(src) {
  return new Promise((resolve, reject) => {
    const image = new Image();
    image.onload = () => resolve(image);
    image.onerror = reject;
    image.src = src;
  });
}

function updateStatus(text, badge = "Ready") {
  refs.statusText.textContent = text;
  refs.statusBadge.textContent = badge;
}

function resetEvaluation() {
  state.comparisonOverlay = null;
  state.comparisonElement = null;
  refs.diceValue.textContent = "--";
  refs.iouValue.textContent = "--";
  refs.studentArea.textContent = "--";
  refs.gtArea.textContent = state.sliceData ? state.sliceData.gtMaskArea.toLocaleString() : "--";
  refs.userPdffMean.textContent = "--";
  refs.userPdffMedian.textContent = "--";
  updateStatus("Draw a contour and close it before starting the evaluation.", "Waiting");
}

function updatePdffStats(targetPrefix, stats) {
  const meanMode = targetPrefix === "gt" ? refs.gtPdffMeanMode.value : "mean";
  const meanValue = stats?.[meanMode];
  refs[`${targetPrefix}PdffMean`].textContent = meanValue !== undefined ? `${meanValue.toFixed(2)}%` : "--";
  refs[`${targetPrefix}PdffMedian`].textContent = stats ? `${stats.median.toFixed(2)}%` : "--";
}

function setImageMode(mode) {
  if (
    (mode === "water" && !state.waterElement) ||
    (mode === "fat" && !state.fatElement) ||
    (mode === "pdff" && !state.pdffElement)
  ) {
    mode = "anatomy";
  }
  state.imageMode = mode;
  refs.imageModeGroup.querySelectorAll("button[data-image-mode]").forEach((button) => {
    button.classList.toggle("active", button.dataset.imageMode === mode);
  });
  updatePdffColorbarVisibility();
  renderSlice();
}

function updatePdffColorbarVisibility() {
  refs.pdffColorbar.classList.toggle("hidden", state.viewMode !== "slice" || state.imageMode !== "pdff");
}

function niceScaleLength(rawMm) {
  if (!Number.isFinite(rawMm) || rawMm <= 0) {
    return null;
  }
  const exponent = Math.floor(Math.log10(rawMm));
  const base = 10 ** exponent;
  const normalized = rawMm / base;
  const niceNormalized = normalized <= 1 ? 1 : normalized <= 2 ? 2 : normalized <= 5 ? 5 : 10;
  return niceNormalized * base;
}

function formatScaleLength(lengthMm) {
  return lengthMm >= 10 ? lengthMm.toFixed(0) : lengthMm.toFixed(1);
}

function updateScaleBar() {
  let cssPixelsPerMm = null;
  let approximate = false;

  if (state.viewMode === "slice" && state.sliceData?.pixelSpacing?.length) {
    cssPixelsPerMm = state.viewport.scale / state.sliceData.pixelSpacing[1];
  } else if (state.viewMode === "volume" && state.volumeData?.bbox?.length) {
    const maxDimensionMm = Math.max(...state.volumeData.bbox);
    cssPixelsPerMm = (180 * state.volumeView.zoom / 3.2) / maxDimensionMm;
    approximate = true;
  }

  if (!cssPixelsPerMm || !Number.isFinite(cssPixelsPerMm)) {
    refs.scaleBar.classList.add("hidden");
    return;
  }

  const targetPixels = 120;
  const lengthMm = niceScaleLength(targetPixels / cssPixelsPerMm);
  if (!lengthMm) {
    refs.scaleBar.classList.add("hidden");
    return;
  }
  const widthPixels = Math.max(36, Math.min(220, lengthMm * cssPixelsPerMm));
  refs.scaleBarLine.style.width = `${widthPixels}px`;
  refs.scaleBarLabel.textContent = `${approximate ? "~" : ""}${formatScaleLength(lengthMm)} mm`;
  refs.scaleBar.classList.remove("hidden");
}

function updateImageModeControls() {
  const supportsDixonViews = Boolean(state.waterElement && state.fatElement);
  const supportsPdffView = Boolean(state.pdffElement);
  refs.imageModeGroup.querySelectorAll("button[data-image-mode]").forEach((button) => {
    button.disabled =
      (button.dataset.imageMode === "water" || button.dataset.imageMode === "fat") && !supportsDixonViews ||
      button.dataset.imageMode === "pdff" && !supportsPdffView;
  });
  if (
    (state.imageMode === "water" || state.imageMode === "fat") && !supportsDixonViews ||
    state.imageMode === "pdff" && !supportsPdffView
  ) {
    setImageMode("anatomy");
  } else {
    refs.imageModeGroup.querySelectorAll("button[data-image-mode]").forEach((button) => {
      button.classList.toggle("active", button.dataset.imageMode === state.imageMode);
    });
  }
}

function populatePatientSelect() {
  refs.patientSelect.innerHTML = "";
  state.cases.forEach((item) => {
    const option = document.createElement("option");
    option.value = item.patientId;
    option.textContent = `Patient ${item.patientId}`;
    refs.patientSelect.appendChild(option);
  });
}

function populateSequenceSelect() {
  const patient = state.cases.find((item) => item.patientId === state.patient);
  refs.sequenceSelect.innerHTML = "";
  patient.sequences.forEach((sequence) => {
    const option = document.createElement("option");
    option.value = sequence.name;
    option.textContent = sequence.name;
    refs.sequenceSelect.appendChild(option);
  });
}

function populateOrganSelect() {
  refs.organSelect.innerHTML = "";
  state.organs.forEach((organ) => {
    const option = document.createElement("option");
    option.value = organ.key;
    option.textContent = `${organ.name} (${organ.value})`;
    refs.organSelect.appendChild(option);
  });
  refs.organSelect.value = state.organ;
}

async function loadCases() {
  const payload = await apiGet("/api/cases");
  state.cases = payload.cases;
  state.organs = payload.organs || [];
  state.organ = payload.defaultOrgan || "liver";
  refs.datasetSummary.textContent = `${state.cases.length} Patients`;
  populatePatientSelect();
  state.patient = state.cases[0]?.patientId || null;
  refs.patientSelect.value = state.patient;
  populateSequenceSelect();
  state.sequence = state.cases[0]?.sequences[0]?.name || null;
  refs.sequenceSelect.value = state.sequence;
  populateOrganSelect();
  await loadCaseDetail();
}

async function loadCaseDetail() {
  if (!state.patient || !state.sequence) {
    return;
  }
  state.caseDetail = await apiGet(`/api/case?patient=${encodeURIComponent(state.patient)}&sequence=${encodeURIComponent(state.sequence)}`);
  refs.sliceCount.textContent = state.caseDetail.sliceCount;
  refs.sliceSlider.max = Math.max(0, state.caseDetail.sliceCount - 1);
  state.sliceIndex = Math.min(state.sliceIndex, state.caseDetail.sliceCount - 1);
  refs.sliceSlider.value = state.sliceIndex;
  await Promise.all([loadSlice(), loadVolume()]);
}

function setCanvasSize() {
  const container = refs.sliceCanvas.getBoundingClientRect();
  refs.sliceCanvas.width = Math.max(1, Math.floor(container.width * window.devicePixelRatio));
  refs.sliceCanvas.height = Math.max(1, Math.floor(container.height * window.devicePixelRatio));
  sliceCtx.setTransform(1, 0, 0, 1, 0, 0);
  sliceCtx.scale(window.devicePixelRatio, window.devicePixelRatio);

  const volumeRect = refs.volumeCanvas.getBoundingClientRect();
  refs.volumeCanvas.width = Math.max(1, Math.floor(volumeRect.width * window.devicePixelRatio));
  refs.volumeCanvas.height = Math.max(1, Math.floor(volumeRect.height * window.devicePixelRatio));
  volumeCtx.setTransform(1, 0, 0, 1, 0, 0);
  volumeCtx.scale(window.devicePixelRatio, window.devicePixelRatio);

  [
    [refs.segCanvas, segCtx],
    [refs.segEvalCanvas, segEvalCtx],
    [refs.segStudentVolumeCanvas, segStudentVolumeCtx],
    [refs.segGtVolumeCanvas, segGtVolumeCtx],
  ].forEach(([canvas, ctx]) => {
    const rect = canvas.getBoundingClientRect();
    canvas.width = Math.max(1, Math.floor(rect.width * window.devicePixelRatio));
    canvas.height = Math.max(1, Math.floor(rect.height * window.devicePixelRatio));
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
  });
}

function fitSliceToView() {
  if (!state.sliceData) {
    return;
  }
  const canvasWidth = refs.sliceCanvas.clientWidth;
  const canvasHeight = refs.sliceCanvas.clientHeight;
  const scale = Math.min(canvasWidth / state.sliceData.width, canvasHeight / state.sliceData.height) * 0.92;
  state.viewport.scale = scale;
  state.viewport.offsetX = canvasWidth / 2 - (state.sliceData.width / 2) * scale;
  state.viewport.offsetY = canvasHeight / 2 - (state.sliceData.height / 2) * scale;
}

async function loadSlice() {
  const payload = await apiGet(`/api/slice?patient=${encodeURIComponent(state.patient)}&sequence=${encodeURIComponent(state.sequence)}&index=${state.sliceIndex}&organ=${encodeURIComponent(state.organ)}`);
  state.sliceData = payload;
  state.polygon = [];
  state.closed = false;
  refs.sliceBadge.textContent = `${state.sliceIndex + 1} / ${payload.sliceCount}`;
  refs.sliceSlider.value = state.sliceIndex;
  refs.spacingText.textContent = `${payload.pixelSpacing[0].toFixed(2)} x ${payload.pixelSpacing[1].toFixed(2)} mm`;
  refs.thicknessText.textContent = `${payload.sliceThickness.toFixed(2)} mm`;
  refs.sliceLabel.textContent = payload.basename;
  refs.teachingText.textContent = payload.teachingText;
  refs.gtArea.textContent = payload.gtMaskArea.toLocaleString();
  refs.pdffLabel.textContent = payload.pdffLabel || "Approx. PDFF (%)";
  updatePdffStats("gt", payload.gtPdffStats);
  const imagePromises = [loadImage(payload.image), loadImage(payload.gtOverlay)];
  const waterImageIndex = payload.waterImage ? imagePromises.push(loadImage(payload.waterImage)) - 1 : -1;
  const fatImageIndex = payload.fatImage ? imagePromises.push(loadImage(payload.fatImage)) - 1 : -1;
  const pdffImageIndex = payload.pdffOverlay ? imagePromises.length : -1;
  if (payload.pdffOverlay) {
    imagePromises.push(loadImage(payload.pdffOverlay));
  }
  const loadedImages = await Promise.all(imagePromises);
  state.imageElement = loadedImages[0];
  state.gtElement = loadedImages[1];
  state.waterElement = waterImageIndex >= 0 ? loadedImages[waterImageIndex] : null;
  state.fatElement = fatImageIndex >= 0 ? loadedImages[fatImageIndex] : null;
  state.pdffElement = pdffImageIndex >= 0 ? loadedImages[pdffImageIndex] : null;
  updateImageModeControls();
  fitSliceToView();
  resetEvaluation();
  renderSlice();
  if (state.viewMode === "volume") {
    renderVolume();
  }
  if (state.viewMode === "tri") {
    state.triView.axial = state.sliceIndex;
    await loadOrthogonalViews();
  }
}

async function loadVolume() {
  const payload = await apiGet(`/api/volume?patient=${encodeURIComponent(state.patient)}&sequence=${encodeURIComponent(state.sequence)}&organ=${encodeURIComponent(state.organ)}`);
  state.volumeData = payload;
  refs.volumePdffMedian.textContent = payload.volumePdffMedian !== null && payload.volumePdffMedian !== undefined ? `${payload.volumePdffMedian.toFixed(2)}%` : "--";
  renderVolume();
}

async function loadOrthogonalViews() {
  const axialIndex = state.triView.axial ?? state.sliceIndex;
  const params = new URLSearchParams({
    patient: state.patient,
    sequence: state.sequence,
    index: String(axialIndex),
    organ: state.organ,
  });
  if (state.triView.coronal !== null) {
    params.set("coronal", String(state.triView.coronal));
  }
  if (state.triView.sagittal !== null) {
    params.set("sagittal", String(state.triView.sagittal));
  }
  const payload = await apiGet(`/api/orthogonal?${params.toString()}`);
  state.orthogonalData = payload;
  renderOrthogonalViews();
}

function renderOrthogonalViews() {
  if (!state.orthogonalData?.views?.length) {
    return;
  }
  state.orthogonalData.views.forEach((view) => {
    const prefix = view.key;
    refs[`${prefix}Title`].textContent = view.name;
    refs[`${prefix}Meta`].textContent = `${view.slice} / ${view.sliceCount}`;
    refs[`${prefix}Image`].src = view.image;
    state.triView[prefix] = view.index;
  });
  renderTriViewDetail();
}

function getTriView(viewKey) {
  return state.orthogonalData?.views?.find((view) => view.key === viewKey) || null;
}

function renderDirectionFigure(viewKey) {
  const info = TRI_VIEW_EXPLAINERS[viewKey] || TRI_VIEW_EXPLAINERS.axial;
  refs.triDirectionFigure.innerHTML = `
    <img src="${info.image}" alt="${info.title} direction diagram" />
  `;
}

function renderTriViewDetail() {
  const active = state.triView.active;
  refs.triViewOverview.classList.toggle("hidden", Boolean(active));
  refs.triViewDetail.classList.toggle("hidden", !active);
  if (!active) {
    return;
  }

  const view = getTriView(active);
  if (!view) {
    return;
  }
  refs.triDetailTitle.textContent = view.name;
  refs.triDetailMeta.textContent = `${view.slice} / ${view.sliceCount}`;
  refs.triDetailImage.src = view.image;
  refs.triDetailSlider.max = Math.max(0, view.sliceCount - 1);
  refs.triDetailSlider.value = view.index;
  refs.triExplainTitle.textContent = TRI_VIEW_EXPLAINERS[active].title;
  refs.triExplainText.textContent = TRI_VIEW_EXPLAINERS[active].text;
  renderDirectionFigure(active);
}

function imageToCanvas(point) {
  return {
    x: point[0] * state.viewport.scale + state.viewport.offsetX,
    y: point[1] * state.viewport.scale + state.viewport.offsetY,
  };
}

function canvasToImage(x, y) {
  return {
    x: (x - state.viewport.offsetX) / state.viewport.scale,
    y: (y - state.viewport.offsetY) / state.viewport.scale,
  };
}

function drawImageLandmarks(points, color) {
  if (!points?.length) {
    return;
  }
  sliceCtx.save();
  sliceCtx.translate(state.viewport.offsetX, state.viewport.offsetY);
  sliceCtx.scale(state.viewport.scale, state.viewport.scale);
  sliceCtx.fillStyle = color;
  points.forEach(([x, y]) => {
    sliceCtx.beginPath();
    sliceCtx.arc(x, y, 1.6, 0, Math.PI * 2);
    sliceCtx.fill();
  });
  sliceCtx.restore();
}

function drawPolygon() {
  if (!state.polygon.length) {
    return;
  }
  sliceCtx.save();
  sliceCtx.strokeStyle = "#ffbe49";
  sliceCtx.lineWidth = 2;
  sliceCtx.fillStyle = "#ffbe49";

  state.polygon.forEach((point, index) => {
    const canvasPoint = imageToCanvas(point);
    if (index === 0) {
      sliceCtx.beginPath();
      sliceCtx.moveTo(canvasPoint.x, canvasPoint.y);
    } else {
      sliceCtx.lineTo(canvasPoint.x, canvasPoint.y);
    }
  });

  if (state.closed && state.polygon.length > 2) {
    const first = imageToCanvas(state.polygon[0]);
    sliceCtx.lineTo(first.x, first.y);
  }
  sliceCtx.stroke();

  state.polygon.forEach((point, index) => {
    const canvasPoint = imageToCanvas(point);
    sliceCtx.beginPath();
    sliceCtx.arc(canvasPoint.x, canvasPoint.y, index === 0 ? 5 : 4, 0, Math.PI * 2);
    sliceCtx.fill();
  });
  sliceCtx.restore();
}

function renderSlice() {
  const width = refs.sliceCanvas.clientWidth;
  const height = refs.sliceCanvas.clientHeight;
  sliceCtx.clearRect(0, 0, width, height);
  if (!state.imageElement) {
    return;
  }
  const baseImage =
    state.imageMode === "water" && state.waterElement
      ? state.waterElement
      : state.imageMode === "fat" && state.fatElement
        ? state.fatElement
        : state.imageElement;

  sliceCtx.save();
  sliceCtx.translate(state.viewport.offsetX, state.viewport.offsetY);
  sliceCtx.scale(state.viewport.scale, state.viewport.scale);
  sliceCtx.drawImage(baseImage, 0, 0, state.sliceData.width, state.sliceData.height);
  if (state.imageMode === "pdff" && state.pdffElement) {
    sliceCtx.drawImage(state.pdffElement, 0, 0, state.sliceData.width, state.sliceData.height);
  }
  if (refs.showGtToggle.checked && state.gtElement) {
    sliceCtx.drawImage(state.gtElement, 0, 0, state.sliceData.width, state.sliceData.height);
  }
  if (state.comparisonElement) {
    sliceCtx.drawImage(state.comparisonElement, 0, 0, state.sliceData.width, state.sliceData.height);
  }
  sliceCtx.restore();

  if (refs.showContourToggle.checked) {
    drawImageLandmarks(state.sliceData.gtContour, "#42d7d0");
  }
  drawImageLandmarks(state.comparisonOverlay?.studentContour || [], "#ffbe49");
  drawPolygon();
  updateScaleBar();
}

function zoomAroundImagePoint(multiplier, imageX, imageY) {
  const nextScale = Math.max(0.4, Math.min(8, state.viewport.scale * multiplier));
  const canvasWidth = refs.sliceCanvas.clientWidth;
  const canvasHeight = refs.sliceCanvas.clientHeight;
  state.viewport.scale = nextScale;
  state.viewport.offsetX = canvasWidth / 2 - imageX * nextScale;
  state.viewport.offsetY = canvasHeight / 2 - imageY * nextScale;
  renderSlice();
}

function zoomAtImageCenter(multiplier) {
  if (!state.sliceData) {
    return;
  }
  zoomAroundImagePoint(multiplier, state.sliceData.width / 2, state.sliceData.height / 2);
}

function projectPoint(point) {
  let [x, y, z] = point;
  const cosYaw = Math.cos(state.volumeView.yaw);
  const sinYaw = Math.sin(state.volumeView.yaw);
  const cosPitch = Math.cos(state.volumeView.pitch);
  const sinPitch = Math.sin(state.volumeView.pitch);
  const x1 = x * cosYaw - z * sinYaw;
  const z1 = x * sinYaw + z * cosYaw;
  const y1 = y * cosPitch - z1 * sinPitch;
  const z2 = y * sinPitch + z1 * cosPitch;
  const perspective = 180 * state.volumeView.zoom / (z2 + 3.2);
  return { x: x1 * perspective, y: y1 * perspective, depth: z2 + 2.5 };
}

function drawVolumePoints(projected, width, height) {
  projected.forEach((point) => {
    if (point.sliceIndex === state.sliceIndex) {
      return;
    }
    const alpha = Math.max(0.12, 0.85 - point.depth * 0.25);
    const radius = Math.max(1.1, 4.5 - point.depth * 0.9);
    volumeCtx.beginPath();
    volumeCtx.fillStyle = `rgba(66, 215, 208, ${alpha})`;
    volumeCtx.arc(width / 2 + point.x, height / 2 + point.y, radius, 0, Math.PI * 2);
    volumeCtx.fill();
  });
}

function drawCurrentSliceFace(width, height) {
  const quads = state.volumeData?.slicePlanes?.[String(state.sliceIndex)];
  if (!quads?.length) {
    return;
  }
  volumeCtx.fillStyle = "rgba(255, 190, 73, 0.46)";
  quads.forEach((quad) => {
    const projectedQuad = quad.map((point) => projectPoint(point));
    volumeCtx.beginPath();
    projectedQuad.forEach((point, index) => {
      const x = width / 2 + point.x;
      const y = height / 2 + point.y;
      if (index === 0) {
        volumeCtx.moveTo(x, y);
      } else {
        volumeCtx.lineTo(x, y);
      }
    });
    volumeCtx.closePath();
    volumeCtx.fill();
  });
}

function renderVolume() {
  const width = refs.volumeCanvas.clientWidth;
  const height = refs.volumeCanvas.clientHeight;
  volumeCtx.clearRect(0, 0, width, height);
  volumeCtx.fillStyle = "rgba(255,255,255,0.02)";
  volumeCtx.fillRect(0, 0, width, height);
  if (!state.volumeData?.points?.length) {
    return;
  }

  const projected = state.volumeData.points.map((point, index) => ({
    ...projectPoint(point),
    sliceIndex: state.volumeData.pointSliceIndices?.[index],
  })).sort((a, b) => a.depth - b.depth);
  drawVolumePoints(projected, width, height);
  drawCurrentSliceFace(width, height);
  updateScaleBar();
}

async function setViewMode(mode) {
  state.viewMode = mode;
  const isVolumeMode = mode === "volume";
  const isTriViewMode = mode === "tri";
  refs.sliceCanvas.classList.toggle("hidden", isVolumeMode || isTriViewMode);
  refs.volumeCanvas.classList.toggle("hidden", !isVolumeMode);
  refs.triViewPanel.classList.toggle("hidden", !isTriViewMode);
  refs.canvasLegend.classList.toggle("hidden", isVolumeMode || isTriViewMode);
  refs.canvasHelp.classList.toggle("hidden", isTriViewMode);
  refs.imageModeGroup.classList.toggle("hidden", isVolumeMode || isTriViewMode);
  refs.volumePdffBadge.classList.toggle("hidden", !isVolumeMode);
  updatePdffColorbarVisibility();
  refs.viewModeBtn.textContent = isVolumeMode ? "2D Mode" : "3D Mode";
  refs.triViewBtn.textContent = isTriViewMode ? "2D View" : "Tri-View";
  refs.fitBtn.textContent = isVolumeMode ? "Reset View" : "Fit View";
  refs.fitBtn.disabled = isTriViewMode;
  refs.canvasHelp.textContent = isVolumeMode
    ? "Drag to rotate the 3D model. Mouse wheel zooms in and out."
    : isTriViewMode
      ? "Axial, coronal, and sagittal views are reconstructed from the current MRI slice stack."
    : "Left click adds contour points. Mouse wheel zooms around the image center. Right drag pans the image.";
  setCanvasSize();
  if (isVolumeMode) {
    renderVolume();
    return;
  }
  if (isTriViewMode) {
    state.triView.active = null;
    state.triView.axial = state.sliceIndex;
    await loadOrthogonalViews();
    updateScaleBar();
    return;
  }
  if (state.sliceData) {
    if (state.sliceData.index !== state.sliceIndex) {
      await loadSlice();
      return;
    }
    fitSliceToView();
    renderSlice();
  }
}

function segImageToCanvas(point) {
  return {
    x: point[0] * state.seg.viewport.scale + state.seg.viewport.offsetX,
    y: point[1] * state.seg.viewport.scale + state.seg.viewport.offsetY,
  };
}

function segCanvasToImage(x, y) {
  return {
    x: (x - state.seg.viewport.offsetX) / state.seg.viewport.scale,
    y: (y - state.seg.viewport.offsetY) / state.seg.viewport.scale,
  };
}

function fitSegSliceToView() {
  if (!state.seg.sliceData) {
    return;
  }
  const canvasWidth = refs.segCanvas.clientWidth;
  const canvasHeight = refs.segCanvas.clientHeight;
  const scale = Math.min(canvasWidth / state.seg.sliceData.width, canvasHeight / state.seg.sliceData.height) * 0.92 * 1.6;
  state.seg.viewport.scale = scale;
  state.seg.viewport.offsetX = canvasWidth / 2 - (state.seg.sliceData.width / 2) * scale;
  state.seg.viewport.offsetY = canvasHeight / 2 - (state.seg.sliceData.height / 2) * scale;
}

function drawSegPolygon(ctx = segCtx, polygon = state.seg.polygon, viewport = state.seg.viewport, closed = state.seg.closed) {
  if (!polygon.length) {
    return;
  }
  ctx.save();
  ctx.strokeStyle = "#ffbe49";
  ctx.lineWidth = 2;
  ctx.fillStyle = "#ffbe49";
  polygon.forEach((point, index) => {
    const canvasPoint = {
      x: point[0] * viewport.scale + viewport.offsetX,
      y: point[1] * viewport.scale + viewport.offsetY,
    };
    if (index === 0) {
      ctx.beginPath();
      ctx.moveTo(canvasPoint.x, canvasPoint.y);
    } else {
      ctx.lineTo(canvasPoint.x, canvasPoint.y);
    }
  });
  if (closed && polygon.length > 2) {
    const first = polygon[0];
    ctx.lineTo(first[0] * viewport.scale + viewport.offsetX, first[1] * viewport.scale + viewport.offsetY);
  }
  ctx.stroke();
  polygon.forEach((point, index) => {
    const canvasPoint = {
      x: point[0] * viewport.scale + viewport.offsetX,
      y: point[1] * viewport.scale + viewport.offsetY,
    };
    ctx.beginPath();
    ctx.arc(canvasPoint.x, canvasPoint.y, index === 0 ? 5 : 4, 0, Math.PI * 2);
    ctx.fill();
  });
  ctx.restore();
}

function renderSegSlice() {
  const width = refs.segCanvas.clientWidth;
  const height = refs.segCanvas.clientHeight;
  segCtx.clearRect(0, 0, width, height);
  if (!state.seg.imageElement || !state.seg.sliceData) {
    return;
  }
  segCtx.save();
  segCtx.translate(state.seg.viewport.offsetX, state.seg.viewport.offsetY);
  segCtx.scale(state.seg.viewport.scale, state.seg.viewport.scale);
  segCtx.drawImage(state.seg.imageElement, 0, 0, state.seg.sliceData.width, state.seg.sliceData.height);
  segCtx.restore();
  drawSegPolygon();
}

function updateSegStatus() {
  const record = state.seg.records[state.seg.current];
  const saved = Boolean(record?.saved);
  refs.segStatusBadge.textContent = saved ? "Saved" : "Not saved";
  refs.segStatusText.textContent = saved ? "This slice has a saved mask. Redo to redraw it." : "Draw a closed contour, then save the mask.";
  refs.finishSegBtn.disabled = !state.seg.records.length || state.seg.records.some((item) => !item.saved);
  const completed = state.seg.records.filter((item) => item.saved).length;
  const percent = state.seg.records.length ? Math.round((completed / state.seg.records.length) * 100) : 0;
  refs.segCompletionFill.style.width = `${percent}%`;
  refs.segCompletionText.textContent = `${percent}%`;
}

function renderSegProgress(activeIndex = state.seg.current, target = refs.segProgressStrip, clickable = true) {
  target.innerHTML = "";
  state.seg.records.forEach((record, index) => {
    const button = document.createElement("button");
    button.textContent = `${index + 1}: ${record.index}`;
    button.classList.toggle("done", Boolean(record.saved));
    button.classList.toggle("pending", !record.saved);
    button.classList.toggle("active", index === activeIndex);
    if (clickable) {
      button.addEventListener("click", () => loadSegPracticeIndex(index));
    } else {
      button.addEventListener("click", () => showSegEvaluationSlice(index));
    }
    target.appendChild(button);
  });
}

async function loadSegPracticeIndex(index) {
  if (!state.seg.session) {
    return;
  }
  state.seg.current = Math.max(0, Math.min(index, state.seg.records.length - 1));
  refs.segSliceQuickSlider.value = state.seg.current;
  const record = state.seg.records[state.seg.current];
  const payload = await apiGet(`/api/slice?patient=${encodeURIComponent(state.seg.session.patientId)}&sequence=${encodeURIComponent(state.seg.session.sequence)}&index=${record.index}&organ=${encodeURIComponent(state.seg.session.organKey)}`);
  state.seg.sliceData = payload;
  state.seg.imageElement = await loadImage(payload.image);
  state.seg.polygon = record.points ? record.points.map((point) => [...point]) : [];
  state.seg.closed = Boolean(record.closed);
  refs.segSliceTitle.textContent = `${record.label} (${state.seg.current + 1} / ${state.seg.records.length})`;
  fitSegSliceToView();
  renderSegProgress();
  updateSegStatus();
  renderSegSlice();
}

function addSegPoint(clientX, clientY) {
  if (!state.seg.sliceData || state.seg.closed) {
    return;
  }
  const rect = refs.segCanvas.getBoundingClientRect();
  const point = segCanvasToImage(clientX - rect.left, clientY - rect.top);
  if (point.x < 0 || point.x >= state.seg.sliceData.width || point.y < 0 || point.y >= state.seg.sliceData.height) {
    return;
  }
  if (state.seg.polygon.length >= 3) {
    const first = segImageToCanvas(state.seg.polygon[0]);
    const distance = Math.hypot(first.x - (clientX - rect.left), first.y - (clientY - rect.top));
    if (distance < 14) {
      state.seg.closed = true;
      renderSegSlice();
      return;
    }
  }
  state.seg.polygon.push([point.x, point.y]);
  renderSegSlice();
}

function saveSegMask() {
  if (!state.seg.closed || state.seg.polygon.length < 3) {
    refs.segStatusText.textContent = "Close the contour before saving.";
    return;
  }
  const record = state.seg.records[state.seg.current];
  record.points = state.seg.polygon.map((point) => [...point]);
  record.closed = true;
  record.saved = true;
  renderSegProgress();
  updateSegStatus();
}

function resetSegCurrent() {
  const record = state.seg.records[state.seg.current];
  record.points = [];
  record.closed = false;
  record.saved = false;
  state.seg.polygon = [];
  state.seg.closed = false;
  renderSegProgress();
  updateSegStatus();
  renderSegSlice();
}

async function startSegmentationSession() {
  refs.segStartStatus.textContent = "Selecting slices...";
  try {
    const payload = await apiPost("/api/segmentation/start", {
      patient: refs.segPatientSelect.value,
      organ: "liver",
      count: 10,
      minArea: 500,
    });
    state.seg.session = payload;
    state.seg.records = payload.slices.map((item) => ({ ...item, saved: false, points: [], closed: false }));
    state.seg.current = 0;
    refs.segSliceQuickSlider.max = Math.max(0, state.seg.records.length - 1);
    refs.segSliceQuickSlider.value = 0;
    refs.segStartPanel.classList.add("hidden");
    refs.segWorkspace.classList.remove("hidden");
    refs.segEvaluation.classList.add("hidden");
    setCanvasSize();
    await loadSegPracticeIndex(0);
  } catch (error) {
    refs.segStartStatus.textContent = error.message;
  }
}

function enterSegmentationMode() {
  refs.demoShell.classList.add("hidden");
  refs.segmentationShell.classList.remove("hidden");
  refs.segStartPanel.classList.remove("hidden");
  refs.segWorkspace.classList.add("hidden");
  refs.segEvaluation.classList.add("hidden");
  refs.segPatientSelect.innerHTML = "";
  state.cases.forEach((item) => {
    const option = document.createElement("option");
    option.value = item.patientId;
    option.textContent = item.patientId;
    refs.segPatientSelect.appendChild(option);
  });
  setCanvasSize();
}

function backToDemoMode() {
  refs.segmentationShell.classList.add("hidden");
  refs.demoShell.classList.remove("hidden");
  setCanvasSize();
  renderSlice();
  renderVolume();
}

async function finishSegmentationSession() {
  if (state.seg.records.some((item) => !item.saved)) {
    return;
  }
  refs.segStatusText.textContent = "Evaluating all saved masks...";
  const payload = await apiPost("/api/segmentation/evaluate", {
    patient: state.seg.session.patientId,
    sequence: state.seg.session.sequence,
    organ: state.seg.session.organKey,
    submissions: state.seg.records.map((record) => ({ index: record.index, points: record.points })),
  });
  state.seg.evaluation = payload;
  await Promise.all(
    payload.perSlice.map(async (item) => {
      item.comparisonElement = await loadImage(item.comparisonOverlay);
    })
  );
  refs.segWorkspace.classList.add("hidden");
  refs.segEvaluation.classList.remove("hidden");
  refs.segScoreBadge.textContent = `Score ${payload.score}`;
  refs.segStudentVolumePdff.textContent = payload.studentVolume.volumePdffMedian !== null && payload.studentVolume.volumePdffMedian !== undefined ? `${payload.studentVolume.volumePdffMedian.toFixed(2)}%` : "--";
  refs.segGtVolumePdff.textContent = payload.gtVolume.volumePdffMedian !== null && payload.gtVolume.volumePdffMedian !== undefined ? `${payload.gtVolume.volumePdffMedian.toFixed(2)}%` : "--";
  state.seg.evalCurrent = 0;
  state.seg.evalMode = "2d";
  refs.segEvalSliceSlider.max = Math.max(0, payload.perSlice.length - 1);
  refs.segEvalSliceSlider.value = "0";
  setCanvasSize();
  renderSegEvalStrip();
  await showSegEvaluationSlice(0);
}

function renderSegEvalStrip() {
  refs.segEvalStrip.innerHTML = "";
  state.seg.evaluation.perSlice.forEach((item, index) => {
    const button = document.createElement("button");
    button.textContent = `${index + 1}: Dice ${item.dice.toFixed(2)}`;
    button.classList.add("done");
    button.classList.toggle("active", index === state.seg.evalCurrent);
    button.addEventListener("click", () => showSegEvaluationSlice(index));
    refs.segEvalStrip.appendChild(button);
  });
}

async function showSegEvaluationSlice(index) {
  if (!state.seg.evaluation) {
    return;
  }
  state.seg.evalCurrent = Math.max(0, Math.min(index, state.seg.evaluation.perSlice.length - 1));
  refs.segEvalSliceSlider.value = String(state.seg.evalCurrent);
  const item = state.seg.evaluation.perSlice[state.seg.evalCurrent];
  const payload = await apiGet(`/api/slice?patient=${encodeURIComponent(state.seg.session.patientId)}&sequence=${encodeURIComponent(state.seg.session.sequence)}&index=${item.index}&organ=${encodeURIComponent(state.seg.session.organKey)}`);
  state.seg.sliceData = payload;
  state.seg.imageElement = await loadImage(payload.image);
  refs.segEvalTitle.textContent = `${item.label} (${state.seg.evalCurrent + 1} / ${state.seg.evaluation.perSlice.length})`;
  refs.segEvalDice.textContent = item.dice.toFixed(3);
  refs.segEvalIou.textContent = item.iou.toFixed(3);
  refs.segEvalUserPdff.textContent = item.studentPdffStats?.median !== undefined ? `${item.studentPdffStats.median.toFixed(2)}%` : "--";
  refs.segEvalGtPdff.textContent = item.gtPdffStats?.median !== undefined ? `${item.gtPdffStats.median.toFixed(2)}%` : "--";
  renderSegEvalStrip();
  fitSegEvalToView();
  renderSegEvaluation2d();
  renderSegEvaluationVolumes();
}

function fitSegEvalToView() {
  if (!state.seg.sliceData) {
    return;
  }
  const canvasWidth = refs.segEvalCanvas.clientWidth;
  const canvasHeight = refs.segEvalCanvas.clientHeight;
  const scale = Math.min(canvasWidth / state.seg.sliceData.width, canvasHeight / state.seg.sliceData.height) * 0.92;
  state.seg.viewport.scale = scale;
  state.seg.viewport.offsetX = canvasWidth / 2 - (state.seg.sliceData.width / 2) * scale;
  state.seg.viewport.offsetY = canvasHeight / 2 - (state.seg.sliceData.height / 2) * scale;
}

function renderSegEvaluation2d() {
  const width = refs.segEvalCanvas.clientWidth;
  const height = refs.segEvalCanvas.clientHeight;
  segEvalCtx.clearRect(0, 0, width, height);
  const item = state.seg.evaluation?.perSlice?.[state.seg.evalCurrent];
  if (!state.seg.imageElement || !state.seg.sliceData || !item) {
    return;
  }
  segEvalCtx.save();
  segEvalCtx.translate(state.seg.viewport.offsetX, state.seg.viewport.offsetY);
  segEvalCtx.scale(state.seg.viewport.scale, state.seg.viewport.scale);
  segEvalCtx.drawImage(state.seg.imageElement, 0, 0, state.seg.sliceData.width, state.seg.sliceData.height);
  segEvalCtx.drawImage(item.comparisonElement, 0, 0, state.seg.sliceData.width, state.seg.sliceData.height);
  segEvalCtx.restore();
}

function projectSegVolumePoint(point, projectionBase) {
  let [x, y, z] = point;
  const cosYaw = Math.cos(state.seg.volumeView.yaw);
  const sinYaw = Math.sin(state.seg.volumeView.yaw);
  const cosPitch = Math.cos(state.seg.volumeView.pitch);
  const sinPitch = Math.sin(state.seg.volumeView.pitch);
  const x1 = x * cosYaw - z * sinYaw;
  const z1 = x * sinYaw + z * cosYaw;
  const y1 = y * cosPitch - z1 * sinPitch;
  const z2 = y * sinPitch + z1 * cosPitch;
  const perspective = projectionBase * state.seg.volumeView.zoom / (z2 + 3.2);
  return { x: x1 * perspective, y: y1 * perspective, depth: z2 + 2.5 };
}

function drawSegVolume(ctx, canvas, volume, color) {
  const width = canvas.clientWidth;
  const height = canvas.clientHeight;
  ctx.clearRect(0, 0, width, height);
  ctx.fillStyle = "rgba(255,255,255,0.02)";
  ctx.fillRect(0, 0, width, height);
  if (!volume?.points?.length) {
    return;
  }
  const projectionBase = Math.min(width, height) * 0.23;
  const projected = volume.points.map((point, index) => ({
    ...projectSegVolumePoint(point, projectionBase),
    sliceIndex: volume.pointSliceIndices?.[index],
  })).sort((a, b) => a.depth - b.depth);
  projected.forEach((point) => {
    if (point.sliceIndex === state.seg.evalCurrent) {
      return;
    }
    const alpha = Math.max(0.12, 0.85 - point.depth * 0.25);
    ctx.beginPath();
    ctx.fillStyle = `rgba(${color}, ${alpha})`;
    ctx.arc(width / 2 + point.x, height / 2 + point.y, Math.max(1.1, 4.5 - point.depth * 0.9), 0, Math.PI * 2);
    ctx.fill();
  });
  const quads = volume.slicePlanes?.[String(state.seg.evalCurrent)] || [];
  ctx.fillStyle = "rgba(255, 190, 73, 0.46)";
  quads.forEach((quad) => {
    const projectedQuad = quad.map((point) => projectSegVolumePoint(point, projectionBase));
    ctx.beginPath();
    projectedQuad.forEach((point, index) => {
      const x = width / 2 + point.x;
      const y = height / 2 + point.y;
      if (index === 0) {
        ctx.moveTo(x, y);
      } else {
        ctx.lineTo(x, y);
      }
    });
    ctx.closePath();
    ctx.fill();
  });
}

function renderSegEvaluationVolumes() {
  if (!state.seg.evaluation) {
    return;
  }
  drawSegVolume(segStudentVolumeCtx, refs.segStudentVolumeCanvas, state.seg.evaluation.studentVolume, "180, 124, 255");
  drawSegVolume(segGtVolumeCtx, refs.segGtVolumeCanvas, state.seg.evaluation.gtVolume, "66, 215, 208");
}

function setSegEvalMode(mode) {
  state.seg.evalMode = mode;
  refs.segEval2dPanel.classList.toggle("hidden", mode !== "2d");
  refs.segEval3dPanel.classList.toggle("hidden", mode !== "3d");
  requestAnimationFrame(() => {
    setCanvasSize();
    if (mode === "2d") {
      renderSegEvaluation2d();
    } else {
      renderSegEvaluationVolumes();
    }
  });
}

function closeContour() {
  if (state.polygon.length < 3) {
    updateStatus("At least three points are required to close the contour.", "Warning");
    return;
  }
  state.closed = true;
  updateStatus("Contour closed. Press Evaluate to compare against the GT mask.", "Closed");
  renderSlice();
}

async function evaluateContour() {
  if (!state.closed) {
    updateStatus("Close the contour before evaluation.", "Warning");
    return;
  }
  try {
    const payload = await apiPost("/api/evaluate", {
      patient: state.patient,
      sequence: state.sequence,
      organ: state.organ,
      index: state.sliceIndex,
      points: state.polygon,
    });
    state.comparisonOverlay = payload;
    state.comparisonElement = await loadImage(payload.comparisonOverlay);
    refs.diceValue.textContent = payload.dice.toFixed(3);
    refs.iouValue.textContent = payload.iou.toFixed(3);
    refs.studentArea.textContent = payload.studentArea.toLocaleString();
    refs.gtArea.textContent = payload.groundTruthArea.toLocaleString();
    updatePdffStats("user", payload.studentPdffStats);
    updateStatus("Evaluation complete. Green shows the matched region.", "Scored");
    renderSlice();
  } catch (error) {
    updateStatus(error.message, "Error");
  }
}

function addPolygonPoint(clientX, clientY) {
  const rect = refs.sliceCanvas.getBoundingClientRect();
  const point = canvasToImage(clientX - rect.left, clientY - rect.top);
  if (!state.sliceData) {
    return;
  }
  if (point.x < 0 || point.x >= state.sliceData.width || point.y < 0 || point.y >= state.sliceData.height) {
    return;
  }

  if (!state.closed && state.polygon.length >= 3) {
    const first = imageToCanvas(state.polygon[0]);
    const distance = Math.hypot(first.x - (clientX - rect.left), first.y - (clientY - rect.top));
    if (distance < 14) {
      closeContour();
      return;
    }
  }

  if (state.closed) {
    return;
  }
  state.polygon.push([point.x, point.y]);
  state.comparisonOverlay = null;
  state.comparisonElement = null;
  updatePdffStats("user", null);
  updateStatus("Contour point added. Click near the first point or press C to close.", "Drawing");
  renderSlice();
}

function undoPoint() {
  if (state.closed) {
    state.closed = false;
  } else if (state.polygon.length) {
    state.polygon.pop();
  }
  state.comparisonOverlay = null;
  state.comparisonElement = null;
  updatePdffStats("user", null);
  renderSlice();
}

function resetPolygon() {
  state.polygon = [];
  state.closed = false;
  resetEvaluation();
  renderSlice();
}

function zoom(multiplier, anchorX = refs.sliceCanvas.clientWidth / 2, anchorY = refs.sliceCanvas.clientHeight / 2) {
  const imageX = (anchorX - state.viewport.offsetX) / state.viewport.scale;
  const imageY = (anchorY - state.viewport.offsetY) / state.viewport.scale;
  zoomAroundImagePoint(multiplier, imageX, imageY);
}

function zoomAtViewCenter(multiplier) {
  const centerImageX = (refs.sliceCanvas.clientWidth / 2 - state.viewport.offsetX) / state.viewport.scale;
  const centerImageY = (refs.sliceCanvas.clientHeight / 2 - state.viewport.offsetY) / state.viewport.scale;
  zoomAroundImagePoint(multiplier, centerImageX, centerImageY);
}

refs.patientSelect.addEventListener("change", async (event) => {
  state.patient = event.target.value;
  populateSequenceSelect();
  state.sequence = refs.sequenceSelect.value;
  state.sliceIndex = 0;
  await loadCaseDetail();
});

refs.sequenceSelect.addEventListener("change", async (event) => {
  state.sequence = event.target.value;
  state.sliceIndex = 0;
  await loadCaseDetail();
});

refs.organSelect.addEventListener("change", async (event) => {
  state.organ = event.target.value;
  await loadCaseDetail();
});

refs.sliceSlider.addEventListener("input", async (event) => {
  state.sliceIndex = Number(event.target.value);
  await loadSlice();
});

refs.prevSliceBtn.addEventListener("click", async () => {
  if (state.sliceIndex > 0) {
    state.sliceIndex -= 1;
    await loadSlice();
  }
});

refs.nextSliceBtn.addEventListener("click", async () => {
  if (state.caseDetail && state.sliceIndex < state.caseDetail.sliceCount - 1) {
    state.sliceIndex += 1;
    await loadSlice();
  }
});

refs.undoBtn.addEventListener("click", undoPoint);
refs.resetBtn.addEventListener("click", resetPolygon);
refs.closeBtn.addEventListener("click", closeContour);
refs.evaluateBtn.addEventListener("click", evaluateContour);
refs.viewModeBtn.addEventListener("click", () => {
  setViewMode(state.viewMode === "volume" ? "slice" : "volume");
});
refs.triViewBtn.addEventListener("click", () => {
  setViewMode(state.viewMode === "tri" ? "slice" : "tri");
});
refs.triViewOverview.addEventListener("click", (event) => {
  const card = event.target.closest("[data-tri-view]");
  if (!card) {
    return;
  }
  state.triView.active = card.dataset.triView;
  renderTriViewDetail();
});
refs.triBackBtn.addEventListener("click", () => {
  state.triView.active = null;
  renderTriViewDetail();
});
refs.triDetailSlider.addEventListener("input", async (event) => {
  const active = state.triView.active;
  if (!active) {
    return;
  }
  const index = Number(event.target.value);
  state.triView[active] = index;
  if (active === "axial") {
    state.sliceIndex = index;
    refs.sliceSlider.value = index;
    refs.sliceBadge.textContent = `${index + 1} / ${state.caseDetail.sliceCount}`;
  }
  await loadOrthogonalViews();
});
refs.fitBtn.addEventListener("click", () => {
  if (state.viewMode === "volume") {
    state.volumeView = { yaw: -0.6, pitch: 0.55, zoom: 10 };
    renderVolume();
    return;
  }
  fitSliceToView();
  renderSlice();
});
refs.showGtToggle.addEventListener("change", renderSlice);
refs.showContourToggle.addEventListener("change", renderSlice);
refs.gtPdffMeanMode.addEventListener("change", () => {
  updatePdffStats("gt", state.sliceData?.gtPdffStats || null);
});
refs.imageModeGroup.addEventListener("click", (event) => {
  const button = event.target.closest("button[data-image-mode]");
  if (!button || button.disabled) {
    return;
  }
  setImageMode(button.dataset.imageMode);
});

refs.enterSegmentationBtn.addEventListener("click", enterSegmentationMode);
refs.backToDemoBtn.addEventListener("click", backToDemoMode);
refs.startSegSessionBtn.addEventListener("click", startSegmentationSession);
refs.segPrevBtn.addEventListener("click", () => loadSegPracticeIndex(state.seg.current - 1));
refs.segNextBtn.addEventListener("click", () => loadSegPracticeIndex(state.seg.current + 1));
refs.segSliceQuickSlider.addEventListener("input", (event) => {
  loadSegPracticeIndex(Number(event.target.value));
});
refs.segUndoBtn.addEventListener("click", () => {
  if (state.seg.closed) {
    state.seg.closed = false;
  } else {
    state.seg.polygon.pop();
  }
  renderSegSlice();
});
refs.segRedoBtn.addEventListener("click", resetSegCurrent);
refs.segCloseBtn.addEventListener("click", () => {
  if (state.seg.polygon.length >= 3) {
    state.seg.closed = true;
    renderSegSlice();
  } else {
    refs.segStatusText.textContent = "At least three points are required.";
  }
});
refs.segSaveBtn.addEventListener("click", saveSegMask);
refs.finishSegBtn.addEventListener("click", finishSegmentationSession);
refs.segEval2dBtn.addEventListener("click", () => setSegEvalMode("2d"));
refs.segEval3dBtn.addEventListener("click", () => setSegEvalMode("3d"));
refs.segEvalSliceSlider.addEventListener("input", (event) => {
  showSegEvaluationSlice(Number(event.target.value));
});

refs.segCanvas.addEventListener("mousedown", (event) => {
  if (event.shiftKey || event.button === 1 || event.button === 2) {
    state.dragging = true;
    state.dragMode = "seg-pan";
    state.dragStart = {
      x: event.clientX,
      y: event.clientY,
      offsetX: state.seg.viewport.offsetX,
      offsetY: state.seg.viewport.offsetY,
    };
    return;
  }
  addSegPoint(event.clientX, event.clientY);
});

refs.segCanvas.addEventListener("mousemove", (event) => {
  if (!state.dragging || state.dragMode !== "seg-pan") {
    return;
  }
  state.seg.viewport.offsetX = state.dragStart.offsetX + (event.clientX - state.dragStart.x);
  state.seg.viewport.offsetY = state.dragStart.offsetY + (event.clientY - state.dragStart.y);
  renderSegSlice();
});

refs.segCanvas.addEventListener("wheel", (event) => {
  event.preventDefault();
  if (!state.seg.sliceData) {
    return;
  }
  const nextScale = Math.max(0.4, Math.min(8, state.seg.viewport.scale * (event.deltaY < 0 ? 1.08 : 1 / 1.08)));
  state.seg.viewport.scale = nextScale;
  state.seg.viewport.offsetX = refs.segCanvas.clientWidth / 2 - (state.seg.sliceData.width / 2) * nextScale;
  state.seg.viewport.offsetY = refs.segCanvas.clientHeight / 2 - (state.seg.sliceData.height / 2) * nextScale;
  renderSegSlice();
});

refs.segCanvas.addEventListener("contextmenu", (event) => event.preventDefault());

[refs.segStudentVolumeCanvas, refs.segGtVolumeCanvas].forEach((canvas) => {
  canvas.addEventListener("mousedown", (event) => {
    state.dragging = true;
    state.dragMode = "seg-volume";
    state.dragStart = { x: event.clientX, y: event.clientY, yaw: state.seg.volumeView.yaw, pitch: state.seg.volumeView.pitch };
  });
  canvas.addEventListener("mousemove", (event) => {
    if (!state.dragging || state.dragMode !== "seg-volume") {
      return;
    }
    state.seg.volumeView.yaw = state.dragStart.yaw + (event.clientX - state.dragStart.x) * 0.01;
    state.seg.volumeView.pitch = state.dragStart.pitch + (event.clientY - state.dragStart.y) * 0.01;
    renderSegEvaluationVolumes();
  });
  canvas.addEventListener("wheel", (event) => {
    event.preventDefault();
    state.seg.volumeView.zoom = Math.max(5, Math.min(15, state.seg.volumeView.zoom * (event.deltaY < 0 ? 1.08 : 1 / 1.08)));
    renderSegEvaluationVolumes();
  });
});

refs.sliceCanvas.addEventListener("mousedown", (event) => {
  if (event.button !== 0 && event.button !== 1 && event.button !== 2) {
    return;
  }
  if (event.shiftKey || event.button === 1 || event.button === 2) {
    state.dragging = true;
    state.dragMode = "pan";
    state.dragStart = {
      x: event.clientX,
      y: event.clientY,
      offsetX: state.viewport.offsetX,
      offsetY: state.viewport.offsetY,
    };
    return;
  }
  addPolygonPoint(event.clientX, event.clientY);
});

refs.sliceCanvas.addEventListener("mousemove", (event) => {
  if (!state.dragging || state.dragMode !== "pan") {
    return;
  }
  state.viewport.offsetX = state.dragStart.offsetX + (event.clientX - state.dragStart.x);
  state.viewport.offsetY = state.dragStart.offsetY + (event.clientY - state.dragStart.y);
  renderSlice();
});

refs.sliceCanvas.addEventListener("wheel", (event) => {
  event.preventDefault();
  zoomAtImageCenter(event.deltaY < 0 ? 1.08 : 1 / 1.08);
});

refs.sliceCanvas.addEventListener("contextmenu", (event) => {
  event.preventDefault();
});

refs.volumeCanvas.addEventListener("mousedown", (event) => {
  state.dragging = true;
  state.dragMode = "volume";
  state.dragStart = { x: event.clientX, y: event.clientY, yaw: state.volumeView.yaw, pitch: state.volumeView.pitch };
});

refs.volumeCanvas.addEventListener("mousemove", (event) => {
  if (!state.dragging || state.dragMode !== "volume") {
    return;
  }
  state.volumeView.yaw = state.dragStart.yaw + (event.clientX - state.dragStart.x) * 0.01;
  state.volumeView.pitch = state.dragStart.pitch + (event.clientY - state.dragStart.y) * 0.01;
  renderVolume();
});

refs.volumeCanvas.addEventListener("wheel", (event) => {
  event.preventDefault();
  state.volumeView.zoom = Math.max(5, Math.min(15, state.volumeView.zoom * (event.deltaY < 0 ? 1.08 : 1 / 1.08)));
  renderVolume();
});

window.addEventListener("mouseup", () => {
  state.dragging = false;
  state.dragMode = null;
});

window.addEventListener("keydown", async (event) => {
  if (event.target.tagName === "SELECT") {
    return;
  }
  if (event.key === "ArrowLeft" && state.sliceIndex > 0) {
    state.sliceIndex -= 1;
    await loadSlice();
  }
  if (event.key === "ArrowRight" && state.caseDetail && state.sliceIndex < state.caseDetail.sliceCount - 1) {
    state.sliceIndex += 1;
    await loadSlice();
  }
  if (event.key.toLowerCase() === "z") {
    undoPoint();
  }
  if (event.key.toLowerCase() === "r") {
    resetPolygon();
  }
  if (event.key.toLowerCase() === "c") {
    closeContour();
  }
  if (event.key.toLowerCase() === "g") {
    refs.showGtToggle.checked = !refs.showGtToggle.checked;
    renderSlice();
  }
  if (event.key === "Enter") {
    await evaluateContour();
  }
});

window.addEventListener("resize", () => {
  setCanvasSize();
  if (state.sliceData) {
    fitSliceToView();
    renderSlice();
  }
  renderVolume();
  if (state.viewMode === "tri") {
    renderOrthogonalViews();
  }
  if (!refs.segmentationShell.classList.contains("hidden")) {
    if (!refs.segWorkspace.classList.contains("hidden") && state.seg.sliceData) {
      fitSegSliceToView();
      renderSegSlice();
    }
    if (!refs.segEvaluation.classList.contains("hidden")) {
      fitSegEvalToView();
      renderSegEvaluation2d();
      renderSegEvaluationVolumes();
    }
  }
});

async function bootstrap() {
  setCanvasSize();
  await loadCases();
}

bootstrap().catch((error) => {
  updateStatus(error.message, "Error");
});
