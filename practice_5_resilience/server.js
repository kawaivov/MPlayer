import express from "express";
import cors from "cors";
import { randomUUID } from "crypto";

const app = express();
app.use(cors());
app.use(express.json());

// --- Зберігання стану (In-Memory) ---
const idemStore = new Map(); // Idempotency-Key -> { status, body }
const rate = new Map();      // IP -> { count, ts }

// Конфігурація
const WINDOW_MS = 10_000;
const MAX_REQ = 5; // Зменшив до 5, щоб легше було відтворити 429
const PORT = 8081;

// --- Middleware 1: X-Request-Id ---
app.use((req, res, next) => {
    const rid = req.get("X-Request-Id") || randomUUID();
    req.rid = rid;
    res.setHeader("X-Request-Id", rid);
    next();
});

// --- Middleware 2: Rate Limiting ---
app.use((req, res, next) => {
    // Пропускаємо preflight запити
    if (req.method === 'OPTIONS') return next();

    const ip = req.headers["x-forwarded-for"] || req.socket.remoteAddress || "local";
    const now = Date.now();
    
    const record = rate.get(ip) ?? { count: 0, ts: now };
    const isWithinWindow = now - record.ts < WINDOW_MS;

    if (isWithinWindow) {
        if (record.count >= MAX_REQ) {
            res.setHeader("Retry-After", "3"); // Чекати 3 секунди
            return res.status(429).json({
                error: "too_many_requests",
                code: "RATE_LIMIT_EXCEEDED",
                details: "Try again later",
                requestId: req.rid
            });
        }
        record.count++;
    } else {
        rate.set(ip, { count: 1, ts: now });
    }
    next();
});

// --- Middleware 3: Chaos Monkey (Симуляція збоїв) ---
app.use(async (req, res, next) => {
    if (req.path === '/health') return next(); // Health check не чіпаємо

    const r = Math.random();
    
    // 20% шанс затримки (simulating network lag)
    if (r < 0.20) {
        await new Promise(resolve => setTimeout(resolve, 1500)); 
    }

    // 15% шанс критичної помилки (500/503)
    if (r > 0.85) {
        const isServiceUnavailable = Math.random() < 0.5;
        const status = isServiceUnavailable ? 503 : 500;
        const errorType = isServiceUnavailable ? "service_unavailable" : "internal_server_error";
        
        return res.status(status).json({
            error: errorType,
            code: status === 503 ? "SERVER_BUSY" : "CRASH",
            requestId: req.rid
        });
    }
    
    next();
});

// --- Routes ---

// Ідемпотентний POST
app.post("/orders", (req, res) => {
    const key = req.get("Idempotency-Key");

    // Перевірка наявності ключа
    if (!key) {
        return res.status(400).json({
            error: "bad_request",
            code: "IDEMPOTENCY_KEY_MISSING",
            requestId: req.rid
        });
    }

    // 1. Перевірка ідемпотентності
    if (idemStore.has(key)) {
        console.log(`[Server] Returning cached response for key: ${key}`);
        const cached = idemStore.get(key);
        return res.status(cached.status).json({ ...cached.body, requestId: req.rid, cached: true });
    }

    // 2. Обробка "нового" запиту
    const newOrder = {
        id: "ord_" + randomUUID().slice(0, 8),
        title: req.body?.title || "Untitled",
        createdAt: new Date().toISOString(),
        status: "created"
    };

    // 3. Збереження результату
    idemStore.set(key, { status: 201, body: newOrder });

    console.log(`[Server] Created new order: ${newOrder.id}`);
    return res.status(201).json({ ...newOrder, requestId: req.rid });
});

// Health check
app.get("/health", (req, res) => {
    res.json({ status: "ok" });
});

app.listen(PORT, () => {
    console.log(`Server running on http://localhost:${PORT}`);
});