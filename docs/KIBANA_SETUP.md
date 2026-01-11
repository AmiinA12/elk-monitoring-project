# Kibana Setup Guide - E-Commerce Log Analysis

This guide provides step-by-step instructions for setting up Kibana visualizations and dashboards for the E-commerce log monitoring platform.

## Prerequisites

- Elasticsearch must be running at http://localhost:9200
- Kibana must be running at http://localhost:5601
- Log data must be indexed in Elasticsearch (indices matching `logs-*`)

## Step 1: Create Index Pattern

### 1.1 Access Kibana
1. Open your browser and navigate to http://localhost:5601
2. Wait for Kibana to fully load

### 1.2 Create Index Pattern
1. Click on the **☰ Menu** (hamburger icon) in the top-left
2. Navigate to **Stack Management** → **Index Patterns**
3. Click **Create index pattern**
4. In the **Index pattern name** field, enter: `logs-*`
5. Click **Next step**
6. Select **@timestamp** as the Time field
7. Click **Create index pattern**

✅ **Success**: You should now see your index pattern with all available fields listed.

---

## Step 2: Explore Your Data

### 2.1 Access Discover
1. Click on **☰ Menu** → **Discover**
2. Ensure `logs-*` is selected in the index pattern dropdown
3. Adjust the time range (top-right) to see your data

### 2.2 Verify Data Fields
Confirm that the following fields are present:
- `@timestamp` - Log timestamp
- `level` - Log level (INFO, WARNING, ERROR, DEBUG)
- `service` - Service name (payment-service, inventory-service, etc.)
- `message` - Log message
- `action` - User action
- `user_id` - User identifier
- `response_time_ms` - Response time in milliseconds

---

## Step 3: Create Visualizations

### Visualization 1: Line Chart - Transactions per Hour (24h)

**Purpose**: Track log volume over time to identify peak hours and patterns.

1. Click **☰ Menu** → **Visualize Library** → **Create visualization**
2. Select **Lens** (recommended) or **Legacy: Line**
3. Configure the visualization:
   - **Index pattern**: `logs-*`
   - **X-axis**: Date Histogram on `@timestamp` with interval `1 hour`
   - **Y-axis**: Count
   - **Split series** (optional): By `level.keyword` to show different log levels
4. Set the time range to **Last 24 hours**
5. **Save** the visualization as: `E-commerce - Logs per Hour`

**Expected Result**: A line chart showing log volume trends over the past 24 hours.

---

### Visualization 2: Pie Chart - Distribution of Errors by Type

**Purpose**: Understand which types of errors are most common.

1. Click **☰ Menu** → **Visualize Library** → **Create visualization**
2. Select **Pie Chart**
3. Configure:
   - **Index pattern**: `logs-*`
   - **Slice by**: Terms aggregation on `level.keyword`
   - **Metrics**: Count
   - Add a filter: `level: ERROR` to show only errors
4. **Save** as: `E-commerce - Error Distribution`

**Expected Result**: A pie chart showing the breakdown of error types.

---

### Visualization 3: Bar Chart - Top 10 Services with Most Logs

**Purpose**: Identify which services generate the most logs (potential issues or high activity).

1. Click **☰ Menu** → **Visualize Library** → **Create visualization**
2. Select **Vertical Bar Chart**
3. Configure:
   - **Index pattern**: `logs-*`
   - **X-axis**: Terms aggregation on `service.keyword`, ordered by Count descending, size 10
   - **Y-axis**: Count
4. Optionally split by `level.keyword` to show log levels per service
5. **Save** as: `E-commerce - Top 10 Services`

**Expected Result**: A bar chart ranking the top 10 services by log count.

---

### Visualization 4 (Bonus): Metric - Average Response Time

**Purpose**: Display the average API response time for performance monitoring.

1. Click **☰ Menu** → **Visualize Library** → **Create visualization**
2. Select **Metric**
3. Configure:
   - **Index pattern**: `logs-*`
   - **Metric**: Average of `response_time_ms`
4. **Save** as: `E-commerce - Avg Response Time`

**Expected Result**: A large number displaying average response time in milliseconds.

---

### Visualization 5 (Bonus): Data Table - Recent Error Logs

**Purpose**: Show detailed error logs for quick troubleshooting.

