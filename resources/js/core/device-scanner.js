class DeviceScanner {
    constructor() {
        this.isScanning = false;
        this.discoveredDevices = new Map();
        this.scanTimeout = 5000; // 5 seconds timeout per device
    }

    async scanNetwork(baseIp = null) {
        if (this.isScanning) {
            console.log('Scan already in progress');
            return Array.from(this.discoveredDevices.values());
        }

        this.isScanning = true;
        this.discoveredDevices.clear();

        console.log('Starting Pixoo device scan...');

        try {
            // If no base IP provided, try to detect local network
            if (!baseIp) {
                baseIp = await this.detectLocalNetwork();
            }

            if (!baseIp) {
                throw new Error('Could not determine local network range');
            }

            console.log(`Scanning network: ${baseIp}.x`);

            // Scan common IP ranges in parallel
            const scanPromises = [];

            // Scan 192.168.x.1 to 192.168.x.254
            for (let i = 1; i <= 254; i++) {
                const ip = `${baseIp}.${i}`;
                scanPromises.push(this.testDevice(ip));
            }

            // Wait for all scans to complete with a reasonable timeout
            await Promise.allSettled(scanPromises);

            console.log(`Scan completed. Found ${this.discoveredDevices.size} Pixoo devices.`);

        } catch (error) {
            console.error('Network scan failed:', error);
        } finally {
            this.isScanning = false;
        }

        return Array.from(this.discoveredDevices.values());
    }

    async testDevice(ip) {
        // Try different ports and endpoints commonly used by Pixoo devices
        const endpoints = [
            { port: 80, path: '/post' },
            { port: 64, path: '/post' },
            { port: 80, path: '/api/post' },
            { port: 8080, path: '/post' }
        ];

        for (const endpoint of endpoints) {
            try {
                // Test if device responds to Pixoo API
                const response = await fetch(`http://${ip}:${endpoint.port}${endpoint.path}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        Command: "Device/GetDeviceInfo"
                    }),
                    signal: AbortSignal.timeout(this.scanTimeout)
                });

                if (response.ok) {
                    const data = await response.json();

                    // Check if this looks like a Pixoo device response
                    if (this.isPixooDevice(data)) {
                        const deviceInfo = {
                            ip: ip,
                            port: endpoint.port,
                            path: endpoint.path,
                            name: this.extractDeviceName(data),
                            model: this.extractDeviceModel(data),
                            size: this.extractDeviceSize(data),
                            response: data,
                            discoveredAt: new Date().toISOString()
                        };

                        this.discoveredDevices.set(ip, deviceInfo);
                        console.log(`Found Pixoo device at ${ip}:${endpoint.port}:`, deviceInfo.name);
                        return; // Stop trying other endpoints once we find one that works
                    }
                }

            } catch (error) {
                // Continue trying other endpoints
            }
        }
    }

    isPixooDevice(response) {
        // Check if response looks like a Pixoo device
        if (!response || typeof response !== 'object') {
            return false;
        }

        // Look for common Pixoo response indicators
        const indicators = [
            'error_code' in response,
            'ReturnCode' in response,
            'DeviceName' in response,
            'DeviceId' in response,
            'brightness' in response,
            'channel' in response
        ];

        // If at least 2 indicators are present, it's likely a Pixoo
        return indicators.filter(Boolean).length >= 2;
    }

    extractDeviceName(response) {
        // Try to extract device name from various possible fields
        return response.DeviceName ||
               response.device_name ||
               response.name ||
               'Pixoo Device';
    }

    extractDeviceModel(response) {
        // Try to extract device model
        return response.DeviceModel ||
               response.model ||
               response.HardwareInfo ||
               'Unknown';
    }

    extractDeviceSize(response) {
        // Try to determine screen size
        if (response.DeviceModel && response.DeviceModel.includes('64')) {
            return 64;
        }
        if (response.DeviceModel && response.DeviceModel.includes('32')) {
            return 32;
        }
        if (response.DeviceModel && response.DeviceModel.includes('16')) {
            return 16;
        }
        return 64; // Default to 64x64
    }

    async detectLocalNetwork() {
        try {
            // Try to get local IP using WebRTC
            const ip = await this.getLocalIP();
            if (ip) {
                // Extract network portion (e.g., "192.168.1.100" -> "192.168.1")
                const parts = ip.split('.');
                if (parts.length === 4) {
                    return `${parts[0]}.${parts[1]}.${parts[2]}`;
                }
            }
        } catch (error) {
            console.log('Could not detect local IP via WebRTC:', error.message);
        }

        // Fallback to common network ranges
        const commonRanges = [
            '192.168.1',
            '192.168.0',
            '192.168.2',
            '10.0.0',
            '10.0.1',
            '172.16.0'
        ];

        // Return the first common range as fallback
        return commonRanges[0];
    }

    async getLocalIP() {
        return new Promise((resolve, reject) => {
            const timeout = setTimeout(() => {
                reject(new Error('Timeout getting local IP'));
            }, 5000);

            try {
                const pc = new RTCPeerConnection({
                    iceServers: [{ urls: 'stun:stun.l.google.com:19302' }]
                });

                pc.createDataChannel('');

                pc.createOffer()
                    .then(offer => pc.setLocalDescription(offer))
                    .catch(reject);

                pc.onicecandidate = (ice) => {
                    if (ice && ice.candidate && ice.candidate.candidate) {
                        const candidate = ice.candidate.candidate;
                        const match = candidate.match(/(\d+\.\d+\.\d+\.\d+)/);

                        if (match && match[1]) {
                            const ip = match[1];
                            // Filter out non-local IPs
                            if (ip.startsWith('192.168.') ||
                                ip.startsWith('10.') ||
                                ip.startsWith('172.')) {
                                clearTimeout(timeout);
                                pc.close();
                                resolve(ip);
                            }
                        }
                    }
                };

            } catch (error) {
                clearTimeout(timeout);
                reject(error);
            }
        });
    }

    async scanCommonRanges() {
        const commonRanges = [
            '192.168.1',
            '192.168.0',
            '192.168.2',
            '10.0.0',
            '10.0.1'
        ];

        console.log('Scanning common network ranges...');

        for (const range of commonRanges) {
            console.log(`Scanning ${range}.x...`);
            const devices = await this.scanNetwork(range);

            if (devices.length > 0) {
                console.log(`Found ${devices.length} devices in ${range}.x`);
                return devices;
            }
        }

        return Array.from(this.discoveredDevices.values());
    }

    getDiscoveredDevices() {
        return Array.from(this.discoveredDevices.values());
    }

    clearDiscoveredDevices() {
        this.discoveredDevices.clear();
    }

    isScanning() {
        return this.isScanning;
    }
}

window.DeviceScanner = DeviceScanner;