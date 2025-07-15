document.addEventListener("DOMContentLoaded", () => {
  //get reddit news
  fetch('/api_reddit')
    .then(response => response.json())
    .then(data => {
      if (data.success){
        data.news.forEach(post => {
          const postContainer = document.createElement("div");
          const link = document.createElement("a");
          const score = document.createElement("span");

          link.href = post.url;
          link.textContent = post.title;
          link.target = "_blank";
          link.rel = "noopener noreferrer";

          score.textContent = ` (Score: ${post.score})`;

          postContainer.appendChild(link);
          postContainer.appendChild(score);
          document.querySelector("#reddit").appendChild(postContainer);
        });
      }
    })
    .catch(error => {
      console.error("Reddit API error:", error);
      const errorMessage = document.createElement("p");
      errorMessage.textContent = "Unable to load Reddit posts at the moment.";
      document.querySelector("#reddit").appendChild(errorMessage);
    });
});
//candle graph
let priceChart = null;
let volumeChart = null;
let currentSymbol = "GLD";
let currentTimeframe = 30; // default days

// Create card container with Tailwind styling and return favorite button
function createStockCard(container, symbol) {
  // Clear previous content first
  container.innerHTML = "";

  // Create card container
  const card = document.createElement("div");
  card.className = "border p-4 rounded shadow-md";

  // Title row with symbol and heart button
  const titleRow = document.createElement("div");
  titleRow.className = "flex items-center justify-between mb-2";

  const title = document.createElement("h3");
  title.className = "text-xl font-semibold";
  title.textContent = symbol;

  const favBtn = document.createElement("button");
  favBtn.className = "favorite noto-emoji text-2xl";
  favBtn.id = `favorite-${symbol}`;
  favBtn.textContent = "♡"; // default, update later

  titleRow.append(title, favBtn);

  // Price chart container - full width
  const priceDiv = document.createElement("div");
  priceDiv.id = `chart-${symbol}`;
  priceDiv.className = "w-full";

  // Volume chart container - full width with margin top
  const volumeDiv = document.createElement("div");
  volumeDiv.id = `volume-${symbol}`;
  volumeDiv.className = "mt-4 w-full";

  // Assemble card content
  card.append(titleRow, priceDiv, volumeDiv);

  // Append to main container
  container.appendChild(card);

  return { favBtn, priceDivId: priceDiv.id, volumeDivId: volumeDiv.id };
}

