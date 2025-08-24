// static/js/index.js
(function() {
  let width = 320;
  let height = 0;
  let streaming = false;

  const video = document.getElementById('video');
  const canvas = document.getElementById('canvas');
  const photo = document.getElementById('photo');
  const formInput = document.getElementById('webimg');
  const startbutton = document.getElementById('startbutton');

  function startup() {
    navigator.mediaDevices.getUserMedia({ video: true, audio: false })
      .then(stream => {
        video.srcObject = stream;
        video.play();
      })
      .catch(err => console.error("Camera error:", err));

    video.addEventListener('canplay', () => {
      if (!streaming) {
        height = video.videoHeight / (video.videoWidth / width) || (width / 4 * 3);
        video.setAttribute('width', width);
        video.setAttribute('height', height);
        canvas.setAttribute('width', width);
        canvas.setAttribute('height', height);
        streaming = true;
      }
    }, false);

    startbutton.addEventListener('click', ev => {
      takepicture();
      ev.preventDefault();
    }, false);

    clearphoto();
  }

  function clearphoto() {
    const ctx = canvas.getContext('2d');
    ctx.fillStyle = "#AAA";
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    const data = canvas.toDataURL('image/png');
    photo.setAttribute('src', data);
  }

  function takepicture() {
    const ctx = canvas.getContext('2d');
    if (width && height) {
      canvas.width = width;
      canvas.height = height;
      ctx.drawImage(video, 0, 0, width, height);
      const data = canvas.toDataURL('image/png');
      photo.setAttribute('src', data);
      formInput.value = data;
    } else {
      clearphoto();
    }
  }

  window.addEventListener('load', startup, false);
})();
