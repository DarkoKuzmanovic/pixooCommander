// Core Widgets Plugin

class ClockWidget extends Widget {
    static TYPE = 'clock';
    static NAME = 'Digital Clock';
    static DESCRIPTION = 'Displays current time';
    static ICON = '🕐';

    getDefaultConfig() {
        return {
            ...super.getDefaultConfig(),
            format24: true,
            color: [255, 255, 255],
            backgroundColor: [0, 0, 0],
            fontSize: 'small',
            showSeconds: true
        };
    }

    async onRender() {
        const now = new Date();
        let timeString;

        if (this.config.format24) {
            timeString = now.toLocaleTimeString('en-GB', {
                hour12: false,
                hour: '2-digit',
                minute: '2-digit',
                second: this.config.showSeconds ? '2-digit' : undefined
            });
        } else {
            timeString = now.toLocaleTimeString('en-US', {
                hour12: true,
                hour: 'numeric',
                minute: '2-digit',
                second: this.config.showSeconds ? '2-digit' : undefined
            });
        }

        // Fill background
        if (this.config.backgroundColor[0] || this.config.backgroundColor[1] || this.config.backgroundColor[2]) {
            await this.drawRect(0, 0, this.width, this.height, this.config.backgroundColor, true);
        }

        // Draw time text
        await this.drawText(timeString, 2, 2, this.config.color);
    }
}

class WeatherWidget extends DataWidget {
    static TYPE = 'weather';
    static NAME = 'Weather Display';
    static DESCRIPTION = 'Shows current weather information';
    static ICON = '🌤️';

    getDefaultConfig() {
        return {
            ...super.getDefaultConfig(),
            location: 'London',
            units: 'metric',
            showIcon: true,
            color: [255, 255, 255]
        };
    }

    async fetchData() {
        // Note: In a real implementation, you'd use a proper weather API
        // This is a mock implementation
        return {
            temperature: Math.floor(Math.random() * 30) + 5,
            condition: ['Sunny', 'Cloudy', 'Rainy', 'Snowy'][Math.floor(Math.random() * 4)],
            humidity: Math.floor(Math.random() * 100)
        };
    }

    async onRenderWithData(data) {
        if (!data) {
            await this.drawText('Loading...', 2, 2, this.config.color);
            return;
        }

        const tempText = `${data.temperature}°C`;
        const conditionText = data.condition;

        await this.drawText(tempText, 2, 2, this.config.color);
        await this.drawText(conditionText, 2, 12, this.config.color);
        await this.drawText(`${data.humidity}%`, 2, 22, [100, 150, 255]);
    }
}

class CounterWidget extends Widget {
    static TYPE = 'counter';
    static NAME = 'Counter';
    static DESCRIPTION = 'Simple incrementing counter';
    static ICON = '🔢';

    constructor(id, config, pixooClient) {
        super(id, config, pixooClient);
        this.count = this.config.initialValue || 0;
        this.increment = this.config.increment || 1;
    }

    getDefaultConfig() {
        return {
            ...super.getDefaultConfig(),
            initialValue: 0,
            increment: 1,
            color: [0, 255, 0],
            autoIncrement: true,
            maxValue: 999
        };
    }

    async onRender() {
        if (this.config.autoIncrement) {
            this.count += this.increment;
            if (this.count > this.config.maxValue) {
                this.count = 0;
            }
        }

        const countText = this.count.toString();
        await this.drawText(countText, 2, 2, this.config.color);
    }

    onConfigUpdate() {
        this.count = this.config.initialValue || 0;
        this.increment = this.config.increment || 1;
    }
}

class ProgressBarWidget extends AnimatedWidget {
    static TYPE = 'progressbar';
    static NAME = 'Progress Bar';
    static DESCRIPTION = 'Animated progress bar';
    static ICON = '📊';

    constructor(id, config, pixooClient) {
        super(id, config, pixooClient);
        this.progress = 0;
        this.direction = 1;
    }

    getDefaultConfig() {
        return {
            ...super.getDefaultConfig(),
            width: 40,
            height: 8,
            color: [0, 255, 0],
            backgroundColor: [64, 64, 64],
            speed: 2,
            pingPong: true
        };
    }

    async onAnimationFrame(frame) {
        // Fill background
        await this.drawRect(0, 0, this.width, this.height, this.config.backgroundColor, true);

        // Draw progress
        const progressWidth = Math.floor((this.progress / 100) * this.width);
        if (progressWidth > 0) {
            await this.drawRect(0, 0, progressWidth, this.height, this.config.color, true);
        }

        // Update progress
        this.progress += this.config.speed * this.direction;

        if (this.config.pingPong) {
            if (this.progress >= 100) {
                this.progress = 100;
                this.direction = -1;
            } else if (this.progress <= 0) {
                this.progress = 0;
                this.direction = 1;
            }
        } else {
            if (this.progress > 100) {
                this.progress = 0;
            }
        }
    }
}

class TextScrollerWidget extends AnimatedWidget {
    static TYPE = 'textscroller';
    static NAME = 'Text Scroller';
    static DESCRIPTION = 'Scrolling text display';
    static ICON = '📜';

    constructor(id, config, pixooClient) {
        super(id, config, pixooClient);
        this.scrollPosition = 0;
    }

    getDefaultConfig() {
        return {
            ...super.getDefaultConfig(),
            text: 'Hello World!',
            color: [255, 255, 255],
            backgroundColor: [0, 0, 0],
            scrollSpeed: 1,
            direction: 'left'
        };
    }

