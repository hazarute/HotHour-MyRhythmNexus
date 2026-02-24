import { io } from "socket.io-client";

// Using Vite environment variables (import.meta.env)
// If VITE_API_URL is not set, default to localhost:8000
const SOCKET_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

class SocketService {
  constructor() {
    this.socket = null;
    this.isConnected = false;
  }

  connect() {
    if (this.socket && this.socket.connected) return;

    this.socket = io(SOCKET_URL, {
      path: "/socket.io/",
      transports: ["websocket", "polling"],
      reconnectionAttempts: 5,
      reconnectionDelay: 2000,
    });

    this.socket.on("connect", () => {
      console.log("[SocketService] Connected:", this.socket.id);
      this.isConnected = true;
    });

    this.socket.on("disconnect", (reason) => {
      console.warn("[SocketService] Disconnected:", reason);
      this.isConnected = false;
    });

    this.socket.on("connect_error", (error) => {
      console.error("[SocketService] Connection Error:", error);
    });
  }

  disconnect() {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
      this.isConnected = false;
    }
  }

  // Room Subscription Methods
  subscribeAuction(auctionId) {
    if (!this.socket) return;
    console.log(`[SocketService] Subscribing to auction:${auctionId}`);
    this.socket.emit("subscribe_auction", { auction_id: auctionId });
  }

  unsubscribeAuction(auctionId) {
    if (!this.socket) return;
    console.log(`[SocketService] Unsubscribing from auction:${auctionId}`);
    this.socket.emit("unsubscribe_auction", { auction_id: auctionId });
  }

  subscribeUser(userId) {
    if (!this.socket) return;
    console.log(`[SocketService] Subscribing to user:${userId}`);
    this.socket.emit("subscribe_user", { user_id: userId });
  }

  // Event Listeners
  on(event, callback) {
    if (!this.socket) return;
    this.socket.on(event, callback);
  }

  off(event, callback) {
    if (!this.socket) return;
    this.socket.off(event, callback);
  }
}

export default new SocketService();
