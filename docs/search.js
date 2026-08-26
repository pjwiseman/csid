(function () {
  var input = document.getElementById("food-search");
  var table = document.getElementById("foods-table");
  var countEl = document.getElementById("search-count");
  var toggle = document.getElementById("show-phases");
  var rows = table
    ? Array.prototype.slice.call(table.querySelectorAll("tbody tr"))
    : [];

  function filter() {
    if (!table) return;
    var q = input ? input.value.trim().toLowerCase() : "";
    var visible = 0;

    rows.forEach(function (row) {
      var text = row.textContent.toLowerCase();
      var show = !q || text.indexOf(q) !== -1;
      row.classList.toggle("hidden", !show);
      if (show) visible += 1;
    });

    if (countEl) {
      countEl.textContent =
        q === ""
          ? rows.length + " foods"
          : visible + " of " + rows.length + " foods";
    }
  }

  function applyPhases() {
    var on = !!(toggle && toggle.checked);
    document.body.classList.toggle("show-phases", on);
    try {
      localStorage.setItem("csid-show-phases", on ? "1" : "0");
    } catch (e) {
      /* ignore */
    }
  }

  if (toggle) {
    try {
      toggle.checked = localStorage.getItem("csid-show-phases") === "1";
    } catch (e) {
      /* ignore */
    }
    toggle.addEventListener("change", applyPhases);
    applyPhases();
  }

  if (input && table) {
    input.addEventListener("input", filter);
    filter();
  }
})();