// Fetch data and render charts inside the card container
function loadChart(symbol, days) {
  const container = document.querySelector("#chart-container") || document.querySelector("#chart");
  if (!container) {
    console.error("No container element found to render charts");
    return;
  }

  // Create card & get elements
  const { favBtn, priceDivId, volumeDivId } = createStockCard(container, symbol);

  // Setup favorite button with fetched symbol and button element
  setupFavoriteButton(symbol, favBtn);

  const now = new Date();
  const end = new Date(now.getTime() - 1000 * 60 * 20); // buffer 20 min
  const start = new Date(end.getTime() - days * 24 * 60 * 60 * 1000);

  const params = new URLSearchParams({
    symbol,
    start: start.toISOString(),
    end: end.toISOString()
  });

  fetch(`/api_alpaca?${params}`)
    .then(res => res.json())
    .then(data => {
      if (!data.success) throw new Error(data.error || "Failed to fetch stock data");

      const priceData = data.news.map(bar => ({
        x: new Date(bar.timestamp),
        y: [bar.open, bar.high, bar.low, bar.close]
      }));

      const volumeData = data.news.map(bar => ({
        x: new Date(bar.timestamp),
        y: bar.volume
      }));

      // If charts already exist, destroy before recreating
      if (priceChart) priceChart.destroy();
      if (volumeChart) volumeChart.destroy();

      const priceOptions = {
        series: [{ data: priceData }],
        chart: {
          type: "candlestick",
          height: 350,
          toolbar: {
            tools: {
              pan: true,
              zoom: true,
              zoomin: true,
              zoomout: true,
              reset: true
            }
          },
          zoom: { enabled: true, type: "x", autoScaleYaxis: true },
          pan: { enabled: true, type: "x" },
          events: {
            zoomed(chartContext, { xaxis }) {
              if (chartContext === priceChart) {
                volumeChart.updateOptions({
                  xaxis: {
                    min: xaxis.min,
                    max: xaxis.max,
                    type: "datetime"
                  }
                }, false, false);
              }
            },
            scrolled(chartContext, { xaxis }) {
              if (chartContext === priceChart) {
                volumeChart.updateOptions({
                  xaxis: {
                    min: xaxis.min,
                    max: xaxis.max,
                    type: "datetime"
                  }
                }, false, false);
              }
            }
          }
        },
        title: {
          text: `${symbol} Candlestick Chart (${days}-Day)`,
          align: "left"
        },
        xaxis: { type: "datetime" },
        yaxis: { tooltip: { enabled: true } }
      };

      const volumeOptions = {
        series: [{ name: "Volume", data: volumeData }],
        chart: {
          type: "bar",
          height: 150,
          toolbar: { show: false },
          zoom: { enabled: false },
          events: {
            zoomed(chartContext, { xaxis }) {
              if (chartContext === volumeChart) {
                priceChart.updateOptions({
                  xaxis: {
                    min: xaxis.min,
                    max: xaxis.max,
                    type: "datetime"
                  }
                }, false, false);
              }
            },
            scrolled(chartContext, { xaxis }) {
              if (chartContext === volumeChart) {
                priceChart.updateOptions({
                  xaxis: {
                    min: xaxis.min,
                    max: xaxis.max,
                    type: "datetime"
                  }
                }, false, false);
              }
            }
          }
        },
        dataLabels: {
          enabled: false
        },
        title: {
          text: "Volume",
          align: "left",
          offsetX: 10
        },
        xaxis: {
          type: "datetime",
          labels: { show: false }
        },
        yaxis: {
          labels: {
            formatter: val => {
              if (val >= 1_000_000) return (val / 1_000_000).toFixed(1) + "M";
              if (val >= 1_000) return (val / 1_000).toFixed(1) + "K";
              return val;
            }
          }
        },
        tooltip: { shared: true, intersect: false }
      };

      priceChart = new ApexCharts(document.getElementById(priceDivId), priceOptions);
      volumeChart = new ApexCharts(document.getElementById(volumeDivId), volumeOptions);

      Promise.all([priceChart.render(), volumeChart.render()])
        .catch(err => {
          console.error("Error rendering charts:", err);
          alert("Error rendering charts: " + err.message);
        });
    })
    .catch(err => {
      console.error("Error fetching data:", err);
      alert("Error loading chart: " + err.message);
    });
}

// Called on search form submit
function fetchStockData() {
  const input = document.getElementById("symbolInput").value.trim().toUpperCase();
  if (input) currentSymbol = input;
  loadChart(currentSymbol, currentTimeframe);
}

// Called on timeframe buttons click
function setTimeframe(days) {
  currentTimeframe = days;
  loadChart(currentSymbol, currentTimeframe);
}

// Initialize page event listeners and load default chart
document.addEventListener("DOMContentLoaded", () => {
  loadChart(currentSymbol, currentTimeframe);

  const form = document.getElementById("searchForm");
  if (form) {
    form.addEventListener("submit", e => {
      e.preventDefault();
      fetchStockData();
    });
  }
});

// Function to get CSRF token
function getCSRFToken() {
  return document.querySelector('[name=csrf-token]')?.getAttribute('content');
}

// Setup favorite button with symbol and button element
function setupFavoriteButton(symbol, buttonElement) {
  if (!buttonElement) return;

  // Check current favorite status
  fetch(`/check_favorite_status?symbol=${symbol}`)
    .then(res => res.json())
    .then(data => {
      buttonElement.textContent = data.favorited ? "♥︎" : "♡";
    })
    .catch(() => {
      buttonElement.textContent = "♡"; // fallback
    });

  buttonElement.onclick = () => {
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
        buttonElement.textContent = data.favorited ? "♥︎" : "♡";
      } else {
        alert(data.message || "Failed to update favorite.");
      }
    })
    .catch(() => {
      alert("Network error toggling favorite.");
    });
  };
}
