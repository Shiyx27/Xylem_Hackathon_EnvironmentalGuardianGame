let map;
let currentActivity = null;
let currentActivityId = null;
let markersLayer;
let alertsLayer;
let weatherAlerts = [];

// Initialize the game
function initMap() {
    map = L.map('map', {
        worldCopyJump: true,
        maxBounds: [[-90, -180], [90, 180]],
        maxBoundsViscosity: 1.0,
        minZoom: 2,
        maxZoom: 12
    }).setView([25, 0], 2);
    
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        noWrap: false,
        bounds: [[-85, -180], [85, 180]]
    }).addTo(map);
    
    markersLayer = L.layerGroup().addTo(map);
    alertsLayer = L.layerGroup().addTo(map);
    
    loadActivities();
    loadWeatherAlerts();
    
    // Update alerts every 5 minutes
    setInterval(loadWeatherAlerts, 300000);
    
    // Update scan time display
    updateScanTimeDisplay();
    setInterval(updateScanTimeDisplay, 30000);
}

// Load LIVE weather alerts and display in right sidebar
function loadWeatherAlerts() {
    fetch('/get_weather_alerts')
    .then(response => response.json())
    .then(data => {
        weatherAlerts = data.alerts || [];
        displayAlertsInSidebar(data);
        displayWeatherAlertsOnMap();
        updateTotalCitiesDisplay(data.coastal_cities_monitored);
    })
    .catch(error => {
        console.error('Error loading weather alerts:', error);
        showErrorInSidebar(error);
    });
}

// Display alerts in RIGHT SIDEBAR
function displayAlertsInSidebar(data) {
    const container = document.getElementById('emergency-alerts-container');
    const counter = document.getElementById('alert-counter');
    const scanTime = document.getElementById('last-scan-time');
    const apiSource = document.getElementById('api-source');
    
    // Update counter
    counter.textContent = data.total_alerts;
    
    // Update scan time
    scanTime.textContent = new Date(data.last_updated).toLocaleTimeString();
    
    // Update API source
    apiSource.textContent = data.api_status.primary_api;
    
    if (weatherAlerts.length === 0) {
        container.innerHTML = `
            <div class="text-center p-4">
                <div class="text-success">
                    <i class="h1">✅</i>
                    <h6 class="text-success">All Clear</h6>
                    <p class="mb-0">No severe weather emergencies detected</p>
                    <small class="text-muted">Monitoring ${data.coastal_cities_monitored} cities globally</small>
                </div>
            </div>
        `;
        return;
    }
    
    let alertsHtml = '';
    
    weatherAlerts.forEach((alert, index) => {
        const severityClass = getSeverityBootstrapClass(alert.severity);
        const emergencyIcon = getEmergencyIcon(alert.alert_type);
        
        alertsHtml += `
            <div class="alert-item border-bottom ${index === 0 ? 'border-top' : ''} p-3">
                <div class="d-flex justify-content-between align-items-start mb-2">
                    <div>
                        <h6 class="mb-1 text-${severityClass}">
                            ${emergencyIcon} ${alert.city}
                        </h6>
                        <span class="badge bg-${severityClass}">${alert.emergency_level}</span>
                    </div>
                    <button class="btn btn-outline-${severityClass} btn-sm" onclick="focusOnAlert(${alert.lat}, ${alert.lng})">
                        🎯
                    </button>
                </div>
                
                <div class="alert-details">
                    <p class="small mb-2"><strong>${alert.alert_type}</strong></p>
                    <div class="row text-center mb-2">
                        <div class="col-4">
                            <div class="bg-light rounded p-1">
                                <div class="fw-bold text-${severityClass}">${alert.wind_speed}</div>
                                <small>Wind km/h</small>
                            </div>
                        </div>
                        <div class="col-4">
                            <div class="bg-light rounded p-1">
                                <div class="fw-bold text-primary">${alert.precipitation}</div>
                                <small>Rain mm</small>
                            </div>
                        </div>
                        <div class="col-4">
                            <div class="bg-light rounded p-1">
                                <div class="fw-bold text-warning">${alert.temperature}</div>
                                <small>Temp °C</small>
                            </div>
                        </div>
                    </div>
                    
                    <div class="mb-2">
                        <small class="text-muted">
                            <strong>👥 Population:</strong> ${alert.population}<br>
                            <strong>🌍 Country:</strong> ${alert.country}<br>
                            <strong>📍 Coordinates:</strong> ${alert.coordinates}
                        </small>
                    </div>
                    
                    <div class="mb-2">
                        <small class="text-info">
                            <strong>🕒 Time:</strong> ${alert.api_time}<br>
                            <strong>📅 Date:</strong> ${alert.api_date}<br>
                            <strong>📡 Source:</strong> ${alert.source}
                        </small>
                    </div>
                    
                    <div class="weather-details bg-light rounded p-2 mb-2">
                        <small>
                            <strong>🌤️ Weather:</strong> ${alert.weather_description}<br>
                            <strong>💨 Max Wind:</strong> ${alert.max_wind} km/h<br>
                            <strong>🌡️ Temperature Range:</strong> ${alert.min_temp}°C to ${alert.max_temp}°C<br>
                            <strong>🌧️ Daily Rain:</strong> ${alert.daily_precip} mm
                        </small>
                    </div>
                    
                    <p class="small mb-0">${alert.description}</p>
                </div>
            </div>
        `;
    });
    
    container.innerHTML = alertsHtml;
    
    // Show notification for critical alerts
    const criticalAlerts = weatherAlerts.filter(a => a.severity === 'critical');
    if (criticalAlerts.length > 0) {
        showCriticalAlertNotification(criticalAlerts.length);
    }
}

