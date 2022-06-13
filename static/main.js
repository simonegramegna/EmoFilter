const liveStreamingButton = document.querySelector(".button-livestreaming")
const uploadButton = document.querySelector(".button-upload")
const uploadModal = document.querySelector(".modal-upload")
const liveStreamingModal = document.querySelector(".modal-livestream")
const overlay = document.querySelector(".overlay")
const exitButton = document.querySelector(".button-exit")
const button_screen = document.querySelector(".button-screen")
const modal_screenshot = document.querySelector(".modal_screenshot")
const modalImg = document.querySelector(".modal_screenshot .screenshot img")

liveStreamingButton.addEventListener("click", () => {
    overlay.classList.add("open")
    liveStreamingModal.classList.add("open")
})


uploadButton.addEventListener("click", () => {
    overlay.classList.add("open")
    uploadModal.classList.add("open")
})


overlay.addEventListener("click", () => {
    uploadModal.classList.remove("open")
    liveStreamingModal.classList.remove("open")
    overlay.classList.remove("open")
    modal_screenshot.classList.remove('open')
    modalImg.removeAttribute('src')
})

exitButton.addEventListener("click", () => {
    uploadModal.classList.remove("open")
    liveStreamingModal.classList.remove("open")
    overlay.classList.remove("open")
    modal_screenshot.classList.remove('open')
    modalImg.removeAttribute('src')
})

button_screen.addEventListener("click", async() => {

    let img = document.getElementById("im1")
    let canvas = document.getElementById("canvas")

    canvas.getContext('2d').drawImage(img, 0, 0, canvas.width, canvas.height);

    let image_data_url = canvas.toDataURL('image/jpeg');
    console.log(image_data_url)

    liveStreamingModal.classList.remove("open")
    modal_screenshot.classList.add("open")
})

function save_img(){
    fetch("/save_frame", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
   
  })
    .then(resp => {
      if (resp.ok)
        resp.json().then(data => {
         
        });
    })
    .catch(err => {
      console.log("An error occured", err.message);
      window.alert("Oops! Something went wrong.");
    });
}


function download(url) {
  var element = document.createElement('a');
  var imageURI = canvas.toDataURL("image/jpg");
  element.setAttribute('href', imageURI);

  let file_name = "face_capture_" + Date.now().toString() + '.jpg'
  element.setAttribute('download', file_name);

  element.style.display = 'none';
  document.body.appendChild(element);

  element.click();

  document.body.removeChild(element);
  if(url)
  window.location.href=url;
  
}

