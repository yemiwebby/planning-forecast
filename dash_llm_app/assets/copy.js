document.addEventListener("DOMContentLoaded", function () {
  const textarea = document.getElementById("copy-box");
  if (textarea) {
    textarea.addEventListener("focus", function () {
      textarea.select();
    });
  }
});