function displayWeatherAlertsOnMap() {
    alertsLayer.clearLayers();
    
    weatherAlerts.forEach(alert => {
        let alertIcon = L.divIcon({
            html: `<div class="live-emergency-marker ${alert.severity} emergency-pulse" title="${alert.title}">
                     <div class="alert-icon">${getEmergencyIcon(alert.alert_type)}</div>
                     <div class="alert-badge">${alert.severity.charAt(0).toUpperCase()}</div>
                   </div>`,
            className: 'live-emergency-icon',
            iconSize: [50, 50],
            iconAnchor: [25, 25]
        });
        
        let marker = L.marker([alert.lat, alert.lng], {
            icon: alertIcon,
            title: alert.title,
            zIndexOffset: 2000
        });
        
        marker.bindPopup(`
            <div class="emergency-popup">
                <h5 class="text-${getSeverityBootstrapClass(alert.severity)} mb-2">
                    ${getEmergencyIcon(alert.alert_type)} ${alert.alert_type}
                </h5>
                <div class="alert alert-${getSeverityBootstrapClass(alert.severity)} p-2 mb-2">
                    <strong>🚨 ${alert.emergency_level}</strong>
                </div>
                <p><strong>📍 Location:</strong> ${alert.city}, ${alert.country}</p>
                <p><strong>👥 Population at Risk:</strong> ${alert.population}</p>
                <p><strong>🕒 Live Time:</strong> ${alert.api_time}</p>
                <p><strong>📅 Date:</strong> ${alert.api_date}</p>
                
                <div class="row text-center mb-2">
                    <div class="col-4">
                        <div class="p-2 bg-danger bg-opacity-10 rounded">
                            <div class="h6 text-danger mb-0">${alert.wind_speed}</div>
                            <small>Wind km/h</small>
                        </div>
                    </div>
                    <div class="col-4">
                        <div class="p-2 bg-primary bg-opacity-10 rounded">
                            <div class="h6 text-primary mb-0">${alert.precipitation}</div>
                            <small>Rain mm</small>
                        </div>
                    </div>
                    <div class="col-4">
                        <div class="p-2 bg-warning bg-opacity-10 rounded">
                            <div class="h6 text-warning mb-0">${alert.temperature}</div>
                            <small>Temp °C</small>
                        </div>
                    </div>
                </div>
                
                <p><strong>🌤️ Weather:</strong> ${alert.weather_description}</p>
                <p><strong>📡 Live Source:</strong> ${alert.source}</p>
                
                <div class="text-center">
                    <button class="btn btn-danger btn-sm" onclick="focusOnAlert(${alert.lat}, ${alert.lng})">
                        🎯 Center View
                    </button>
                </div>
            </div>
        `);
        
        alertsLayer.addLayer(marker);
    });
}

