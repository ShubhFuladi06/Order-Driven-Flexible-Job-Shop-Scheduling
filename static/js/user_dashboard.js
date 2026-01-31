console.log("✅ JS Loaded");
document.addEventListener("DOMContentLoaded", () => {

  const tableBody = document.getElementById("order-table-body");
  const addRowBtn = document.getElementById("add-row-btn");
  const finalSubmitBtn = document.getElementById("final-submit-btn");
  const resetBtn = document.getElementById("reset-dashboard-btn");
  const submittedSection = document.getElementById("submitted-orders-section");
  const submittedBody = document.getElementById("submitted-orders-body");

  const productOptions = `
    <option disabled selected>Select Product</option>
    <option value="Pant">Pant</option>
    <option value="Shirt">Shirt</option>
    <option value="Curtain">Curtain</option>
    <option value="Towel">Towel</option>
    <option value="T-shirt">T-shirt</option>
  `;

  loadTableData();

  addRowBtn.addEventListener("click", () => {
    addTableRow();
    saveTableData();
  });

  function addTableRow(product = "", quantity = "") {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>
        <select class="form-select product-name">
          ${productOptions}
        </select>
      </td>
      <td><input type="number" class="form-control" min="1" value="${quantity}" placeholder="Quantity"></td>
      <td>
        <button class="btn btn-sm btn-primary done-btn">Done</button>
        <button class="btn btn-sm btn-danger delete-btn ms-1">Remove</button>
      </td>
    `;
    tableBody.appendChild(row);

    if (product) {
      row.querySelector("select").value = product;
    }

    updateSubmitState();
  }

  tableBody.addEventListener("click", (e) => {
    if (e.target.classList.contains("done-btn")) {
      const row = e.target.closest("tr");
      const select = row.querySelector("select");
      const inputs = row.querySelectorAll("input");
      const allFilled = select.value && [...inputs].every(input =>
        input.value.trim() !== "" && (input.type !== "number" || parseInt(input.value) > 0)
      );
      if (!allFilled) {
        alert("Please fill all fields correctly before marking as Done.");
        return;
      }

      e.target.classList.replace("btn-primary", "btn-success");
      e.target.textContent = "Done ✔️";
      e.target.disabled = true;

      select.disabled = true;
      inputs.forEach(input => input.disabled = true);
      saveTableData();
      updateSubmitState();
    }

    if (e.target.classList.contains("delete-btn")) {
      e.target.closest("tr").remove();
      saveTableData();
      updateSubmitState();
    }
  });

  finalSubmitBtn.addEventListener("click", () => {
    const rows = tableBody.querySelectorAll("tr");
    const orders = [];

    rows.forEach(row => {
      const select = row.querySelector("select");
      const inputs = row.querySelectorAll("input");
      orders.push({
        product: select.value,
        quantity: inputs[0].value
      });
    });

    fetch("/save-product-demand/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCookie("csrftoken")
      },
      body: JSON.stringify(orders)
    })
      .then(res => res.json())
      .then(data => {
        if (data.status === "success") {
          alert("Product demand submitted successfully!");
          localStorage.removeItem("dashboardData");
          tableBody.innerHTML = "";
          submittedBody.innerHTML = "";
          orders.forEach(order => {
            const row = document.createElement("tr");
            row.innerHTML = `
              <td>${order.product}</td>
              <td>${order.quantity}</td>
            `;
            submittedBody.appendChild(row);
          });
          submittedSection.style.display = "block";
          finalSubmitBtn.disabled = true;
        }
      });
  });

  resetBtn.addEventListener("click", () => {
    tableBody.innerHTML = "";
    submittedBody.innerHTML = "";
    submittedSection.style.display = "none";
    localStorage.removeItem("dashboardData");
    finalSubmitBtn.disabled = true;
  });

  function updateSubmitState() {
    const rows = tableBody.querySelectorAll("tr");
    const allDone = [...rows].every(row => row.querySelector(".done-btn")?.disabled);
    finalSubmitBtn.disabled = !allDone || rows.length === 0;
  }

  function saveTableData() {
    const data = [];
    tableBody.querySelectorAll("tr").forEach(row => {
      const select = row.querySelector("select");
      const inputs = row.querySelectorAll("input");
      data.push({
        product: select.value,
        quantity: inputs[0].value,
        done: row.querySelector(".done-btn").disabled
      });
    });
    localStorage.setItem("dashboardData", JSON.stringify(data));
  }

  function loadTableData() {
    const saved = JSON.parse(localStorage.getItem("dashboardData") || "[]");
    saved.forEach(item => {
      addTableRow(item.product, item.quantity);
      const lastRow = tableBody.lastElementChild;
      if (item.done) {
        const doneBtn = lastRow.querySelector(".done-btn");
        doneBtn.classList.replace("btn-primary", "btn-success");
        doneBtn.textContent = "Done ✔️";
        doneBtn.disabled = true;
        lastRow.querySelector("select").disabled = true;
        lastRow.querySelectorAll("input").forEach(input => input.disabled = true);
      }
    });
    updateSubmitState();
  }

  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
      const cookies = document.cookie.split(";");
      for (let cookie of cookies) {
        const trimmed = cookie.trim();
        if (trimmed.startsWith(name + "=")) {
          cookieValue = decodeURIComponent(trimmed.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }
});
