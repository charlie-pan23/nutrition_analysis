import { io } from "socket.io-client";

const socket = io("ws://localhost:7777"); // 替换为你的 Flask 地址

socket.on("connect", () => {
  console.log("Connected to server");
});

socket.on("connect_error", (err) => {
  console.error("Connection error:", err);
});

socket.on("disconnect", () => {
  console.log("Disconnected from server");
});

export default socket;
