'use strict';

document.addEventListener('DOMContentLoaded', function() {
    const deleteModalWatchFilm = document.getElementById('deleteModalWatchFilm');
    deleteModalWatchFilm.addEventListener('show.bs.modal', function(event) {
      const button = event.relatedTarget;
      const recordId = button.getAttribute('data-record-id');
      const form = document.getElementById('deleteModalWatchFilmForm');
      form.action = `/users/watch_film/${recordId}/delete_watch_film`;
    });
});

document.addEventListener('DOMContentLoaded', function() {
  const deleteModalFilm = document.getElementById('deleteModalFilm');
  deleteModalFilm.addEventListener('show.bs.modal', function(event) {
    const button = event.relatedTarget;
    const filmId = button.getAttribute('data-film-id');
    const form = document.getElementById('deleteModalFilmForm');
    form.action = `/admin_films/${filmId}/delete_film`;
  });
});


function imagePreviewHandler(event, previewElement) {
  if (event.target.files && event.target.files[0]) {
      let reader = new FileReader();
      reader.onload = function(e) {
          previewElement.src = e.target.result;
      }
      reader.readAsDataURL(event.target.files[0]);
  }
}

let posterField = document.getElementById('poster');
let posterPreview = document.querySelector('.background-preview > img');
if (posterField && posterPreview) {
  posterField.addEventListener('change', function(event) {
      imagePreviewHandler(event, posterPreview);
  });
}

let stillField1 = document.getElementById('still1');
let stillPreview1 = document.getElementById('still-img1');
if (stillField1 && stillPreview1) {
  stillField1.addEventListener('change', function(event) {
      imagePreviewHandler(event, stillPreview1);
  });
}

let stillField2 = document.getElementById('still2');
let stillPreview2 = document.getElementById('still-img2');
if (stillField2 && stillPreview2) {
  stillField2.addEventListener('change', function(event) {
      imagePreviewHandler(event, stillPreview2);
  });
}

let stillField3 = document.getElementById('still3');
let stillPreview3 = document.getElementById('still-img3');
if (stillField3 && stillPreview3) {
  stillField3.addEventListener('change', function(event) {
      imagePreviewHandler(event, stillPreview3);
  });
}