$(document).ready(function() {
    $('#user').select2();
});

const plot_margin = {
    t: 30,
    b: 90
};

const plot_height = 225;

async function fetchData() {
    const response = await fetch('/mid_price');
    const data = await response.json();
    return data;
}

async function fetchOrderBook() {
    const response = await fetch('/orderbook');
    const data = await response.json();
    return data;
}

async function fetchPnlHistory(user) {
    const response = await fetch(`/pnl_history/${user}`);
    const data = await response.json();
    return data;
}

async function fetchPositions(user) {
    const response = await fetch(`/positions/${user}`);
    const data = await response.json();
    return data;
}

async function updatePlot() {
    const data = await fetchData();
    Plotly.react('plot', [{
        x: data.times,
        y: data.prices,
        mode: 'lines',
        name: 'Price',
        line: { color: '#1f77b4', shape: 'hv' }
    }], {
        xaxis: {
            title: 'Time',
            titlefont: {
                family: 'Arial, sans-serif',
                size: 18,
                color: 'black',
                weight: 'bold'
            },
            tickfont: {
                family: 'Arial, sans-serif',
                size: 14,
                color: 'black',
                weight: 'bold'
            },
            tickangle: 0
        },
        yaxis: {
            title: 'Price',
            titlefont: {
                family: 'Arial, sans-serif',
                size: 18,
                color: 'black',
                weight: 'bold'
            },
            tickfont: {
                family: 'Arial, sans-serif',
                size: 14,
                color: 'black',
                weight: 'bold'
            }
        },
        margin: plot_margin,
        height: plot_height,
        barmode: 'overlay'
    }, {
        responsive: true
    });
}

async function updateOrderBook() {
    const data = await fetchOrderBook();
    const bidPrices = data.bids.map(d => d[0]);
    const bidVolumes = data.bids.map(d => d[1]);
    const askPrices = data.asks.map(d => d[0]);
    const askVolumes = data.asks.map(d => d[1]);
    Plotly.react('orderbook', [
        {
            x: bidPrices,
            y: bidVolumes,
            type: 'bar',
            orientation: 'v',
            name: 'Bids',
            marker: { color: 'rgb(119, 221, 119)' }
        },
        {
            x: askPrices,
            y: askVolumes,
            type: 'bar',
            orientation: 'v',
            name: 'Asks',
            marker: { color: 'rgb(255, 179, 186)' }
        }
    ], {
        xaxis: {
            title: 'Price',
            titlefont: {
                family: 'Arial, sans-serif',
                size: 18,
                color: 'black',
                weight: 'bold'
            },
            tickfont: {
                family: 'Arial, sans-serif',
                size: 14,
                color: 'black',
                weight: 'bold'
            }
        },
        yaxis: {
            title: 'Volume',
            titlefont: {
                family: 'Arial, sans-serif',
                size: 18,
                color: 'black',
                weight: 'bold'
            },
            tickfont: {
                family: 'Arial, sans-serif',
                size: 14,
                color: 'black',
                weight: 'bold'
            }
        },
        margin: plot_margin,
        height: plot_height,
        barmode: 'overlay'
    }, {
        responsive: true
    });
}

async function updatePnlPlot(user) {
    const data = await fetchPnlHistory(user);
    Plotly.react('pnlPlot', [{
        x: data.times,
        y: data.pnls,
        mode: 'lines',
        name: `PnL for ${data.user}`,
        line: { color: '#9467bd', shape: 'hv' }
    }], {
        xaxis: {
            title: 'Time',
            titlefont: {
                family: 'Arial, sans-serif',
                size: 18,
                color: 'black',
                weight: 'bold'
            },
            tickfont: {
                family: 'Arial, sans-serif',
                size: 14,
                color: 'black',
                weight: 'bold'
            },
            tickangle: 0
        },
        yaxis: {
            title: 'PnL',
            titlefont: {
                family: 'Arial, sans-serif',
                size: 18,
                color: 'black',
                weight: 'bold'
            },
            tickfont: {
                family: 'Arial, sans-serif',
                size: 14,
                color: 'black',
                weight: 'bold'
            }
        },
        margin: plot_margin,
        height: plot_height,
        barmode: 'overlay'
    }, {
        responsive: true
    });
}

async function updatePositionsPlot(user) {
    const data = await fetchPositions(user);
    Plotly.react('positionsPlot', [{
        x: data.times,
        y: data.positions,
        mode: 'lines',
        name: `Positions for ${data.user}`,
        line: { color: '#ff7f0e', shape: 'hv' }
    }], {
        xaxis: {
            title: 'Time',
            titlefont: {
                family: 'Arial, sans-serif',
                size: 18,
                color: 'black',
                weight: 'bold'
            },
            tickfont: {
                family: 'Arial, sans-serif',
                size: 14,
                color: 'black',
                weight: 'bold'
            },
            tickangle: 0
        },
        yaxis: {
            title: 'Position',
            titlefont: {
                family: 'Arial, sans-serif',
                size: 18,
                color: 'black',
                weight: 'bold'
            },
            tickfont: {
                family: 'Arial, sans-serif',
                size: 14,
                color: 'black',
                weight: 'bold'
            }
        },
        margin: plot_margin,
        height: plot_height,
        barmode: 'overlay'
    }, {
        responsive: true
    });
}

async function fetchUsers() {
    const response = await fetch('/users');
    const data = await response.json();
    return data;
}

async function populateUserDropdown() {
    const users = await fetchUsers();
    const orderUserSelect = document.getElementById('user');
    const selectedOrderUser = orderUserSelect.value || 'basic-market-maker';
    orderUserSelect.innerHTML = '';
    users.forEach(user => {
        const option = document.createElement('option');
        option.value = user;
        option.text = user;
        orderUserSelect.appendChild(option);
    });
    orderUserSelect.value = selectedOrderUser;
    $('#user').trigger('change');
}

populateUserDropdown();

async function initializeDefaultUser() {
    const defaultUser = 'basic-market-maker';
    document.getElementById('user').value = defaultUser;
    $('#user').trigger('change');
    await updatePnlPlot(defaultUser);
    await updatePositionsPlot(defaultUser);
}

setInterval(updatePlot, 100);
setInterval(updateOrderBook, 100);
setInterval(async () => {
    const user = document.getElementById('user').value;
    if (user) {
        await updatePnlPlot(user);
        await updatePositionsPlot(user);
    }
}, 100);

initializeDefaultUser();
