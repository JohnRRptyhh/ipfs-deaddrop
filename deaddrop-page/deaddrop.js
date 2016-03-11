var state = {
  view: 'welcome',
  url: 'http://siri.cbrp3.c-base.org/deaddrop.json',
  progress: {
    message: 'Publishing on IPFS...',
    percent: 100,
    qrcode: null
  },
  timer: null,
  lastShown: null
};

var drawQr = function (size, element, address) {
  element.innerHTML = '';
  var qrcode = new QRCode(element.id, {
    width: size,
    height: size
  });
  qrcode.makeCode(address);
};

var renderQr = function () {
  var size = window.innerHeight * 0.5;
  var qrcodeEl = document.getElementById('qrcode')
  drawQr(size, qrcodeEl, state.progress.qrcode);
  qrcodeEl.style.width = size + 'px';
  qrcodeEl.style.height = size + 'px';

  qrcodeEl.addEventListener('click', function () {
    window.location.href = state.progress.qrcode;
  });
  var parts = state.progress.qrcode.split('/ipfs/');
  if (parts.length == 1) {
    var qrString = state.progress.qrcode;
  } else {
    var qrString = parts[0] + '/ipfs/<br>' + parts[1];
  }
  document.getElementById('address').innerHTML = qrString;
};

var renderProgress = function () {
  var messageEl = document.getElementById('message');
  var statusEl = document.getElementById('status');
  messageEl.innerHTML = state.progress.message;
  statusEl.value = state.progress.percent;
};

var determineView = function () {
  if (state.progress.qrcode && state.progress.qrcode !== state.lastShown) {
    state.view = 'result';
    return;
  }
  if (state.progress.percent === 100) {
    state.view = 'welcome';
    return;
  }
  state.view = 'progress';
};

var render = function (address) {
  if (state.timer && state.lastShown && state.lastShown !== state.progress.qrcode) {
    window.clearTimeout(state.timer);
    state.timer = null;
  }
  var welcomeEl = document.getElementById('welcome');
  var progressEl = document.getElementById('progress');
  var resultEl = document.getElementById('result');
  switch (state.view) {
    case 'welcome':
      progressEl.style.display = 'none';
      resultEl.style.display = 'none';
      welcomeEl.style.display = 'block';
      break;
    case 'progress':
      state.lastShown = null;
      resultEl.style.display = 'none';
      welcomeEl.style.display = 'none';
      progressEl.style.display = 'block'
      renderProgress();
      break;
    case 'result':
      progressEl.style.display = 'none'
      welcomeEl.style.display = 'none';
      resultEl.style.display = 'block';
      renderQr();
      state.timer = window.setTimeout(function () {
        state.view = 'welcome';
        state.lastShown = state.progress.qrcode;
        state.progress.qrcode = null;
        render();
      }, 240 * 1000);
      break;
  }
};

var address = 'http://siri.cbrp3.c-base.org/deaddrop.json';
if (window.location.search) {
  address = window.location.search.substr(1);
}
state.url = address;

document.addEventListener('DOMContentLoaded', function () {
  render();
  setInterval(function () {
    fetchState();
  }, 1000);
  fetchState();
});
window.addEventListener('resize', function () {
  render();
});

var fetchState = function () {
  var req = new XMLHttpRequest;  
  req.open('GET', state.url, true);
  req.onload  = function() {
    if (req.readyState !== 4) {
      return;
    }
    if (req.status === 200) {
      state.progress = JSON.parse(req.responseText);
      determineView();
      render();
    }
  };
  req.send(null);
};
