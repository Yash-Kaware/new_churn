let fetchedData = [];

async function fetchData() {
    const response = await fetch('/api/data');
    const data = await response.json();
    fetchedData = data;
    updateVisualizations();
}

setInterval(fetchData, 1000);

function updateVisualizations() {
    if (fetchedData.length === 0) return;

    const df = fetchedData;

    const timeData = df.map(row => row.time_spent_on_website);
    Plotly.newPlot('time-distribution', [{
        x: timeData,
        type: 'histogram'
    }], { title: 'Time Spent on Website Distribution' });

    const pageViews = df.map(row => row.page_views_per_visit);
    Plotly.newPlot('pageviews', [{
        x: pageViews,
        type: 'histogram'
    }], { title: 'Page Views per Visit Distribution' });

    const referralCounts = {};
    df.forEach(row => {
        referralCounts[row.referral] = (referralCounts[row.referral] || 0) + 1;
    });
    Plotly.newPlot('referral', [{
        labels: Object.keys(referralCounts),
        values: Object.values(referralCounts),
        type: 'pie'
    }], { title: 'Referral Status' });

    // Correlation Heatmap
    const keys = Object.keys(df[0]).filter(k => typeof df[0][k] === 'number');
    const matrix = keys.map(k1 => keys.map(k2 => {
        const values1 = df.map(d => d[k1]);
        const values2 = df.map(d => d[k2]);
        const mean1 = values1.reduce((a, b) => a + b, 0) / values1.length;
        const mean2 = values2.reduce((a, b) => a + b, 0) / values2.length;
        const numerator = values1.map((v, i) => (v - mean1) * (values2[i] - mean2)).reduce((a, b) => a + b, 0);
        const denominator = Math.sqrt(values1.map(v => Math.pow(v - mean1, 2)).reduce((a, b) => a + b, 0)) *
            Math.sqrt(values2.map(v => Math.pow(v - mean2, 2)).reduce((a, b) => a + b, 0));
        return denominator === 0 ? 0 : numerator / denominator;
    }));
    Plotly.newPlot('heatmap', [{
        z: matrix,
        x: keys,
        y: keys,
        type: 'heatmap',
        colorscale: 'Viridis'
    }], { title: 'Correlation Heatmap' });

    // Stacked Barplot
    const group = {};
    df.forEach(row => {
        const category = row.gender;
        const status = row.referral;
        if (!group[category]) group[category] = {};
        group[category][status] = (group[category][status] || 0) + 1;
    });
    const categories = Object.keys(group);
    const statuses = Object.keys(Object.values(group)[0]);
    const traces = statuses.map(status => {
        return {
            x: categories,
            y: categories.map(cat => group[cat][status] || 0),
            name: status,
            type: 'bar'
        }
    });
    Plotly.newPlot('stacked-bar', traces, { title: 'Referral by Gender', barmode: 'stack' });

    // Boxplot
    Plotly.newPlot('boxplot', [{
        y: timeData,
        type: 'box'
    }], { title: 'Time Spent Boxplot' });

    // Decision Tree Text
    fetch('/api/tree')
        .then(res => res.json())
        .then(treeData => {
            document.getElementById('tree').innerText = treeData.tree || "Waiting for data...";
        });

    // Feature Importance
    fetch('/api/feature_importance')
        .then(res => res.json())
        .then(data => {
            if (!data.importance || Object.keys(data.importance).length === 0) {
                document.getElementById('feature-importance').innerText = "Waiting for data...";
                return;
            }
            const labels = Object.keys(data.importance);
            const values = Object.values(data.importance);
            Plotly.newPlot('feature-importance', [{
                x: labels,
                y: values,
                type: 'bar'
            }], { title: 'Feature Importance' });
        });
}
