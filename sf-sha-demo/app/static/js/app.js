// Small, shared browser behaviour. Each feature is switched on by a
// data-* attribute in the HTML, so templates never need inline scripts.
(function () {
  "use strict";

  // 1. Login page: "Use" buttons fill the email and password boxes.
  document.querySelectorAll("[data-fill-email]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      document.getElementById("email").value = btn.dataset.fillEmail;
      document.getElementById("password").value = btn.dataset.fillPassword;
      document.getElementById("password").focus();
    });
  });

  // 2. Forms with data-confirm ask "Are you sure?" before submitting (e.g. reset).
  document.querySelectorAll("form[data-confirm]").forEach(function (form) {
    form.addEventListener("submit", function (event) {
      if (!window.confirm(form.dataset.confirm)) event.preventDefault();
    });
  });

  // 3. Forms with data-validate show friendly messages next to empty or invalid
  //    fields before sending. The server checks again — this is only for comfort.
  document.querySelectorAll("form[data-validate]").forEach(function (form) {
    form.addEventListener("submit", function (event) {
      var firstBad = null;
      form.querySelectorAll("input[required]").forEach(function (input) {
        var old = input.parentElement.querySelector(".field-error");
        if (old) old.remove();
        input.removeAttribute("aria-invalid");
        if (!input.checkValidity()) {
          var msg = document.createElement("span");
          msg.className = "field-error";
          msg.textContent = input.value ? "Please check this value." : "This field is required.";
          input.setAttribute("aria-invalid", "true");
          input.parentElement.appendChild(msg);
          firstBad = firstBad || input;
        }
      });
      if (firstBad) { event.preventDefault(); firstBad.focus(); }
    });
  });

  // 4. Small screens: the ☰ button opens and closes the sidebar.
  var toggle = document.querySelector("[data-toggle-sidebar]");
  var sidebar = document.getElementById("sidebar");
  if (toggle && sidebar) {
    toggle.addEventListener("click", function () { sidebar.classList.toggle("open"); });
    document.addEventListener("click", function (event) {
      if (sidebar.classList.contains("open") && !sidebar.contains(event.target) && event.target !== toggle) {
        sidebar.classList.remove("open");
      }
    });
  }
})();
