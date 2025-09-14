class Widget {
    static TYPE = 'base';
    static NAME = 'Base Widget';
    static DESCRIPTION = 'Base widget class';
    static ICON = '🔲';

    constructor(id, config = {}, pixooClient) {
        this.id = id;
        this.config = { ...this.getDefaultConfig(), ...config };
        this.pixooClient = pixooClient;
        this.initialized = false;
        this.enabled = true;
        this.x = this.config.x || 0;
        this.y = this.config.y || 0;
        this.width = this.config.width || 64;
        this.height = this.config.height || 64;
        this.lastUpdate = 0;
        this.updateInterval = this.config.updateInterval || 1000;
    }

    getDefaultConfig() {
        return {
            x: 0,
            y: 0,
            width: 64,
            height: 64,
            updateInterval: 1000,
            enabled: true
        };
    }

    init() {
        if (this.initialized) return;

        this.initialized = true;
        this.onInit();
        console.log(`Widget ${this.id} initialized`);
    }

    destroy() {
        if (!this.initialized) return;

        this.onDestroy();
        this.initialized = false;
        console.log(`Widget ${this.id} destroyed`);
    }

    async render() {
        if (!this.initialized || !this.enabled) return;

        const now = Date.now();
        if (now - this.lastUpdate >= this.updateInterval) {
            await this.onRender();
            this.lastUpdate = now;
        }
    }

    onInit() {
        // Override in subclasses
    }

    onDestroy() {
        // Override in subclasses
    }

    async onRender() {
        // Override in subclasses
    }

    updateConfig(newConfig) {
        this.config = { ...this.config, ...newConfig };
        this.x = this.config.x || this.x;
        this.y = this.config.y || this.y;
        this.width = this.config.width || this.width;
        this.height = this.config.height || this.height;
        this.updateInterval = this.config.updateInterval || this.updateInterval;
        this.enabled = this.config.enabled !== undefined ? this.config.enabled : this.enabled;

        this.onConfigUpdate();
    }

    onConfigUpdate() {
        // Override in subclasses
    }

    isEnabled() {
        return this.enabled;
    }

    setEnabled(enabled) {
        this.enabled = enabled;
    }

    toJSON() {
        return {
            id: this.id,
            type: this.constructor.TYPE,
            config: this.config,
            enabled: this.enabled
        };
    }

    // Helper methods for drawing
    async setPixel(x, y, color) {
        const screenX = this.x + x;
        const screenY = this.y + y;

        if (screenX >= 0 && screenX < 64 && screenY >= 0 && screenY < 64) {
            await this.pixooClient.setPixel(screenX, screenY, color);
        }
    }

    async drawRect(x, y, width, height, color, filled = false) {
        if (filled) {
            for (let dy = 0; dy < height; dy++) {
                for (let dx = 0; dx < width; dx++) {
                    await this.setPixel(x + dx, y + dy, color);
                }
            }
        } else {
            // Draw rectangle outline
            for (let dx = 0; dx < width; dx++) {
                await this.setPixel(x + dx, y, color); // Top
                await this.setPixel(x + dx, y + height - 1, color); // Bottom
            }
            for (let dy = 0; dy < height; dy++) {
                await this.setPixel(x, y + dy, color); // Left
                await this.setPixel(x + width - 1, y + dy, color); // Right
            }
        }
    }

    async drawLine(x1, y1, x2, y2, color) {
        const dx = Math.abs(x2 - x1);
        const dy = Math.abs(y2 - y1);
        const sx = x1 < x2 ? 1 : -1;
        const sy = y1 < y2 ? 1 : -1;
        let err = dx - dy;

        let currentX = x1;
        let currentY = y1;

        while (true) {
            await this.setPixel(currentX, currentY, color);

            if (currentX === x2 && currentY === y2) break;

            const e2 = 2 * err;
            if (e2 > -dy) {
                err -= dy;
                currentX += sx;
            }
            if (e2 < dx) {
                err += dx;
                currentY += sy;
            }
        }
    }

    async drawText(text, x, y, color = [255, 255, 255]) {
        // Simple bitmap font rendering using pixel drawing
        // This creates a basic 5x7 pixel font for each character
        const font = {
            '0': [0x3E, 0x51, 0x49, 0x45, 0x3E],
            '1': [0x00, 0x42, 0x7F, 0x40, 0x00],
            '2': [0x42, 0x61, 0x51, 0x49, 0x46],
            '3': [0x21, 0x41, 0x45, 0x4B, 0x31],
            '4': [0x18, 0x14, 0x12, 0x7F, 0x10],
            '5': [0x27, 0x45, 0x45, 0x45, 0x39],
            '6': [0x3C, 0x4A, 0x49, 0x49, 0x30],
            '7': [0x01, 0x71, 0x09, 0x05, 0x03],
            '8': [0x36, 0x49, 0x49, 0x49, 0x36],
            '9': [0x06, 0x49, 0x49, 0x29, 0x1E],
            ':': [0x00, 0x36, 0x36, 0x00, 0x00],
            ' ': [0x00, 0x00, 0x00, 0x00, 0x00],
            'A': [0x7E, 0x09, 0x09, 0x09, 0x7E],
            'B': [0x7F, 0x49, 0x49, 0x49, 0x36],
            'C': [0x3E, 0x41, 0x41, 0x41, 0x22],
            'D': [0x7F, 0x41, 0x41, 0x22, 0x1C],
            'E': [0x7F, 0x49, 0x49, 0x49, 0x41],
            'F': [0x7F, 0x09, 0x09, 0x09, 0x01],
            'G': [0x3E, 0x41, 0x49, 0x49, 0x7A],
            'H': [0x7F, 0x08, 0x08, 0x08, 0x7F],
            'I': [0x00, 0x41, 0x7F, 0x41, 0x00],
            'L': [0x7F, 0x40, 0x40, 0x40, 0x40],
            'M': [0x7F, 0x02, 0x0C, 0x02, 0x7F],
            'P': [0x7F, 0x09, 0x09, 0x09, 0x06],
            'a': [0x20, 0x54, 0x54, 0x54, 0x78],
            'e': [0x38, 0x54, 0x54, 0x54, 0x18],
            'l': [0x00, 0x41, 0x7F, 0x40, 0x00],
            'o': [0x38, 0x44, 0x44, 0x44, 0x38],
            'r': [0x7C, 0x08, 0x04, 0x04, 0x08],
            'W': [0x7F, 0x20, 0x18, 0x20, 0x7F],
            'd': [0x38, 0x44, 0x44, 0x48, 0x7F],
            '!': [0x00, 0x00, 0x5F, 0x00, 0x00],
            '.': [0x00, 0x60, 0x60, 0x00, 0x00],
            '%': [0x23, 0x13, 0x08, 0x64, 0x62]
        };

        let currentX = x;
        for (let i = 0; i < text.length; i++) {
            const char = text[i];
            const charData = font[char] || font[char.toUpperCase()] || font[' '];

            for (let col = 0; col < 5; col++) {
                const columnData = charData[col];
                for (let row = 0; row < 7; row++) {
                    if (columnData & (1 << (6 - row))) {
                        await this.setPixel(currentX + col, y + row, color);
                    }
                }
            }
            currentX += 6; // 5 pixels + 1 space
        }
    }

    // Utility methods
    constrainToWidget(x, y) {
        return {
            x: Math.max(0, Math.min(x, this.width - 1)),
            y: Math.max(0, Math.min(y, this.height - 1))
        };
    }

    isPointInWidget(x, y) {
        return x >= 0 && x < this.width && y >= 0 && y < this.height;
    }
}

