export class SyncService {
    private ws: WebSocket | null = null;
    private isConnected: boolean = false;
    private messageHandlers: ((msg: any) => void)[] = [];

    // TAILSCALE IP (Works from anywhere if Tailscale VPN is On)
    // Local IP: 192.168.0.19 (Only works at home)
    private serverUrl = 'ws://100.114.243.42:8000/ws/sync/iphone-1';

    connect() {
        if (this.ws) {
            this.ws.close();
        }

        try {
            this.ws = new WebSocket(this.serverUrl);

            this.ws.onopen = () => {
                console.log('Connected to Sync Server');
                this.isConnected = true;
            };

            this.ws.onmessage = (e) => {
                try {
                    const data = JSON.parse(e.data);
                    this.messageHandlers.forEach(handler => handler(data));
                } catch (err) {
                    console.error('Failed to parse sync message', err);
                }
            };

            this.ws.onerror = (e) => {
                console.log('Sync Error:', e);
            };

            this.ws.onclose = () => {
                console.log('Sync Disconnected');
                this.isConnected = false;
                // Simple reconnect logic
                setTimeout(() => this.connect(), 5000);
            };
        } catch (e) {
            console.error('Connection failed', e);
        }
    }

    send(data: any) {
        if (this.ws && this.isConnected) {
            this.ws.send(JSON.stringify(data));
        }
    }

    onMessage(handler: (msg: any) => void) {
        this.messageHandlers.push(handler);
    }
}

export const syncService = new SyncService();