    async onAnimationFrame(frame) {
        // Fill background
        if (this.config.backgroundColor[0] || this.config.backgroundColor[1] || this.config.backgroundColor[2]) {
            await this.drawRect(0, 0, this.width, this.height, this.config.backgroundColor, true);
        }

        // Calculate text position based on scroll
        let textX = this.scrollPosition;
        let textY = Math.floor(this.height / 2) - 4; // Center vertically

        if (this.config.direction === 'left') {
            textX = this.width - this.scrollPosition;
            this.scrollPosition += this.config.scrollSpeed;
            if (this.scrollPosition > this.width + (this.config.text.length * 6)) {
                this.scrollPosition = 0;
            }
        } else {
            textX = this.scrollPosition - (this.config.text.length * 6);
            this.scrollPosition += this.config.scrollSpeed;
            if (this.scrollPosition > this.width + (this.config.text.length * 6)) {
                this.scrollPosition = 0;
            }
        }

        await this.drawText(this.config.text, textX, textY, this.config.color);
    }
}

class BouncingBallWidget extends AnimatedWidget {
    static TYPE = 'bouncingball';
    static NAME = 'Bouncing Ball';
    static DESCRIPTION = 'Animated bouncing ball';
    static ICON = '⚽';

    constructor(id, config, pixooClient) {
        super(id, config, pixooClient);
        this.ballX = this.width / 2;
        this.ballY = this.height / 2;
        this.velocityX = 1;
        this.velocityY = 1;
        this.ballSize = this.config.ballSize || 2;
    }

    getDefaultConfig() {
        return {
            ...super.getDefaultConfig(),
            ballSize: 2,
            color: [255, 100, 100],
            backgroundColor: [0, 0, 0],
            speed: 1
        };
    }

    async onAnimationFrame(frame) {
        // Fill background
        if (this.config.backgroundColor[0] || this.config.backgroundColor[1] || this.config.backgroundColor[2]) {
            await this.drawRect(0, 0, this.width, this.height, this.config.backgroundColor, true);
        }

        // Update ball position
        this.ballX += this.velocityX * this.config.speed;
        this.ballY += this.velocityY * this.config.speed;

        // Bounce off walls
        if (this.ballX <= 0 || this.ballX >= this.width - this.ballSize) {
            this.velocityX *= -1;
            this.ballX = Math.max(0, Math.min(this.ballX, this.width - this.ballSize));
        }
        if (this.ballY <= 0 || this.ballY >= this.height - this.ballSize) {
            this.velocityY *= -1;
            this.ballY = Math.max(0, Math.min(this.ballY, this.height - this.ballSize));
        }

        // Draw ball
        await this.drawRect(
            Math.floor(this.ballX),
            Math.floor(this.ballY),
            this.ballSize,
            this.ballSize,
            this.config.color,
            true
        );
    }

    onConfigUpdate() {
        super.onConfigUpdate();
        this.ballSize = this.config.ballSize || 2;
    }
}

class SystemInfoWidget extends DataWidget {
    static TYPE = 'systeminfo';
    static NAME = 'System Info';
    static DESCRIPTION = 'Shows basic system information';
    static ICON = '💻';

    getDefaultConfig() {
        return {
            ...super.getDefaultConfig(),
            showMemory: true,
            showTime: true,
            color: [100, 255, 100]
        };
    }

    async fetchData() {
        // Mock system data - in a real NeutralinoJS app, you could use the OS API
        return {
            memory: `${Math.floor(Math.random() * 8 + 4)}GB`,
            time: new Date().toLocaleTimeString(),
            cpu: `${Math.floor(Math.random() * 100)}%`
        };
    }

    async onRenderWithData(data) {
        if (!data) {
            await this.drawText('Loading...', 2, 2, this.config.color);
            return;
        }

        let y = 2;
        if (this.config.showMemory) {
            await this.drawText(`RAM: ${data.memory}`, 2, y, this.config.color);
            y += 10;
        }

        await this.drawText(`CPU: ${data.cpu}`, 2, y, this.config.color);
        y += 10;

        if (this.config.showTime) {
            await this.drawText(data.time, 2, y, this.config.color);
        }
    }
}

// Register the core widgets plugin
const coreWidgetsPlugin = new Plugin(
    'core-widgets',
    'Core Widgets',
    '1.0.0',
    'Essential widgets for Pixoo Commander'
);

coreWidgetsPlugin.widgets = [
    ClockWidget,
    WeatherWidget,
    CounterWidget,
    ProgressBarWidget,
    TextScrollerWidget,
    BouncingBallWidget,
    SystemInfoWidget
];

// Auto-register the plugin when this script loads
if (window.pluginManager) {
    console.log('Registering core widgets plugin immediately');
    window.pluginManager.registerPlugin(coreWidgetsPlugin);
} else {
    // If plugin manager isn't ready yet, wait for it
    console.log('Plugin manager not ready, waiting...');
    const checkInterval = setInterval(() => {
        if (window.pluginManager) {
            console.log('Plugin manager ready, registering core widgets plugin');
            window.pluginManager.registerPlugin(coreWidgetsPlugin);
            clearInterval(checkInterval);
        }
    }, 50); // Check more frequently
}

window.CoreWidgetsPlugin = coreWidgetsPlugin;