(function () {
  var input = document.getElementById("food-search");
  var table = document.getElementById("foods-table");
  var countEl = document.getElementById("search-count");
  if (!input || !table) return;

  var rows = Array.prototype.slice.call(table.querySelectorAll("tbody tr"));

  function filter() {
    var q = input.value.trim().toLowerCase();
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

  input.addEventListener("input", filter);
  filter();
})();
