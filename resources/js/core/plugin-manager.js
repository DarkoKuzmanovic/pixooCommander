class PluginManager {
    constructor() {
        this.plugins = new Map();
        this.widgetTypes = new Map();
        this.loadedPlugins = new Set();
    }

    async loadPlugin(pluginPath) {
        if (this.loadedPlugins.has(pluginPath)) {
            console.warn(`Plugin ${pluginPath} is already loaded`);
            return false;
        }

        try {
            // For NeutralinoJS environment, we'll load plugins dynamically
            const script = document.createElement('script');
            script.src = pluginPath;

            await new Promise((resolve, reject) => {
                script.onload = resolve;
                script.onerror = reject;
                document.head.appendChild(script);
            });

            this.loadedPlugins.add(pluginPath);
            console.log(`Plugin loaded: ${pluginPath}`);
            return true;

        } catch (error) {
            console.error(`Failed to load plugin ${pluginPath}:`, error);
            return false;
        }
    }

    registerPlugin(plugin) {
        console.log('Registering plugin:', plugin.id, 'with', plugin.widgets?.length || 0, 'widgets');

        if (!plugin.id || !plugin.name || !plugin.version) {
            throw new Error('Plugin must have id, name, and version properties');
        }

        if (this.plugins.has(plugin.id)) {
            throw new Error(`Plugin with ID ${plugin.id} is already registered`);
        }

        this.plugins.set(plugin.id, plugin);

        // Register widget types provided by this plugin
        if (plugin.widgets && Array.isArray(plugin.widgets)) {
            console.log('Registering widgets:', plugin.widgets.map(w => w.TYPE || w.name));
            plugin.widgets.forEach(widgetClass => {
                if (widgetClass.TYPE) {
                    this.registerWidgetType(widgetClass.TYPE, widgetClass);
                }
            });
        }

        // Call plugin initialization if it exists
        if (typeof plugin.init === 'function') {
            try {
                plugin.init();
            } catch (error) {
                console.error(`Failed to initialize plugin ${plugin.id}:`, error);
            }
        }

        console.log(`Plugin registered: ${plugin.name} v${plugin.version}`);

        // Notify UI that widgets have been updated
        if (window.uiManager && typeof window.uiManager.updateWidgetTypesDisplay === 'function') {
            console.log('Notifying UI manager of new widgets');
            window.uiManager.updateWidgetTypesDisplay();
        }
    }

    unregisterPlugin(pluginId) {
        if (!this.plugins.has(pluginId)) {
            return false;
        }

        const plugin = this.plugins.get(pluginId);

        // Unregister widget types
        if (plugin.widgets && Array.isArray(plugin.widgets)) {
            plugin.widgets.forEach(widgetClass => {
                if (widgetClass.TYPE) {
                    this.unregisterWidgetType(widgetClass.TYPE);
                }
            });
        }

        // Call plugin cleanup if it exists
        if (typeof plugin.destroy === 'function') {
            try {
                plugin.destroy();
            } catch (error) {
                console.error(`Failed to cleanup plugin ${pluginId}:`, error);
            }
        }

        this.plugins.delete(pluginId);
        console.log(`Plugin unregistered: ${pluginId}`);
        return true;
    }

    registerWidgetType(type, widgetClass) {
        if (this.widgetTypes.has(type)) {
            console.warn(`Widget type ${type} is already registered, overwriting`);
        }

        this.widgetTypes.set(type, widgetClass);
        console.log(`Widget type registered: ${type}`);
    }

    unregisterWidgetType(type) {
        return this.widgetTypes.delete(type);
    }

    getWidgetType(type) {
        return this.widgetTypes.get(type);
    }

    getAllWidgetTypes() {
        return Array.from(this.widgetTypes.keys());
    }

    getPlugin(pluginId) {
        return this.plugins.get(pluginId);
    }

    getAllPlugins() {
        return Array.from(this.plugins.values());
    }

    createWidget(type, config = {}) {
        const WidgetClass = this.widgetTypes.get(type);
        if (!WidgetClass) {
            throw new Error(`Unknown widget type: ${type}`);
        }

        return WidgetClass;
    }

    async loadBuiltinPlugins() {
        const builtinPlugins = [
            '/js/plugins/core-widgets.js'
        ];

        for (const pluginPath of builtinPlugins) {
            await this.loadPlugin(pluginPath);
        }
    }

    getWidgetTypesMetadata() {
        const metadata = {};

        for (const [type, widgetClass] of this.widgetTypes.entries()) {
            metadata[type] = {
                name: widgetClass.NAME || type,
                description: widgetClass.DESCRIPTION || 'No description available',
                icon: widgetClass.ICON || '🔲',
                configurable: Boolean(widgetClass.CONFIG_SCHEMA),
                configSchema: widgetClass.CONFIG_SCHEMA || {}
            };
        }

        return metadata;
    }
}

// Plugin base class
class Plugin {
    constructor(id, name, version, description = '') {
        this.id = id;
        this.name = name;
        this.version = version;
        this.description = description;
        this.widgets = [];
    }

    init() {
        // Override in subclasses
    }

    destroy() {
        // Override in subclasses
    }
}

window.PluginManager = PluginManager;
window.Plugin = Plugin;