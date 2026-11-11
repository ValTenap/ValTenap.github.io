/* A live q-plate vector beam.
   Each ellipse is the local polarization of a doughnut beam after a q-plate:
     orientation  psi(phi) = q * phi + beta       (beta = input polarizer angle)
     ellipticity  set by the slider below (0 = linear, 1 = circular)
   Colour encodes orientation, like the hue maps in a Stokes measurement.
   Move the pointer across the beam to rotate the input polarizer. */
(function () {
  var fig = document.querySelector('.beam');
  if (!fig) return;
  var canvas = fig.querySelector('canvas');
  var out = fig.querySelector('output');
  var ctx = canvas.getContext('2d');
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  var Q = parseFloat(fig.getAttribute('data-q') || '0.5');
  var beta = 0, target = 0, t0 = performance.now(), size = 0, dpr = 1;
  var userMoved = false;

  function resize() {
    dpr = Math.min(window.devicePixelRatio || 1, 2);
    var r = canvas.getBoundingClientRect();
    size = r.width;
    canvas.width = Math.round(r.width * dpr);
    canvas.height = Math.round(r.height * dpr);
  }

  function hue(psi) {               // orientation in [0, pi) -> hue in degrees
    var a = ((psi % Math.PI) + Math.PI) % Math.PI;
    return (a / Math.PI) * 360;
  }

  function draw(now) {
    var t = (now - t0) / 1000;
    if (!userMoved && !reduce) target = 0.35 * Math.sin(t * 0.25) * Math.PI;
    beta = reduce ? target : beta + (target - beta) * 0.08;

    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, size, size);
    var c = size / 2, R = size * 0.46;

    // glow of the doughnut intensity |r|^2 exp(-2 r^2)
    var g = ctx.createRadialGradient(c, c, R * 0.05, c, c, R);
    g.addColorStop(0.0, 'rgba(232,49,42,0)');
    g.addColorStop(0.42, 'rgba(232,49,42,0.20)');
    g.addColorStop(0.62, 'rgba(232,49,42,0.12)');
    g.addColorStop(1.0, 'rgba(232,49,42,0)');
    ctx.fillStyle = g;
    ctx.beginPath(); ctx.arc(c, c, R, 0, 2 * Math.PI); ctx.fill();

    var n = size < 380 ? 15 : 19, step = (2 * R) / n;
    var ell = 0.18 + 0.08 * Math.sin(t * 0.6);            // gentle breathing ellipticity
    if (reduce) ell = 0.18;
    for (var i = 0; i < n; i++) {
      for (var j = 0; j < n; j++) {
        var x = -R + step * (i + 0.5), y = -R + step * (j + 0.5);
        var rr = Math.sqrt(x * x + y * y) / R;              // 0..1
        if (rr > 1) continue;
        var s = rr * 1.6;
        var I = (s * s) * Math.exp(-2 * s * s) / (0.5 * Math.exp(-1));
        if (I < 0.08) continue;
        var phi = Math.atan2(-y, x);
        var psi = Q * phi + beta;
        var a = step * 0.46 * Math.pow(I, 0.35), b = a * ell;
        ctx.save();
        ctx.translate(c + x, c + y);
        ctx.rotate(-psi);
        ctx.beginPath();
        ctx.ellipse(0, 0, a, b, 0, 0, 2 * Math.PI);
        ctx.strokeStyle = 'hsla(' + hue(psi).toFixed(0) + ',85%,68%,' + (0.35 + 0.65 * I).toFixed(2) + ')';
        ctx.lineWidth = 1.4;
        ctx.stroke();
        ctx.restore();
      }
    }
    if (out) {
      var deg = ((beta * 180 / Math.PI) % 180 + 180) % 180;
      out.textContent = deg.toFixed(0) + '°';
    }
    if (!reduce) requestAnimationFrame(draw);
  }

  function pointer(e) {
    var r = canvas.getBoundingClientRect();
    var fx = (e.clientX - r.left) / r.width;                // 0..1 across the beam
    target = (fx - 0.5) * Math.PI;                          // -90..90 degrees
    userMoved = true;
    if (reduce) requestAnimationFrame(draw);
  }
  canvas.addEventListener('pointermove', pointer);
  canvas.addEventListener('pointerdown', pointer);
  canvas.addEventListener('keydown', function (e) {
    if (e.key === 'ArrowLeft' || e.key === 'ArrowRight') {
      target += (e.key === 'ArrowLeft' ? -1 : 1) * Math.PI / 36;
      userMoved = true;
      if (reduce) requestAnimationFrame(draw);
      e.preventDefault();
    }
  });
  window.addEventListener('resize', function () { resize(); if (reduce) draw(performance.now()); });
  resize();
  requestAnimationFrame(draw);
})();
