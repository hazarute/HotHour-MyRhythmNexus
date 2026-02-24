// src/stores/socket.js
import { defineStore } from 'pinia'

// If SocketService export default new SocketService()
// import socketService from '../services/socket.js'
// But wait, Pinia stores must be setup in `main.js`.
// I'll stick to a store that encapsulates socket logic or uses the service.

// Let's integrate SocketService and Pinia Store together
// The store will provide reactive state (isConnected)
// The service handles raw connection logic

import SocketService from '../services/socket.js'

export const useSocketStore = defineStore('socket', {
  state: () => ({
    isConnected: false,
    socketId: null,
  }),

  actions: {
    connect() {
      if (this.isConnected) return

      SocketService.connect()

      // Bind service events to store state
      SocketService.on('connect', () => {
        this.isConnected = true
        this.socketId = SocketService.socket.id
      })

      SocketService.on('disconnect', () => {
        this.isConnected = false
        this.socketId = null
      })
    },

    disconnect() {
      SocketService.disconnect()
      this.isConnected = false
      this.socketId = null
    },

    subscribeAuction(auctionId) {
      SocketService.subscribeAuction(auctionId)
    },

    unsubscribeAuction(auctionId) {
      SocketService.unsubscribeAuction(auctionId)
    },

    subscribeUser(userId) {
      SocketService.subscribeUser(userId)
    },

    // Add listener for specific event
    on(event, callback) {
      SocketService.on(event, callback)
    },

    off(event, callback) {
      SocketService.off(event, callback)
    }
  }
})
