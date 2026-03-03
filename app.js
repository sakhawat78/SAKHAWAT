const videoEl = document.getElementById('video');
const urlInput = document.getElementById('video-url');
const loadUrlBtn = document.getElementById('load-url');
const fileInput = document.getElementById('file-input');
const qualitySelect = document.getElementById('quality-select');
const statusEl = document.getElementById('status');

let hls = null;
let dashPlayer = null;
let objectUrl = null;

function setStatus(message) {
  statusEl.textContent = message;
}

function cleanupPlayers() {
  if (hls) {
    hls.destroy();
    hls = null;
  }
  if (dashPlayer) {
    dashPlayer.reset();
    dashPlayer = null;
  }
  if (objectUrl) {
    URL.revokeObjectURL(objectUrl);
    objectUrl = null;
  }
  qualitySelect.innerHTML = '<option value="auto">Auto</option>';
  qualitySelect.disabled = true;
}

function setVideoSource(src, typeHint = '') {
  cleanupPlayers();

  const source = src.toLowerCase();
  const isHls = source.includes('.m3u8') || typeHint.includes('mpegurl');
  const isDash = source.includes('.mpd') || typeHint.includes('dash+xml');

  if (isHls) {
    if (window.Hls?.isSupported()) {
      hls = new Hls({
        capLevelToPlayerSize: true,
        startLevel: -1
      });
      hls.loadSource(src);
      hls.attachMedia(videoEl);
      hls.on(Hls.Events.MANIFEST_PARSED, () => {
        populateHlsQualities();
        setStatus('HLS stream loaded with adaptive quality.');
        videoEl.play().catch(() => null);
      });
      hls.on(Hls.Events.ERROR, (_event, data) => {
        setStatus(`HLS error: ${data.details || data.type}`);
      });
      return;
    }

    if (videoEl.canPlayType('application/vnd.apple.mpegurl')) {
      videoEl.src = src;
      setStatus('Using native HLS playback.');
      videoEl.play().catch(() => null);
      return;
    }

    setStatus('HLS is not supported in this browser.');
    return;
  }

  if (isDash) {
    if (window.dashjs) {
      dashPlayer = dashjs.MediaPlayer().create();
      dashPlayer.initialize(videoEl, src, true);
      dashPlayer.updateSettings({
        streaming: {
          abr: { autoSwitchBitrate: { video: true } }
        }
      });
      dashPlayer.on(dashjs.MediaPlayer.events.STREAM_INITIALIZED, () => {
        populateDashQualities();
        setStatus('DASH stream loaded with adaptive quality.');
      });
      dashPlayer.on(dashjs.MediaPlayer.events.ERROR, (error) => {
        setStatus(`DASH error: ${error?.error || 'unknown'}`);
      });
      return;
    }
    setStatus('DASH player script failed to load.');
    return;
  }

  videoEl.src = src;
  videoEl.load();
  setStatus('Standard video loaded.');
}

function populateHlsQualities() {
  if (!hls) return;

  qualitySelect.disabled = false;
  qualitySelect.innerHTML = '<option value="auto">Auto</option>';
  hls.levels.forEach((level, index) => {
    const label = `${level.height || '?'}p (${Math.round(level.bitrate / 1000)} kbps)`;
    qualitySelect.insertAdjacentHTML(
      'beforeend',
      `<option value="${index}">${label}</option>`
    );
  });

  qualitySelect.onchange = () => {
    hls.currentLevel = qualitySelect.value === 'auto' ? -1 : Number(qualitySelect.value);
  };
}

function populateDashQualities() {
  if (!dashPlayer) return;

  const qualities = dashPlayer.getBitrateInfoListFor('video');
  qualitySelect.disabled = false;
  qualitySelect.innerHTML = '<option value="auto">Auto</option>';

  qualities.forEach((q, index) => {
    const label = `${q.height || '?'}p (${Math.round(q.bitrate / 1000)} kbps)`;
    qualitySelect.insertAdjacentHTML('beforeend', `<option value="${index}">${label}</option>`);
  });

  qualitySelect.onchange = () => {
    const auto = qualitySelect.value === 'auto';
    dashPlayer.updateSettings({
      streaming: { abr: { autoSwitchBitrate: { video: auto } } }
    });
    if (!auto) {
      dashPlayer.setQualityFor('video', Number(qualitySelect.value));
    }
  };
}

function loadFromInputUrl() {
  const url = urlInput.value.trim();
  if (!url) {
    setStatus('Please enter a video URL.');
    return;
  }
  setVideoSource(url);
}

function loadFromFile(file) {
  if (!file) return;

  objectUrl = URL.createObjectURL(file);
  const typeHint = file.type.toLowerCase();
  setVideoSource(objectUrl, typeHint);
}

loadUrlBtn.addEventListener('click', loadFromInputUrl);
urlInput.addEventListener('keydown', (event) => {
  if (event.key === 'Enter') loadFromInputUrl();
});

fileInput.addEventListener('change', () => {
  loadFromFile(fileInput.files?.[0]);
});

videoEl.addEventListener('error', () => {
  const err = videoEl.error;
  const message = err ? `Playback error code ${err.code}` : 'Playback failed.';
  setStatus(message);
});
