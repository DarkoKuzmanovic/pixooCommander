class SceneManager {
    constructor(pixooClient) {
        this.pixooClient = pixooClient;
        this.scenes = new Map();
        this.activeScene = null;
        this.activeSceneId = null;
        this.sceneCounter = 0;
    }

    createScene(name, description = '') {
        const sceneId = `scene_${++this.sceneCounter}`;
        const scene = new Scene(sceneId, name, description, this.pixooClient);
        this.scenes.set(sceneId, scene);

        // If this is the first scene, make it active
        if (this.scenes.size === 1) {
            this.setActiveScene(sceneId);
        }

        return scene;
    }

    deleteScene(sceneId) {
        if (this.scenes.has(sceneId)) {
            const scene = this.scenes.get(sceneId);
            scene.stop();
            this.scenes.delete(sceneId);

            // If we deleted the active scene, switch to another one
            if (this.activeSceneId === sceneId) {
                const remainingScenes = Array.from(this.scenes.keys());
                if (remainingScenes.length > 0) {
                    this.setActiveScene(remainingScenes[0]);
                } else {
                    this.activeScene = null;
                    this.activeSceneId = null;
                }
            }
            return true;
        }
        return false;
    }

    setActiveScene(sceneId) {
        if (!this.scenes.has(sceneId)) {
            throw new Error(`Scene with ID ${sceneId} does not exist`);
        }

        // Stop the current active scene
        if (this.activeScene) {
            this.activeScene.stop();
        }

        // Set the new active scene
        this.activeScene = this.scenes.get(sceneId);
        this.activeSceneId = sceneId;

        // Start the new active scene
        this.activeScene.start();

        this.dispatchEvent(new CustomEvent('sceneChanged', {
            detail: { sceneId, scene: this.activeScene }
        }));
    }

    getActiveScene() {
        return this.activeScene;
    }

    getActiveSceneId() {
        return this.activeSceneId;
    }

    getAllScenes() {
        return Array.from(this.scenes.values());
    }

    getScene(sceneId) {
        return this.scenes.get(sceneId);
    }

    dispatchEvent(event) {
        if (this.eventTarget) {
            this.eventTarget.dispatchEvent(event);
        }
    }

    setEventTarget(target) {
        this.eventTarget = target;
    }
}

class Scene {
    constructor(id, name, description, pixooClient) {
        this.id = id;
        this.name = name;
        this.description = description;
        this.pixooClient = pixooClient;
        this.widgets = new Map();
        this.isActive = false;
        this.updateInterval = null;
        this.refreshRate = 1000; // 1 second by default
        this.widgetCounter = 0;
    }

    addWidget(widgetClass, config = {}) {
        const widgetId = `widget_${++this.widgetCounter}`;
        const widget = new widgetClass(widgetId, config, this.pixooClient);

        this.widgets.set(widgetId, widget);

        // If the scene is active, initialize the widget
        if (this.isActive) {
            widget.init();
        }

        return widget;
    }

    removeWidget(widgetId) {
        if (this.widgets.has(widgetId)) {
            const widget = this.widgets.get(widgetId);
            widget.destroy();
            this.widgets.delete(widgetId);
            return true;
        }
        return false;
    }

    getWidget(widgetId) {
        return this.widgets.get(widgetId);
    }

    getAllWidgets() {
        return Array.from(this.widgets.values());
    }

    start() {
        if (this.isActive) return;

        this.isActive = true;

        // Initialize all widgets
        for (const widget of this.widgets.values()) {
            try {
                widget.init();
            } catch (error) {
                console.error(`Failed to initialize widget ${widget.id}:`, error);
            }
        }

        // Start the render loop
        this.updateInterval = setInterval(() => {
            this.render();
        }, this.refreshRate);

        console.log(`Scene ${this.name} started`);
    }

    stop() {
        if (!this.isActive) return;

        this.isActive = false;

        // Stop the render loop
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
        }

        // Stop all widgets
        for (const widget of this.widgets.values()) {
            try {
                widget.destroy();
            } catch (error) {
                console.error(`Failed to stop widget ${widget.id}:`, error);
            }
        }

        console.log(`Scene ${this.name} stopped`);
    }

    async render() {
        if (!this.isActive) return;

        try {
            // Clear the screen
            await this.pixooClient.clear();

            // Render all widgets
            for (const widget of this.widgets.values()) {
                if (widget.isEnabled()) {
                    await widget.render();
                }
            }

            // Push the frame to the device only if connected
            if (this.pixooClient.connected) {
                try {
                    await this.pixooClient.push();
                } catch (pushError) {
                    console.error('Failed to push to device:', pushError);
                    // Don't stop the scene, just log the error
                    // The pixooClient will handle marking itself as disconnected
                }
            }

        } catch (error) {
            console.error('Error during scene render:', error);
        }
    }

    async renderPreview() {
        // Render scene for preview purposes (doesn't require active state or connection)
        try {
            // Clear the buffer
            await this.pixooClient.clear();

            // Render all widgets
            for (const widget of this.widgets.values()) {
                if (widget.isEnabled()) {
                    await widget.render();
                }
            }

            // Don't push to device - this is just for preview

        } catch (error) {
            console.error('Error during preview render:', error);
        }
    }

    setRefreshRate(rate) {
        this.refreshRate = Math.max(100, rate); // Minimum 100ms

        // Restart the render loop with new rate if scene is active
        if (this.isActive && this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = setInterval(() => {
                this.render();
            }, this.refreshRate);
        }
    }

    toJSON() {
        return {
            id: this.id,
            name: this.name,
            description: this.description,
            refreshRate: this.refreshRate,
            widgets: Array.from(this.widgets.values()).map(w => w.toJSON())
        };
    }
}

window.SceneManager = SceneManager;
window.Scene = Scene;