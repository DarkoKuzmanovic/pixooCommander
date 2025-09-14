class PixooClient {
    constructor(ipAddress = null, size = 64) {
        this.ipAddress = ipAddress;
        this.size = size;
        this.connected = false;
        this.buffer = this.createBuffer();
    }

    createBuffer() {
        return Array(this.size).fill().map(() => Array(this.size).fill([0, 0, 0]));
    }

    async connect() {
        if (!this.ipAddress) {
            throw new Error('IP address not set');
        }

        // Try different ports and endpoints commonly used by Pixoo devices
        const endpoints = [
            { port: 80, path: '/post' },
            { port: 64, path: '/post' },
            { port: 80, path: '/api/post' },
            { port: 8080, path: '/post' },
            { port: 443, path: '/post' }
        ];

        let lastError;

        for (const endpoint of endpoints) {
            try {
                console.log(`Trying connection to ${this.ipAddress}:${endpoint.port}${endpoint.path}`);

                // Test connection with a simple API call
                const testPayload = {
                    Command: "Channel/GetIndex"
                };

                const response = await fetch(`http://${this.ipAddress}:${endpoint.port}${endpoint.path}`, {
                    method: 'POST',
                    mode: 'no-cors', // Bypass CORS for local device communication
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(testPayload),
                    signal: AbortSignal.timeout(3000) // 3 second timeout per attempt
                });

                // With no-cors mode, we can't check response.ok, so assume success if no error was thrown
                // Store the working endpoint
                this.port = endpoint.port;
                this.path = endpoint.path;
                this.connected = true;
                console.log(`Successfully connected to Pixoo device at ${this.ipAddress}:${endpoint.port}${endpoint.path}`);
                return;

            } catch (error) {
                lastError = error;
                console.log(`Failed to connect on port ${endpoint.port}: ${error.message}`);
            }
        }

        // If we get here, none of the endpoints worked
        this.connected = false;
        throw new Error(`Failed to connect to Pixoo device on any port. Last error: ${lastError?.message || 'Unknown error'}`);
    }

    async setPixel(x, y, color) {
        if (x >= 0 && x < this.size && y >= 0 && y < this.size) {
            this.buffer[y][x] = color;
        }
    }

    async drawText(text, x, y, color = [255, 255, 255]) {
        // Simple text drawing - this would be enhanced with a proper font system
        const payload = {
            Command: "Draw/SendHttpText",
            TextId: 1,
            x: x,
            y: y,
            dir: 0,
            font: 0,
            TextWidth: text.length * 6,
            TextString: text,
            speed: 0,
            color: `rgb(${color[0]}, ${color[1]}, ${color[2]})`
        };

        return this.sendCommand(payload);
    }

    async drawImage(imageData, x = 0, y = 0) {
        const payload = {
            Command: "Draw/SendHttpGif",
            PicNum: 1,
            PicWidth: this.size,
            PicHeight: this.size,
            PicData: imageData,
            PicSpeed: 1000,
            PicId: 1
        };

        return this.sendCommand(payload);
    }

    async fillScreen(color) {
        for (let y = 0; y < this.size; y++) {
            for (let x = 0; x < this.size; x++) {
                this.buffer[y][x] = color;
            }
        }
    }

    async clear() {
        this.fillScreen([0, 0, 0]);
    }

    async push() {
        // Convert buffer to the format expected by Pixoo
        const picData = this.bufferToPicData();

        const payload = {
            Command: "Draw/SendHttpGif",
            PicNum: 1,
            PicWidth: this.size,
            PicHeight: this.size,
            PicData: picData,
            PicSpeed: 1000,
            PicId: 1
        };

        return this.sendCommand(payload);
    }

    bufferToPicData() {
        let result = '';
        for (let y = 0; y < this.size; y++) {
            for (let x = 0; x < this.size; x++) {
                const [r, g, b] = this.buffer[y][x];
                // Convert RGB to hex and pad with zeros
                const hex = ((r << 16) | (g << 8) | b).toString(16).padStart(6, '0');
                result += hex;
            }
        }
        return result;
    }

    async sendCommand(payload, retryCount = 3) {
        if (!this.connected) {
            throw new Error('Not connected to Pixoo device');
        }

        // Use the endpoint that was discovered during connection
        const port = this.port || 80;
        const path = this.path || '/post';

        for (let attempt = 1; attempt <= retryCount; attempt++) {
            try {
                const controller = new AbortController();
                const timeoutId = setTimeout(() => controller.abort(), 5000); // 5 second timeout

                const response = await fetch(`http://${this.ipAddress}:${port}${path}`, {
                    method: 'POST',
                    mode: 'no-cors', // Bypass CORS for local device communication
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(payload),
                    signal: controller.signal
                });

                clearTimeout(timeoutId);

                // With no-cors mode, we can't read the response body or check status
                // Just assume success if no error was thrown
                console.log(`Command sent to Pixoo device: ${payload.Command}${attempt > 1 ? ` (attempt ${attempt})` : ''}`);
                return { success: true };

            } catch (error) {
                console.log(`Attempt ${attempt}/${retryCount} failed for command ${payload.Command}: ${error.message}`);

                // If this is the last attempt, handle the error
                if (attempt === retryCount) {
                    console.error('Failed to send command to Pixoo:', error);

                    // If we get a connection error, mark as disconnected
                    if (error.message.includes('Failed to fetch') ||
                        error.message.includes('NetworkError') ||
                        error.message.includes('TypeError') ||
                        error.message.includes('signal timed out') ||
                        error.name === 'TimeoutError' ||
                        error.name === 'AbortError') {
                        console.log('Connection lost, marking device as disconnected');
                        this.connected = false;

                        // Notify UI of disconnection
                        if (window.uiManager) {
                            const statusElement = document.getElementById('connection-status');
                            const connectBtn = document.getElementById('connect-btn');
                            if (statusElement && connectBtn) {
                                statusElement.textContent = 'Disconnected';
                                statusElement.className = 'disconnected';
                                connectBtn.textContent = 'Connect';
                            }
                        }
                    }

                    throw error;
                }

                // Wait before retrying (exponential backoff)
                await new Promise(resolve => setTimeout(resolve, Math.min(1000 * Math.pow(2, attempt - 1), 3000)));
            }
        }
    }

    async setBrightness(level) {
        if (level < 0 || level > 100) {
            throw new Error('Brightness level must be between 0 and 100');
        }

        const payload = {
            Command: "Channel/SetBrightness",
            Brightness: level
        };

        return this.sendCommand(payload);
    }

    async setChannel(channel) {
        const payload = {
            Command: "Channel/SetIndex",
            SelectIndex: channel
        };

        return this.sendCommand(payload);
    }
}

window.PixooClient = PixooClient;