function getEmergencyIcon(alertType) {
    if (alertType.includes('HURRICANE') || alertType.includes('CYCLONE')) return '🌀';
    if (alertType.includes('THUNDERSTORM') || alertType.includes('STORM')) return '⛈️';
    if (alertType.includes('HEAT')) return '🔥';
    if (alertType.includes('FLOOD')) return '🌊';
    if (alertType.includes('BLIZZARD') || alertType.includes('SNOW')) return '❄️';
    return '⚠️';
}

function getSeverityBootstrapClass(severity) {
    switch(severity) {
        case 'critical': return 'danger';
        case 'high': return 'warning';
        case 'medium': return 'info';
        default: return 'secondary';
    }
}

function focusOnAlert(lat, lng) {
    map.setView([lat, lng], 10);
    showFeedbackMessage('🎯 Focusing on emergency location with live data', 'info');
}

function showErrorInSidebar(error) {
    const container = document.getElementById('emergency-alerts-container');
    container.innerHTML = `
        <div class="text-center p-4">
            <div class="text-danger">
                <i class="h1">❌</i>
                <h6 class="text-danger">Connection Error</h6>
                <p class="mb-0">Unable to load live weather data</p>
                <small class="text-muted">Retrying in 5 minutes...</small>
            </div>
        </div>
    `;
}

function updateTotalCitiesDisplay(totalCities) {
    const element = document.getElementById('total-cities');
    if (element) {
        element.textContent = totalCities;
    }
}

function updateScanTimeDisplay() {
    const element = document.getElementById('last-scan-time');
    if (element && element.textContent === 'Initializing...') {
        element.textContent = 'Scanning...';
    }
}

function showCriticalAlertNotification(criticalCount) {
    if (window.lastCriticalNotification && 
        Date.now() - window.lastCriticalNotification < 300000) {
        return;
    }
    
    showFeedbackMessage(
        `🚨 CRITICAL EMERGENCY: ${criticalCount} severe weather emergencies detected with live data from global coastal cities!`,
        'danger'
    );
    
    window.lastCriticalNotification = Date.now();
}

// Load environmental activities
function loadActivities() {
    fetch('/get_activities')
    .then(response => response.json())
    .then(activities => {
        markersLayer.clearLayers();
        
        activities.forEach(activity => {
            addActivityMarker(activity);
        });
        
        updateActivityInfo(activities);
    })
    .catch(error => console.error('Error loading activities:', error));
}

function addActivityMarker(activity) {
    let iconColor = getMarkerColor(activity.risk);
    let riskEmoji = getRiskEmoji(activity.risk);
    let isApiActivity = activity.category === 'api';
    let isCompleted = activity.completed;
    
    let markerClass = isApiActivity ? 'api-marker' : 'env-marker';
    let borderColor = isApiActivity ? '#00ff00' : '#ffffff';
    let borderWidth = isApiActivity ? '4px' : '2px';
    
    let opacity = isCompleted && !isApiActivity ? '0.6' : '1';
    let completedStyle = isCompleted ? 'filter: grayscale(30%);' : '';
    
    let customIcon = L.divIcon({
        html: `<div class="${markerClass} ${activity.risk} ${isCompleted ? 'completed' : ''}" style="
            background-color: ${iconColor};
            width: ${isApiActivity ? '36px' : '30px'};
            height: ${isApiActivity ? '36px' : '30px'};
            border-radius: 50%;
            border: ${borderWidth} solid ${borderColor};
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: ${isApiActivity ? '18px' : '14px'};
            box-shadow: 0 4px 15px rgba(0,0,0,0.6);
            color: white;
            font-weight: bold;
            opacity: ${opacity};
            ${completedStyle}
            ${isApiActivity && !isCompleted ? 'animation: api-pulse 2s infinite;' : ''}
        ">${riskEmoji}</div>`,
        className: `environmental-marker risk-${activity.risk} ${markerClass}`,
        iconSize: [isApiActivity ? 36 : 30, isApiActivity ? 36 : 30],
        iconAnchor: [isApiActivity ? 18 : 15, isApiActivity ? 18 : 15]
    });
    
    let marker = L.marker([activity.lat, activity.lng], {
        icon: customIcon,
        title: activity.title
    });
    
    let activityBadge = isApiActivity ? 
        '<span class="badge bg-success">LIVE EMERGENCY DATA</span>' : 
        '<span class="badge bg-primary">ENVIRONMENTAL</span>';
        
    let completedBadge = isCompleted ? 
        '<span class="badge bg-secondary">COMPLETED</span>' : '';
        
    let cityInfo = activity.city ? 
        `<p class="small"><strong>🏙️ Major City:</strong> ${activity.city}</p>` : '';
    
    marker.bindPopup(`
        <div class="marker-popup">
            <h6>${riskEmoji} ${activity.title}</h6>
            ${cityInfo}
            <p class="small text-muted">
                Risk Level: <span class="badge bg-${getBootstrapColor(activity.risk)}">${activity.risk.toUpperCase()}</span>
                ${activityBadge}
                ${completedBadge}
            </p>
            ${isCompleted && isApiActivity ? 
                '<p class="small text-info"><em>🔄 Live emergency monitoring continues</em></p>' : 
                ''}
            <button class="btn btn-primary btn-sm" onclick="showActivityModal('${activity.type}', '${activity.title}', '${activity.id}')">
                ${isCompleted ? '🔄 View Latest Emergency Data' : '🔍 Learn More & Take Action'}
            </button>
        </div>
    `);
    
    markersLayer.addLayer(marker);
}

