// Pixoo Commander - Main Application

class PixooCommanderApp {
    constructor() {
        this.pixooClient = null;
        this.sceneManager = null;
        this.pluginManager = null;
        this.uiManager = null;

        this.initialize();
    }

    async initialize() {
        console.log('Initializing Pixoo Commander...');

        try {
            // Initialize core systems
            this.pixooClient = new PixooClient();
            this.sceneManager = new SceneManager(this.pixooClient);
            this.pluginManager = new PluginManager();

            // Make plugin manager globally accessible before loading plugins
            window.pluginManager = this.pluginManager;
            window.sceneManager = this.sceneManager;
            window.pixooClient = this.pixooClient;

            // Load built-in plugins
            await this.pluginManager.loadBuiltinPlugins();

            // Initialize UI
            this.uiManager = new UIManager(
                this.sceneManager,
                this.pluginManager,
                this.pixooClient
            );

            // Make UI manager globally accessible
            window.uiManager = this.uiManager;

            // Create a default scene
            this.createDefaultScene();

            console.log('Pixoo Commander initialized successfully');

        } catch (error) {
            console.error('Failed to initialize Pixoo Commander:', error);
            this.showError('Failed to initialize application: ' + error.message);
        }
    }

    createDefaultScene() {
        try {
            const defaultScene = this.sceneManager.createScene(
                'Welcome Scene',
                'Default scene with example widgets'
            );

            // Add some default widgets
            const clockWidget = defaultScene.addWidget(ClockWidget, {
                x: 2,
                y: 2,
                width: 60,
                height: 10,
                format24: true,
                color: [0, 255, 255]
            });

            const counterWidget = defaultScene.addWidget(CounterWidget, {
                x: 2,
                y: 20,
                color: [255, 255, 0],
                increment: 1,
                maxValue: 100
            });

            const progressWidget = defaultScene.addWidget(ProgressBarWidget, {
                x: 10,
                y: 40,
                width: 40,
                height: 6,
                color: [255, 100, 100],
                speed: 1
            });

            // Update UI to reflect the new scene
            this.uiManager.updateScenesDisplay();
            this.uiManager.updateSceneEditor();

            // Start the default scene for preview
            defaultScene.start();

            console.log('Default scene created with sample widgets');

        } catch (error) {
            console.error('Failed to create default scene:', error);
        }
    }

    showError(message) {
        // Simple error display - in a real app you might want a more sophisticated error handling
        const errorDiv = document.createElement('div');
        errorDiv.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #dc2626;
            color: white;
            padding: 1rem;
            border-radius: 4px;
            z-index: 10000;
            max-width: 400px;
        `;
        errorDiv.textContent = message;

        document.body.appendChild(errorDiv);

        // Remove after 5 seconds
        setTimeout(() => {
            if (errorDiv.parentNode) {
                errorDiv.parentNode.removeChild(errorDiv);
            }
        }, 5000);
    }
}

// Initialize the application when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.pixooCommanderApp = new PixooCommanderApp();
});

// Handle app shutdown
window.addEventListener('beforeunload', () => {
    if (window.sceneManager) {
        // Stop all active scenes
        const activeScene = window.sceneManager.getActiveScene();
        if (activeScene) {
            activeScene.stop();
        }
    }
});

// NeutralinoJS event handling
Neutralino.init();

Neutralino.events.on('windowClose', () => {
    Neutralino.app.exit();
});

// Export for global access
window.PixooCommanderApp = PixooCommanderApp;