// Specialized widget types
class AnimatedWidget extends Widget {
    constructor(id, config, pixooClient) {
        super(id, config, pixooClient);
        this.animationFrame = 0;
        this.animationSpeed = this.config.animationSpeed || 100;
    }

    getDefaultConfig() {
        return {
            ...super.getDefaultConfig(),
            animationSpeed: 100
        };
    }

    async render() {
        if (!this.initialized || !this.enabled) return;

        const now = Date.now();
        if (now - this.lastUpdate >= this.animationSpeed) {
            await this.onAnimationFrame(this.animationFrame);
            this.animationFrame++;
            this.lastUpdate = now;
        }
    }

    async onAnimationFrame(frame) {
        // Override in subclasses
    }

    resetAnimation() {
        this.animationFrame = 0;
    }
}

class DataWidget extends Widget {
    constructor(id, config, pixooClient) {
        super(id, config, pixooClient);
        this.data = null;
        this.lastDataFetch = 0;
        this.dataFetchInterval = this.config.dataFetchInterval || 30000; // 30 seconds
    }

    getDefaultConfig() {
        return {
            ...super.getDefaultConfig(),
            dataFetchInterval: 30000
        };
    }

    async render() {
        if (!this.initialized || !this.enabled) return;

        const now = Date.now();

        // Check if we need to fetch new data
        if (now - this.lastDataFetch >= this.dataFetchInterval) {
            try {
                this.data = await this.fetchData();
                this.lastDataFetch = now;
            } catch (error) {
                console.error(`Failed to fetch data for widget ${this.id}:`, error);
            }
        }

        // Render with current data
        if (now - this.lastUpdate >= this.updateInterval) {
            await this.onRenderWithData(this.data);
            this.lastUpdate = now;
        }
    }

    async fetchData() {
        // Override in subclasses
        return null;
    }

    async onRenderWithData(data) {
        // Override in subclasses
    }

    refreshData() {
        this.lastDataFetch = 0;
    }
}

window.Widget = Widget;
window.AnimatedWidget = AnimatedWidget;
window.DataWidget = DataWidget;