function updateActivityInfo(activities) {
    const apiActivities = activities.filter(a => a.category === 'api');
    const envActivities = activities.filter(a => a.category === 'environmental');
    const completedEnv = envActivities.filter(a => a.completed).length;
    const remainingEnv = envActivities.length - completedEnv;
    
    let activityInfo = document.getElementById('activity-info-display');
    if (!activityInfo) {
        activityInfo = document.createElement('div');
        activityInfo.id = 'activity-info-display';
        
        const container = document.querySelector('#activity-info-display') || document.querySelector('.col-md-2');
        if (container) container.appendChild(activityInfo);
    }
    
    activityInfo.innerHTML = `
        <div class="row text-center">
            <div class="col-6">
                <div class="p-2 bg-success bg-opacity-10 rounded">
                    <div class="h5 text-success mb-0">${apiActivities.length}</div>
                    <small class="text-muted">🌐 Live Coastal</small>
                </div>
            </div>
            <div class="col-6">
                <div class="p-2 bg-primary bg-opacity-10 rounded">
                    <div class="h5 text-primary mb-0">${remainingEnv}</div>
                    <small class="text-muted">🌍 Environmental</small>
                </div>
            </div>
        </div>
        <small class="text-muted mt-2 d-block">
            🏙️ Monitoring ${apiActivities.length} major coastal cities<br>
            🌍 ${remainingEnv} environmental challenges remaining<br>
            📊 ${completedEnv} environmental challenges completed
        </small>
        ${remainingEnv === 0 ? '<div class="alert alert-success p-2 mt-2"><small>🎉 All environmental challenges completed!</small></div>' : ''}
    `;
}

function getMarkerColor(risk) {
    switch(risk) {
        case 'critical': return '#dc3545';
        case 'high': return '#fd7e14';
        case 'medium': return '#ffc107';
        default: return '#28a745';
    }
}

function getRiskEmoji(risk) {
    switch(risk) {
        case 'critical': return '🚨';
        case 'high': return '⚠️';
        case 'medium': return '⚡';
        default: return '📍';
    }
}

function getBootstrapColor(risk) {
    switch(risk) {
        case 'critical': return 'danger';
        case 'high': return 'warning';
        case 'medium': return 'info';
        default: return 'success';
    }
}

function showActivityModal(activityType, title, activityId) {
    currentActivity = activityType;
    currentActivityId = activityId;
    
    document.getElementById('modalTitle').textContent = title;
    
    fetch(`/get_fact/${activityType}`)
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            document.getElementById('factText').textContent = 'Environmental fact not available.';
            document.getElementById('impactText').textContent = 'Impact information not available.';
        } else {
            document.getElementById('factText').textContent = data.fact;
            
            let impactHtml = data.impact;
            
            if (data.solution) {
                impactHtml += `<br><br><strong>💡 Solutions:</strong> ${data.solution}`;
            }
            
            if (data.year) {
                impactHtml += `<br><small class="text-muted"><strong>📅 Timeline:</strong> ${data.year}</small>`;
            }
            
            if (data.real_time_alert) {
                impactHtml += `<br><div class="alert alert-danger mt-2"><strong>📡 ${data.real_time_alert}</strong></div>`;
            }
            
            if (data.api_enhanced) {
                impactHtml += `<br><span class="badge bg-danger">🚨 Enhanced with REAL Emergency Data</span>`;
            }
            
            if (data.live_source) {
                impactHtml += `<br><small class="text-info"><strong>📡 Live Source:</strong> ${data.live_source}</small>`;
            }
            
            if (data.live_time) {
                impactHtml += `<br><small class="text-info"><strong>🕒 Live Time:</strong> ${data.live_time}</small>`;
            }
            
            document.getElementById('impactText').innerHTML = impactHtml;
        }
        
        const modal = new bootstrap.Modal(document.getElementById('activityModal'));
        modal.show();
    })
    .catch(error => {
        console.error('Error fetching fact:', error);
        document.getElementById('factText').textContent = 'Error loading environmental data.';
    });
}