1. Click **☰ Menu** → **Visualize Library** → **Create visualization**
2. Select **Data Table**
3. Configure:
   - **Index pattern**: `logs-*`
   - Add filter: `level: ERROR`
   - **Buckets**: Terms on `message.keyword`, size 20
   - **Metrics**: Count
4. **Save** as: `E-commerce - Recent Errors`

---

## Step 4: Create Dashboard

### 4.1 Create New Dashboard
1. Click **☰ Menu** → **Dashboard**
2. Click **Create dashboard**
3. Click **Add from library**

### 4.2 Add Visualizations
Select and add the following visualizations:
- ✅ E-commerce - Logs per Hour
- ✅ E-commerce - Error Distribution
- ✅ E-commerce - Top 10 Services
- ✅ E-commerce - Avg Response Time (optional)
- ✅ E-commerce - Recent Errors (optional)

### 4.3 Arrange Dashboard
1. Drag and resize visualizations to create a clean layout
2. Suggested layout:
   ```
   [ Avg Response Time ]  [ Error Distribution ]
   [    Logs per Hour (fullwidth)              ]
   [    Top 10 Services  ]  [ Recent Errors    ]
   ```

### 4.4 Configure Dashboard Settings
1. Click **Options** (gear icon)
2. Enable **Use margins between panels**
3. Set refresh interval: **Off** or **30 seconds** for auto-refresh

### 4.5 Save Dashboard
1. Click **Save** (top-right)
2. Title: `E-commerce Log Monitoring Dashboard`
3. Description: `Real-time monitoring of e-commerce platform logs with error tracking and performance metrics`
4. Tags: `ecommerce`, `monitoring`, `logs`
5. Click **Save**

---

## Step 5: Export Dashboard Configuration

### 5.1 Export for Backup
1. Go to **☰ Menu** → **Stack Management** → **Saved Objects**
2. Search for your dashboard: `E-commerce Log Monitoring Dashboard`
3. Select the checkbox next to it
4. Click **Export X objects**
5. Save the JSON file to: `docs/kibana-dashboard-export.json`

### 5.2 Import on Another Instance
To restore or deploy to another Kibana instance:
1. Go to **Stack Management** → **Saved Objects**
2. Click **Import**
3. Select the exported JSON file
4. Click **Import**

---

## Step 6: Set Up Filters and Time Controls

### 6.1 Add Global Filters
On your dashboard, you can add filters:
1. Click **Add filter**
2. Examples:
   - Field: `level`, Operator: `is`, Value: `ERROR`
   - Field: `service`, Operator: `is`, Value: `payment-service`

### 6.2 Configure Time Range
1. Click the time picker (top-right)
2. Common ranges:
   - **Last 15 minutes** - Real-time monitoring
   - **Last 24 hours** - Daily overview
   - **Last 7 days** - Weekly trends
3. Enable **Auto-refresh** for live monitoring

---

## Troubleshooting

### No Data Showing
- Verify Elasticsearch has data: `http://localhost:9200/logs-*/_count`
- Check the time range - expand it to include your data
- Verify index pattern matches your indices

### Field Not Found
- Go to **Stack Management** → **Index Patterns** → `logs-*`
- Click **Refresh field list** (circular arrow icon)

### Dashboard Looks Different
- Kibana versions may have different interfaces
- Core functionality remains the same across versions 7.x

---

## Next Steps

1. ✅ Create additional visualizations based on specific business needs
2. ✅ Set up Kibana Alerts for critical errors (Advanced feature)
3. ✅ Configure Watcher for automated notifications
4. ✅ Embed Kibana visualizations in your Flask webapp using iframe

---

## Embedded Dashboard in Web App

To embed the Kibana dashboard in your Flask web application:

### Option 1: IFrame Embedding
Add this to a new page template:
```html
<iframe 
    src="http://localhost:5601/app/dashboards#/view/YOUR_DASHBOARD_ID?embed=true&_g=(refreshInterval:(pause:!f,value:30000),time:(from:now-24h,to:now))" 
    height="800" 
    width="100%" 
    frameborder="0">
</iframe>
```

### Option 2: Direct Link
Add a navigation link in your Flask app:
```python
@app.route('/kibana')
def kibana_redirect():
    return redirect('http://localhost:5601/app/dashboards#/view/YOUR_DASHBOARD_ID')
```

---

**✅ Congratulations!** Your Kibana setup is complete. You now have a full monitoring dashboard for your E-commerce platform logs.
