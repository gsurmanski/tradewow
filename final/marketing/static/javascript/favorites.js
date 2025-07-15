document.addEventListener("DOMContentLoaded", () => {
  fetch("/favorites_data")
    .then(res => res.json())
    .then(data => {
      if (!data.success || !data.data) throw new Error(data.error || "Invalid data");

      const container = document.getElementById("favorites-container");
      const symbols = Object.keys(data.data);

      symbols.forEach(symbol => {
        const bars = data.data[symbol];

        //create card container
        const card = document.createElement("div");
        card.className = "border p-4 rounded shadow-md";

        //title with symbol and heart button
        const titleRow = document.createElement("div");
        titleRow.className = "flex items-center justify-between mb-2";

        const title = document.createElement("h3");
        title.className = "text-xl font-semibold";
        title.textContent = symbol;

        const favBtn = document.createElement("button");
        favBtn.className = "favorite noto-emoji text-xl";
        favBtn.id = `favorite-${symbol}`;
        favBtn.textContent = "♡"; //default, will update after

        titleRow.append(title, favBtn);

        //chart containers
        const priceDiv = document.createElement("div");
        priceDiv.id = `chart-${symbol}`;

        const volumeDiv = document.createElement("div");
        volumeDiv.id = `volume-${symbol}`;
        volumeDiv.className = "mt-4";

        //assemble card
        card.append(titleRow, priceDiv, volumeDiv);
        container.appendChild(card);

        //render charts
        renderCharts(symbol, bars);

        //setup favorite button
        setupFavoriteButton(symbol, favBtn);
      });
    })
    .catch(err => {
      console.error("Error loading favorites:", err);
      alert("Error loading favorites.");
    });
});

function renderCharts(symbol, bars) {
  const priceData = bars.map(bar => ({
    x: new Date(bar.timestamp),
    y: [bar.open, bar.high, bar.low, bar.close]
  }));

  const volumeData = bars.map(bar => ({
    x: new Date(bar.timestamp),
    y: bar.volume
  }));

  const priceChart = new ApexCharts(document.querySelector(`#chart-${symbol}`), {
    series: [{ name: symbol, data: priceData }],
    chart: { type: "candlestick", height: 300 },
    title: { text: `${symbol} Price`, align: "left" },
    xaxis: { type: "datetime" },
    yaxis: { tooltip: { enabled: true } }
  });

  const volumeChart = new ApexCharts(document.querySelector(`#volume-${symbol}`), {
    series: [{ name: "Volume", data: volumeData }],
    chart: { type: "bar", height: 150 },
    title: { text: "Volume", align: "left" },
    xaxis: { type: "datetime", labels: { show: false } },
    yaxis: {
      labels: {
        formatter: val =>
          val >= 1e6 ? (val / 1e6).toFixed(1) + "M" :
          val >= 1e3 ? (val / 1e3).toFixed(1) + "K" :
          val
      }
    },
    dataLabels: { enabled: false }
  });

  priceChart.render();
  volumeChart.render();
}

//get CSRF token
function getCSRFToken() {
  return document.querySelector('[name=csrf-token]')?.getAttribute("content");
}

//Setup heart/favorite button per stock
function setupFavoriteButton(symbol, buttonEl) {
  fetch(`/check_favorite_status?symbol=${symbol}`)
    .then(res => res.json())
    .then(data => {
      buttonEl.textContent = data.favorited ? "♥︎" : "♡";
    });

  buttonEl.addEventListener("click", () => {
    fetch("/toggle_favorite_stock", {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCSRFToken()
      },
      body: JSON.stringify({ symbol })
    })
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          buttonEl.textContent = data.favorited ? "♥︎" : "♡";
        } else {
          alert(data.message || "Failed to update favorite.");
        }
      });
  });
}