function makeDecision(decision) {
    if (!currentActivity || !currentActivityId) return;
    
    const buttonStop = document.querySelector('button[onclick="makeDecision(\'stop\')"]');
    const buttonContinue = document.querySelector('button[onclick="makeDecision(\'continue\')"]');
    
    buttonStop.innerHTML = '<span class="loading"></span> Processing...';
    buttonContinue.innerHTML = '<span class="loading"></span> Processing...';
    buttonStop.disabled = true;
    buttonContinue.disabled = true;
    
    fetch('/make_decision', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            activity_type: currentActivity,
            activity_id: currentActivityId,
            decision: decision
        })
    })
    .then(response => response.json())
    .then(data => {
        updateScore(data.score);
        updateSeaLevel(data.sea_level_impact);
        
        let enhancedMessage = data.message;
        if (data.points_earned) {
            enhancedMessage += ` (${data.points_earned > 0 ? '+' : ''}${data.points_earned} points)`;
        }
        
        if (data.is_persistent) {
            enhancedMessage += ' 🔄 Live emergency monitoring continues';
        }
        
        showFeedbackMessage(enhancedMessage, data.message_type);
        
        if (data.live_data) {
            setTimeout(() => {
                showFeedbackMessage(`${data.live_data}`, 'danger');
            }, 2000);
        }
        
        const modal = bootstrap.Modal.getInstance(document.getElementById('activityModal'));
        modal.hide();
        
        resetDecisionButtons();
        
        setTimeout(() => {
            loadActivities();
        }, 1000);
        
        if (data.remaining_activities === 0) {
            setTimeout(() => {
                showFeedbackMessage('🎉 All environmental challenges completed! Live coastal monitoring continues. Check your detailed analysis!', 'success');
                setTimeout(() => {
                    window.location.href = '/stats';
                }, 4000);
            }, 2000);
        }
    })
    .catch(error => {
        console.error('Error making decision:', error);
        showFeedbackMessage('Error processing your decision. Please try again.', 'danger');
        resetDecisionButtons();
    });
}

function resetDecisionButtons() {
    const buttonStop = document.querySelector('button[onclick="makeDecision(\'stop\')"]');
    const buttonContinue = document.querySelector('button[onclick="makeDecision(\'continue\')"]');
    
    buttonStop.innerHTML = '🛑 STOP This Activity';
    buttonContinue.innerHTML = '▶️ Continue Activity';
    buttonStop.disabled = false;
    buttonContinue.disabled = false;
}

function updateScore(score) {
    document.getElementById('current-score').textContent = score;
}

function updateSeaLevel(seaLevel) {
    const element = document.getElementById('sea-level');
    const clampedSeaLevel = Math.max(0, seaLevel);
    element.textContent = clampedSeaLevel + 'm';
    
    element.className = 'badge ' + (clampedSeaLevel === 0 ? 'bg-success' : clampedSeaLevel < 1 ? 'bg-info' : 'bg-danger');
}

function showFeedbackMessage(message, type) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show feedback-message`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alertDiv);
    
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 12000);
}

function resetGame() {
    if (confirm('Are you sure you want to reset your game progress? All environmental decisions and live monitoring data will be cleared.')) {
        fetch('/reset_game')
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                location.reload();
            }
        })
        .catch(error => {
            console.error('Error resetting game:', error);
            showFeedbackMessage('Error resetting game. Please try again.', 'danger');
        });
    }
}

// Initialize map when page loads
document.addEventListener('DOMContentLoaded', function() {
    initMap();
});
