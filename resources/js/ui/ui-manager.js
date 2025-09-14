class UIManager {
    constructor(sceneManager, pluginManager, pixooClient) {
        this.sceneManager = sceneManager;
        this.pluginManager = pluginManager;
        this.pixooClient = pixooClient;
        this.currentScene = null;
        this.canvas = null;
        this.ctx = null;
        this.previewInterval = null;
        this.deviceScanner = new DeviceScanner();

        this.initializeUI();
        this.bindEvents();
    }

    initializeUI() {
        this.canvas = document.getElementById('pixoo-canvas');
        this.ctx = this.canvas.getContext('2d');
        this.ctx.imageSmoothingEnabled = false;

        // Set up overlay canvas for interaction
        this.overlayCanvas = document.getElementById('pixoo-overlay');
        this.overlayCtx = this.overlayCanvas.getContext('2d');
        this.overlayCtx.imageSmoothingEnabled = false;

        // Drag and drop state
        this.dragState = {
            isDragging: false,
            widget: null,
            startX: 0,
            startY: 0,
            offsetX: 0,
            offsetY: 0
        };
        this.selectedWidget = null;
        this.hoveredWidget = null;

        // Set up drag and drop event listeners
        this.initializeDragAndDrop();

        // Set up scene manager event target
        this.sceneManager.setEventTarget(document);

        // Listen for scene changes
        document.addEventListener('sceneChanged', (e) => {
            this.onSceneChanged(e.detail);
        });

        // Initialize widget types display after a short delay to ensure plugins are loaded
        setTimeout(() => {
            this.updateWidgetTypesDisplay();
        }, 100);

        // Start preview update loop
        this.startPreviewLoop();
    }

    bindEvents() {
        // Connection
        document.getElementById('connect-btn').addEventListener('click', () => {
            this.handleConnect();
        });

        // Device scanning
        document.getElementById('scan-devices-btn').addEventListener('click', () => {
            this.scanForDevices();
        });

        // Brightness control
        const brightnessSlider = document.getElementById('brightness');
        const brightnessValue = document.getElementById('brightness-value');

        brightnessSlider.addEventListener('input', (e) => {
            const value = e.target.value;
            brightnessValue.textContent = value;
            this.setBrightness(parseInt(value));
        });

        // Scene management
        document.getElementById('add-scene-btn').addEventListener('click', () => {
            this.showAddSceneModal();
        });

        document.getElementById('create-scene-btn').addEventListener('click', () => {
            this.createScene();
        });

        document.getElementById('cancel-scene-btn').addEventListener('click', () => {
            this.hideAddSceneModal();
        });

        // Scene actions
        document.getElementById('play-scene-btn').addEventListener('click', () => {
            this.playScene();
        });

        document.getElementById('stop-scene-btn').addEventListener('click', () => {
            this.stopScene();
        });

        document.getElementById('delete-scene-btn').addEventListener('click', () => {
            this.deleteScene();
        });

        // Widget config modal
        document.getElementById('save-widget-config-btn').addEventListener('click', () => {
            this.saveWidgetConfig();
        });

        document.getElementById('cancel-widget-config-btn').addEventListener('click', () => {
            this.hideWidgetConfigModal();
        });

        // Modal overlay clicks
        document.getElementById('add-scene-modal').addEventListener('click', (e) => {
            if (e.target.classList.contains('modal')) {
                this.hideAddSceneModal();
            }
        });

        document.getElementById('widget-config-modal').addEventListener('click', (e) => {
            if (e.target.classList.contains('modal')) {
                this.hideWidgetConfigModal();
            }
        });
    }

    async handleConnect() {
        const ipAddress = document.getElementById('device-ip').value;
        const connectBtn = document.getElementById('connect-btn');
        const statusElement = document.getElementById('connection-status');

        if (!ipAddress) {
            alert('Please enter a device IP address');
            return;
        }

        connectBtn.disabled = true;
        connectBtn.textContent = 'Connecting...';

        try {
            this.pixooClient.ipAddress = ipAddress;
            await this.pixooClient.connect();

            statusElement.textContent = 'Connected';
            statusElement.className = 'connected';
            connectBtn.textContent = 'Disconnect';
            connectBtn.disabled = false;

        } catch (error) {
            console.error('Connection failed:', error);
            alert(`Failed to connect: ${error.message}`);

            statusElement.textContent = 'Disconnected';
            statusElement.className = 'disconnected';
            connectBtn.textContent = 'Connect';
            connectBtn.disabled = false;
        }
    }

    async setBrightness(level) {
        if (this.pixooClient.connected) {
            try {
                await this.pixooClient.setBrightness(level);
            } catch (error) {
                console.error('Failed to set brightness:', error);
            }
        }
    }

    showAddSceneModal() {
        document.getElementById('add-scene-modal').classList.add('open');
        document.getElementById('scene-name').focus();
    }

    hideAddSceneModal() {
        document.getElementById('add-scene-modal').classList.remove('open');
        document.getElementById('scene-name').value = '';
        document.getElementById('scene-description').value = '';
    }

    createScene() {
        const name = document.getElementById('scene-name').value.trim();
        const description = document.getElementById('scene-description').value.trim();

        if (!name) {
            alert('Please enter a scene name');
            return;
        }

        const scene = this.sceneManager.createScene(name, description);
        this.updateScenesDisplay();
        this.selectScene(scene.id);
        this.hideAddSceneModal();
    }

    updateScenesDisplay() {
        const sceneList = document.getElementById('scene-list');
        const scenes = this.sceneManager.getAllScenes();

        sceneList.innerHTML = '';

        scenes.forEach(scene => {
            const sceneElement = document.createElement('div');
            sceneElement.className = 'scene-item';
            sceneElement.dataset.sceneId = scene.id;

            sceneElement.innerHTML = `
                <h4>${scene.name}</h4>
                <p>${scene.description || 'No description'}</p>
            `;

            sceneElement.addEventListener('click', () => {
                this.selectScene(scene.id);
            });

            sceneList.appendChild(sceneElement);
        });

        // Update active scene highlight
        const activeSceneId = this.sceneManager.getActiveSceneId();
        if (activeSceneId) {
            const activeElement = sceneList.querySelector(`[data-scene-id="${activeSceneId}"]`);
            if (activeElement) {
                activeElement.classList.add('active');
            }
        }
    }

    selectScene(sceneId) {
        this.sceneManager.setActiveScene(sceneId);
        this.updateScenesDisplay();
        this.updateSceneEditor();
    }

    playScene() {
        if (this.currentScene) {
            this.currentScene.start();
            this.updateSceneControls();
        }
    }

    stopScene() {
        if (this.currentScene) {
            this.currentScene.stop();
            this.updateSceneControls();
        }
    }

    deleteScene() {
        if (!this.currentScene) return;

        if (confirm(`Are you sure you want to delete the scene "${this.currentScene.name}"?`)) {
            this.sceneManager.deleteScene(this.currentScene.id);
            this.updateScenesDisplay();
            this.updateSceneEditor();
        }
    }

    onSceneChanged(detail) {
        this.currentScene = detail.scene;
        this.updateSceneEditor();
    }

    updateSceneEditor() {
        const scene = this.sceneManager.getActiveScene();
        const sceneNameElement = document.getElementById('current-scene-name');

        if (scene) {
            sceneNameElement.textContent = scene.name;
            this.currentScene = scene;
        } else {
            sceneNameElement.textContent = 'No Scene Selected';
            this.currentScene = null;
        }

        this.updateSceneControls();
        this.updateSceneWidgetsDisplay();

        // Ensure widget types are displayed when scene changes
        this.updateWidgetTypesDisplay();

        // Update the overlay when scene changes
        this.updateOverlay();
    }

    updateSceneControls() {
        const playBtn = document.getElementById('play-scene-btn');
        const stopBtn = document.getElementById('stop-scene-btn');
        const deleteBtn = document.getElementById('delete-scene-btn');

        const hasScene = Boolean(this.currentScene);
        const isActive = hasScene && this.currentScene.isActive;

        playBtn.disabled = !hasScene || isActive;
        stopBtn.disabled = !hasScene || !isActive;
        deleteBtn.disabled = !hasScene;
    }

    updateSceneWidgetsDisplay() {
        const widgetsContainer = document.getElementById('scene-widgets');

        if (!this.currentScene) {
            widgetsContainer.innerHTML = '<div class="no-widgets">No scene selected</div>';
            return;
        }

        const widgets = this.currentScene.getAllWidgets();

        if (widgets.length === 0) {
            widgetsContainer.innerHTML = '<div class="no-widgets">No widgets in this scene</div>';
            return;
        }

        widgetsContainer.innerHTML = '';

        widgets.forEach(widget => {
            const widgetElement = document.createElement('div');
            widgetElement.className = 'widget-item';

            widgetElement.innerHTML = `
                <div class="widget-item-info">
                    <h5>${widget.constructor.NAME || widget.constructor.TYPE}</h5>
                    <p>ID: ${widget.id} | Enabled: ${widget.isEnabled() ? 'Yes' : 'No'}</p>
                </div>
                <div class="widget-item-actions">
                    <button class="secondary" onclick="uiManager.configureWidget('${widget.id}')">Config</button>
                    <button class="secondary" onclick="uiManager.toggleWidget('${widget.id}')">${widget.isEnabled() ? 'Disable' : 'Enable'}</button>
                    <button class="danger" onclick="uiManager.removeWidget('${widget.id}')">Remove</button>
                </div>
            `;

            widgetsContainer.appendChild(widgetElement);
        });
    }

    updateWidgetTypesDisplay() {
        const widgetTypesContainer = document.getElementById('widget-types');
        const widgetMetadata = this.pluginManager.getWidgetTypesMetadata();

        console.log('Updating widget types display, found:', Object.keys(widgetMetadata).length, 'widget types');

        widgetTypesContainer.innerHTML = '';

        if (Object.keys(widgetMetadata).length === 0) {
            widgetTypesContainer.innerHTML = '<div style="color: #999; text-align: center; padding: 1rem;">No widgets available. Loading...</div>';
            return;
        }

        Object.entries(widgetMetadata).forEach(([type, metadata]) => {
            const widgetTypeElement = document.createElement('div');
            widgetTypeElement.className = 'widget-type';
            widgetTypeElement.dataset.widgetType = type;

            widgetTypeElement.innerHTML = `
                <div class="icon">${metadata.icon}</div>
                <div class="name">${metadata.name}</div>
            `;

            // Add drag and drop functionality
            widgetTypeElement.draggable = true;
            widgetTypeElement.addEventListener('dragstart', (e) => {
                e.dataTransfer.setData('text/plain', type);
                e.dataTransfer.effectAllowed = 'copy';
            });

            widgetTypeElement.addEventListener('click', () => {
                this.addWidget(type);
            });

            widgetTypesContainer.appendChild(widgetTypeElement);
        });
    }

    addWidget(type) {
        if (!this.currentScene) {
            alert('Please select a scene first');
            return;
        }

        try {
            const WidgetClass = this.pluginManager.getWidgetType(type);
            if (!WidgetClass) {
                throw new Error(`Widget type ${type} not found`);
            }

            const widget = this.currentScene.addWidget(WidgetClass, {});
            this.updateSceneWidgetsDisplay();

            console.log(`Added widget ${type} to scene ${this.currentScene.name}`);

        } catch (error) {
            console.error('Failed to add widget:', error);
            alert(`Failed to add widget: ${error.message}`);
        }
    }

    configureWidget(widgetId) {
        if (!this.currentScene) return;

        const widget = this.currentScene.getWidget(widgetId);
        if (!widget) return;

        this.showWidgetConfigModal(widget);
    }

    toggleWidget(widgetId) {
        if (!this.currentScene) return;

        const widget = this.currentScene.getWidget(widgetId);
        if (!widget) return;

        widget.setEnabled(!widget.isEnabled());
        this.updateSceneWidgetsDisplay();
    }

    removeWidget(widgetId) {
        if (!this.currentScene) return;

        if (confirm('Are you sure you want to remove this widget?')) {
            this.currentScene.removeWidget(widgetId);
            this.updateSceneWidgetsDisplay();
        }
    }

    showWidgetConfigModal(widget) {
        const modal = document.getElementById('widget-config-modal');
        const form = document.getElementById('widget-config-form');

        // Create basic config form
        form.innerHTML = `
            <div class="form-group">
                <label for="widget-x">X Position:</label>
                <input type="number" id="widget-x" min="0" max="63" value="${widget.x}">
            </div>
            <div class="form-group">
                <label for="widget-y">Y Position:</label>
                <input type="number" id="widget-y" min="0" max="63" value="${widget.y}">
            </div>
            <div class="form-group">
                <label for="widget-enabled">Enabled:</label>
                <input type="checkbox" id="widget-enabled" ${widget.isEnabled() ? 'checked' : ''}>
            </div>
            <div class="form-group">
                <label for="widget-update-interval">Update Interval (ms):</label>
                <input type="number" id="widget-update-interval" min="100" value="${widget.updateInterval}">
            </div>
        `;

        modal.dataset.widgetId = widget.id;
        modal.classList.add('open');
    }

    hideWidgetConfigModal() {
        document.getElementById('widget-config-modal').classList.remove('open');
    }

    saveWidgetConfig() {
        const modal = document.getElementById('widget-config-modal');
        const widgetId = modal.dataset.widgetId;

        if (!this.currentScene || !widgetId) return;

        const widget = this.currentScene.getWidget(widgetId);
        if (!widget) return;

        const config = {
            x: parseInt(document.getElementById('widget-x').value),
            y: parseInt(document.getElementById('widget-y').value),
            enabled: document.getElementById('widget-enabled').checked,
            updateInterval: parseInt(document.getElementById('widget-update-interval').value)
        };

        widget.updateConfig(config);
        this.updateSceneWidgetsDisplay();
        this.hideWidgetConfigModal();
    }

    startPreviewLoop() {
        this.previewInterval = setInterval(() => {
            this.updatePreview();
        }, 100);
    }

    async updatePreview() {
        if (!this.pixooClient || !this.ctx) return;

        // Render the current scene to the buffer for preview
        if (this.currentScene) {
            await this.currentScene.renderPreview();
        }

        // Clear canvas
        this.ctx.fillStyle = '#000000';
        this.ctx.fillRect(0, 0, 320, 320);

        // Draw pixels from the Pixoo client buffer
        const buffer = this.pixooClient.buffer;
        if (buffer) {
            for (let y = 0; y < 64; y++) {
                for (let x = 0; x < 64; x++) {
                    const [r, g, b] = buffer[y][x];
                    if (r || g || b) { // Only draw non-black pixels
                        this.ctx.fillStyle = `rgb(${r}, ${g}, ${b})`;
                        this.ctx.fillRect(x * 5, y * 5, 5, 5);
                    }
                }
            }
        }
    }

    async scanForDevices() {
        const scanBtn = document.getElementById('scan-devices-btn');
        const discoveredDevicesSection = document.getElementById('discovered-devices');
        const deviceList = document.getElementById('device-list');

        // Show scanning state
        scanBtn.disabled = true;
        scanBtn.textContent = '🔄 Scanning...';

        discoveredDevicesSection.style.display = 'block';
        deviceList.innerHTML = '<div class="scanning-indicator"><span class="scanning-spinner">🔄</span>Scanning local network for Pixoo devices...</div>';

        try {
            // Scan for devices
            const devices = await this.deviceScanner.scanCommonRanges();

            // Update UI with results
            this.displayDiscoveredDevices(devices);

        } catch (error) {
            console.error('Device scan failed:', error);
            deviceList.innerHTML = '<div style="color: #f87171; text-align: center; padding: 1rem;">Scan failed. Please check your network connection.</div>';

        } finally {
            // Reset scan button
            scanBtn.disabled = false;
            scanBtn.textContent = '🔍 Scan';
        }
    }

    displayDiscoveredDevices(devices) {
        const deviceList = document.getElementById('device-list');
        const discoveredDevicesSection = document.getElementById('discovered-devices');

        if (devices.length === 0) {
            deviceList.innerHTML = '<div style="color: #999; text-align: center; padding: 1rem;">No Pixoo devices found on the network.</div>';
            return;
        }

        discoveredDevicesSection.style.display = 'block';
        deviceList.innerHTML = '';

        devices.forEach(device => {
            const deviceElement = document.createElement('div');
            deviceElement.className = 'device-item';
            deviceElement.dataset.deviceIp = device.ip;

            deviceElement.innerHTML = `
                <div class="device-item-header">
                    <span class="device-name">${device.name}</span>
                    <span class="device-ip">${device.ip}:${device.port || 80}</span>
                </div>
                <div class="device-details">
                    Model: ${device.model} | Size: ${device.size}x${device.size} | Port: ${device.port || 80}
                </div>
            `;

            deviceElement.addEventListener('click', () => {
                this.selectDevice(device);
            });

            deviceList.appendChild(deviceElement);
        });
    }

    selectDevice(device) {
        // Update IP input field
        document.getElementById('device-ip').value = device.ip;

        // Store the discovered port and path info in the pixoo client
        if (device.port && device.path) {
            this.pixooClient.port = device.port;
            this.pixooClient.path = device.path;
            console.log(`Pre-configured connection to use port ${device.port} and path ${device.path}`);
        }

        // Update visual selection
        const deviceItems = document.querySelectorAll('.device-item');
        deviceItems.forEach(item => {
            if (item.dataset.deviceIp === device.ip) {
                item.style.background = '#1a4a4a';
                item.style.borderColor = '#00d4aa';
            } else {
                item.style.background = '#3a3a3a';
                item.style.borderColor = '#555';
            }
        });

        console.log(`Selected Pixoo device: ${device.name} at ${device.ip}:${device.port}${device.path}`);

        // Optionally auto-connect to the selected device
        // this.handleConnect();
    }

    initializeDragAndDrop() {
        // Mouse events
        this.overlayCanvas.addEventListener('mousedown', (e) => this.handleMouseDown(e));
        this.overlayCanvas.addEventListener('mousemove', (e) => this.handleMouseMove(e));
        this.overlayCanvas.addEventListener('mouseup', (e) => this.handleMouseUp(e));
        this.overlayCanvas.addEventListener('mouseleave', (e) => this.handleMouseLeave(e));

        // Touch events for mobile support
        this.overlayCanvas.addEventListener('touchstart', (e) => this.handleTouchStart(e));
        this.overlayCanvas.addEventListener('touchmove', (e) => this.handleTouchMove(e));
        this.overlayCanvas.addEventListener('touchend', (e) => this.handleTouchEnd(e));

        // Right-click for context menu
        this.overlayCanvas.addEventListener('contextmenu', (e) => this.handleContextMenu(e));

        // Drag and drop from widget library
        this.overlayCanvas.addEventListener('dragover', (e) => this.handleDragOver(e));
        this.overlayCanvas.addEventListener('drop', (e) => this.handleDrop(e));
    }

    getCanvasCoordinates(event) {
        const rect = this.overlayCanvas.getBoundingClientRect();
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;

        // Convert to grid coordinates (each pixel is 5x5 canvas pixels)
        const gridX = Math.floor(x / 5);
        const gridY = Math.floor(y / 5);

        return { canvasX: x, canvasY: y, gridX, gridY };
    }

    getWidgetAtPosition(gridX, gridY) {
        if (!this.currentScene) return null;

        const widgets = this.currentScene.getAllWidgets();

        // Check widgets in reverse order (top widget first)
        for (let i = widgets.length - 1; i >= 0; i--) {
            const widget = widgets[i];
            if (!widget.isEnabled()) continue;

            const withinX = gridX >= widget.x && gridX < widget.x + widget.width;
            const withinY = gridY >= widget.y && gridY < widget.y + widget.height;

            if (withinX && withinY) {
                return widget;
            }
        }

        return null;
    }

    handleMouseDown(event) {
        event.preventDefault();
        const { gridX, gridY } = this.getCanvasCoordinates(event);
        const widget = this.getWidgetAtPosition(gridX, gridY);

        if (widget) {
            this.selectedWidget = widget;
            this.dragState = {
                isDragging: true,
                widget: widget,
                startX: gridX,
                startY: gridY,
                offsetX: gridX - widget.x,
                offsetY: gridY - widget.y
            };

            document.body.style.userSelect = 'none';
            this.overlayCanvas.parentElement.classList.add('dragging');

        } else {
            // Clicked on empty space - deselect
            this.selectedWidget = null;
        }

        this.updateOverlay();
    }

    handleMouseMove(event) {
        const { gridX, gridY } = this.getCanvasCoordinates(event);

        if (this.dragState.isDragging && this.dragState.widget) {
            // Update widget position during drag
            const newX = Math.max(0, Math.min(63, gridX - this.dragState.offsetX));
            const newY = Math.max(0, Math.min(63, gridY - this.dragState.offsetY));

            this.dragState.widget.updateConfig({
                x: newX,
                y: newY
            });

            this.updateOverlay();
        } else {
            // Handle hover
            const widget = this.getWidgetAtPosition(gridX, gridY);
            if (widget !== this.hoveredWidget) {
                this.hoveredWidget = widget;
                this.updateOverlay();
            }
        }
    }

    handleMouseUp(event) {
        if (this.dragState.isDragging) {
            // Drag ended
            this.dragState.isDragging = false;
            document.body.style.userSelect = '';
            this.overlayCanvas.parentElement.classList.remove('dragging');

            // Update widget display in sidebar
            this.updateSceneWidgetsDisplay();
        }
    }

    handleMouseLeave(event) {
        this.hoveredWidget = null;
        this.updateOverlay();
    }

    handleTouchStart(event) {
        event.preventDefault();
        if (event.touches.length === 1) {
            const touch = event.touches[0];
            const mouseEvent = new MouseEvent('mousedown', {
                clientX: touch.clientX,
                clientY: touch.clientY
            });
            this.handleMouseDown(mouseEvent);
        }
    }

    handleTouchMove(event) {
        event.preventDefault();
        if (event.touches.length === 1) {
            const touch = event.touches[0];
            const mouseEvent = new MouseEvent('mousemove', {
                clientX: touch.clientX,
                clientY: touch.clientY
            });
            this.handleMouseMove(mouseEvent);
        }
    }

    handleTouchEnd(event) {
        event.preventDefault();
        const mouseEvent = new MouseEvent('mouseup', {});
        this.handleMouseUp(mouseEvent);
    }

    handleContextMenu(event) {
        event.preventDefault();
        const { gridX, gridY } = this.getCanvasCoordinates(event);
        const widget = this.getWidgetAtPosition(gridX, gridY);

        if (widget) {
            // Show context menu for widget
            this.showWidgetContextMenu(widget, event.clientX, event.clientY);
        }
    }

    showWidgetContextMenu(widget, x, y) {
        // Create a simple context menu
        const menu = document.createElement('div');
        menu.className = 'context-menu';
        menu.style.cssText = `
            position: fixed;
            top: ${y}px;
            left: ${x}px;
            background: #2d2d2d;
            border: 1px solid #444;
            border-radius: 4px;
            padding: 0.5rem 0;
            z-index: 10000;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        `;

        const menuItems = [
            { text: 'Configure', action: () => this.configureWidget(widget.id) },
            { text: widget.isEnabled() ? 'Disable' : 'Enable', action: () => this.toggleWidget(widget.id) },
            { text: 'Remove', action: () => this.removeWidget(widget.id) }
        ];

        menuItems.forEach(item => {
            const menuItem = document.createElement('div');
            menuItem.textContent = item.text;
            menuItem.style.cssText = `
                padding: 0.5rem 1rem;
                cursor: pointer;
                color: #fff;
                font-size: 0.875rem;
            `;
            menuItem.addEventListener('mouseenter', () => {
                menuItem.style.background = '#404040';
            });
            menuItem.addEventListener('mouseleave', () => {
                menuItem.style.background = 'transparent';
            });
            menuItem.addEventListener('click', () => {
                item.action();
                document.body.removeChild(menu);
            });
            menu.appendChild(menuItem);
        });

        // Remove menu when clicking elsewhere
        const removeMenu = () => {
            if (document.body.contains(menu)) {
                document.body.removeChild(menu);
            }
            document.removeEventListener('click', removeMenu);
        };

        setTimeout(() => {
            document.addEventListener('click', removeMenu);
        }, 100);

        document.body.appendChild(menu);
    }

    handleDragOver(event) {
        event.preventDefault();
        event.dataTransfer.dropEffect = 'copy';
    }

    handleDrop(event) {
        event.preventDefault();
        const widgetType = event.dataTransfer.getData('text/plain');

        if (widgetType && this.currentScene) {
            const { gridX, gridY } = this.getCanvasCoordinates(event);

            // Create widget at drop position
            try {
                const WidgetClass = this.pluginManager.getWidgetType(widgetType);
                if (!WidgetClass) {
                    throw new Error(`Widget type ${widgetType} not found`);
                }

                const widget = this.currentScene.addWidget(WidgetClass, {
                    x: Math.max(0, Math.min(63, gridX)),
                    y: Math.max(0, Math.min(63, gridY))
                });

                // Select the newly created widget
                this.selectedWidget = widget;

                this.updateSceneWidgetsDisplay();
                this.updateOverlay();

                console.log(`Added widget ${widgetType} at position (${gridX}, ${gridY})`);

            } catch (error) {
                console.error('Failed to add widget:', error);
                alert(`Failed to add widget: ${error.message}`);
            }
        }
    }

    updateOverlay() {
        // Clear overlay
        this.overlayCtx.clearRect(0, 0, 320, 320);

        if (!this.currentScene) return;

        const widgets = this.currentScene.getAllWidgets();

        widgets.forEach(widget => {
            if (!widget.isEnabled()) return;

            const x = widget.x * 5;
            const y = widget.y * 5;
            const width = widget.width * 5;
            const height = widget.height * 5;

            // Draw widget outline
            this.overlayCtx.strokeStyle = '#00d4aa';
            this.overlayCtx.lineWidth = 1;

            if (widget === this.selectedWidget) {
                // Selected widget
                this.overlayCtx.fillStyle = 'rgba(0, 212, 170, 0.2)';
                this.overlayCtx.fillRect(x, y, width, height);
                this.overlayCtx.strokeStyle = '#ffffff';
                this.overlayCtx.lineWidth = 2;
            } else if (widget === this.hoveredWidget) {
                // Hovered widget
                this.overlayCtx.fillStyle = 'rgba(0, 212, 170, 0.1)';
                this.overlayCtx.fillRect(x, y, width, height);
                this.overlayCtx.strokeStyle = '#00d4aa';
                this.overlayCtx.lineWidth = 1;
            }

            this.overlayCtx.strokeRect(x, y, width, height);

            // Draw widget label
            if (widget === this.selectedWidget || widget === this.hoveredWidget) {
                const label = widget.constructor.NAME || widget.constructor.TYPE || 'Widget';
                this.overlayCtx.fillStyle = '#000';
                this.overlayCtx.fillRect(x, y - 20, label.length * 6 + 8, 16);
                this.overlayCtx.fillStyle = '#fff';
                this.overlayCtx.font = '12px monospace';
                this.overlayCtx.fillText(label, x + 4, y - 8);
            }
        });
    }
}

window.UIManager = UIManager;